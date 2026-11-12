## Decisions

Usar `db.get usuarios` com `lock = true` dentro de `db.transaction`. O usuário existe mesmo sem viagens, evitando a falha de bloquear somente a consulta potencialmente vazia de viagens. O bloqueio termina com commit ou rollback e é específico ao registro, sem bloqueio global e sem modificar campos do usuário.

Adquirir o bloqueio depois da validação e cálculo, mantendo curta a seção crítica. Dentro dela, reler estado/verificação/versão de sessão, atualizar o instante da confirmação e rejeitar referência com mais de 30 segundos após a espera. Deslocamentos, padrões, cronologia de embarque e margem pública não são alterados.

A segunda requisição deve esperar e consultar as viagens depois do commit da primeira. Ambas podem responder sucesso, mas somente a última permanece ativa. Qualquer falha deve reverter substituições e inserção. A deduplicação defensiva existente na busca continua, mas não substitui a garantia do registro.

Backup: exportação integral sem segredos/env e snapshots das tabelas de referência/viagens, fora do Git. Prévia limitada ao endpoint; releitura e comparação após publicação. Rollback: restaurar apenas o endpoint do backup se a publicação divergir ou houver regressão; dados de teste não serão apagados.

Fonte oficial do bloqueio: https://docs.xano.com/the-function-stack/functions/database-requests/get-record . A validação sintática e a prévia não comprovam execução nem concorrência; o reteste HTTP deve permanecer pendente até sua conclusão.
