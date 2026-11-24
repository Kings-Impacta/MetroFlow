# Preparação para Render Free — sem publicação

## Integração de leitura de status — 24/11/2026

O serviço existente `metroflow-demo.onrender.com` está publicado. O modo remoto usa
`METROFLOW_STATUS_XANO_URL=https://x8ki-letl-twmt.n7.xano.io/api:metroflow-status-operacional`.
Após a entrega do código e checks, essa variável deve ser aplicada ao serviço
existente e uma nova publicação manual deve carregar a versão validada. Não criar
outro serviço. As quatro flags de coleta permanecem em `0`; ler o banco não consulta
operadoras nem altera o cálculo de trajetos. Não configurar credenciais do coletor
no Render. O snapshot permanece vazio até a liberação e alimentação das fontes.

O leitor compartilha o último retorno entre sessões. HTTP 503/429 e dados inválidos
preservam valores e horários; a volta de um servidor novo recupera o registro Xano.
Isso não garante coleta enquanto o coletor local estiver desligado. Consulte
`docs/xano/rascunhos/status-persistente/README.md` para a operação e a evidência real.

O restante deste documento preserva o histórico da preparação inicial.

Estado: pacote local atualizado para a main `03342d5` (PR #54), em 23/11/2026. Nenhum serviço foi criado, nenhum push/merge foi realizado e nenhum dado ou parâmetro do Xano foi alterado. O README de uso continua indicando execução local.

## Arquivos e configuração

`render.yaml` define um único Web Service Python no plano `free`, com publicação automática desligada, uv 0.12.23, Python 3.12.14 e Node 22.22.0. Nenhum banco, disco, tarefa agendada ou recurso pago é provisionado. A importação de um Blueprint pode iniciar a primeira publicação mesmo com atualização automática desligada: **não importar nem sincronizar nesta etapa**.

O build usa `uv sync --frozen --no-dev` e `python -m deploy.render.build`. A execução usa `python -m deploy.render.serve`, sem recompilar no servidor. O pacote usa npm e mantém o Reflex 0.9.10.post1 e o uv.lock existentes. Os dados CSV de coordenadas e orientações devem permanecer na cópia completa do repositório.

A origem pública vem de `RENDER_EXTERNAL_URL`, fornecida pelo Render; `METROFLOW_PUBLIC_URL` permite uma origem explícita. Ela é aplicada ao build e ao servidor e deve coincidir em ambos. Alterar o domínio exige novo build. A mesma origem serve interface, API `/api/` e WebSocket `/_event`. Porta `PORT` (padrão local 10000), host 0.0.0.0 e um worker. Health check `/ping` não autentica nem consulta o Xano.

`METROFLOW_ENV=production` mantém o cookie HttpOnly/Secure. `--local` admite somente HTTP em localhost/127.0.0.1 para o laboratório; não deve ser usado no Render. Login real em HTTP pode ser limitado pelo cookie Secure; validar sessão por HTTPS antes de homologar.

As três URLs existentes do Xano continuam com os padrões da aplicação. Overrides opcionais: `XANO_AUTH_API_BASE_URL`, `XANO_PLANNING_API_BASE_URL` e `XANO_ADMIN_API_BASE_URL`. Não inserir chaves, senhas ou tokens no Blueprint. Nenhum script deste pacote cria ou atualiza a malha ou configurações remotas.

## Status pendente

Todas as flags de fontes estão em 0. O pacote recusa inicialização se alguma delas for ativada: DDT, CPTM, quadro Metrô e Motiva. O aplicativo retorna status indisponível sem coletar fontes externas; busca e registro continuam independentes. O iniciador local existente não foi alterado.

A ativação pública exige revisão posterior das condições de uso, do acesso a partir da hospedagem, do cache compartilhado e dos limites. O SQLite `.cache/render-line-status.sqlite3` é efêmero: não se promete guardar o último retorno após reinício, suspensão ou nova publicação. Nenhum armazenamento externo foi acrescentado nesta etapa.

## Reproduzir o laboratório (PowerShell)

Na raiz desta cópia separada:

```powershell
$env:UV_CACHE_DIR = Join-Path $PWD '.uv-cache'
uv sync --frozen --group dev --python 3.12
$env:METROFLOW_PUBLIC_URL = 'http://localhost:10000'
$env:PORT = '10000'
$env:npm_config_cache = Join-Path $PWD '.cache/npm'
uv run --no-sync python -m deploy.render.build --local
uv run --no-sync python -m deploy.render.serve --local
```

Os comandos iniciam um servidor local, sem publicar. Pare somente este processo com Ctrl+C. Não pare o servidor usado pelo grupo. O endereço para esta cópia é http://localhost:10000.

## Homologação futura, ainda não executada

- Autorizar publicação e confirmar plano Free e ausência de recursos cobrados no painel.
- Conferir build Linux, consumo de memória e retomada após suspensão; os testes Windows não os comprovam.
- Validar HTTPS, WebSocket, cookie, login/logout, confirmação e recuperação de e-mail; conferir se os links do Xano retornam ao domínio publicado. Se precisarem de ajuste, tratar separadamente, sem alterar a malha.
- Repetir Barra Funda → Paraíso com duas contas reais e conferir exclusividade, calibração, cronologia e limites no Xano. Testes com doubles locais não comprovam esse resultado remoto.
- Testar passageiro, painel administrativo somente leitura e localização por HTTPS.
- Somente após homologação, atualizar o README com o endereço efetivamente acessível.

O Render Free suspende após 15 minutos sem tráfego e pode levar cerca de um minuto para retornar. Há cotas de build, tráfego e horas compartilhadas; não é garantia de disponibilidade contínua. Não configurar monitor externo para contornar suspensão. Uma reinicialização pode exigir nova sessão; as viagens já gravadas continuam no Xano até sua expiração normal.

## Referências consultadas em 22/11/2026

- [Blueprint](https://render.com/docs/blueprint-spec)
- [Plano gratuito e limites](https://render.com/docs/free)
- [Runtime nativo e ferramentas](https://render.com/docs/native-runtimes)
- [Versão do uv](https://render.com/docs/uv-version)
- [Hospedagem Reflex](https://reflex.dev/docs/hosting/self-hosting/)

Resultados do laboratório: ver `validacao-local.md` nesta pasta.

## Retomada local em 23/11/2026

A exportação completa foi executada com uma cópia física de `node_modules` da instalação local já existente, após conferir que `package.json`, dependências e overrides eram idênticos. A instalação foi ignorada **somente nesse laboratório**, por substituição temporária em memória da função de instalação do Reflex; compilação, geração das páginas, bundle e compressão foram executados. Essa substituição não está no `build.py`, no Blueprint ou no código do framework. Instalar do zero pelo comando de build continua falhando com EPERM no Windows desta sessão, inclusive com Node 22.22.0 portátil conferido pelo checksum oficial.

O frontend compilado foi servido junto com a fábrica ASGI real: páginas e asset HTTP 200; APIs sem cookie HTTP 401; upgrade WebSocket HTTP 101. O teste usou o Granian incorporado, que é experimental e fica exclusivo do laboratório, em loopback. **Não validou o supervisor multiprocesso de `serve.py`**, cujo worker encerrou neste Windows sem detalhar a causa. Não alterar o inicializador de produção para usar esse modo de teste.

Para repetir somente o teste HTTP, com o build local compatível já existente:

```powershell
$env:METROFLOW_PUBLIC_URL = 'http://localhost:10000'
$env:PORT = '10000'
uv run --no-sync python -m deploy.render.validar_http_local
```

O script encerra seu próprio servidor ao terminar e não faz login, busca autenticada ou registro remoto. Não usar a porta se estiver ocupada. O build local inclui a origem localhost e não deve ser reutilizado para um domínio público: recompile para a origem homologada.

O leitor e os rascunhos de persistência em `docs/xano/rascunhos/status-persistente/` foram preparados e testados separadamente, mas continuam desconectados. Não há coleta nem persistência Xano ativada pelo pacote Render. Os critérios de aceitação para instalação limpa, Linux, memória, sessão real, supervisor e duas contas públicas continuam abertos.

## Laboratório Linux

O [laboratório Docker](linux/README.md) executou instalação limpa, testes e o inicializador de produção com imagens oficiais. O runtime ficou isolado da rede externa e do Xano real. A execução pelo terminal normal do usuário foi concluída e os logs foram conferidos: **484 testes/119 subtestes**, páginas/asset 200, APIs sem sessão 401, WebSocket 101, supervisor multiprocesso e reinício aprovados. A amostra de uso foi 106,8 MiB/512 MiB, sem OOM; não é teste de carga. Nenhuma imagem foi enviada a registry e nenhum serviço foi publicado.

Os impedimentos de instalação/supervisor no Windows não se reproduziram no Linux testado. A preparação local está fechada para uma futura publicação inicial com status desligados. Continuam pendentes a autorização de publicação e a homologação no Render: domínio HTTPS, cookies, e-mails, localização, duas contas e seus registros reais, memória sob uso e retomada da plataforma. O leitor/coletor de status no Xano permanece uma preparação separada, desconectada e não publicada.


## Publicação inicial autorizada em 23/11/2026

O usuário autorizou a publicação inicial exclusivamente no Render Free, com status desligados e sem custos, seguida da homologação pública. Esta entrega contém apenas implantação e seus testes; a persistência Xano continua fora deste pacote. Os resultados anteriores de 484 testes incluem a preparação de persistência separada; a suíte desta branch terá somente os testes presentes no repositório e os 20 novos testes de deploy.

Antes de criar o serviço, confirmar conta/plano gratuito, cotas disponíveis e ausência de cobrança adicional automática ou limite de gastos que impeça custos. Não cadastrar pagamento, aceitar upgrades nem criar bancos, discos ou tarefas pagos. `autoDeployTrigger: off` evita publicações automáticas futuras; a primeira criação manual ainda publica o serviço. A origem deve ser a URL fornecida pelo Render, nunca o domínio reservado do laboratório.

O código não altera os endpoints Xano nem as regras de viagens. A validação pública de login e das duas contas deverá usar os fluxos normais do aplicativo. Não há credenciais no repositório e o README principal só receberá o endereço depois de confirmar o serviço em funcionamento.
