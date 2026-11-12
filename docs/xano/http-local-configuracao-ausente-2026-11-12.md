# Configuração ausente por HTTP local — 12/11/2026

## Resultado e alcance aceito

Por solicitação explícita do usuário, a pendência foi concluída no escopo de integração **HTTP local isolada**, sem custo, sem chamadas ao Xano e sem modificar produção. Isso complementa a validação anterior da mesma função no motor remoto. **Não é uma instância local do Xano e não é teste HTTP nativo do Xano.** SQLite e autenticação em memória implementam somente a camada de teste; não comprovam as particularidades de SQL, JWT, permissões ou infraestrutura do fornecedor.

O ambiente pessoal de teste não estava disponível no plano Free, o painel exigia upgrade para mais workspaces e a API recusou a criação independente. A tentativa de preparar objetos na v1 foi barrada antes da publicação. Nenhum objeto dessa tentativa foi criado em produção. Não houve upgrade, contratação ou ampliação de credenciais.

## Execução

O script `scripts/validar_http_local_configuracao.py` iniciou um servidor em `127.0.0.1`, com porta efêmera distinta da aplicação, e banco SQLite descartável. As chamadas foram realizadas por socket HTTP pelo próprio `XanoPlanningClient` do projeto e normalizadas no domínio real do cliente. Não foi usado MockTransport nem TestClient para produzir as respostas.

O cálculo executado com Node.js foi extraído sem alterar o corpo da lambda de uma exportação previamente conferida do endpoint publicado. O servidor leu por SQL o registro `configuracao_lotacao.id=1`, inclusive depois de sua exclusão real no SQLite. Malha de referência e relógio controlado vieram das fixtures já utilizadas na validação de 11/11. Usuários e viagens foram remapeados para identificadores sintéticos. O token local ficou apenas em memória, sem ser salvo ou enviado ao Xano.

| Caso | HTTP | Resultado |
|---|---|---|
| Referência sem ocupação | 200 | Linha 3 → Sé → Linha 1; 1185 s físicos, 1245 s públicos |
| Controle ocupado com configuração | 200 | Linha 11 → Luz → Linha 1; 1625 s físicos, 1685 s públicos |
| Configuração realmente ausente no SQLite | 200 | Mesmo percurso e tempos da referência principal |
| Repetição sem configuração | 200 | Principal preservado, sem configuração antiga em cache |
| Sessão local inválida | 401 | Nenhum resultado protegido |
| Origem igual ao destino | 400 | Entrada recusada |
| Restauração exclusivamente local | 200 | Alternativa do controle voltou a ser escolhida |
| Contrato público | 200 | Sem token, identificação de usuário, viagens internas, parâmetros ou dados de exposição |

Todos os oito casos passaram. As consultas ausentes comprovaram `SELECT ... WHERE id=1` sem linha retornada, e o controle positivo mudou a rota: não foi um teste sem conflito. A margem pública continuou sendo 60 segundos uma vez no total. As referências da malha e a ocupação sintética não foram alteradas durante os casos.

## Preservação

O servidor foi vinculado somente ao loopback e encerrado no `finally`; o banco temporário foi fechado e removido. O processo não lê credenciais Xano, não chama Meta API, não modifica variáveis do aplicativo, não usa a porta 3000 e não contém código de publicação. Código da aplicação, malha e parâmetros em produção permanecem inalterados por esta execução.

Evidência sem credenciais: [resultado dos oito casos](evidencias/http-local-configuracao-2026-11-12.json). A evidência registra o hash da exportação/lambda, tipos de teste, valores HTTP e a exclusão do banco, sem incluir os dados restritos das fixtures.

## Repetir

Executar na raiz do projeto com Python do ambiente e Node.js já instalados:

```powershell
.\.venv\Scripts\python.exe scripts\validar_http_local_configuracao.py --xanoscript "CAMINHO_LOCAL_DO_EXPORT\buscar_POST.xs" --fixtures "CAMINHO_LOCAL\entradas-configuracao.json" --relatorio "resultado-http-local.json"
```

A fixture local esperada contém `referencia_sem_ocupacao.dados` e `controle_ocupado_configurado.dados`, no formato do cálculo já auditado. As referências restritas desta execução estão em `outputs/sessao-configuracao-20261111/`, na pasta de trabalho do agente, e não são incluídas no repositório. O processo não baixa arquivos nem instala dependências.

A configuração só é apagada/restaurada no banco temporário. O laboratório não deve ser conectado à instância remota nem interpretado como certificação do runtime Xano. O ensaio HTTP nativo permanece **não executado** como limitação conhecida; deixou de ser bloqueio de fechamento desta pendência após a aceitação explícita do teste local pelo usuário.

## Validação da entrega

Após a inclusão do laboratório e da documentação, a suíte existente passou com 276 testes e 86 subtestes; OpenSpec estrito passou nos 13 itens. Permaneceu o aviso já existente de depreciação do TestClient. Os oito casos do laboratório foram executados separadamente por socket real com os arquivos de referência locais; não afirmar que o CI os repetiu, pois as fixtures restritas não integram o repositório. O aplicativo e seus endpoints não importam nem iniciam esse script automaticamente.
