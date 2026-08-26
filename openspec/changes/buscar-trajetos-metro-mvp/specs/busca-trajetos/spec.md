## Purpose

Permitir que uma pessoa consulte o trajeto principal de metrô entre duas estações e compreenda o caminho, as linhas utilizadas e as baldeações necessárias.

## ADDED Requirements

### Requirement: Seleção de estações de origem e destino

O sistema SHALL permitir que o usuário selecione uma estação de origem e uma estação de destino a partir das estações disponíveis no sistema.

#### Scenario: Estações disponíveis para seleção
- **WHEN** o usuário acessa o fluxo de busca de trajeto
- **THEN** o sistema apresenta controles que permitem escolher uma estação de origem e uma estação de destino entre as estações disponíveis

#### Scenario: Busca sem seleções completas
- **WHEN** o usuário tenta solicitar uma rota sem selecionar origem ou destino
- **THEN** o sistema não solicita um trajeto e informa que as duas estações devem ser selecionadas

#### Scenario: Origem e destino iguais
- **WHEN** o usuário seleciona a mesma estação como origem e destino e solicita uma rota
- **THEN** o sistema não solicita um trajeto e informa que origem e destino devem ser diferentes

### Requirement: Consulta do trajeto principal

O sistema SHALL consultar os trajetos disponíveis entre a origem e o destino selecionados e retornar um resultado somente quando houver um caminho válido entre as duas estações.

#### Scenario: Consulta bem-sucedida
- **WHEN** o usuário seleciona duas estações diferentes conectadas pela rede e solicita uma rota
- **THEN** o sistema consulta o serviço de trajetos e apresenta o trajeto principal retornado

#### Scenario: Consulta em andamento
- **WHEN** uma solicitação de trajeto está sendo processada
- **THEN** o sistema indica que a consulta está em andamento e impede solicitações concorrentes para a mesma busca

#### Scenario: Não existe trajeto
- **WHEN** o serviço informa que não há caminho entre a origem e o destino selecionados
- **THEN** o sistema informa que não foi encontrado um trajeto e não apresenta um resultado incompleto como se fosse uma rota

#### Scenario: Falha no serviço
- **WHEN** o serviço de trajetos não responde ou retorna um erro
- **THEN** o sistema informa que não foi possível consultar o trajeto e permite que o usuário tente novamente

### Requirement: Definição do trajeto principal

O sistema SHALL considerar como trajeto principal o caminho com menor tempo estimado de percurso entre a estação de origem e a estação de destino. Quando houver dois ou mais trajetos com o mesmo tempo estimado, SHALL priorizar o trajeto com menor quantidade de baldeações.

#### Scenario: Trajetos com tempos diferentes
- **WHEN** existem dois ou mais trajetos válidos entre a origem e o destino com tempos estimados diferentes
- **THEN** o sistema seleciona como trajeto principal aquele com menor tempo estimado

#### Scenario: Trajetos com o mesmo tempo estimado
- **WHEN** existem dois ou mais trajetos válidos com o mesmo tempo estimado
- **THEN** o sistema prioriza aquele que possui menor quantidade de baldeações

### Requirement: Apresentação do trajeto

O sistema SHALL apresentar as estações do caminho na ordem do percurso, as linhas utilizadas e os pontos em que o usuário deve realizar uma baldeação.

#### Scenario: Trajeto sem baldeação
- **WHEN** o trajeto principal utiliza uma única linha
- **THEN** o sistema apresenta a sequência de estações e identifica a linha utilizada sem indicar pontos de baldeação

#### Scenario: Trajeto com baldeação
- **WHEN** o trajeto principal exige a troca de uma linha para outra
- **THEN** o sistema apresenta a sequência ordenada de estações, identifica cada linha utilizada e marca a estação ou estações onde a troca deve ocorrer

#### Scenario: Resultado substituído por nova busca
- **WHEN** o usuário conclui uma nova consulta após já visualizar um trajeto
- **THEN** o sistema substitui o resultado anterior pelo novo trajeto ou pelo estado correspondente à nova consulta

### Requirement: Escopo do MVP

O sistema SHALL limitar o resultado desta capacidade às informações necessárias para apresentar o trajeto principal e SHALL omitir dados de lotação e rotas alternativas.

#### Scenario: Resultado do MVP
- **WHEN** um trajeto principal é apresentado
- **THEN** o resultado contém as estações do caminho, as linhas utilizadas e as baldeações necessárias para esta consulta

#### Scenario: Recursos futuros não disponíveis
- **WHEN** o usuário consulta um trajeto neste MVP
- **THEN** o sistema não calcula nem exibe nível de lotação ou rotas alternativas