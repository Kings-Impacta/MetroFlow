## Context



O MetroFlow usa Reflex na interface e Xano como backend. O workspace do Xano possui atualmente apenas as tabelas de transporte, todas sem autenticação, e ainda não existem grupos de API. O planejamento de trajetos deverá exigir uma identidade autenticada antes da execução da busca.



A autenticação deve permanecer independente da lógica de Dijkstra e do futuro histórico de trajetos. O Xano será a fonte de identidade e o emissor do token; o Reflex será responsável pela experiência de cadastro, login, restauração da sessão e logout.



## Goals / Non-Goals



**Goals:**



- Criar identidade de usuário com e-mail e senha no Xano.

- Normalizar e proteger o e-mail com unicidade independente de caixa.

- Usar o mecanismo nativo do Xano para hash e verificação de senha.

- Disponibilizar cadastro, login e consulta da sessão atual.

- Exigir autenticação nos endpoints de planejamento.

- Manter o token fora de URLs, logs, mensagens e conteúdo renderizado.

- Tratar estados de sessão ausente, inválida e expirada no Reflex.

- Permitir rollback sem excluir contas ou dados existentes.



**Non-Goals:**



- Recuperação ou alteração de senha.

- Verificação de endereço de e-mail.

- Login social, autenticação multifator ou login sem senha.

- Perfis, permissões administrativas ou múltiplos papéis.

- Histórico de trajetos.

- Revogação individual de tokens antes da expiração.

- Alteração da lógica de cálculo de trajetos.



## Decisions



### Tabela autenticada de usuários no Xano



Será criada a tabela autenticada `usuarios`, seguindo a nomenclatura em português e sem acentos usada pelo projeto. Ela conterá `id`, `created\_at`, `email`, `senha` e `ativo`.



`email` será obrigatório, normalizado com `trim` e conversão para minúsculas, e protegido por índice único. `senha` utilizará o tipo de senha e o mecanismo de hash do Xano; o valor original e o hash nunca serão retornados. `ativo` será obrigatório, não anulável e terá padrão `true`.



Uma conta inativa não poderá obter uma nova sessão nem utilizar endpoints protegidos.



Alternativa considerada: usar uma tabela genérica chamada `user`. Foi rejeitada para manter consistência com as demais tabelas do domínio e tornar explícito o significado no projeto.



### Grupo e contratos de API



Será criado um grupo de API `auth` com três operações:



- cadastro por e-mail e senha;

- login por e-mail e senha;

- consulta da sessão atual.



Cadastro e login retornarão um token de autenticação e os dados públicos mínimos do usuário: `id` e `email`. A consulta da sessão atual exigirá token válido e retornará os mesmos dados públicos.



Os endpoints de planejamento usarão o mesmo mecanismo de autenticação e resolverão o usuário antes de executar validações ou cálculo de rota.



Alternativa considerada: gerar CRUD automático para `usuarios`. Foi rejeitada porque exporia operações desnecessárias e aumentaria o risco de retornar campos sensíveis.



### Normalização e mensagens de erro



O e-mail será normalizado antes das consultas e gravações. A unicidade no banco continuará sendo a última barreira contra concorrência e cadastros duplicados.



Falhas de login usarão uma mensagem genérica para e-mail inexistente, senha incorreta ou conta inativa. As respostas não indicarão qual condição falhou.



Validações de formato de e-mail e senha mínima de oito caracteres ocorrerão no backend mesmo quando o Reflex também validar os campos.



### Token e duração da sessão



O Xano emitirá tokens com duração inicial de 24 horas. A duração limita a exposição de um token perdido sem exigir infraestrutura de revogação no MVP.



O token será enviado ao Xano somente no cabeçalho de autorização. Ele não será incluído em parâmetros de URL, corpo de resposta da sessão atual, logs de aplicação ou mensagens de erro.



Alternativa considerada: sessão sem expiração longa para reduzir logins repetidos. Foi rejeitada pelo risco de acesso prolongado em caso de comprometimento.



### Armazenamento do token no Reflex



O Reflex atuará como intermediário entre o navegador e o Xano. O token será mantido em cookie de sessão com `HttpOnly`, `Secure` em produção e `SameSite=Lax`. O código de interface não terá acesso direto ao valor do token.



Nas chamadas protegidas, o backend Reflex lerá a sessão e enviará o token ao Xano no cabeçalho de autorização. O logout removerá o cookie e limpará o estado autenticado.



Alternativa considerada: armazenar o token em `localStorage`. Foi rejeitada porque scripts executados na página poderiam acessá-lo e porque persistiria além da sessão do navegador.



### Recuperação da sessão e navegação



Ao iniciar a aplicação, o Reflex consultará a sessão atual quando existir um cookie de sessão. Enquanto a verificação estiver em andamento, a interface exibirá estado de carregamento e não enviará solicitações duplicadas.



Sessão válida carregará os dados públicos do usuário. Sessão ausente, inválida ou expirada limpará o estado local e direcionará o usuário ao login quando ele tentar acessar o planejamento.



### Separação de responsabilidades



A autenticação será implementada e testada separadamente da busca de trajetos. A busca dependerá apenas de uma identidade autenticada já resolvida; não conhecerá detalhes de senha, cadastro ou emissão do token.



O histórico de trajetos será tratado em outra mudança OpenSpec e poderá usar o identificador do usuário estabelecido por esta capacidade.



## Risks / Trade-offs



- **Cookie seguro no desenvolvimento local:** `Secure` não funciona em HTTP local.

&#x20; **Mitigação:** habilitar `Secure` por ambiente e mantê-lo obrigatório em produção.



- **Token válido até expirar após logout:** remover o cookie encerra a sessão no cliente, mas não revoga uma cópia do token.

&#x20; **Mitigação:** duração de 24 horas, transporte seguro e futura mudança de revogação se o risco justificar.



- **Corrida entre cadastros com o mesmo e-mail:** duas solicitações podem passar pela consulta inicial.

&#x20; **Mitigação:** índice único no banco e tratamento controlado do conflito.



- **Enumeração de contas por mensagens diferentes:** respostas distintas podem revelar e-mails existentes.

&#x20; **Mitigação:** mensagem genérica no login e ausência de campos sensíveis nas respostas.



- **Acoplamento do planejamento à disponibilidade da autenticação:** falha na resolução da sessão impede a busca.

&#x20; **Mitigação:** respostas explícitas de não autorizado e separação entre falha de autenticação e falha do serviço de trajetos.



## Migration Plan



1\. Fazer backup do workspace Xano com esquema e registros.

2\. Criar `usuarios` sem CRUD automático.

3\. Aplicar restrições e índice único de e-mail.

4\. Criar e testar os endpoints de autenticação.

5\. Integrar o estado de sessão no Reflex.

6\. Proteger os endpoints de planejamento somente após os testes de autenticação.

7\. Validar cadastro, login, sessão, logout e respostas de erro.

8\. Fazer novo backup e comparar com o estado anterior.



Rollback: desativar os endpoints e remover a exigência de autenticação do planejamento. A tabela e as contas serão preservadas; nenhum dado de usuário será excluído automaticamente.
