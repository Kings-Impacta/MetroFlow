# Revisão local — 02/10/2026

## Estado encontrado e preservação

Branch `feat/p4-recuperacao-senha-email`, baseada no commit `ba5a514` (correção da verificação de sessão antes da busca). A entrega de planejamento já avançou em relação ao teste inicial com cinco estações. Não foi feito reset de branch, descarte de alterações, commit, push ou alteração remota.

Antes das correções desta auditoria, o estado local foi copiado para `outputs/auditoria-2026-10-02` na área da conversa Codex, fora do repositório, com patch, arquivos não rastreados, estado do Git e referência do commit. A pasta alegada anteriormente, `outputs/revisao-2026-10-02`, não foi encontrada e não é tratada como evidência.

## Correções

- Autenticação, sessão, planejamento e ações por e-mail deixam de trocar à força a porta 3000 pela 8000. As requisições usam a origem da página, compatível com a execução documentada em porta única.
- Confirmação e redefinição capturam o token ao montar o formulário e removem o fragmento da URL. O valor fica apenas em uma propriedade JavaScript do elemento, sem atributo HTML, estado Reflex ou armazenamento persistente.
- Senha inválida, erro de rede ou resposta de validação permitem uma nova tentativa sem perder o token. Sucesso e rejeições definitivas 401/403/410 removem o valor. O formulário impede envios simultâneos e limpa os campos após sucesso.
- Redefinição bem-sucedida remove o cookie HttpOnly local. A invalidação de sessões de outros dispositivos continua dependendo do Xano.
- Redefinição bem-sucedida conduz ao login. Links rejeitados passam a apresentar a mensagem específica de link inválido ou expirado, sem serem confundidos com credenciais de login.
- Pedidos de recuperação e reenvio mantêm a mesma resposta pública para rejeições esperadas do Xano, inclusive respostas 400, 404, 409, 410 e 422.
- O workflow prepara Node.js para os novos testes de comportamento JavaScript.

## Evidências e limites

- Antes das correções: 72 testes e 10 subtestes passaram. Esses testes não detectavam os problemas de execução JavaScript.
- Depois das correções desta auditoria: 97 testes e 10 subtestes passaram, sem casos ignorados, com dois avisos de depreciação (TestClient/httpx e metadados de pacotes).
- A compilação seca da aplicação Reflex passou em 41/40 etapas exibidas pelo compilador. Houve somente o aviso conhecido de habilitação implícita do Radix Themes. `git diff --check` também passou.
- A validação estrita foi executada com `@fission-ai/openspec@1.7.0`, a mesma versão fixada no workflow: 6 itens passaram e nenhum falhou.
- Os novos testes executam os scripts com DOM e rede simulados em Node.js. Cobrem origem das chamadas em localhost, outra porta e HTTPS, tentativa após erro de rede/validação, envio duplicado e limpeza do token.
- O executável da venv não iniciou dentro do ambiente restrito da revisão (erro de permissão do trampoline uv). A suíte e a compilação usaram Python 3.12 do runtime disponível com as dependências da `.venv`; isso não demonstra defeito da venv no terminal do usuário.
- Na auditoria local inicial, nenhuma senha real, login remoto ou envio de e-mail foi utilizado. Em 04/10/2026, somente os endpoints de confirmação e redefinição foram corrigidos e publicados no Xano; o teste negativo utilizou um token fictício e não alterou usuários.

## Verificação remota em 04/10/2026

- O endpoint `email/confirmar` foi publicado com consulta bloqueante e com validação, consumo do token e confirmação do usuário dentro da mesma transação.
- O endpoint `senha/redefinir` recebeu a mesma proteção. A leitura do token, as precondições, o carregamento do usuário, o consumo do token, a troca da senha e o incremento de `versao_sessao` agora pertencem a uma única transação.
- Um token fictício de formato válido foi rejeitado com a mensagem segura de link inválido ou expirado. O Xano executou somente o caminho de validação, sem alterar dados.
- Após a publicação, o contador de rascunhos do Xano voltou a zero.
- O envio transacional foi repetido com uma nova chave da API configurada como variável secreta no Xano. A chamada retornou HTTP 201 e identificador de mensagem; o Brevo registrou os eventos `Enviado` e `Entregue` para `metroflow.projeto@gmail.com` e `raphael.matos@aluno.impacta.edu.br`.
- Os links mais recentes foram utilizados com sucesso. A tabela `usuarios` confirmou as duas contas com `ativo = true` e `email_verificado = true`.

## Auditoria remota em 06/10/2026

- Foram revisados no Xano os sete endpoints do grupo `auth`, as variáveis de ambiente usadas pelo Brevo e as tabelas `usuarios` e `tokens_autenticacao`.
- Cadastro, confirmação, reenvio e recuperação mantinham geração criptográfica, persistência exclusiva do hash, expiração, consumo único e transações atômicas. A sessão continuava com validade de 24 horas.
- Foi encontrada uma regressão em `auth/me`: a precondição verificava somente se `versao_sessao` existia no usuário e não comparava esse valor com a versão incluída no JWT.
- A precondição foi restaurada para exigir `auth.extras.versao_sessao == usuarios.versao_sessao`. O Xano aceitou o XanoScript e publicou o endpoint `auth/me` sem deixar rascunhos.
- Na auditoria de 06/10/2026 ainda faltava o teste ponta a ponta com uma sessão real anterior à redefinição. Ele foi concluído no fechamento de 08/10/2026 e registrado na mudança arquivada `2026-10-08-recuperacao-senha-verificacao-email`.
- A tabela `usuarios` parecia conter somente uma conta porque a visualização estava filtrada pelo e-mail do aluno. Após remover a pesquisa, foram exibidas três contas, incluindo `metroflow.projeto@gmail.com`, ativa e verificada.
- O cadastro de um e-mail já existente era traduzido pela API local como “Credenciais ou sessão inválidas”. A resposta foi separada do fluxo de login e agora orienta entrar ou recuperar a senha, mantendo uma mensagem segura para duplicidade.

## Roteiro manual registrado antes do fechamento

Esta lista preserva o roteiro definido durante a revisão. Os itens foram posteriormente concluídos ou cobertos pelas evidências e testes indicados no fechamento deste documento e na mudança OpenSpec arquivada.

1. Reiniciar o projeto em porta única e abrir localhost na porta indicada.
2. Entrar com uma conta existente e consultar origem/destino na malha atual; recarregar e confirmar restauração da sessão.
3. Sair e confirmar que a busca protegida solicita login.
4. Desativar o rastreamento dos links transacionais no Brevo ou comprovar que nenhum token fica retido nos históricos do provedor. A verificação posterior confirmou que o redirecionamento preserva o fragmento e que os registros examinados não expõem o token.
5. Em ambiente de teste autorizado, concluir recuperação de senha, expiração, uso único e invalidação de sessões anteriores.

O teste antigo de Vergueiro a Trianon-Masp em 360 segundos é histórico: o modelo atual inclui 600 segundos por mudança de linha e uma malha ampliada. Não deve ser usado como resultado esperado fixo.

## Referência consultada

A [documentação oficial de hospedagem Reflex](https://reflex.dev/docs/hosting/self-hosting/) descreve implantação em porta única e a configuração necessária para processos separados. A revisão mantém o modo de execução exigido pelo skill local e pela versão fixada do projeto; não atualiza o framework.


## Fechamento da validação em 06/10/2026

- A redefinição de senha da conta `metroflow.projeto@gmail.com` foi concluída e o login com a nova senha foi validado.
- O Xano mantém `versao_sessao` nos extras do JWT. As precondições publicadas em `auth/me`, `estacoes` e `trajetos/buscar` leem `$auth.extras.versao_sessao` como expressão e comparam esse valor à versão persistida do usuário.
- A consulta direta de `estacoes` no Xano passou e retornou a malha cadastrada, incluindo Palmeiras-Barra Funda e o Expresso Aeroporto.
- Na aplicação local em porta única, a sessão permaneceu ativa após recarregar a página. A porta da interface mudou de 3000 para 3001 quando a anterior estava ocupada, sem exigir alteração no código porque as chamadas usam a origem atual.
- Os trajetos Palmeiras-Barra Funda → Brigadeiro e Brigadeiro → Palmeiras-Barra Funda foram calculados com sucesso. O resultado utilizou as linhas 3-Vermelha, 4-Amarela e 2-Verde, com a integração Paulista–Consolação.
- A suíte completa terminou com 98 testes e 10 subtestes aprovados; houve um aviso de depreciação do `TestClient` sem falha funcional.
- `openspec.cmd validate --all --strict --no-interactive` aprovou os 6 itens existentes, sem falhas.
- O cenário complementar com uma sessão criada antes da redefinição foi concluído: o token antigo foi rejeitado, a aplicação redirecionou para o login e a tarefa correspondente foi encerrada antes do arquivamento da mudança.
