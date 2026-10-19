## ADDED Requirements

### Requirement: Extremos distintos

O sistema SHALL impedir o armazenamento de um trecho cuja origem seja igual ao destino.

#### Scenario: Extremos iguais

- **WHEN** uma gravação tenta usar a mesma estação como origem e destino
- **THEN** a operação é rejeitada antes de persistir o trecho

### Requirement: Unicidade física por linha

O sistema SHALL impedir o armazenamento de dois trechos físicos não direcionados entre as mesmas estações na mesma linha, independentemente do sentido informado. Trechos explicitamente direcionados de serviços especiais SHALL preservar a orientação para permitir arcos opostos legítimos.

#### Scenario: Duplicata inversa

- **WHEN** já existe um trecho entre duas estações de uma linha e uma gravação inverte seus extremos
- **THEN** a operação é rejeitada sem criar outro registro

#### Scenario: Serviço explicitamente direcionado

- **WHEN** um serviço especial possui trechos direcionados opostos entre as mesmas estações
- **THEN** cada orientação é preservada como um arco distinto
