## MODIFIED Requirements

### Requirement: Escopo do MVP

O sistema SHALL omitir tempos reais ou específicos de caminhada, espera e transferência, SHALL aplicar somente a penalidade fixa definida nesta especificação e SHALL não oferecer área administrativa. A lotação estimada e a substituição do trajeto por lotação SHALL seguir a especificação `concorrencia-rotas`, sem apresentação da lotação ao usuário. O resultado MAY incluir as orientações opcionais de desembarque definidas na capacidade `orientacoes-viagem`, sem que elas alterem a escolha do trajeto, os trechos ou o tempo estimado.

#### Scenario: Resultado do MVP

- **WHEN** um trajeto é apresentado
- **THEN** o resultado contém somente as informações de um único trajeto, que é o trajeto principal ou, conforme `concorrencia-rotas`, o caminho que o substitui por lotação, e, quando cadastradas, as orientações opcionais das suas etapas

#### Scenario: Orientações não alteram o cálculo

- **WHEN** existem orientações cadastradas para estações do trajeto
- **THEN** a escolha do trajeto e o tempo total seguem apenas as regras desta especificação e de `concorrencia-rotas`
