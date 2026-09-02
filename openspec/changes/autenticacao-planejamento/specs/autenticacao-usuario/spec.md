## Purpose



Define a autenticação mínima por e-mail e senha para identificar usuários, manter uma sessão e restringir o planejamento de trajetos a solicitações autenticadas.



## ADDED Requirements



### Requirement: Cadastro de usuário



O sistema SHALL permitir o cadastro com um e-mail válido e uma senha de, no mínimo, oito caracteres. O e-mail SHALL ser normalizado com remoção de espaços nas extremidades e conversão para minúsculas antes da validação de unicidade.



#### Scenario: Cadastro válido



- **WHEN** o usuário informa um e-mail ainda não cadastrado e uma senha válida

- **THEN** o sistema cria a conta e retorna uma sessão autenticada associada ao novo usuário



#### Scenario: E-mail duplicado com variação de caixa ou espaços



- **WHEN** o usuário informa um e-mail que, após normalização, já pertence a outra conta

- **THEN** o sistema rejeita o cadastro sem criar um segundo usuário



#### Scenario: Dados de cadastro inválidos



- **WHEN** o usuário informa um e-mail inválido ou uma senha com menos de oito caracteres

- **THEN** o sistema rejeita o cadastro e identifica os campos inválidos sem retornar dados sensíveis



### Requirement: Proteção da senha



O sistema SHALL armazenar a senha somente por meio de um mecanismo seguro de hash e SHALL excluir a senha e seu hash de todas as respostas, históricos e mensagens de erro.



#### Scenario: Resposta após cadastro ou login



- **WHEN** uma operação de cadastro ou login é concluída

- **THEN** a resposta não contém a senha nem seu hash



### Requirement: Login por e-mail e senha



O sistema SHALL autenticar uma conta ativa quando receber o e-mail normalizado e a senha correspondentes, emitindo um token de sessão.



#### Scenario: Login válido



- **WHEN** o usuário informa credenciais válidas de uma conta ativa

- **THEN** o sistema retorna um token de sessão e os dados públicos do usuário autenticado



#### Scenario: Credenciais inválidas



- **WHEN** o e-mail não existe ou a senha não corresponde à conta

- **THEN** o sistema rejeita o login com uma mensagem genérica que não revela qual credencial falhou



### Requirement: Consulta da sessão atual



O sistema SHALL permitir que o cliente consulte a identidade associada a um token de sessão válido.



#### Scenario: Sessão válida



- **WHEN** o cliente consulta a sessão atual com um token válido

- **THEN** o sistema retorna o identificador e o e-mail do usuário autenticado



#### Scenario: Sessão ausente, inválida ou expirada



- **WHEN** o cliente consulta a sessão atual sem token ou com um token inválido ou expirado

- **THEN** o sistema retorna uma resposta de não autorizado sem dados de usuário



### Requirement: Autenticação das solicitações protegidas



O sistema SHALL aceitar o token de sessão no cabeçalho de autorização das solicitações protegidas e SHALL validar a sessão antes de executar o planejamento de trajetos.



#### Scenario: Planejamento com sessão válida



- **WHEN** o usuário solicita um planejamento de trajeto com um token válido

- **THEN** o sistema permite que a solicitação prossiga para as validações e o cálculo do trajeto



#### Scenario: Planejamento sem sessão válida



- **WHEN** o usuário solicita um planejamento sem token ou com um token inválido ou expirado

- **THEN** o sistema rejeita a solicitação como não autorizada antes de calcular o trajeto



### Requirement: Logout no cliente



O cliente SHALL encerrar a sessão local descartando o token e limpando o estado do usuário autenticado.



#### Scenario: Logout concluído



- **WHEN** o usuário solicita logout

- **THEN** o cliente remove o token e os dados locais da sessão e passa a tratar novas solicitações como não autenticadas
