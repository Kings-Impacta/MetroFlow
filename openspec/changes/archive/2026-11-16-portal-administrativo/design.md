## Context

A motivação e o alcance estão em `proposal.md`, e os comportamentos, nas especificações desta mudança. Este documento registra as decisões técnicas.

Estado observado no repositório em 09/11/2026:

- Não existe papel de administrador. Em `MetroFlow/auth`, o usuário público contém somente `id` e `email`, e o design arquivado de autenticação excluiu perfis e permissões.
- O campo `estacoes.ativa` já existe e é respeitado. `GET estacoes` devolve só as ativas. `trajetos/buscar` rejeita origem ou destino inativos e retira as estações inativas do grafo, então uma estação inativa interrompe a linha naquele ponto.
- O token fica em cookie HttpOnly. A interface Reflex chama os endpoints locais com `fetch` por meio de `rx.call_script`, e o estado Reflex não guarda credenciais.
- Os clientes Python tratam 401 e 403 da mesma forma, como sessão inválida.
- `viagens_confirmadas` guarda `usuario_id`, `confirmada_em`, `fim_janela`, `substituida` e `trechos` (JSON), sem prazo de exclusão, com índice em `fim_janela`. Desde a calibração, cada trecho gravado pode trazer `inicio_previsto_em`, `espera_estimada_segundos` e `baldeacao_antes_segundos`; registros antigos não têm esses campos.
- O Xano está no plano gratuito, com um único branch (`v1`) que é produção. Já houve respostas `429` em `auth/me`.

**Conferência do Xano em 16/11/2026:** o `xano workspace pull` confirmou `usuarios` com `id`, `email`, `senha`, `ativo` (padrão `true`), `email_verificado` (padrão `true`) e `versao_sessao`. Confirmou também `auth/me`, com as mesmas verificações de sessão, resposta `{id, email}` e `history = false`. As funções publicadas de `trajetos/buscar` e `viagens/confirmar` estão mais novas que os rascunhos em `docs/xano/rascunhos/concorrencia-rotas/`, que são de 26/10.

## Goals / Non-Goals

**Goals:**

- Manter dados, autorização e apuração dos indicadores no Xano, com o backend Python validando e normalizando o contrato.
- Publicar no Xano somente alterações aditivas, sem tocar no esquema de `usuarios` e da malha.
- Consumir o mínimo de requisições do Xano por interação.

**Non-Goals:**

- Alterar `trajetos/buscar`, `viagens/confirmar` ou o critério de lotação.
- Extrair o cálculo de lotação para uma função compartilhada do Xano; isso exigiria republicar `trajetos/buscar` durante a validação de `concorrencia-rotas`.

## Decisions

### 1. Administradores em tabela própria

A tabela `administradores` guarda `usuario_id` (único) e `created_at`. A concessão e a revogação são feitas no painel do Xano, inserindo ou removendo a linha.

- *Campo `perfil` em `usuarios`:* mais direto, mas exige republicar o esquema da tabela de autenticação em produção. Depois do incidente de `trechos`, a opção aditiva é preferível, pois uma falha não afeta o login.
- *Lista de e-mails em variável de ambiente no Python:* descartada. A autorização precisa existir no Xano, onde a escrita acontece, porque o token de um usuário comum também é aceito pela API do Xano.

### 2. Autorização em cada endpoint do Xano

Cada endpoint administrativo repete as verificações de sessão de `trajetos/buscar` (usuário ativo, e-mail verificado e `$auth.extras.versao_sessao`), com erro `unauthorized`, e depois verifica a existência da linha em `administradores`, com erro `accessdenied`. A consulta ao banco a cada chamada faz a revogação valer imediatamente, sem depender da validade do token.

O backend Python não chama `auth/me` antes dos endpoints administrativos, ao contrário do planejamento: o Xano já valida tudo no próprio endpoint, e isso economiza uma requisição por operação. Um novo `XanoAdminClient` distingue 401 de 403, permitindo direcionar ao login somente quando a sessão acabou.

### 3. Contrato de integração

Novo grupo Xano `administracao`, com canonical `metroflow-administracao`, e variável opcional `XANO_ADMIN_API_BASE_URL`.

| Reflex/navegador → Python | Python → Xano | Retorno |
| --- | --- | --- |
| `GET /api/admin/indicators` | `GET admin/indicadores` | Indicadores e momento da apuração |
| `GET /api/admin/stations` | `GET admin/estacoes` | Todas as estações, com situação e linhas |
| `POST /api/admin/stations/{station_id}/status` com `{"active": bool}` | `POST admin/estacoes/situacao` com `{estacao_id, ativa}` | `{id, ativa}` vigentes |

Indicadores e estações ficam em endpoints separados para que uma falha na apuração não impeça o gerenciamento das estações. Abrir o painel custa duas chamadas ao Xano. A alteração usa `POST` porque o cookie `SameSite=Lax` não acompanha `POST` entre sites. As respostas usam `Cache-Control: no-store` e os modelos de entrada usam `extra="forbid"`.

Mapeamento de erros: 401 → sessão expirada, com redirecionamento a `/login`; 403 → acesso restrito, mantendo a sessão; 400/404/422 → mensagem de verificação; indisponibilidade → 503; contrato inválido → 502.

### 4. Definição dos indicadores no Xano

A apuração ocorre em uma função `lambda` do XanoScript, testável com o `tests/unit/planning/xano_lambda.py`.

| Indicador | Regra |
| --- | --- |
| `rotas_ativas` | Viagens com `substituida == false` e `confirmada_em <= agora < fim_janela`, mantendo só a mais recente por usuário |
| `usuarios_em_viagem` | Usuários distintos do conjunto acima |
| `usuarios_uso_recente` | `usuario_id` distintos com `confirmada_em >= agora − 7×24 h` |
| `contas_habilitadas` | `usuarios` com `ativo` e `email_verificado` |
| `estacoes_ativas` / `estacoes_inativas` | Contagem por `estacoes.ativa` |
| `linhas_ativas` | `linhas.ativa` e `operadores.ativo` |
| `trechos_ativos` | `trechos.ativo`, `linhas.ativa` e `operadores.ativo`, o mesmo filtro da busca |
| `viagens_hoje` | Registros com `confirmada_em` desde 00:00 em São Paulo, incluindo substituídas |
| `viagens_7_dias` | Registros com `confirmada_em >= agora − 7×24 h`, incluindo substituídas |
| `ranking_estacoes` | Primeira origem e último destino de `trechos`, últimos 7 dias, cinco maiores |
| `trechos_lotados` | Pares (trecho, sentido) que atendem ao critério; `null` com configuração ausente ou inválida |

A consulta do período usa `fim_janela >= agora − 7 dias` para aproveitar o índice existente, já que `fim_janela` nunca é anterior a `confirmada_em`. A função então confere `confirmada_em`.

O início do dia usa o deslocamento fixo de −3 h, pois o Brasil não adota horário de verão desde 2019 e a regra fica testável sem depender de fuso no ambiente do Xano.

`trechos_lotados` replica o critério publicado em `trajetos/buscar` e conferido no `pull` de 16/11:

- **Viagens consideradas:** ativas, deduplicadas por usuário, sem excluir ninguém, já que não há quem esteja buscando.
- **Intervalo de passagem:** começa em `inicio_previsto_em` ou, em registros antigos, no cursor somado à espera e à baldeação anteriores; termina somando `tempo_estimado`.
- **Ocupação:** quantidade de usuários distintos cujo intervalo contém o instante da apuração, por trecho e sentido.
- **Lotação:** ocupação maior ou igual ao mínimo e percentual maior ou igual ao limite, comparado ao total de viagens ativas.

A busca compara intervalos com a passagem prevista do candidato; o painel, sem candidato, usa o instante da apuração. A resposta inclui `minimo_usuarios` e `percentual_lotacao` para que o número seja lido com o critério ao lado.

As contagens agregadas são compatíveis com `concorrencia-rotas`, que proíbe devolver registros de viagens e apresentar lotação ao passageiro.

### 5. Alteração da situação e auditoria

`POST admin/estacoes/situacao` lê a estação e, se a situação mudar, executa em `db.transaction` a edição somente de `ativa` e a inclusão em `estacoes_situacao_historico` (`estacao_id`, `ativa`, `usuario_id`, `alterada_em`). Se a situação já for a pedida, responde com o valor atual, sem gravar. O `usuario_id` vem de `$auth.id`.

A auditoria não estava no pedido original. Foi incluída porque a ação afeta todos os passageiros e o custo é uma tabela aditiva e uma gravação.

### 6. Interface Reflex

Novo `AdminState` em `MetroFlow/admin/presentation/`, com as chamadas via `rx.call_script` usando o padrão de `request_script` e um identificador de requisição para descartar respostas antigas, como em `PlanningState`.

A confirmação de inativação usa `rx.alert_dialog`, com o nome da estação e as linhas atendidas. A pesquisa e o filtro ocorrem no estado, sem chamadas adicionais, pois são cerca de 182 estações; `normalize_search` é reutilizado.

A interface reage a três estados de autorização: carregando (sem dados nem controles), restrito (403) e autorizado.

### 7. Indicação de administrador na sessão

`auth/me` passa a devolver `administrador`, calculado pela existência da linha em `administradores`. Isso evita uma chamada extra a cada troca de página. No Python, somente o valor booleano `true` é aceito, e qualquer outro resultado equivale a `false`. Assim, o backend pode ser implantado antes do Xano. `/api/auth/login` permanece como está; o valor chega à interface pelo `restore_session` executado depois do redirecionamento.

A indicação controla apenas a exibição do link. A autorização real é a da decisão 2.

### 8. Atualização sem consulta periódica

Os indicadores são apurados ao abrir, sob demanda e após alterações. Uma consulta periódica consumiria o limite do plano gratuito, onde já ocorreram erros `429`. Se a equipe quiser atualização automática, ela pode ser adicionada depois sem mudar o contrato.

### 9. Requisito `Escopo do MVP`

`concorrencia-rotas` e `orientacoes-embarque-baldeacao` foram arquivadas em 12/11/2026, e o requisito consolidado ainda contém a frase que proíbe a área administrativa. O delta desta mudança parte desse texto consolidado e troca somente essa frase.

## Risks / Trade-offs

- [Inativar uma estação de baldeação corta várias linhas e faz buscas não encontrarem caminho] → A confirmação lista as linhas e avisa sobre a interrupção; a reativação leva um clique; a auditoria registra o responsável.
- [O cálculo de lotação fica duplicado e pode divergir de `trajetos/buscar`, cuja versão publicada não está versionada no repositório] → Os testes cobrem os cenários da spec consolidada de `concorrencia-rotas`, com cronograma calibrado e registros antigos; o README do painel registra a versão conferida. Uma alteração futura do critério precisa atualizar as duas funções.
- [`trechos_lotados` engana enquanto a configuração usar os valores de teste, 1 usuário e 1%] → O critério vigente aparece ao lado do número; a definição dos valores reais já está pendente em `concorrencia-rotas`.
- [Rotas ativas e usuários em viagem agora sempre terão o mesmo valor, pois cada usuário tem no máximo uma viagem ativa] → Os dois indicadores foram pedidos e são mantidos; a repetição é uma consequência esperada, não um defeito.
- [Viagens registradas medem buscas bem-sucedidas, não viagens realizadas] → A interface usa o rótulo "registradas".
- [`trechos_ativos` não diminui ao inativar uma estação] → Regra explícita na especificação; a quantidade de estações inativas aparece junto.
- [`viagens_confirmadas` cresce sem limite] → A apuração filtra pelo índice de `fim_janela` e lê só os últimos 7 dias.
- [`xano workspace push` vai direto para produção em um workspace compartilhado] → Fluxo de publicação abaixo.

## Migration Plan

1. Baixar o workspace atual com `xano workspace pull` e conferir `usuarios` e `auth/me`.
2. Simular com `xano workspace push --dry-run`, em comando separado, conferir que lista somente as operações esperadas e obter aprovação antes de enviar. Não usar `PUT` da Metadata API com `xanoscript`.
3. Publicar as tabelas, o grupo e os endpoints; depois, a alteração de `auth/me`.
4. Baixar novamente, conferir o resultado e inserir a linha do primeiro administrador.
5. Implantar o backend e a interface e validar com sessões reais.

**Reversão:** os novos itens do Xano são aditivos e podem ficar sem uso; o campo `administrador` é ignorado por versões anteriores do Python; o link e a rota saem com a reversão do código; estações inativadas durante os testes são reativadas pelo painel, ou diretamente no Xano se o painel estiver fora do ar.

## Open Questions

- Quem serão os primeiros administradores? A resposta define apenas as linhas inseridas em `administradores`.
