# exclusividade-viagens Specification

## Purpose
Garantir no máximo uma viagem ativa por usuário após confirmações simultâneas, preservando autenticação, histórico, calibração e isolamento entre contas.

## Requirements

### Requirement: Exclusividade transacional por conta
O sistema SHALL serializar confirmações do mesmo usuário desde antes da leitura das viagens substituídas até o commit da nova viagem, usando um registro estável mesmo quando ainda não exista viagem anterior.

#### Scenario: Duas confirmações simultâneas
- **WHEN** duas requisições válidas da mesma conta são enviadas com sobreposição
- **THEN** ambas podem confirmar com sucesso, mas após os commits somente a última viagem permanece ativa, com a anterior substituída

#### Scenario: Primeira viagem da conta
- **WHEN** duas confirmações disputam a primeira viagem de um usuário sem viagem ativa
- **THEN** a exclusividade não depende da existência de um registro anterior em viagens

#### Scenario: Outra conta
- **WHEN** contas distintas confirmam trajetos
- **THEN** não compartilham o bloqueio por usuário e não substituem viagens umas das outras

### Requirement: Validar após a espera
O sistema SHALL revalidar a sessão e a idade máxima de 30 segundos da referência após adquirir o bloqueio e SHALL não gravar viagem caso essa validação falhe.

#### Scenario: Referência vence esperando
- **WHEN** o bloqueio só é obtido depois de a referência da busca vencer
- **THEN** a confirmação é rejeitada sem substituir nem inserir viagens

#### Scenario: Sessão invalidada durante espera
- **WHEN** estado, e-mail verificado ou versão de sessão mudam antes de adquirir o bloqueio
- **THEN** o registro rejeita a sessão sem alterar viagens

### Requirement: Preservar cálculo e dados
A correção SHALL manter contrato de resposta, cálculo de trajetos, calibração, malha e parâmetros atuais. O bloqueio SHALL ser liberado automaticamente por commit ou rollback, sem alterar campos do usuário.

#### Scenario: Erro na transação
- **WHEN** ocorre erro depois de adquirir o bloqueio
- **THEN** a transação reverte suas alterações e libera o bloqueio
