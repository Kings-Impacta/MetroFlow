## MODIFIED Requirements

### Requirement: Confirmação de viagem

O sistema SHALL permitir que o usuário autenticado confirme, por um botão no resultado do trajeto, que vai fazer a viagem apresentada, e SHALL registrar no Xano o usuário, o momento da confirmação e os trechos em ordem com seu sentido e `tempo_estimado`. Enquanto a confirmação é enviada, o botão SHALL ficar desativado e indicar carregamento. Após o registro, o botão SHALL ficar desativado e exibir "Viagem confirmada" até que outro resultado seja apresentado. Se a confirmação falhar por motivo diferente de sessão inválida, a interface SHALL exibir uma mensagem de erro e SHALL manter o botão disponível para nova tentativa. O retorno ao usuário SHALL não conter a lotação estimada nem indicar substituição do trajeto.

#### Scenario: Confirmação bem-sucedida

- **WHEN** o usuário autenticado aciona o botão de confirmação no resultado do trajeto
- **THEN** o sistema registra a viagem apresentada como viagem ativa desse usuário

#### Scenario: Sessão inválida na confirmação

- **WHEN** a confirmação é solicitada sem sessão válida
- **THEN** o sistema não registra a viagem e direciona o usuário para autenticação

#### Scenario: Usuário da viagem

- **WHEN** uma viagem é registrada
- **THEN** o usuário associado é obtido da sessão autenticada e não de um dado enviado pela interface

#### Scenario: Confirmação em andamento

- **WHEN** o usuário aciona o botão e a resposta da confirmação ainda não chegou
- **THEN** o botão fica desativado, indica carregamento e não envia outra confirmação

#### Scenario: Interface após a confirmação

- **WHEN** a viagem é registrada
- **THEN** o botão fica desativado e exibe "Viagem confirmada", sem informar lotação nem substituição do trajeto

#### Scenario: Falha na confirmação

- **WHEN** a confirmação falha por indisponibilidade do serviço, erro de rede ou recusa da viagem, com sessão válida
- **THEN** a interface exibe uma mensagem de erro e o botão "Confirmar viagem" volta a ficar disponível

#### Scenario: Novo resultado após a confirmação

- **WHEN** o usuário faz uma nova busca, troca as estações ou inverte origem e destino depois de confirmar
- **THEN** o novo resultado apresenta o botão "Confirmar viagem" disponível e sem mensagem de erro

#### Scenario: Resposta de confirmação de resultado anterior

- **WHEN** a resposta de uma confirmação chega depois que outro resultado foi apresentado ou a sessão local foi encerrada
- **THEN** a resposta é descartada e não altera o botão nem as mensagens do resultado atual
