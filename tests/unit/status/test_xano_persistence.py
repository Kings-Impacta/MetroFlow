"""Contrato de persistência em laboratório; não executa no runtime Xano."""
from concurrent.futures import ThreadPoolExecutor
import copy
import json
from pathlib import Path
import sqlite3
import httpx
import pytest
from MetroFlow.status.xano_snapshot import XanoStatusSnapshotReader
from tests.unit.planning.xano_lambda import run_lambda, requires_node, lambda_body

DRAFT = Path(__file__).parents[3]/"docs/xano/rascunhos/status-persistente"
T0 = 1795359600000


def initial():
    return {"codigo":"cptm", "autorizada":True, "habilitada":True, "condicoes":{}, "controle":{}}


def condition(code="L10", **changes):
    item = {"line_code":code, "situation":"normal", "label":"Operação Normal", "description":"",
        "source":"CPTM", "source_url":"https://www.cptm.sp.gov.br/cptm", "collected_at":T0/1000,
        "updated_at":T0/1000, "verified_at":T0/1000, "validity":"current", "attribution":"CPTM"}
    return item | changes


def reduce(row, action, now=T0, **params):
    result = run_lambda(DRAFT/"controle_post.xs", {"fonte":row, "pedido":{"acao":action, **params}, "agora":now})
    if result["ok"]:
        row.update(result["data"])
    return result


def publish(row, now=T0, items=None, **options):
    lease = reduce(row,"reserve",now)["response"]
    assert lease["granted"]
    return reduce(row,"publish",now, generation=lease["generation"],
                  conditions=items if items is not None else [condition()], cacheable=True, **options)


def snapshot(row, now=T0):
    return run_lambda(DRAFT/"snapshot_get.xs", {"fontes":[row], "agora":now})


@requires_node
class TestStatusPersistence:
    def test_exact_engine_embedded(self):
        assert lambda_body(DRAFT/"controle_post.xs") == (DRAFT/"reduzir_status.js").read_text(encoding="utf-8")

    def test_success_and_failure_keep_original_dates(self):
        row=initial();publish(row)
        old=copy.deepcopy(row["condicoes"])
        lease=reduce(row,"reserve",T0+300000)["response"]
        reduce(row,"fail",T0+300000,generation=lease["generation"],refresh_after=3600)
        assert row["condicoes"] == old
        assert row["controle"]["next_call"] == T0+3900000
        item=snapshot(row,T0+300000)["sources"][0]["conditions"][0]
        assert item["collected_at"] == T0/1000 and item["validity"] == "stale"

    def test_initial_import_of_old_cache_does_not_make_it_fresh(self):
        row = initial()
        now = T0 + 86400000
        assert publish(row, now, [condition()])["response"]["stored"] == 1
        old = snapshot(row, now)["sources"][0]["conditions"][0]
        assert old["collected_at"] == T0/1000
        assert old["validity"] == "stale"

    def test_partial_preserves_missing_line(self):
        row=initial();publish(row,items=[condition(),condition("L11")])
        later=T0+300000
        new=condition(situation="restricted",label="Velocidade reduzida",collected_at=later/1000,verified_at=later/1000,updated_at=later/1000)
        publish(row,later,[new])
        assert row["condicoes"]["L10"]["condition"]["situation"] == "restricted"
        assert row["condicoes"]["L11"]["condition"]["validity"] == "stale"
        assert row["condicoes"]["L11"]["condition"]["collected_at"] == T0/1000

    def test_empty_is_not_normal_and_keeps_value(self):
        row=initial();publish(row)
        assert publish(row,T0+300000,[])["response"]["stored"] == 0
        assert row["condicoes"]["L10"]["condition"]["collected_at"] == T0/1000
        assert row["controle"]["failed"]

    def test_no_store_preserves_original(self):
        row=initial();publish(row)
        lease=reduce(row,"reserve",T0+300000)["response"]
        reduce(row,"publish",T0+300000,generation=lease["generation"],conditions=[condition(collected_at=T0/1000+300,verified_at=T0/1000+300)],cacheable=False)
        assert row["condicoes"]["L10"]["condition"]["collected_at"] == T0/1000
        assert row["controle"]["failed"]

    def test_same_status_renews_only_valid_verification(self):
        row=initial();publish(row)
        later=T0+300000
        publish(row,later,[condition(collected_at=later/1000,verified_at=later/1000)])
        item=row["condicoes"]["L10"]["condition"]
        assert item["situation"]=="normal" and item["updated_at"]==T0/1000
        assert item["verified_at"]==later/1000

    def test_late_generation_cannot_replace_new(self):
        row=initial();lease=reduce(row,"reserve")["response"]
        publish(row,T0+300000,[condition(collected_at=T0/1000+300,verified_at=T0/1000+300)])
        saved=copy.deepcopy(row)
        assert reduce(row,"publish",T0+300000,generation=lease["generation"],conditions=[condition()],cacheable=True)["reason"] == "lease"
        assert row == saved

    def test_expired_lease(self):
        row=initial();lease=reduce(row,"reserve")["response"]
        assert reduce(row,"publish",T0+60001,generation=lease["generation"],conditions=[condition()],cacheable=True)["reason"] == "lease"
        assert not row["condicoes"]

    @pytest.mark.parametrize("changes", [{"line_code":"L3"},{"situation":"inventada"},{"collected_at":T0/1000+1000},{"label":"x"*121}])
    def test_invalid_batch_atomic(self, changes):
        row=initial();lease=reduce(row,"reserve")["response"]
        result=reduce(row,"publish",generation=lease["generation"],conditions=[condition(),condition("L11",**changes)],cacheable=True)
        assert not result["ok"] and not row["condicoes"]

    def test_old_source_timestamp_does_not_rollback(self):
        row=initial();publish(row)
        later=T0+300000
        result=publish(row,later,[condition(collected_at=later/1000,verified_at=later/1000,updated_at=T0/1000-10)])
        assert result["response"]["stored"]==0
        assert row["condicoes"]["L10"]["condition"]["updated_at"]==T0/1000

    def test_source_not_authorized(self):
        row=initial();row["autorizada"]=False
        assert reduce(row,"reserve")["reason"]=="disabled"

    def test_rate_limit_and_failure_counts_attempt(self):
        row=initial();lease=reduce(row,"reserve")["response"]
        reduce(row,"fail",generation=lease["generation"])
        assert not reduce(row,"reserve",T0+299999)["response"]["granted"]
        assert reduce(row,"reserve",T0+300000)["response"]["granted"]
        row["controle"]["attempts"]=[T0+300000-i for i in range(12)]
        row["controle"]["next_call"]=0
        assert not reduce(row,"reserve",T0+300000)["response"]["granted"]

    def test_sqlite_restart_and_concurrent_reservations(self,tmp_path):
        # SQLite simula persistência e serialização; não equivale ao PostgreSQL/Xano.
        path=tmp_path/"status.sqlite3"
        with sqlite3.connect(path) as db:
            db.execute("CREATE TABLE fonte (id INTEGER PRIMARY KEY, payload TEXT)")
            db.execute("INSERT INTO fonte VALUES (1,?)",(json.dumps(initial()),))
        def reserve_once():
            with sqlite3.connect(path,timeout=10) as db:
                db.execute("BEGIN IMMEDIATE")
                row=json.loads(db.execute("SELECT payload FROM fonte WHERE id=1").fetchone()[0])
                result=reduce(row,"reserve")
                db.execute("UPDATE fonte SET payload=? WHERE id=1",(json.dumps(row),))
                return result["response"]["granted"]
        with ThreadPoolExecutor(max_workers=2) as executor:
            assert sorted(executor.map(lambda _: reserve_once(),range(2)))==[False,True]
        with sqlite3.connect(path) as db:
            row=json.loads(db.execute("SELECT payload FROM fonte WHERE id=1").fetchone()[0])
            reduce(row,"publish",generation=row["controle"]["generation"],conditions=[condition()],cacheable=True)
            db.execute("UPDATE fonte SET payload=? WHERE id=1",(json.dumps(row),))
        with sqlite3.connect(path) as restarted:
            restored=json.loads(restarted.execute("SELECT payload FROM fonte WHERE id=1").fetchone()[0])
        assert restored["condicoes"]["L10"]["condition"]["collected_at"]==T0/1000
        assert snapshot(restored,T0+86400000)["sources"][0]["conditions"][0]["validity"]=="stale"


def test_reader_shared_cache_failure_and_restart():
    clock=[T0/1000];calls=[];fails=[False]
    body={"version":1,"sources":[{"source":"cptm","conditions":[condition()]}]}
    def handler(request):
        calls.append(request)
        return httpx.Response(503 if fails[0] else 200,json=body)
    transport=httpx.MockTransport(handler)
    reader=XanoStatusSnapshotReader("https://status.example/api:test",transport=transport,clock=lambda:clock[0])
    try:
        assert reader.conditions()[0].validity=="current"
        for _ in range(20): assert reader.conditions()[0].line_code=="L10"
        assert len(calls)==1
        clock[0]+=61;fails[0]=True
        old=reader.conditions()[0]
        assert old.validity=="stale" and old.collected_at==T0/1000
        clock[0]+=10;reader.conditions();assert len(calls)==2
    finally: reader.close()
    fails[0]=False
    restarted=XanoStatusSnapshotReader("https://status.example/api:test",transport=transport,clock=lambda:clock[0])
    try: assert restarted.conditions()[0].collected_at==T0/1000
    finally: restarted.close()


def test_reader_revoked_source_clears_only_on_valid_snapshot():
    clock=[T0/1000];body={"version":1,"sources":[{"source":"cptm","conditions":[condition()]}]}
    reader=XanoStatusSnapshotReader("https://status.example",transport=httpx.MockTransport(lambda _:httpx.Response(200,json=body)),clock=lambda:clock[0])
    try:
        assert reader.conditions()
        body["sources"]=[];clock[0]+=61
        assert reader.conditions()==[]
    finally: reader.close()


@pytest.mark.parametrize("url",["http://example.com", "https://user:secret@example.com", "https://example.com?token=secret"])
def test_reader_rejects_insecure_urls(url):
    with pytest.raises(ValueError): XanoStatusSnapshotReader(url)


def test_reader_respects_429_retry_after_and_no_immediate_retry():
    clock=[T0/1000];calls=[]
    def handler(request):
        calls.append(request)
        return httpx.Response(429,headers={"Retry-After":"7200"})
    reader=XanoStatusSnapshotReader("https://status.example",transport=httpx.MockTransport(handler),clock=lambda:clock[0])
    try:
        assert reader.conditions()==[]
        clock[0]+=3601
        assert reader.conditions()==[] and len(calls)==1
        clock[0]+=3600
        reader.conditions()
        assert len(calls)==2
    finally: reader.close()


def test_reader_rejects_non_finite_timestamps():
    body={"version":1,"sources":[{"source":"cptm","conditions":[condition(collected_at="NaN")]}]}
    reader=XanoStatusSnapshotReader("https://status.example",transport=httpx.MockTransport(lambda _:httpx.Response(200,json=body)),clock=lambda:T0/1000)
    try: assert reader.conditions()==[]
    finally: reader.close()
