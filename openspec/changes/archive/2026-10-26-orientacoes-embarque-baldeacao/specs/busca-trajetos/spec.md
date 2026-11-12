## MODIFIED Requirements

### Requirement: Escopo do MVP

O sistema SHALL considerar deslocamentos, esperas, disponibilidade de serviços e tempos específicos de caminhada e baldeação conforme as capacidades de calibração e espera de partidas. A penalidade fixa de 600 segundos SHALL ficar restrita ao contrato legado. O tempo público SHALL ser estimado, com margem única de 60 segundos sobre o total, fora da ocupação. O sistema SHALL não oferecer área administrativa. A lotação estimada e a substituição do trajeto SHALL seguir `concorrencia-rotas`, sem apresentação da lotação ao usuário. O resultado MAY incluir as orientações opcionais de desembarque definidas em `orientacoes-viagem`, sem alterar a escolha, os trechos ou o tempo estimado.

#### Scenario: Resultado do MVP

- **WHEN** um trajeto é apresentado
- **THEN** o resultado contém um único trajeto principal ou alternativa elegível conforme `concorrencia-rotas`, com as informações opcionais disponíveis

#### Scenario: Orientações não alteram o cálculo

- **WHEN** existem orientações cadastradas para estações do trajeto
- **THEN** a escolha do trajeto e o tempo total seguem as regras de busca, calibração, espera de partidas e `concorrencia-rotas`, independentemente das orientações
