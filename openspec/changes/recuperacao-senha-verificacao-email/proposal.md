## Why

O MetroFlow ainda não permite confirmar que o endereço informado pertence ao usuário nem recuperar o acesso sem intervenção manual. A implementação deve evitar enumeração de contas, vazamento de tokens e reutilização de links.

## What Changes

- Tornar a verificação de e-mail obrigatória antes do primeiro login.
- Permitir reenvio controlado da mensagem de verificação.
- Criar solicitação e conclusão de recuperação de senha com resposta genérica.
- Usar tokens aleatórios, temporários, de uso único e armazenados apenas como hash.
- Invalidar tokens anteriores e sessões existentes após a redefinição de senha.
- Adicionar páginas Reflex e endpoints locais que não exponham segredos ao navegador, às URLs persistidas ou aos logs.

## Capabilities

### New Capabilities

Nenhuma. Os novos fluxos ampliam `autenticacao-usuario`.

### Modified Capabilities

- `autenticacao-usuario`: passa a exigir e-mail verificado e oferece recuperação segura de senha.

## Impact

Novos campos e uma tabela de tokens no Xano, endpoints de autenticação, integração com um provedor de e-mail, páginas Reflex e testes. O login atual continuará aceitando somente contas ativas e passará a distinguir internamente a pendência de verificação sem revelar dados indevidos ao público.