## ADDED Requirements

### Requirement: Recuperação limitada de consultas administrativas

O cliente SHALL repetir no máximo uma vez uma consulta GET administrativa em timeout/falha de conexão ou HTTP 502/503/504 sem Retry-After, aguardando um segundo entre tentativas e mantendo a autenticação no Xano a cada chamada. SHALL não repetir POST, HTTP 401/403/429, respostas com Retry-After ou falhas de contrato. A indisponibilidade persistente SHALL ser apresentada como falha do serviço, sem presumir falta de permissão nem exibir dados protegidos antes de resposta autorizada.

#### Scenario: Leitura recuperável

- **WHEN** a primeira leitura sofre falha transitória e a segunda responde corretamente
- **THEN** a consulta apresenta a resposta válida após somente uma repetição

#### Scenario: Revogação durante a recuperação

- **WHEN** a segunda tentativa retorna 403
- **THEN** o acesso é negado sem usar informação ou autorização anterior

#### Scenario: Limite ou alteração

- **WHEN** há 429, Retry-After, resposta de contrato inválido ou uma alteração POST falha
- **THEN** não há repetição automática

#### Scenario: Serviço continua indisponível

- **WHEN** as duas tentativas permitidas falham
- **THEN** o painel informa indisponibilidade do serviço e permite nova tentativa manual, sem rotular o usuário como não administrador
