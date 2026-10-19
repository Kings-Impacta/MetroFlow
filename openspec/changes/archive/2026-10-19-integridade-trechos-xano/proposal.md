## Why

O Xano impede duplicatas diretas, mas não há garantia de armazenamento contra extremos iguais ou duplicatas inversas. O plano atual não oferece trigger de tabela para aplicar as duas regras.

## What Changes

- Definir um único ponto de gravação que rejeite extremos iguais e duplicatas inversas antes de persistir trechos.
- Testar essas regras e as demais invariantes dos trechos com dados controlados.

## Capabilities

### New Capabilities

- `integridade-trechos`: Protege o cadastro de trechos contra entradas estruturalmente inválidas.

### Modified Capabilities

Nenhuma até que a implementação seja aprovada.

## Impact

Fluxo de escrita do Xano e testes de integridade. A proposta não autoriza alteração remota nem exige mudança de plano.
