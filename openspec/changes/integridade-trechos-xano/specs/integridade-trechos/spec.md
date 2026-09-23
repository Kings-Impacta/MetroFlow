## ADDED Requirements

### Requirement: Extremos distintos

O sistema SHALL impedir o armazenamento de um trecho cuja origem seja igual ao destino.

#### Scenario: Extremos iguais

- **WHEN** uma gravação tenta usar a mesma estação como origem e destino
- **THEN** a operação é rejeitada antes de persistir o trecho

### Requirement: Unicidade física por linha

O sistema SHALL impedir o armazenamento de dois trechos entre as mesmas estações na mesma linha, independentemente do sentido informado.

#### Scenario: Duplicata inversa

- **WHEN** já existe um trecho entre duas estações de uma linha e uma gravação inverte seus extremos
- **THEN** a operação é rejeitada sem criar outro registro
