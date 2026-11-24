# Validação local do pacote Render — 22/11/2026

**Histórico da primeira rodada. A retomada de 23/11/2026 abaixo substitui o estado de bloqueio total da exportação, sem dar instalação limpa ou runtime Render como homologados.**

Base: main 3169cbf (PR #53). Cópia e branch separadas, sem push, merge, criação de serviço, ativação pública de fontes ou acesso de escrita ao Xano.

## Executado

- Dependências Python instaladas com uv.lock congelado, Python 3.12.14 e Reflex 0.9.10.post1.
- Suíte completa: **458 testes e 119 subtestes aprovados**, um aviso existente do TestClient. Este total inclui os primeiros 18 testes do pacote. Após reforço da validação de URL, os **20 testes finais do pacote** passaram separadamente. Não somar os totais como testes distintos.
- A primeira execução teve uma falha no fixture de ambiente do teste novo; corrigida antes da suíte aprovada. Nenhuma regra de negócio foi alterada.
- Busca, API, sessão, calibração, concorrência, exclusividade e status são cobertos pela suíte existente com mocks/malhas controladas e funções JavaScript em Node. **Não é teste com duas contas reais no Render ou novo registro em produção.**
- `reflex compile --dry`: sucesso (43/42 etapas exibidas pelo compilador), com aviso existente de Radix implícito. Sem upgrade do framework.
- HTTP em processo com a fábrica ASGI real da aplicação e TestClient: `/ping` 200; `/api/planning/stations`, `/api/planning/line-status` e `/api/admin/indicators` 401 sem cookie. Não houve chamada ao Xano nesses casos. A montagem da interface estática não fez parte desta verificação.
- Blueprint aprovado pelo JSON Schema oficial https://render.com/schema/render.yaml.json, usando ferramentas temporárias, sem acrescentar dependências ao projeto ou criar recursos.
- OpenSpec estrito: 17 itens aprovados.

## Bloqueio local e pendências

O **build completo da interface não foi concluído** nesta sessão. Bun falhou no Windows; npm foi selecionado e a preservação de versões exatas resolveu o conflito EOVERRIDE do PostCSS. O Windows continuou recusando criação de subpastas de node_modules (EPERM), inclusive com cache e temporários dentro da cópia de trabalho. A compilação Python passou, mas isso não equivale à exportação completa nem ao servidor público funcionando.

O iniciador final `serve.py` utiliza as variáveis internas pelo mecanismo do Reflex (nomes internos têm prefixo `__REFLEX_`), monta o build já existente e recusa build ausente ou origem/versão incompatíveis. A inicialização **com frontend compilado**, o WebSocket no navegador, consumo de memória, Linux/Render, HTTPS e retomada após suspensão permanecem por validar. O Docker Desktop não estava ativo; nenhum contêiner foi executado e ele não é requisito do pacote nativo.

Para fechar o build no terminal do usuário, executar `deploy/render/validar-local.ps1` na cópia preparada. Esse script não publica e não inicia servidor se testes ou build falharem. As fontes continuam desligadas, mesmo no teste local deste pacote. Manter o aplicativo habitual separado; nenhuma cópia principal foi substituída.

## Preservação

Nenhum arquivo de aplicação em MetroFlow/, rxconfig.py, pyproject.toml, uv.lock, reflex.lock/ ou dados CSV foi alterado. Não houve migração, importação, modificação da malha, parâmetros ou publicação de endpoints. Somente preparação de implantação, testes e OpenSpec foram acrescentados. Nenhuma conta ou segredo está no pacote.

A ativação pública dos status e a retenção durável do último retorno continuam pendentes. O cache local continua efêmero; não se promete preservação entre reinícios do plano Free.

## Retomada em 23/11/2026

- Backup dos 27 arquivos da preparação anterior antes das alterações; cópia separada atualizada por fast-forward para main `03342d5` (PR #54), apenas a documentação da main havia mudado.
- Corrigida a sintaxe do leitor `xano_snapshot.py`, que ainda não é importado pela aplicação. Os arquivos versionados originais da main, incluindo os lockfiles, foram preservados. O compilador reformatou `reflex.lock/package.json`; foi conferida a igualdade do JSON e restaurado o conteúdo original.
- **484 testes e 119 subtestes aprovados**, com um aviso existente do TestClient. Inclui os 20 testes do pacote Render, 23 casos de persistência e o novo laboratório HTTPS; não somar as execuções específicas como testes adicionais.
- **18 itens OpenSpec aprovados** em modo estrito. **Quatro rascunhos XanoScript válidos**, sem avisos. A sintaxe não comprova transações, autenticação ou execução nativa do Xano.
- Blueprint aprovado novamente pelo esquema JSON oficial do Render, com `plan: free`, um serviço, publicação automática desligada e sem bancos/discos/tarefas pagos.
- Exportação completa: compilação Python e **4/4 etapas do frontend**, incluindo as páginas e os assets estáticos, concluídas com dependências existentes copiadas fisicamente. A instalação foi substituída por uma operação vazia somente em memória, no laboratório, após igualdade de `package.json`. O script de build publicado não recebe esse desvio. **Não é validação de instalação limpa**.
- HTTP real em loopback com Granian incorporado e fábrica ASGI real: `/ping`, `/`, `/buscar-trajeto/`, `/admin/`, `/status/` e um asset compilado responderam **200**; `/api/planning/stations`, `/api/planning/line-status` e `/api/admin/indicators` responderam **401 sem cookie**; upgrade Engine.IO/WebSocket respondeu **101**. É abertura de conexão, não execução completa das jornadas no navegador.
- HTTPS local da persistência: servidor e SQLite temporários, TLS verificado, cache de leituras, falha 503 e reinício preservando o status e suas datas. Não equivale a execução no Xano.
- Fontes públicas continuam desligadas; o leitor persistente continua desconectado. Nenhum acesso de escrita ou recurso remoto foi criado no Render/Xano; não houve busca real, registro de viagem, alteração de malha ou parâmetro nesta retomada.

### Limites ainda abertos

1. Instalação do zero no Windows: npm recebeu EPERM em subpastas, inclusive com pasta nova, Node 22.22.0 e permissão adicional na pasta de build. O build via dependências reaproveitadas não resolve nem comprova instalação Linux.
2. `deploy.render.serve` com supervisor Granian multiprocesso: o worker encerrou no Windows desta sessão. O laboratório incorporado funcionou, mas é outro modo e não o substitui. Causa nativa e inicialização Linux/Render não homologadas.
3. Memória de 512 MB, retomada após suspensão, HTTPS público, cookies Secure, e-mails e localização no domínio final, jornadas autenticadas e concorrência com duas contas reais continuam sem teste remoto.
4. Persistência: provisionamento da tabela/grupo, identidade técnica, bloqueios PostgreSQL, JWT, limites de API, integração com a fábrica e o coletor continuam pendentes. O agendamento gratuito não foi confirmado; persistência não fornece coleta durante suspensão.

Os logs desta rodada ficam em `.cache/validation/` e são resumidos no pacote de evidências fora do repositório. O aplicativo habitual não foi parado nem substituído. Não publicar este pacote como homologado antes de fechar esses itens.

## Validação Linux concluída em 23/11/2026

Esta rodada fecha os itens locais 1 e 2 acima; os itens de homologação remota permanecem pendentes. O usuário executou `deploy/render/linux/validar-linux.ps1` no terminal normal, porque o terminal de controle não tinha permissão no canal do Docker. Os arquivos originais de evidência foram lidos e conferidos após a conclusão.

- Imagens oficiais com Python 3.12.14, Node 22.22.0 e uv 0.12.23. `build-tests.log` confirma `uv sync --frozen --no-dev` e `python -m deploy.render.build`, instalação nova e exportação completa 4/4. Não houve reutilização de dependências Windows, servidor incorporado ou substituição da função de instalação nessa rodada.
- O alvo Linux de testes passou com **484 testes, 119 subtestes e um aviso**. O runtime usa outro alvo, sem dependências dev. O cache entre os alvos reutiliza as camadas produzidas por esse build Linux, não `node_modules` do host.
- O comando de produção `deploy.render.serve` iniciou o supervisor Granian e um worker em Linux. `runtime-server.log` confirma inicialização normal e nova inicialização após o reinício. Não foi usado o modo experimental incorporado do teste Windows.
- Nas duas inicializações, `/ping`, `/`, `/login/`, `/buscar-trajeto/`, `/admin/`, `/status/` e um asset responderam **200**; as três APIs protegidas exercidas sem cookie responderam **401**; upgrade Engine.IO/WebSocket respondeu **101**.
- Runtime limitado a 512 MiB, sem swap e 0,1 CPU. Amostra de `docker stats`: **106,8 MiB/512 MiB**, 20,87%; `OOMKilled=false`, `Running=true`. Cgroup medido durante as verificações: 137.105.408 e 112.979.968 bytes. São amostras do smoke test, não certificação de consumo máximo ou carga.
- Runtime sem rede externa (`--network none`), sem portas publicadas e sem volumes do host. URLs Xano apontaram para loopback sem serviço; fontes ficaram desligadas. O script verificou esses valores antes dos pedidos. Não houve login real, escrita no Xano, mudança de malha/parâmetros ou publicação. `stop.log` confirma que o contêiner foi parado ao final.

**Próximo critério:** publicação inicial no Render somente após autorização, seguida de homologação no endereço HTTPS real com duas contas. TLS, cookies Secure, e-mails, localização, registros remotos, cotas e retomada após suspensão continuam sem comprovação pública. Persistência/coleta dos status permanece desativada e depende de sua própria homologação Xano e condições das fontes.
