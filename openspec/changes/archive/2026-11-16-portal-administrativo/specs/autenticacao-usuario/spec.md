## MODIFIED Requirements

### Requirement: Consulta da sessão atual

O sistema SHALL permitir que o cliente consulte a identidade associada a um token de sessão válido, incluindo a indicação de que o usuário é administrador, e SHALL recusar uma sessão ausente, inválida ou expirada antes de consultar o planejamento. A indicação SHALL servir somente para adaptar a interface e SHALL não autorizar operações administrativas.

#### Scenario: Sessão válida

- **WHEN** o cliente consulta a sessão atual com um token válido
- **THEN** o sistema retorna o identificador, o e-mail e a indicação de administrador do usuário autenticado

#### Scenario: Indicação de administrador indisponível

- **WHEN** a resposta do Xano não contém a indicação de administrador ou contém um valor que não é booleano verdadeiro
- **THEN** o usuário é tratado como não administrador e a consulta da sessão continua válida

#### Scenario: Sessão ausente, inválida ou expirada

- **WHEN** o cliente consulta a sessão atual sem token ou com um token inválido ou expirado
- **THEN** o sistema retorna uma resposta de não autorizado sem dados de usuário

#### Scenario: Expiração natural com o planejador aberto

- **WHEN** a sessão expira enquanto o usuário mantém a página de busca aberta e tenta consultar um trajeto
- **THEN** a consulta protegida é bloqueada, o resultado anterior é descartado e a interface direciona o usuário ao login
