# Auditoria complementar de integridade dos trechos — 08/10/2026

Revisão do workspace `149130`, branch `v1`, data source `live`, iniciada em 08/10/2026 e concluída em 11/10/2026. A auditoria foi executada sem backfill; nenhum registro de `trechos` foi criado, alterado ou removido.

## Estado encontrado

- A tabela `trechos` (`882609`) contém 207 registros e passou a exibir o campo `chave_integridade`.
- O grupo `planejamento` (`431173`) contém quatro endpoints. Além das consultas `estacoes` e `trajetos/buscar`, existem `POST /trechos` (`4059961`) e `POST /trechos/auditoria` (`4059960`).
- Os dois novos endpoints exigem autenticação e repetem as verificações de usuário ativo, e-mail confirmado e versão da sessão. A comparação da versão foi normalizada para inteiro e publicada em 11/10/2026.
- O endpoint `trechos` recebe nove entradas e declara validações para extremos distintos, existência das estações e da linha e serviço opcional. O fluxo também calcula uma chave canônica para trechos não direcionados, preserva a orientação dos direcionados, procura conflito e separa criação de atualização.
- O endpoint `trechos/auditoria` lê os registros, calcula um relatório e só executa o backfill quando `executar_backfill` é verdadeiro.

## Evidências obtidas

- A exportação dos 207 registros foi solicitada antes dos testes; o link do arquivo é entregue pelo Xano por e-mail e possui validade limitada.
- A definição XanoScript da tabela confirmou `chave_integridade` como texto interno e índice `btree|unique`. Os 207 registros já estavam preenchidos, portanto não foi necessário executar backfill.
- A auditoria com `executar_backfill=false` analisou 207 registros em 110 ms e retornou `seguro_para_backfill=true`, com listas vazias para extremos iguais, duplicatas diretas, duplicatas inversas e colisões de chave. O retorno confirmou `registros_atualizados=0`.
- A definição XanoScript do endpoint confirmou referências válidas a `servicos` e `trechos`. O texto `Deleted table` era um rótulo desatualizado do diagrama visual, não uma referência ausente no código executável.
- Há 10 trechos associados a serviços. Alguns são direcionados e formam pares opostos legítimos; por isso a chave preserva a orientação quando `direcionado=true` e usa normalização canônica nos demais casos.
- As correções dos endpoints `POST /trechos` e `POST /trechos/auditoria` foram publicadas juntas em 11/10/2026. O painel confirmou zero rascunhos após a publicação.
- Em 14/10/2026, após iniciar o Reflex com `--single-port`, uma sessão real restaurou o acesso autenticado, carregou as estações e calculou Vergueiro → Trianon-Masp em 960 segundos, com quatro estações e uma baldeação. Essa evidência confirma o caminho de leitura usado pela aplicação; ela não substitui os testes pendentes do endpoint administrativo de escrita.
- Em 14/10/2026, uma sessão real também foi usada no `POST /trechos` para oito tentativas inválidas. Extremos iguais, referências inexistentes de origem, destino e linha, tempo zero, tempo negativo e duplicatas direta e inversa foram todos rejeitados com `HTTP 400`. Nenhuma tentativa recebeu resposta de sucesso. O token permaneceu apenas na memória do processo local e não foi registrado.
- Em 19/10/2026, a falha `Unable to locate auth: versao_sessao` foi rastreada até a leitura incorreta do extra do token. Os endpoints `POST /trechos` e `POST /trechos/auditoria` passaram a consultar `$auth.extras.versao_sessao`, em conformidade com o token emitido por `auth/login` e com os demais endpoints autenticados. As duas correções foram publicadas no branch `v1` antes da repetição do teste de concorrência com um token novo.
- Após a correção de sessão, duas requisições simultâneas tentaram criar a chave canônica `B:1:3:1:0`. Exatamente uma foi aceita (`HTTP 200`, registro temporário `id=211`) e a concorrente foi rejeitada pelo índice único com `Duplicate record detected` (`HTTP 500`). Isso comprova que a proteção no banco impede a segunda persistência mesmo quando ambas as requisições passam juntas pela consulta prévia. O registro temporário foi removido após confirmação, e a tabela voltou de 208 para 207 registros.
- A validação `openspec.cmd validate --all --strict --no-interactive` foi executada em 19/10/2026 e aprovou os cinco itens encontrados, sem falhas.
- Uma segunda execução controlada omitiu `ativo` e enviou `tempo_estimado=121` com referências válidas. Uma requisição foi aceita (`HTTP 200`, registro temporário `id=213`) e retornou `ativo=true`; a concorrente foi novamente rejeitada pelo índice único. O registro `213` foi removido após confirmação e a tabela retornou de 208 para 207 registros.

## Limites restantes

Também continuam disponíveis no painel operações administrativas diretas, como adicionar, gerar e importar registros. Elas não passam pelo endpoint. Portanto, o endpoint pode ser o único caminho de escrita da aplicação, mas a integridade ainda depende de restringir as gravações operacionais ao fluxo validado e de não usar edição ou importação direta sem a mesma validação.

O executor interno do Xano não reproduz de forma confiável os extras de autenticação emitidos pelo login da aplicação. A auditoria somente leitura permite execução interna sem versão de sessão, mas qualquer chamada com `executar_backfill=true` continua exigindo que a versão do token corresponda à versão armazenada. O endpoint de gravação também mantém essa exigência. Por isso, os testes de gravação devem usar uma sessão real da aplicação ou registros temporários controlados.

Em 11/10/2026, uma execução do `POST /trechos` pelo painel, selecionando o usuário confirmado `metroflow.projeto@gmail.com`, foi rejeitada com `Unable to locate auth: versao_sessao` após quatro instruções e sem alcançar as validações do trecho. Em 19/10/2026, foi confirmado que essa falha também atingia tokens reais porque os dois endpoints novos consultavam `$auth.versao_sessao`, enquanto o login grava o valor em `$auth.extras.versao_sessao`. O caminho foi corrigido sem remover a proteção de sessão.

## Matriz de validação

| Caso | Resultado esperado |
| --- | --- |
| Estações e linha existentes | gravação aceita |
| Referência inexistente | rejeição sem persistência |
| `tempo_estimado` maior que zero | gravação aceita |
| `tempo_estimado` zero ou negativo | rejeição sem persistência |
| `ativo` omitido | valor padrão `true` |
| Origem igual ao destino | rejeição sem persistência |
| Duplicata direta na mesma linha | rejeição sem segundo registro |
| Duplicata inversa não direcionada | rejeição pela mesma chave canônica |
| Mesmo par em outra linha | gravação aceita |
| Duas gravações concorrentes da mesma chave | somente uma persistência |
| Atualização do próprio registro | aceita sem conflito consigo mesmo |
| Atualização para chave de outro registro | rejeição sem alterar o original |

## Sequência controlada restante

1. Confirmar o recebimento e armazenamento do CSV exportado.
2. Executar a matriz com uma sessão real e registros temporários identificados, removendo-os ao final.
3. Validar que os clientes e integrantes do time usam exclusivamente `POST /trechos` para gravações operacionais.

Para a matriz de escrita, deve ser usado um token recém-emitido pelo endpoint real `auth/login`, mantido somente na sessão de teste e nunca registrado em arquivo, saída de CI, captura de tela ou commit. O total de registros deve ser conferido antes e depois, e os registros temporários devem ser identificados e removidos ao final.

As regras foram publicadas e a base atual passou na auditoria sem alterações. A matriz de referências, tempo, padrão de `ativo`, extremos e duplicatas foi executada por HTTP externo. A proteção concorrente também foi comprovada com uma criação e uma rejeição para a mesma chave, seguida da remoção dos registros temporários. Permanecem como recomendações complementares a atualização controlada e a confirmação de que os clientes não contornam o endpoint por operações administrativas; esses limites estão documentados e não fazem parte das tarefas restantes desta mudança.
