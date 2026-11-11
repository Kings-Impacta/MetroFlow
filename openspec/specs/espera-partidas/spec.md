# espera-partidas Specification

## Purpose
Selecionar o menor tempo total disponível considerando esperas por embarque, horários de funcionamento e continuidade no mesmo trem, com registro consistente.

## Requirements

### Requirement: Tempo total e preferência por serviço regular
O sistema SHALL minimizar viagem, baldeação e espera, priorizando serviços
regulares somente em empate de tempo e usando menos baldeações em seguida.

#### Scenario: Expresso distante da partida
- **WHEN** o próximo Expresso chega depois de uma opção regular de menor tempo total
- **THEN** a opção regular vence a comparação

#### Scenario: Especial efetivamente mais rápido
- **WHEN** a espera mais percurso especial resulta em menor tempo total
- **THEN** o serviço especial vence mesmo havendo serviço regular

#### Scenario: Empate depois de esperar
- **WHEN** dois caminhos empatam após esperar uma conexão, um deles sem serviço especial
- **THEN** vence o caminho sem serviço especial, independentemente da ordem dos trechos

### Requirement: Disponibilidade prevista
O sistema SHALL avaliar disponibilidade no embarque previsto e respeitar dias,
sentidos, feriados e encerramentos, sem cobrar espera por estação no mesmo trem.

#### Scenario: Linha 17 no domingo
- **WHEN** uma conexão alcança a Linha 17 no domingo
- **THEN** o serviço não é sugerido como se funcionasse nesse dia

#### Scenario: Conexão depois do encerramento
- **WHEN** o passageiro chega a uma conexão após sua última partida disponível
- **THEN** esse embarque não participa da rota

#### Scenario: Continuação no mesmo Expresso
- **WHEN** o passageiro permanece no mesmo trem em uma estação intermediária
- **THEN** não se cobra outra espera pela partida

### Requirement: Registro e compatibilidade
O sistema SHALL preservar o contrato legado, detalhar espera para clientes capazes
e recalcular a cronologia da viagem sem aceitar tempos arbitrários do navegador.

#### Scenario: Cliente anterior
- **WHEN** o cliente não solicita espera separada
- **THEN** recebe tempos de trecho que já incluem a espera e preservam a soma total

#### Scenario: Registro fora do prazo
- **WHEN** a confirmação usa uma busca com mais de 30 s de idade
- **THEN** o registro é rejeitado e uma nova busca é necessária
