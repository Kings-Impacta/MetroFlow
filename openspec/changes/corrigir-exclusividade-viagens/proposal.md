## Why

Os testes HTTP de 11/11 reproduziram duas viagens ativas para a mesma conta nos pares 70/71 e 75/76. A transação atual não serializa a leitura anterior à inserção.

## What Changes

- Bloquear o registro já existente do usuário autenticado dentro da transação de confirmação, antes de consultar viagens anteriores.
- Revalidar sessão e idade da referência depois da espera; encerrar as viagens anteriores e inserir a nova sob o mesmo bloqueio.
- Preservar contrato HTTP, cálculo, calibração, histórico e parâmetros. Fazer backup, publicar somente o endpoint de registro e repetir a disputa autenticada.

## Capabilities

### Added Capabilities
- `exclusividade-viagens`: serialização transacional da confirmação por usuário.

## Impact

Somente a transação de `viagens/confirmar` no Xano e evidências/testes/documentação. Sem migração, índice, tabela, novo campo de usuário, alteração de malha ou de parâmetros de lotação.
