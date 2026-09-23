## Auditoria e expiração

- [ ] Verificar que senha, hash e token não aparecem em respostas indevidas, URLs, históricos novos ou logs dos fluxos examinados.
- [ ] Após a publicação das configurações do Xano, executar uma chamada HTTP de cadastro ou login com conta de teste e confirmar que ela não gera Request History nos endpoints emissores de token.
- [ ] Observar uma sessão expirar naturalmente com a página de busca aberta e confirmar bloqueio da consulta e redirecionamento para o login.
- [ ] Registrar evidências sem valores sensíveis, executar os testes pertinentes e validar esta mudança no OpenSpec.
