## Context

O Xano armazena usuários e emite tokens de sessão. O backend Python atua como fronteira de segurança e o Reflex apresenta os formulários. Atualmente o cadastro inicia uma sessão imediatamente e não existe provedor de e-mail configurado.

## Goals / Non-Goals

- Confirmar a posse do e-mail antes de permitir login.
- Recuperar senha sem revelar se o endereço está cadastrado.
- Impedir reutilização, armazenamento em texto puro e validade indefinida dos tokens.
- Não implementar autenticação social, segundo fator ou troca de e-mail nesta mudança.

## Decisions

- O cadastro cria a conta pendente e não inicia sessão antes da confirmação.
- Tokens terão no mínimo 256 bits de entropia. O Xano armazenará apenas um hash criptográfico e metadados de finalidade, usuário, expiração e consumo.
- Verificação de e-mail terá validade de 24 horas; recuperação de senha, 30 minutos.
- Emitir novo token invalida tokens anteriores da mesma finalidade para o usuário.
- Solicitar recuperação sempre retorna a mesma mensagem e status, exista ou não a conta.
- A redefinição bem-sucedida invalida todas as sessões existentes do usuário.
- Os links entregues por e-mail contêm o token somente no fragmento ou em uma página que o remove da barra antes de enviar ao backend; nenhum histórico ou log deve conservá-lo.
- A integração de e-mail será encapsulada e configurada por variáveis de ambiente. Nenhuma chave será versionada.

## Risks / Trade-offs

- Entrega de e-mail depende de um provedor externo e de configuração de domínio/remetente.
- A invalidação de sessões exige um marcador de versão ou data no usuário e validação correspondente nos endpoints protegidos.
- Contas antigas precisarão de migração explícita para não serem bloqueadas acidentalmente.

## Migration Plan

1. Adicionar campos e tabela sem alterar o login existente.
2. Marcar contas existentes como verificadas na migração.
3. Publicar endpoints e integração de e-mail com histórico sensível desativado.
4. Publicar as páginas Reflex e ativar a exigência de verificação.
5. Validar cadastro, confirmação, recuperação, expiração, uso único e revogação de sessão.

## Configuração adotada

- O provedor de e-mail escolhido para o ambiente acadêmico é o Brevo, com remetente `metroflow.projeto@gmail.com`. A chave permanece somente na configuração secreta do Xano.
- Durante o desenvolvimento, os links apontam para a aplicação local na porta em que o Reflex estiver executando. Uma URL pública deverá ser configurada antes de publicar o sistema fora do ambiente local.
- O rastreamento de links do provedor precisa preservar o fragmento usado pelo token ou ser desativado nesses links; essa integração ainda requer validação ponta a ponta.
