## Purpose

Permite que o usuário autenticado, com sua autorização, use a localização do navegador
para preencher a origem com a estação cadastrada mais próxima, sem que a posição saia
do aparelho.

## ADDED Requirements

### Requirement: Cadastro local de coordenadas das estações

O sistema SHALL manter as coordenadas das estações em um arquivo versionado no
repositório, sem alterar o Xano. Cada registro SHALL informar estação, latitude,
longitude, fonte e data de coleta. Registros com coordenadas fora da região
metropolitana de São Paulo, campos obrigatórios ausentes ou estação repetida SHALL ser
descartados sem impedir o uso dos demais. Um arquivo ausente ou ilegível SHALL deixar
a funcionalidade sem coordenadas, sem bloquear o planejamento.

#### Scenario: Registro válido

- **WHEN** o arquivo contém uma estação com latitude e longitude dentro da região metropolitana, fonte e data de coleta
- **THEN** a estação passa a ter coordenadas na lista entregue ao planejador

#### Scenario: Registro inválido

- **WHEN** um registro tem coordenada fora da região metropolitana ou campo obrigatório vazio
- **THEN** esse registro é descartado e os demais continuam válidos

#### Scenario: Arquivo indisponível

- **WHEN** o arquivo de coordenadas está ausente ou ilegível
- **THEN** a lista de estações é entregue sem coordenadas e o planejamento continua disponível

### Requirement: Coordenadas opcionais na lista de estações

A lista de estações do planejador SHALL incluir latitude e longitude somente para as
estações com coordenadas cadastradas, associadas por nome normalizado, sem diferença de
acentos ou de caixa. Estações sem coordenada SHALL continuar na lista e selecionáveis
manualmente.

#### Scenario: Estação com coordenada

- **WHEN** uma estação da malha tem registro correspondente no arquivo de coordenadas
- **THEN** a lista de estações traz a latitude e a longitude dessa estação

#### Scenario: Estação sem coordenada

- **WHEN** uma estação da malha não tem registro correspondente
- **THEN** a estação aparece na lista sem coordenadas e continua disponível para escolha manual

### Requirement: Interruptor da localização

A funcionalidade SHALL ficar ligada por padrão e SHALL ser desligada quando
`METROFLOW_LOCALIZACAO` for `0`. Desligada, a lista de estações SHALL ser entregue sem
coordenadas e o planejador SHALL se comportar como antes da funcionalidade.

#### Scenario: Funcionalidade desligada

- **WHEN** `METROFLOW_LOCALIZACAO` é `0`
- **THEN** a lista de estações não traz coordenadas e o aviso de localização não aparece

### Requirement: Aviso de localização no planejador

Quando ao menos uma estação tiver coordenadas, o planejador SHALL exibir o aviso
"Encontrar a estação mais próxima de você?" com os botões "Usar minha localização" e
"Agora não". O sistema SHALL pedir a permissão de localização somente após o toque em
"Usar minha localização". O botão "Agora não" SHALL ocultar o aviso na página atual sem
pedir a permissão.

#### Scenario: Aviso exibido

- **WHEN** o usuário autenticado abre o planejador e há estações com coordenadas
- **THEN** o aviso aparece com os dois botões e nenhuma permissão é pedida ainda

#### Scenario: Sem coordenadas

- **WHEN** nenhuma estação da lista tem coordenadas
- **THEN** o aviso não aparece

#### Scenario: Usuário recusa o aviso

- **WHEN** o usuário toca em "Agora não"
- **THEN** o aviso é ocultado, a permissão não é pedida e a origem não muda

### Requirement: Sugestão da estação mais próxima

Com a permissão concedida, o sistema SHALL calcular no navegador a distância em linha
reta entre a posição do aparelho e cada estação com coordenadas, preencher a origem com
a mais próxima e exibir "Estação mais próxima: ~N m (distância em linha reta)", com a
distância arredondada. A origem preenchida SHALL poder ser trocada como uma escolha
manual. Se nenhuma estação estiver a até 5 km, o sistema SHALL não preencher a origem e
SHALL informar que não encontrou estação próxima.

#### Scenario: Estação próxima encontrada

- **WHEN** o usuário concede a permissão e há estação com coordenadas a até 5 km
- **THEN** a origem é preenchida com a estação mais próxima e o texto da distância em linha reta é exibido

#### Scenario: Troca da origem sugerida

- **WHEN** a origem foi preenchida pela localização e o usuário escolhe outra estação
- **THEN** a nova escolha substitui a sugestão e o texto da distância deixa de ser exibido

#### Scenario: Nenhuma estação próxima

- **WHEN** a estação com coordenadas mais próxima está a mais de 5 km
- **THEN** a origem não é alterada e o sistema informa que não encontrou estação próxima

### Requirement: Falha ou recusa da localização

Se a permissão for negada, a localização estiver indisponível no navegador ou na
conexão, ou a posição não chegar em até 10 segundos, o sistema SHALL informar que não
foi possível obter a localização, SHALL manter a origem inalterada e SHALL permitir a
escolha manual.

#### Scenario: Permissão negada

- **WHEN** o usuário nega a permissão de localização
- **THEN** o sistema informa que não foi possível obter a localização e a origem não muda

#### Scenario: Localização indisponível

- **WHEN** o navegador não oferece localização, como em uma página sem HTTPS fora do `localhost`
- **THEN** o sistema informa que não foi possível obter a localização e a origem não muda

#### Scenario: Tempo esgotado

- **WHEN** a posição não chega em até 10 segundos
- **THEN** o sistema informa que não foi possível obter a localização e a origem não muda

### Requirement: Privacidade da posição

A posição do usuário SHALL permanecer no navegador. O sistema SHALL enviar ao backend
somente a estação sugerida e a distância calculada, e SHALL não armazenar nem registrar
em logs a latitude e a longitude do usuário.

#### Scenario: Envio ao backend

- **WHEN** a estação mais próxima é calculada
- **THEN** o backend recebe apenas o identificador da estação e a distância, sem a latitude e a longitude do usuário
