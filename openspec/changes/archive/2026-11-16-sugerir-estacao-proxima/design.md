## Context

A lista de estações chega ao planejador por `GET /api/planning/stations`, que o
`PlanningState.load_stations` chama no navegador com `rx.call_script`. A resposta
volta ao estado em `receive_stations` como `StationChoice` (`id`, `name`, `label`). A
escolha manual da origem usa `PlanningState.choose_origin(station_id, label)`. O
modelo `Station` e as tabelas do Xano não têm coordenadas.

O repositório já guarda dados editoriais fora do Xano: as orientações de embarque são
lidas de `docs/dados/orientacoes-estacoes.csv` por
`MetroFlow/planning/infrastructure/guidance_csv.py`, associadas por nome normalizado e
desligáveis por `METROFLOW_ORIENTACOES=0`. Ver `proposal.md` para a motivação.

Restrição desta entrega: o Xano não é alterado, e a apresentação próxima não pode ser
afetada.

## Goals / Non-Goals

**Goals:**

- Isolar a localização da busca, de modo que falhas nela nunca bloqueiem o
  planejamento.
- Manter a posição do usuário somente no navegador.
- Reaproveitar a escolha manual da origem, sem novo fluxo de busca.
- Permitir desligar tudo sem mudar código.

**Non-Goals:**

- Precisão de navegação: a distância é em linha reta e serve só para escolher a
  estação.
- Cobertura completa das estações nesta entrega.

## Decisions

### Arquivo CSV local em vez de campos no Xano

As coordenadas ficam em `docs/dados/coordenadas-estacoes.csv`, com as colunas
`estacao`, `latitude`, `longitude`, `fonte` e `data_coleta` (`AAAA-MM-DD`). O backend
lê o arquivo uma vez, com cache, como faz com as orientações.

O `AGENTS.md` manda manter no Xano os dados da malha. As coordenadas não participam do
cálculo de trajetos, dos trechos nem dos tempos; servem apenas para sugerir uma
origem. A escolha é temporária: uma mudança futura poderá mover as coordenadas para a
tabela de estações do Xano, trocando apenas a origem dos dados atrás da mesma leitura.

Alternativa considerada: campos `latitude` e `longitude` na tabela de estações do
Xano. Foi adiada a pedido do grupo, para não alterar o ambiente remoto antes da
apresentação.

### Fonte das coordenadas

A primeira carga, de 16/11/2026, cobre as 188 estações da malha. As 10 estações
cujas coordenadas já estavam em `docs/dados/tempos/` (GTFS da SPTrans e, para
Ambuitá, a Wikipédia) mantêm esses valores. As demais vêm do OpenStreetMap (licença
ODbL), consultado pela Overpass API, com o identificador do elemento usado na coluna
`fonte`. Os nomes partem de `docs/dados/tempos/cobertura/cobertura-deslocamentos.json`,
que registra os nomes da malha. Nomes comerciais, como `Faria Lima - PagBank`, foram
associados ao nome do OpenStreetMap por equivalência explícita. Vergueiro, Jabaquara e
as duas estações da Lapa (Linhas 7 e 8) foram escolhidas manualmente entre os elementos
do OpenStreetMap. A conferência comparou a distância entre estações vizinhas da malha:
a menor é de cerca de 200 m (Consolação e Paulista) e as maiores correspondem a
serviços expressos.

Os nomes seguem os exibidos pelo planejador. Um nome que não corresponder a nenhuma
estação da malha é ignorado na associação, e a leitura registra em log apenas a
quantidade de registros sem correspondência.

### Validação no backend

Cada registro precisa de latitude entre -24,1 e -23,1, longitude entre -47,3 e -45,9
(região metropolitana com folga), fonte não vazia e data válida. Estação repetida,
após a normalização, invalida as duas ocorrências para não sugerir uma posição
ambígua. Registros inválidos são descartados individualmente; falha de leitura do
arquivo resulta em mapa vazio. Nenhum desses casos gera erro na API.

### Campos opcionais na lista de estações

`StationChoice` ganha `latitude: float | None` e `longitude: float | None`, ambos
nulos por padrão. A rota `GET /api/planning/stations` preenche os campos quando a
funcionalidade está ligada e a estação tem coordenada. O contrato anterior continua
válido para quem ignora os campos novos.

### Interruptor por variável de ambiente

Ligada por padrão e desligada com `METROFLOW_LOCALIZACAO=0`, seguindo
`METROFLOW_ORIENTACOES`. Desligada, o arquivo não é lido e os campos ficam nulos; como
o aviso depende de existir ao menos uma estação com coordenada, a tela volta a ser a
de antes.

### Cálculo no navegador

No Reflex, o estado vive no servidor e todo argumento de evento atravessa a conexão.
Por isso, ao tocar em "Usar minha localização", o estado envia por `rx.call_script` um
script que contém apenas as estações com coordenadas (`id`, latitude e longitude). O
script chama `navigator.geolocation.getCurrentPosition` com limite de 10 segundos,
calcula a distância de Haversine até cada estação e devolve ao callback somente
`{ok, station_id, distance_m}` ou `{ok: false, reason}`. A posição do usuário nunca
deixa o navegador.

Alternativa considerada: enviar a posição ao backend e calcular em Python. Foi
descartada porque levaria um dado pessoal ao servidor sem necessidade.

### Estado e tela

O `PlanningState` guarda se o aviso foi ocultado, se a localização está em andamento,
a distância sugerida e uma mensagem curta. O callback valida o retorno, confere que o
`station_id` existe na lista e chama `choose_origin` com o rótulo da estação. Acima de
5 km, informa que não encontrou estação próxima e não altera a origem. Uma nova
escolha manual da origem limpa o texto da distância. "Agora não" apenas oculta o aviso
no estado da página, sem armazenamento no navegador.

Mensagens:

- distância: "Estação mais próxima: ~N m (distância em linha reta)", arredondada a
  dezenas de metros;
- falha: "Não foi possível obter sua localização. Escolha a origem manualmente.";
- sem estação: "Nenhuma estação cadastrada a até 5 km de você.".

## Risks / Trade-offs

- [Cobertura parcial: a estação realmente mais próxima pode não ter coordenada] → O
  texto mostra a distância, e o usuário pode trocar a origem. A cobertura cresce
  editando o CSV.
- [Celular na rede local por HTTP nega a localização] → A falha mostra a mensagem
  curta e a escolha manual continua. A documentação explica que é preciso HTTPS fora
  do `localhost`.
- [Nome do CSV diferente do nome da malha] → Associação por nome normalizado e
  conferência dos nomes durante a carga dos dados.
- [Permissão negada fica lembrada pelo navegador] → O pedido só ocorre após o toque, e
  a escolha manual não é afetada.

## Migration Plan

Sem migração. Para reverter, definir `METROFLOW_LOCALIZACAO=0` e reiniciar o
servidor; para remover, reverter o merge da branch.
