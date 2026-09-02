## 1. Preparação e segurança



- \[ ] 1.1 Comparar o esquema atual do Xano com esta mudança, registrar divergências e confirmar que não existe tabela autenticada ou grupo de API de autenticação.

- \[ ] 1.2 Fazer backup do workspace Xano com esquema e registros antes de qualquer alteração e verificar a lista e os hashes dos arquivos.

- \[ ] 1.3 Obter aprovação explícita antes de criar ou alterar tabelas, endpoints e configurações de autenticação no Xano.



## 2. Modelagem de usuários no Xano



- \[ ] 2.1 Criar a tabela autenticada `usuarios` sem geração automática de CRUD e verificar que ela contém apenas `id`, `created\_at`, `email`, `senha` e `ativo`.

- \[ ] 2.2 Configurar `email` como obrigatório, não anulável, normalizado com `trim` e minúsculas, e verificar a rejeição de valores sem formato válido.

- \[ ] 2.3 Criar índice único para `email` e verificar que variações de caixa ou espaços não permitem contas duplicadas após normalização.

- \[ ] 2.4 Configurar `senha` com o tipo seguro de senha do Xano, mínimo de oito caracteres e exclusão das respostas e históricos.

- \[ ] 2.5 Configurar `ativo` como booleano obrigatório, não anulável e com padrão `true`, e verificar o valor aplicado em novo cadastro.



## 3. APIs de autenticação



- \[ ] 3.1 Criar o grupo de API `auth` sem CRUD genérico e verificar que somente os endpoints aprovados estão expostos.

- \[ ] 3.2 Implementar o cadastro com normalização, validação, criação da conta e emissão de token, verificando a resposta pública sem senha ou hash.

- \[ ] 3.3 Implementar o login com e-mail e senha, conta ativa e mensagem genérica para credenciais inválidas, verificando que a resposta não permite enumerar contas.

- \[ ] 3.4 Implementar a consulta da sessão atual com autenticação obrigatória e verificar respostas para token válido, ausente, inválido e expirado.

- \[ ] 3.5 Configurar duração inicial de 24 horas para o token e verificar que ele é aceito somente pelo mecanismo de autorização definido.



## 4. Sessão no Reflex



- \[ ] 4.1 Implementar no backend Reflex o cliente dos endpoints de autenticação do Xano e verificar que o token não é enviado em URL nem registrado em logs.

- \[ ] 4.2 Armazenar o token em cookie de sessão `HttpOnly` e `SameSite=Lax`, habilitando `Secure` em produção, e verificar as propriedades por ambiente.

- \[ ] 4.3 Implementar os formulários e estados de cadastro e login, verificando carregamento, sucesso, campos inválidos e falhas de credenciais.

- \[ ] 4.4 Restaurar a sessão ao iniciar a aplicação por meio da consulta da sessão atual e verificar os estados `idle`, `loading`, `authenticated` e `unauthenticated`.

- \[ ] 4.5 Implementar logout por remoção do cookie e limpeza do estado autenticado, verificando que solicitações posteriores sejam tratadas como não autenticadas.

- \[ ] 4.6 Proteger a interface de planejamento e verificar o redirecionamento ao login quando não houver sessão válida.



## 5. Integração com o planejamento



- \[ ] 5.1 Aplicar autenticação obrigatória aos endpoints de planejamento quando forem criados e verificar que a identidade seja resolvida antes das validações e do cálculo.

- \[ ] 5.2 Diferenciar respostas de não autorizado das respostas de entrada inválida, trajeto inexistente e falha do serviço.

- \[ ] 5.3 Atualizar a mudança `buscar-trajetos-metro-mvp` somente após a autenticação estar integrada, marcando apenas as tarefas de dependência efetivamente comprovadas.



## 6. Testes e auditoria



- \[ ] 6.1 Testar cadastro válido, normalização do e-mail, e-mail duplicado, formato inválido e senha curta.

- \[ ] 6.2 Testar login válido, senha incorreta, e-mail inexistente e conta inativa, confirmando a mesma resposta pública para credenciais inválidas.

- \[ ] 6.3 Testar sessão válida, ausente, inválida e expirada e verificar ausência de dados de usuário nas falhas.

- \[ ] 6.4 Testar que senha, hash e token não aparecem em respostas indevidas, URLs, históricos ou logs.

- \[ ] 6.5 Testar restauração da sessão, proteção do planejamento e logout no Reflex.

- \[ ] 6.6 Fazer backup pós-implementação do Xano e comparar arquivos e hashes com o backup anterior, documentando somente as mudanças esperadas.

- \[ ] 6.7 Executar a validação estrita das mudanças OpenSpec relacionadas e os testes automatizados do projeto antes do commit.
