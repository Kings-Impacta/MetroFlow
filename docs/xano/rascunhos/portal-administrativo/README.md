# XanoScript da mudança `portal-administrativo`

Estado em 16/11/2026: **publicado** no workspace 149130, branch `v1` (produção), pelo Xano CLI. Os arquivos desta pasta são as cópias obtidas com `xano workspace pull` logo após o envio, já com o `guid` atribuído pelo Xano. Os testes automatizados leem as funções `|lambda:"…"` destes arquivos e as executam com Node.js; cada arquivo tem uma única função.

| Arquivo | Destino no workspace | Conteúdo |
|---|---|---|
| `administradores.xs` | `table/administradores.xs` | Tabela nova: um registro por administrador, com `usuario_id` único. |
| `estacoes_situacao_historico.xs` | `table/estacoes_situacao_historico.xs` | Tabela nova: estação, situação aplicada, administrador e momento de cada alteração. |
| `administracao_api_group.xs` | `api/administracao/administracao.xs` | Grupo novo `administracao`, canonical `metroflow-administracao`. |
| `admin_indicadores_get.xs` | `api/administracao/admin/indicadores_GET.xs` | `GET admin/indicadores`: indicadores agregados. |
| `admin_estacoes_get.xs` | `api/administracao/admin/estacoes_GET.xs` | `GET admin/estacoes`: todas as estações, ativas e inativas, com as linhas ativas que as atendem. |
| `admin_estacoes_situacao_post.xs` | `api/administracao/admin/estacoes/situacao_POST.xs` | `POST admin/estacoes/situacao`: ativa ou inativa uma estação. |
| `auth_me_get.xs` | `api/auth/auth/me_GET.xs` | Versão de `auth/me` que acrescenta `administrador`; partiu do arquivo publicado, baixado em 16/11/2026. |

Nenhum arquivo altera tabelas existentes, `trajetos/buscar` ou `viagens/confirmar`.

## Regras implementadas

- **Autorização:** os três endpoints repetem as verificações de sessão de `trajetos/buscar`: usuário ativo, e-mail verificado e `$auth.extras.versao_sessao`, com erro `unauthorized` (401). Depois consultam `administradores` pelo `$auth.id`; sem registro, respondem `accessdenied` (403). Como a consulta acontece a cada chamada, a revogação vale na próxima operação.
- **`auth/me`:** devolve `administrador: true` somente quando há registro em `administradores`. O campo apenas adapta a interface.
- **Alteração da situação:** `admin/estacoes/situacao` usa `db.patch` para mudar só `ativa`. A edição e o registro em `estacoes_situacao_historico` ficam na mesma `db.transaction`. Se a situação pedida já for a atual, responde com a vigente sem gravar. O administrador vem de `$auth.id`.
- **Indicadores** (`admin/indicadores`):
  - **Viagem em andamento:** não substituída, com `confirmada_em <= agora < fim_janela`, mantendo só a mais recente por usuário. Por isso `rotas_ativas` e `usuarios_em_viagem` coincidem.
  - **Uso recente e volume de 7 dias:** registros com `confirmada_em` nos últimos 7 × 24 h, incluindo substituídas. A consulta filtra por `fim_janela`, que tem índice e nunca é anterior a `confirmada_em`.
  - **Volume de hoje:** registros desde 00h em São Paulo, com deslocamento fixo de −3 h.
  - **Ranking:** a primeira origem e o último destino de `trechos` recebem um uso cada; ordem decrescente de usos e, em empate, alfabética (`pt-BR`); limite de cinco estações.
  - **Malha:** linhas ativas exigem linha e operador ativos; trechos ativos usam o mesmo filtro da busca e não descontam estações inativas nas pontas.
  - **Trechos lotados:** segue o critério publicado em `trajetos/buscar`, conferido no `pull` de 16/11/2026. O intervalo de passagem vem de `inicio_previsto_em` ou, em registros antigos, do cursor somado à espera e à baldeação anteriores. A ocupação é o número de usuários distintos cujo intervalo contém o instante da apuração. O trecho fica lotado com ocupação maior ou igual ao mínimo e ocupação × 100 maior ou igual ao percentual × total de viagens ativas. Ninguém é excluído, porque não há quem esteja buscando. Sem configuração válida, `trechos_lotados`, `minimo_usuarios` e `percentual_lotacao` são `null`.
  - **Privacidade:** a resposta não contém `usuario_id`, e-mails nem registros de viagem.

A função de lotação está duplicada em relação a `trajetos/buscar`, cuja versão publicada não está versionada neste repositório. Uma mudança futura no critério precisa atualizar as duas.

## Como conceder ou revogar o papel

No painel do Xano, abra a tabela `administradores` e insira um registro com o `id` do usuário em `usuario_id`. Para revogar, remova o registro. O usuário passa a ver o link "Administração" depois de restaurar a sessão, por exemplo ao recarregar a página. Nenhum endpoint da aplicação grava nessa tabela.

## Publicação de 16/11/2026

1. O workspace foi baixado logo antes do envio e comparado com a cópia usada para preparar os rascunhos: não havia alteração remota no intervalo, inclusive em `auth/me`.
2. A simulação (`--dry-run`), em comando separado, listou somente as operações aprovadas pela equipe: criação de `administradores`, `estacoes_situacao_historico`, do grupo `administracao` e de `admin/estacoes/situacao`, `admin/estacoes` e `admin/indicadores`, além da atualização de `auth/me`.
3. O envio foi feito com `xano workspace push --force`. O CLI informou 32 documentos, os 26 existentes mais os 6 novos.
4. Uma nova cópia baixada após o envio difere da anterior somente nesses sete itens. Em relação aos rascunhos, há apenas formatação aplicada pelo Xano e o padrão `swagger = {active: false}` no grupo. As funções de cálculo publicadas são idênticas às testadas.
5. Chamadas sem token responderam `401` em `admin/indicadores`, `admin/estacoes`, `admin/estacoes/situacao` e `auth/me`. Um caminho inexistente no grupo respondeu `404`, o que confirma o canonical `metroflow-administracao`.

A tabela `administradores` foi criada vazia: ninguém tem acesso ao painel até a concessão descrita acima.

**Reversão:** os itens novos são aditivos e podem ficar sem uso. Se `auth/me` apresentar falha, publique de volta a versão anterior, que é este mesmo arquivo sem a consulta a `administradores`, sem `$eh_administrador` e com `response = {id: $usuarios.id, email: $usuarios.email}`. Use sempre `pull`, `--dry-run` e `push`; nunca `PUT` da Metadata API com `xanoscript`, que em 26/10/2026 apagou o esquema de `trechos`.

## Validação pendente no Xano

Adiada no arquivamento de 16/11/2026, por decisão do usuário; não foi executada. A primeira verificação deve ser um login real seguido da restauração da sessão, porque todas as páginas autenticadas dependem de `auth/me`. Depois, repetir com sessões reais, sem registrar tokens:

| Caso | Resultado esperado |
|---|---|
| Chamada sem token | 401 nos três endpoints |
| Usuário sem concessão | 403, sem dados |
| Administrador | 200 com indicadores e estações |
| Concessão removida com a sessão aberta | 403 na chamada seguinte |
| Alteração de situação | estação alterada e um registro no histórico |
| Mesma situação repetida | resposta com a situação vigente e nenhum registro novo |
| Estação inexistente | 404, sem alteração |
| `auth/me` | `administrador` verdadeiro somente para quem tem concessão |

Use uma estação de baixo impacto, reative-a ao final e confira que nenhuma estação ficou inativa por causa do teste.

## Limites da validação local

Os testes locais executam as funções de cálculo com massas controladas e cobrem o backend Python e a interface com transporte simulado. Eles **não** cobrem:

- a execução real do XanoScript, incluindo a sintaxe aceita pelo Xano, `db.patch`, `conditional` e o uso de índices;
- a atomicidade real de `db.transaction` entre a edição da estação e o registro do histórico;
- alterações simultâneas feitas por dois administradores, que seguem a regra "a última vence" e geram um registro cada;
- o comportamento sob o limite de requisições do plano gratuito;
- a renderização visual do painel no navegador.
