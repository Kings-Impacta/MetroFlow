# validacao-planejamento Specification

## Purpose
TBD - created by archiving change validacao-complementar-planejamento. Update Purpose after archive.

## Requirements

### Requirement: Verificação reproduzível do trajeto principal

O projeto SHALL permitir verificar a regra de escolha do trajeto principal com uma malha controlada e resultados observáveis.

#### Scenario: Tempos totais distintos

- **WHEN** dois caminhos ligam as mesmas estações com tempos totais distintos
- **THEN** a verificação identifica o caminho de menor tempo, incluindo a penalidade de baldeação

#### Scenario: Empate no tempo total

- **WHEN** dois caminhos têm o mesmo tempo total e diferentes quantidades de baldeações
- **THEN** a verificação identifica o caminho com menos baldeações
