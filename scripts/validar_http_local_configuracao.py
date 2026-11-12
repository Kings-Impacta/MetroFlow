"""Laboratorio HTTP local de configuracao ausente; nunca conecta ao Xano.

Usa exportacao e fixtures locais como referencia. SQLite/autenticacao sao locais;
nao simula uma instancia nativa do Xano. Requer Node.js ja instalado.
"""
from __future__ import annotations
import argparse
import copy
from contextlib import contextmanager
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import secrets
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import httpx
from MetroFlow.planning.infrastructure.xano_client import (
    PlanningError, PlanningUnauthorized, XanoPlanningClient,
)

HARNESS = """let s='';process.stdin.on('data',c=>s+=c);process.stdin.on('end',()=>{const d=JSON.parse(s);process.stdout.write(JSON.stringify(new Function('$this',d.body)(d.input)));});"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--xanoscript', required=True, type=Path)
    parser.add_argument('--fixtures', required=True, type=Path)
    parser.add_argument('--relatorio', required=True, type=Path)
    args = parser.parse_args()
    node = shutil.which('node')
    if not node:
        raise SystemExit('Node.js precisa estar instalado; nada foi iniciado.')
    source = args.xanoscript.read_text(encoding='utf-8-sig')
    bodies = re.findall(r'\|lambda:"""(.*?)"""', source, re.S)
    if not bodies:
        raise SystemExit('Exportacao sem lambda; nada foi iniciado.')
    body = max(bodies, key=len)
    fixtures = json.loads(args.fixtures.read_text(encoding='utf-8-sig'))
    base = copy.deepcopy(fixtures['referencia_sem_ocupacao']['dados'])
    occupancy = copy.deepcopy(fixtures['controle_ocupado_configurado']['dados']['viagens'][0])
    occupancy['id'] = 1
    occupancy['usuario_id'] = 2002
    occupancy['substituida'] = False
    occupancy['substituida_em'] = None
    for key in ['configuracao', 'viagens', 'usuario_id']:
        base.pop(key, None)
    report = {
        'metodo': 'HTTP real local + SQLite descartavel + cliente real + lambda exportada',
        'limite': 'Camadas de dados e autenticacao locais; nao e HTTP em runtime nativo do Xano.',
        'sha256_exportacao': hashlib.sha256(source.encode()).hexdigest(),
        'sha256_lambda': hashlib.sha256(body.encode()).hexdigest(),
        'chamadas_xano': 0,
        'casos': [],
    }
    token = secrets.token_urlsafe(32)  # Somente memoria; nao e credencial real.
    with tempfile.TemporaryDirectory(prefix='metroflow-http-local-') as folder:
        dbpath = Path(folder) / 'planejamento.sqlite3'
        @contextmanager
        def connect():
            connection = sqlite3.connect(dbpath)
            try:
                with connection:
                    yield connection
            finally:
                connection.close()
        with connect() as db:
            db.execute('CREATE TABLE configuracao_lotacao(id INTEGER PRIMARY KEY, minimo_usuarios INTEGER, percentual_lotacao REAL)')
            db.execute('CREATE TABLE viagens_confirmadas(id INTEGER PRIMARY KEY, payload TEXT NOT NULL)')
            db.execute('CREATE TABLE referencia(id INTEGER PRIMARY KEY, payload TEXT NOT NULL)')
            db.execute('INSERT INTO referencia VALUES(1,?)', (json.dumps(base),))
            db.execute('INSERT INTO configuracao_lotacao VALUES(1,1,1)')
        audit = []
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass  # Nao registrar cabecalhos, token ou payloads.
            def reply(self, status, payload):
                raw = json.dumps(payload, ensure_ascii=False).encode('utf8')
                self.send_response(status)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
            def do_POST(self):
                if self.client_address[0] != '127.0.0.1':
                    return self.reply(403, {'detail':'Origem nao local.'})
                if self.path != '/trajetos/buscar':
                    return self.reply(404, {'detail':'Nao encontrado.'})
                if not secrets.compare_digest(self.headers.get('Authorization',''), 'Bearer '+token):
                    return self.reply(401, {'detail':'Sessao local invalida.'})
                try:
                    length = int(self.headers.get('Content-Length','0'))
                    if length < 1 or length > 16384:
                        return self.reply(400, {'detail':'Corpo invalido.'})
                    requested = json.loads(self.rfile.read(length))
                    origin, destination = requested.get('estacao_origem_id'), requested.get('estacao_destino_id')
                    if type(origin) is not int or type(destination) is not int or origin == destination:
                        return self.reply(400, {'detail':'Selecao invalida.'})
                    with connect() as db:
                        context = json.loads(db.execute('SELECT payload FROM referencia WHERE id=1').fetchone()[0])
                        config = db.execute('SELECT id,minimo_usuarios,percentual_lotacao FROM configuracao_lotacao WHERE id=1').fetchone()
                        context['configuracao'] = dict(zip(['id','minimo_usuarios','percentual_lotacao'],config)) if config else None
                        context['viagens'] = [json.loads(row[0]) for row in db.execute('SELECT payload FROM viagens_confirmadas')]
                    context.update(origem_id=origin, destino_id=destination, usuario_id=1001)
                    for key in ['suporta_calibracao','suporta_espera_partidas','suporta_troca_mesma_linha','suporta_extensao_linha8']:
                        context[key] = requested.get(key) is True
                    completed = subprocess.run([node,'-e',HARNESS], input=json.dumps({'body':body,'input':context}), capture_output=True, text=True, encoding='utf8', timeout=30)
                    if completed.returncode:
                        return self.reply(500, {'detail':'Falha no calculo local.'})
                    result = json.loads(completed.stdout)
                    audit.append({'configuracao_sql_nula':config is None, 'viagens_sinteticas':len(context['viagens'])})
                    return self.reply(200 if result else 404, result)
                except (ValueError, KeyError, sqlite3.Error, subprocess.TimeoutExpired):
                    return self.reply(400, {'detail':'Entrada ou referencia local invalida.'})
        server = ThreadingHTTPServer(('127.0.0.1',0), Handler)
        thread = threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        address = f'http://127.0.0.1:{server.server_port}'
        report['endereco_local'] = address
        client = XanoPlanningClient(address, calibration_enabled=True, timeout=40, transport=httpx.HTTPTransport(trust_env=False))
        try:
            def route(name):
                result = client.find_route(36,2,token)
                assert result is not None, name
                item = {'caso':name,'http':200,'trechos':[s.id for s in result.segments], 'tempo_fisico':result.total_time_seconds,'tempo_publico':result.display_seconds,'configuracao_sql_nula':audit[-1]['configuracao_sql_nula']}
                report['casos'].append(item)
                return item
            reference = route('referencia_sem_ocupacao')
            with connect() as db:
                db.execute('INSERT INTO viagens_confirmadas VALUES(1,?)',(json.dumps(occupancy),))
            crowded = route('controle_ocupado_configurado')
            assert crowded['trechos'] != reference['trechos'], 'Controle nao produziu alternativa.'
            with connect() as db:
                db.execute('DELETE FROM configuracao_lotacao WHERE id=1')
                assert db.execute('SELECT COUNT(*) FROM configuracao_lotacao').fetchone()[0] == 0
            for name in ['configuracao_realmente_ausente','repeticao_sem_configuracao']:
                missing = route(name)
                assert missing['configuracao_sql_nula'] is True
                assert (missing['trechos'],missing['tempo_fisico'],missing['tempo_publico']) == (reference['trechos'],reference['tempo_fisico'],reference['tempo_publico'])
            try:
                client.find_route(36,2,'credencial-local-invalida')
            except PlanningUnauthorized:
                report['casos'].append({'caso':'sessao_local_invalida','http':401})
            else:
                raise AssertionError('Sessao local invalida aceita.')
            try:
                client.find_route(36,36,token)
            except PlanningError as error:
                assert error.status_code == 400
                report['casos'].append({'caso':'origem_destino_iguais','http':400})
            else:
                raise AssertionError('Origem igual ao destino aceita.')
            with connect() as db:
                db.execute('INSERT INTO configuracao_lotacao VALUES(1,1,1)')
            restored = route('configuracao_restaurada_somente_local')
            assert restored['trechos'] == crowded['trechos']
            with httpx.Client(trust_env=False,timeout=40) as raw:
                response = raw.post(address+'/trajetos/buscar',json={'estacao_origem_id':36,'estacao_destino_id':2,'suporta_calibracao':True,'suporta_espera_partidas':True,'suporta_troca_mesma_linha':True,'suporta_extensao_linha8':True},headers={'Authorization':'Bearer '+token})
                response.raise_for_status()
                sensitive = {'authToken','usuario_id','viagens','minimo_usuarios','percentual_lotacao','exposure','lotacao'}
                def keys(value):
                    if isinstance(value,dict):
                        return set(value).union(*(keys(v) for v in value.values()))
                    if isinstance(value,list):
                        return set().union(*(keys(v) for v in value))
                    return set()
                assert not (keys(response.json()) & sensitive)
                assert token not in response.text
                report['casos'].append({'caso':'contrato_sem_dados_internos','http':200})
            with connect() as db:
                assert json.loads(db.execute('SELECT payload FROM referencia WHERE id=1').fetchone()[0]) == base
                assert json.loads(db.execute('SELECT payload FROM viagens_confirmadas WHERE id=1').fetchone()[0]) == occupancy
            report['referencia_e_ocupacao_sintetica_preservadas'] = True
        finally:
            client.close()
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
    report['banco_temporario_removido'] = not dbpath.exists()
    report['aprovado'] = True
    assert report['banco_temporario_removido']
    args.relatorio.parent.mkdir(parents=True,exist_ok=True)
    args.relatorio.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(f'OK: {len(report["casos"])} casos HTTP locais; banco e servidor temporarios encerrados.')
    print('Sem chamadas ao Xano. Autenticacao e banco locais; resultado nao e teste HTTP nativo do Xano.')
    print('Relatorio:',args.relatorio)

if __name__ == '__main__':
    main()
