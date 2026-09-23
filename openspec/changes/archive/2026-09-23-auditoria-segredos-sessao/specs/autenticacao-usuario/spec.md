## MODIFIED Requirements

### Requirement: Proteção da senha

O sistema SHALL armazenar a senha somente por meio de um mecanismo seguro de hash e SHALL excluir senha, hash e token de respostas indevidas, URLs, históricos de requisições e logs.

#### Scenario: Resposta após cadastro ou login

- **WHEN** uma operação de cadastro ou login é concluída
- **THEN** a resposta não contém a senha nem seu hash

#### Scenario: Auditoria após cadastro ou login

- **WHEN** uma chamada HTTP externa de cadastro ou login é concluída após a publicação da configuração de histórico
- **THEN** a resposta pública não contém senha ou hash e o histórico do endpoint não conserva senha, hash ou token

### Requirement: Consulta da sessão atual

O sistema SHALL permitir que o cliente consulte a identidade associada a um token de sessão válido e SHALL recusar uma sessão ausente, inválida ou expirada antes de consultar o planejamento.

#### Scenario: Sessão válida

- **WHEN** o cliente consulta a sessão atual com um token válido
- **THEN** o sistema retorna o identificador e o e-mail do usuário autenticado

#### Scenario: Sessão ausente, inválida ou expirada

- **WHEN** o cliente consulta a sessão atual sem token ou com um token inválido ou expirado
- **THEN** o sistema retorna uma resposta de não autorizado sem dados de usuário

#### Scenario: Expiração natural com o planejador aberto

- **WHEN** a sessão expira enquanto o usuário mantém a página de busca aberta e tenta consultar um trajeto
- **THEN** a consulta protegida é bloqueada, o resultado anterior é descartado e a interface direciona o usuário ao login