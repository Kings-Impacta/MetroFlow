## Why

O painel apresentou falha de verificação de acesso enquanto o Xano registrava consultas administrativas autorizadas (200) com grande latência. O cliente encerra uma tentativa após timeout, e a mensagem geral confunde indisponibilidade com permissão.

## What Changes

- Recuperação limitada a uma repetição de GET administrativo em falha transitória, com pausa de um segundo.
- Nunca repetir alterações POST, 401/403, 429 ou respostas que pedem Retry-After.
- Informar indisponibilidade do serviço quando as consultas falharem, preservando a distinção de acesso restrito.
- Registrar reprodução dos registros reais 89/90 e preservação da malha/parâmetros.

## Capabilities

### Modified Capabilities

- `portal-administrativo`: recuperação segura de consultas e mensagem de indisponibilidade.

## Impact

Somente cliente administrativo, mensagem e testes locais. Sem alterações no Xano, permissões, malha, tempos ou limites de concorrência. Não elimina lentidão externa persistente.
