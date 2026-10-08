## MODIFIED Requirements

### Requirement: Cadastro de usuário

O sistema SHALL permitir o cadastro com um e-mail válido e uma senha de, no mínimo, oito caracteres. O e-mail SHALL ser normalizado com remoção de espaços nas extremidades e conversão para minúsculas antes da validação de unicidade. Uma nova conta SHALL permanecer pendente e sem sessão autenticada até a confirmação do e-mail.

#### Scenario: Cadastro válido

- **WHEN** o usuário informa um e-mail ainda não cadastrado e uma senha válida
- **THEN** o sistema cria a conta pendente, solicita a entrega da mensagem de confirmação e não inicia uma sessão

#### Scenario: E-mail duplicado com variação de caixa ou espaços

- **WHEN** o usuário informa um e-mail que, após normalização, já pertence a outra conta
- **THEN** o sistema não cria um segundo usuário e apresenta uma resposta que não expõe detalhes internos da conta existente

#### Scenario: Dados de cadastro inválidos

- **WHEN** o usuário informa um e-mail inválido ou uma senha com menos de oito caracteres
- **THEN** o sistema rejeita o cadastro e identifica os campos inválidos sem retornar dados sensíveis

### Requirement: Login por e-mail e senha

O sistema SHALL autenticar somente uma conta ativa e com e-mail verificado quando receber o e-mail normalizado e a senha correspondentes, emitindo um token de sessão.

#### Scenario: Login válido

- **WHEN** o usuário informa credenciais válidas de uma conta ativa e verificada
- **THEN** o sistema retorna um token de sessão e os dados públicos do usuário autenticado

#### Scenario: Credenciais inválidas

- **WHEN** o e-mail não existe ou a senha não corresponde à conta
- **THEN** o sistema rejeita o login com uma mensagem genérica que não revela qual credencial falhou

#### Scenario: E-mail ainda não verificado

- **WHEN** a senha está correta, mas o endereço da conta ainda não foi confirmado
- **THEN** o sistema não cria sessão e orienta o usuário a concluir ou reenviar a verificação

## ADDED Requirements

### Requirement: Confirmação do e-mail

O sistema SHALL confirmar o endereço somente com um token válido, temporário, de uso único e associado à finalidade de verificação.

#### Scenario: Confirmação válida

- **WHEN** o usuário apresenta um token de verificação válido dentro de 24 horas
- **THEN** o sistema marca o e-mail como verificado, consome o token e permite login posterior

#### Scenario: Token de confirmação inválido

- **WHEN** o token está expirado, consumido, substituído ou pertence a outra finalidade
- **THEN** o sistema não confirma a conta e oferece a opção de solicitar uma nova mensagem

### Requirement: Reenvio de verificação

O sistema SHALL responder de forma genérica ao pedido de reenvio e SHALL invalidar tokens anteriores da mesma finalidade ao emitir um novo.

#### Scenario: Pedido de reenvio

- **WHEN** qualquer e-mail válido é informado para reenvio
- **THEN** o sistema retorna a mesma resposta pública e somente envia a mensagem quando houver uma conta pendente elegível

### Requirement: Solicitação de recuperação de senha

O sistema SHALL aceitar pedidos de recuperação sem revelar se o e-mail existe, está ativo ou está verificado.

#### Scenario: Pedido para qualquer e-mail válido

- **WHEN** um endereço válido é informado para recuperação
- **THEN** o sistema retorna uma resposta genérica e somente cria e envia um token quando a conta for elegível

### Requirement: Redefinição de senha

O sistema SHALL redefinir a senha somente com um token de recuperação válido, temporário, de uso único e armazenado como hash.

#### Scenario: Redefinição válida

- **WHEN** o usuário apresenta um token de recuperação válido dentro de 30 minutos e uma nova senha válida
- **THEN** o sistema atualiza o hash da senha, consome o token e invalida todas as sessões existentes do usuário

#### Scenario: Token de recuperação inválido

- **WHEN** o token está expirado, consumido, substituído ou pertence a outra finalidade
- **THEN** o sistema não altera a senha e permite solicitar uma nova recuperação

### Requirement: Proteção dos tokens de ação

O sistema SHALL gerar tokens imprevisíveis, armazenar somente seus hashes e impedir que valores completos apareçam em respostas indevidas, logs ou históricos de requisição.

#### Scenario: Auditoria dos fluxos por e-mail

- **WHEN** verificação ou recuperação é executada e seus registros são examinados
- **THEN** nenhum token completo, senha ou chave do provedor está presente nas superfícies auditadas