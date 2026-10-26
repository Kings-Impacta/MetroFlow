## MODIFIED Requirements

### Requirement: Escopo do MVP

O sistema SHALL omitir tempos reais ou específicos de caminhada, espera e transferência, SHALL aplicar somente a penalidade fixa definida nesta especificação e SHALL não oferecer área administrativa. A lotação estimada e a substituição do trajeto por lotação SHALL seguir a especificação `concorrencia-rotas`, sem apresentação da lotação ao usuário.

#### Scenario: Resultado do MVP

- **WHEN** um trajeto é apresentado
- **THEN** o resultado contém somente as informações de um único trajeto, que é o trajeto principal ou, conforme `concorrencia-rotas`, o caminho que o substitui por lotação
