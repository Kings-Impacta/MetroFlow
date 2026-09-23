## MODIFIED Requirements

### Requirement: Proteção da senha

O sistema SHALL armazenar a senha por um mecanismo seguro de hash e SHALL excluir senha, hash e token de respostas indevidas, URLs, históricos de requisições e logs.

#### Scenario: Auditoria após cadastro ou login

- **WHEN** uma chamada HTTP externa de cadastro ou login é concluída após a publicação da configuração de histórico
- **THEN** a resposta pública não contém senha ou hash e o histórico do endpoint não conserva senha, hash ou token

### Requirement: Consulta da sessão atual

O sistema SHALL recusar uma sessão ausente, inválida ou expirada antes de consultar o planejamento.

#### Scenario: Expiração natural com o planejador aberto

- **WHEN** a sessão expira enquanto o usuário mantém a página de busca aberta e tenta consultar um trajeto
- **THEN** a consulta protegida é bloqueada, o resultado anterior é descartado e a interface direciona o usuário ao login
