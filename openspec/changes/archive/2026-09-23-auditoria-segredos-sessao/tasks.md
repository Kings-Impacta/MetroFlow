## Auditoria e expiração

- [x] Verificar que senha, hash e token não aparecem em respostas indevidas, URLs, históricos novos ou logs dos fluxos examinados.
- [x] Após a publicação das configurações do Xano, executar uma chamada HTTP de cadastro ou login com conta de teste e confirmar que ela não gera Request History nos endpoints emissores de token.
- [x] Observar uma sessão expirar com a página de busca aberta e confirmar bloqueio da consulta e redirecionamento para o login.
- [x] Registrar evidências sem valores sensíveis, executar os testes pertinentes e validar esta mudança no OpenSpec.