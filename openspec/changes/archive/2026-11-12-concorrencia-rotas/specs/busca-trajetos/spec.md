## MODIFIED Requirements

### Requirement: Definição do trajeto principal

O sistema SHALL escolher o caminho com menor tempo total estimado, calculado pelos deslocamentos, esperas e baldeações específicos do contrato calibrado, respeitando a disponibilidade no momento do embarque. Em empate, SHALL preferir menos serviços especiais e depois menos baldeações. A margem pública única de 60 segundos SHALL não alterar a seleção. O contrato legado SHALL conservar 600 segundos por mudança de linha.

#### Scenario: Soma do tempo dos trechos
- **WHEN** um caminho possui múltiplos trechos
- **THEN** seu tempo total é a soma calibrada dos deslocamentos, esperas e baldeações, com 60 segundos acrescidos apenas ao total público

#### Scenario: Trajetos com tempos diferentes
- **WHEN** existem caminhos com tempos totais diferentes
- **THEN** o sistema seleciona o de menor tempo total

#### Scenario: Trajetos com o mesmo tempo
- **WHEN** existem caminhos com o mesmo tempo total
- **THEN** o sistema prefere menos serviços especiais e depois menor quantidade de baldeações

#### Scenario: Penalidade fixa de transferência no primeiro MVP
- **WHEN** a consulta usa o contrato legado e o caminho contém uma ou mais mudanças de linha
- **THEN** o sistema acrescenta 600 segundos por mudança ao tempo total usado na seleção e apresentado ao usuário

#### Scenario: Trajeto sem transferência
- **WHEN** todos os trechos do caminho permitem continuar no mesmo trem
- **THEN** nenhum tempo de transferência é acrescentado

### Requirement: Baldeações derivadas

O sistema SHALL derivar uma baldeação quando houver mudança de linha ou troca obrigatória de trem entre serviços consecutivos e SHALL fazer isso sem tabela específica de baldeações.

#### Scenario: Trajeto sem baldeação
- **WHEN** todos os trechos do trajeto permitem continuar no mesmo trem
- **THEN** o sistema informa zero baldeações

#### Scenario: Trajeto com baldeação
- **WHEN** a linha de um trecho difere da linha do trecho seguinte
- **THEN** o sistema identifica a estação comum ou a integração a pé explicitamente cadastrada como ponto de baldeação e informa as linhas envolvidas

### Requirement: Escopo do MVP

O sistema SHALL considerar deslocamentos, esperas, disponibilidade de serviços e tempos específicos de caminhada e baldeação conforme as capacidades de calibração e espera de partidas. A penalidade fixa de 600 segundos SHALL ficar restrita ao contrato legado. O tempo público SHALL ser estimado, com margem única de 60 segundos sobre o total, fora da ocupação. O sistema SHALL não oferecer área administrativa. A lotação estimada e a substituição do trajeto SHALL seguir `concorrencia-rotas`, sem apresentação da lotação ao usuário.

#### Scenario: Resultado do MVP

- **WHEN** um trajeto é apresentado
- **THEN** o resultado contém um único trajeto principal ou alternativa elegível conforme `concorrencia-rotas`, com as informações opcionais disponíveis
