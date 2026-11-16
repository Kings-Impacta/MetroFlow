## MODIFIED Requirements

### Requirement: Escopo do MVP

O sistema SHALL considerar deslocamentos, esperas, disponibilidade de serviços e tempos específicos de caminhada e baldeação conforme as capacidades de calibração e espera de partidas. A penalidade fixa de 600 segundos SHALL ficar restrita ao contrato legado. O tempo público SHALL ser estimado, com margem única de 60 segundos sobre o total, fora da ocupação. A área administrativa SHALL seguir `portal-administrativo` e SHALL não alterar a forma do resultado da busca. A lotação estimada e a substituição do trajeto SHALL seguir `concorrencia-rotas`, sem apresentação da lotação ao usuário. O resultado MAY incluir as orientações opcionais de desembarque definidas em `orientacoes-viagem`, sem alterar a escolha, os trechos ou o tempo estimado.

#### Scenario: Resultado do MVP

- **WHEN** um trajeto é apresentado
- **THEN** o resultado contém um único trajeto principal ou alternativa elegível conforme `concorrencia-rotas`, com as informações opcionais disponíveis

#### Scenario: Orientações não alteram o cálculo

- **WHEN** existem orientações cadastradas para estações do trajeto
- **THEN** a escolha do trajeto e o tempo total seguem as regras de busca, calibração, espera de partidas e `concorrencia-rotas`, independentemente das orientações

## ADDED Requirements

### Requirement: Estações inativas na busca

O sistema SHALL tratar uma estação inativa como indisponível para o planejamento: ela SHALL não aparecer na seleção de origem e destino, SHALL não ser aceita como origem ou destino e nenhum trajeto SHALL atravessá-la. A situação vigente SHALL valer a partir da consulta seguinte, sem alteração de código ou da malha.

#### Scenario: Estação inativa na seleção

- **WHEN** o usuário carrega a lista de estações depois de uma estação ter sido inativada
- **THEN** a estação não aparece entre as opções de origem e destino

#### Scenario: Seleção desatualizada

- **WHEN** o usuário envia como origem ou destino uma estação inativada depois do carregamento da sua lista
- **THEN** o sistema rejeita a busca e orienta o usuário a verificar as estações selecionadas

#### Scenario: Caminho que atravessaria estação inativa

- **WHEN** o melhor caminho entre origem e destino ativas passaria por uma estação inativa
- **THEN** o sistema apresenta o melhor caminho que não passa por ela ou, sem esse caminho, informa que não encontrou trajeto

#### Scenario: Estação reativada

- **WHEN** uma estação inativa é ativada novamente
- **THEN** ela volta a participar da seleção e do cálculo na consulta seguinte
