# Revisão e arquivamento de mudanças — 11/11/2026

Revisão dos artefatos, tarefas, especificações e evidências de entrega. O arquivamento é documental; não altera código em execução, malha ou Xano.

| Mudança | Resultado |
|---|---|
| `calibrar-tempos-e-margens` | Concluída, consolidada em `openspec/specs/calibracao-tempos` e arquivada com data de fechamento 2026-11-09. Corrigida referência antiga de 480 para 540 s e registrada preferência pelo Metrô, conforme publicação já auditada. |
| `considerar-espera-partidas` | Concluída, consolidada em `openspec/specs/espera-partidas` e arquivada com data de fechamento 2026-11-09. |
| `corrigir-qualidade-trajetos` | Concluída, consolidada em `openspec/specs/qualidade-trajetos` e arquivada com data de fechamento 2026-11-09. |
| `concorrencia-rotas` | Mantida ativa: falta completar a matriz remota de falhas. A disputa simultânea do mesmo usuário foi corrigida e validada posteriormente em 81/82; ver `xano/exclusividade-viagens-2026-11-11.md`. |
| `corrigir-pendencias-malha` | Mantida ativa: tempos/cadastro de retornos diretos do Expresso L10 e teste HTTP administrativo de gravações simultâneas. |
| `integrar-status-operacional-multifonte` | Mantida ativa: token/amostra Direto dos Trens, condições de uso público, fuso CPTM e revisão de 6/7/13 e serviços especiais. |
| `orientacoes-embarque-baldeacao` | Implementação concluída (26/26). Arquivamento dependente de `concorrencia-rotas`, conforme o próprio checklist: o delta de Escopo do MVP depende do texto daquela mudança. Não consolidar como concluída uma dependência ainda aberta. Cobertura parcial e dados fictícios de lado de desembarque continuam explicitados no histórico da mudança; não representam orientação certificada em campo. |
| `corrigir-integridade-trechos-legado` | Na pasta normal do usuário, contém apenas diretórios vazios, sem proposta, tarefas ou especificação. Não existe na árvore versionada examinada e nenhuma referência foi localizada no histórico do Git ou no acervo de trabalho pesquisado. Origem não identificada. Pasta vazia removida da cópia normal em 11/11, conforme autorização do usuário, sem excluir arquivos. |

Os requisitos de cada um dos três arquivos arquivados foram confrontados com as especificações consolidadas. O contexto OpenSpec foi atualizado para distinguir o contrato calibrado da penalidade fixa legada. A validação estrita passou nos 12 itens; arquivos de código, dados pessoais e caches não integram esta revisão.

Esta revisão e a atualização anterior do reteste compõem uma entrega exclusivamente documental. Após integrar e atualizar a cópia normal, as pastas passam a refletir os arquivamentos. A única remoção na cópia normal foi o esqueleto vazio `corrigir-integridade-trechos-legado`, autorizado pelo usuário.

Veja [resultado do teste e pendências funcionais](xano/reteste-main-status-concorrencia-2026-11-11.md).

## Data histórica conferida e preferência pelo Metrô

Os três diretórios usam `2026-11-09-` como data de fechamento documental: `git log` registra a última alteração anterior a hoje no commit `6f0a998`, em 09/11/2026 às 15:33:12 de Brasília. Não foi usada a data de modificação do disco, que muda em clones e cópias. A movimentação para arquivo e esta conferência ocorreram em 11/11; as datas das entregas funcionais anteriores permanecem explicitadas nos artefatos arquivados.

Na releitura do Xano em 11/11, busca e registro estavam idênticos aos exportados para a auditoria dos registros 67/68, sem rascunho pendente. A busca inicial sem ocupação minimiza tempo; a preferência pelo Metrô é aplicada à seleção de alternativa por concorrência, até 60 s acima da alternativa elegível original, com min(540 s, 45%) sobre o principal, uma troca extra no máximo e redução mínima de 40% da exposição. Não é prioridade absoluta nem presume a linha em que o usuário já está. O caminho pela Luz no teste foi coerente, pois República excedia tanto o limite percentual quanto o minuto de preferência.

O nome da pasta vazia sugere relação com correções de integridade, mas não há evidência suficiente para atribuir finalidade, autor ou processo de criação. Nenhuma hipótese foi registrada como fato.
