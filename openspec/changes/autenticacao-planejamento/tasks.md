## 1. Preparação e segurança

- [x] 1.1 Comparar o esquema atual do Xano com esta mudança, registrar divergências e confirmar que não existe tabela autenticada ou grupo de API de autenticação.

- [x] 1.2 Fazer backup do workspace Xano com esquema e registros antes de qualquer alteração e verificar a lista e os hashes dos arquivos.

- [x] 1.3 Obter aprovação explícita antes de criar ou alterar tabelas, endpoints e configurações de autenticação no Xano.

## 2. Modelagem de usuários no Xano

- [x] 2.1 Criar a tabela autenticada `usuarios` sem geração automática de CRUD e verificar que ela contém apenas `id`, `created_at`, `email`, `senha` e `ativo`.

- [x] 2.2 Configurar `email` como obrigatório, não anulável, normalizado com `trim` e minúsculas, e verificar a rejeição de valores sem formato válido.

- [x] 2.3 Criar índice único para `email` e verificar que variações de caixa ou espaços não permitem contas duplicadas após normalização.

- [x] 2.4 Configurar `senha` com o tipo seguro de senha do Xano, mínimo de oito caracteres e exclusão das respostas e históricos.

- [x] 2.5 Configurar `ativo` como booleano obrigatório, não anulável e com padrão `true`, e verificar o valor aplicado em novo cadastro.

## 3. APIs de autenticação

- [x] 3.1 Criar o grupo de API `auth` sem CRUD genérico e verificar que somente os endpoints aprovados estão expostos.

- [x] 3.2 Implementar o cadastro com normalização, validação, criação da conta e emissão de token, verificando a resposta pública sem senha ou hash.

- [x] 3.3 Implementar o login com e-mail e senha, conta ativa e mensagem genérica para credenciais inválidas, verificando que a resposta não permite enumerar contas.

- [x] 3.4 Implementar a consulta da sessão atual com autenticação obrigatória e verificar respostas para token válido, ausente, inválido e expirado.

- [x] 3.5 Configurar duração inicial de 24 horas para o token e verificar que ele é aceito somente pelo mecanismo de autorização definido.

## 4. Sessão no Reflex

- [x] 4.1 Implementar no backend Reflex o cliente dos endpoints de autenticação do Xano e verificar que o token não é enviado em URL nem registrado em logs.

- [x] 4.2 Armazenar o token em cookie de sessão `HttpOnly` e `SameSite=Lax`, habilitando `Secure` em produção, e verificar as propriedades por ambiente.

- [x] 4.3 Implementar os formulários e estados de cadastro e login, verificando carregamento, sucesso, campos inválidos e falhas de credenciais.

- [x] 4.4 Restaurar a sessão ao iniciar a aplicação por meio da consulta da sessão atual e verificar os estados `idle`, `loading`, `authenticated` e `unauthenticated`.

- [x] 4.5 Implementar logout por remoção do cookie e limpeza do estado autenticado, verificando que solicitações posteriores sejam tratadas como não autenticadas.

- [x] 4.6 Proteger a interface de planejamento e verificar o redirecionamento ao login quando não houver sessão válida.

## 5. Integração com o planejamento

- [x] 5.1 Aplicar autenticação obrigatória aos endpoints de planejamento e verificar que a identidade seja resolvida antes das validações e do cálculo.

- [x] 5.2 Diferenciar respostas de não autorizado das respostas de entrada inválida, trajeto inexistente e falha do serviço.

- [x] 5.3 Atualizar a mudança `buscar-trajetos-metro-mvp` após a autenticação integrada, marcando apenas as tarefas de dependência efetivamente comprovadas.

## 6. Testes e auditoria

- [x] 6.1 Testar cadastro válido, normalização do e-mail, e-mail duplicado, formato inválido e senha curta.

- [x] 6.2 Testar login válido, senha incorreta, e-mail inexistente e conta inativa, confirmando a mesma resposta pública para credenciais inválidas.

- [x] 6.3 Testar sessão válida, ausente, inválida e expirada e verificar ausência de dados de usuário nas falhas.

- [ ] 6.4 Testar que senha, hash e token não aparecem em respostas indevidas, URLs, históricos ou logs.

- [x] 6.5 Testar restauração da sessão, proteção do planejamento e logout no Reflex.

- [x] 6.6 Fazer backup pós-implementação do Xano e comparar arquivos e hashes com o backup anterior, documentando somente as mudanças esperadas.

- [x] 6.7 Executar a validação estrita das mudanças OpenSpec relacionadas e os testes automatizados do projeto antes do commit.

## Evidencia complementar de 13/09/2026

Login de usuario via cliente Python e consultas autenticadas de estacoes e
trajeto passaram em execucao manual. Isso nao encerra os cenarios de sessao
ausente, invalida ou expirada, nem substitui a verificacao no navegador.
Consulte `docs/validacao-integracao-xano.md`. As marcacoes anteriores foram
preservadas; a revisao atual nao reexecutou a suite completa.

## Atualizacao da suite automatizada — 13/09/2026

O usuario executou novamente a suite no terminal do projeto apos corrigir a
asserção de login bem-sucedido que estava no teste de sessao ausente. Resultado:
`35 passed, 1 warning in 1.84s`. A correcao apenas reposicionou a asserção; nao
alterou o comportamento da aplicacao. O registro anterior de bloqueio descreve
a tentativa no ambiente do assistente. A validacao estrita OpenSpec passou posteriormente para as duas mudancas
(2 passed, 0 failed), conforme captura do usuario. Os cenarios completos no
navegador continuam pendentes.
