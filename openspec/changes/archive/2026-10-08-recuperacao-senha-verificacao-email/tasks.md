## Contratos e dados

- [x] Definir o provedor de e-mail, remetente e URLs por ambiente sem versionar segredos.
- [x] Modelar no Xano o estado de verificação, a revogação de sessões e os tokens com hash, finalidade, expiração e consumo.
- [x] Corrigir e validar o endpoint publicado de confirmação para localizar tokens ainda não consumidos sem rejeitar o valor vazio de `consumido_em`.
- [x] Tornar a validação e o consumo dos tokens de confirmação e recuperação atômicos no Xano, com bloqueio da linha, para impedir usos simultâneos do mesmo token.
- [x] Migrar usuários existentes como verificados antes de exigir confirmação em novos cadastros.

## Backend e interface

- [x] Ampliar o cliente Xano e a API local com respostas genéricas e validação segura dos tokens.
- [x] Alterar o cadastro para informar a necessidade de confirmação sem iniciar sessão.
- [x] Criar páginas Reflex para aguardar confirmação, reenviar e-mail, solicitar recuperação e definir nova senha.
- [x] Confirmar no Xano a invalidação de todas as sessões após redefinir a senha; o redirecionamento local para login foi validado com uma sessão real anterior.
  - [x] Restaurar em `auth/me` a comparação entre a versão do JWT e `versao_sessao` do usuário.
  - [x] Aplicar a mesma comparação autenticada aos endpoints `estacoes` e `trajetos/buscar` e validar o planejamento nos dois sentidos.
  - [x] Comprovar com uma sessão real anterior que o Xano rejeita a consulta e redireciona para o login depois da redefinição.

## Validação

- [x] Cobrir conta existente e inexistente com resposta genérica e duração mínima uniforme de 2 segundos.
- [x] Cobrir token válido, expirado, consumido, substituído e de finalidade incorreta sem revelar o estado interno.
- [x] Confirmar que o redirecionamento rastreado do Brevo preserva o fragmento: links registrados como clicados concluíram confirmações reais sem expor o token nos registros examinados.
- [x] Cobrir login antes e depois da confirmação e migração das contas atuais.
- [x] Validar a entrega real dos e-mails de confirmação e confirmar no Xano duas contas de teste como ativas e verificadas.
- [x] Concluir os cenários de token e sessão antiga; a suíte com 100 testes, 18 subtestes e a validação estrita dos 6 itens OpenSpec passaram em 08/10/2026.
