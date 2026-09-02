## Why



O planejamento de trajetos deve estar disponível somente para usuários autenticados, mas o projeto ainda não possui identidade de usuário nem um contrato de sessão. Esta mudança define a autenticação mínima por e-mail e senha necessária para proteger o planejamento no MVP.



## What Changes



- Adicionar cadastro de usuário com e-mail e senha.

- Exigir e-mail obrigatório, normalizado e único.

- Armazenar senhas exclusivamente pelo mecanismo seguro de autenticação do Xano.

- Adicionar login com e-mail e senha e emissão de token de autenticação.

- Adicionar consulta da sessão atual para validar o usuário autenticado.

- Proteger o planejamento de trajetos para aceitar somente sessões válidas.

- Tratar sessão ausente, inválida ou expirada sem expor dados sensíveis.

- Implementar logout no cliente por descarte do token e limpeza do estado autenticado.

- Manter recuperação de senha e verificação de e-mail fora do escopo desta mudança.



## Capabilities



### New Capabilities



- `autenticacao-usuario`: cadastro por e-mail e senha, login, sessão atual, logout no cliente e exigência de sessão válida para planejar trajetos.



### Modified Capabilities



Nenhuma capacidade publicada existente será modificada.



## Impact



- Nova tabela autenticada de usuários no Xano.

- Novos endpoints de cadastro, login e consulta da sessão atual.

- Endpoints de planejamento protegidos por autenticação.

- Interface Reflex com telas e estados de cadastro, login, sessão e logout.

- Armazenamento e envio seguro do token pelo cliente.

- Novos cenários automatizados para autenticação válida, credenciais inválidas, e-mail duplicado e sessão ausente, inválida ou expirada.
