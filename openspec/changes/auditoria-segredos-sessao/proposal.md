## Why

A autenticação já funciona, mas a exclusão de senha e token de todos os históricos e logs e a expiração natural de uma sessão com o planejador aberto ainda não têm comprovação suficiente.

## What Changes

- Auditar respostas, URLs, históricos e logs dos fluxos de cadastro, login e planejamento sem registrar segredos nas evidências.
- Confirmar por uma chamada HTTP nova que os endpoints emissores de token não criam histórico após a publicação da configuração do Xano.
- Observar uma sessão que expira com a página de busca aberta e confirmar o redirecionamento para o login.

## Capabilities

### New Capabilities

- `auditoria-sessao`: Comprova o tratamento de dados sensíveis e da expiração da sessão.

### Modified Capabilities

- `autenticacao-usuario`: Completa a proteção de segredos nos meios ainda não auditados.

## Impact

Testes e evidências de segurança; possíveis ajustes no Xano ou no Reflex somente se a auditoria encontrar falhas. Nenhuma mudança remota está autorizada por esta proposta.
