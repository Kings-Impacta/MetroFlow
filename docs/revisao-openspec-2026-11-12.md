# Revisão OpenSpec — 12/11/2026

Base: main após PR #44, commit `778a9fd505e45a2d61ba4eeeabf9246b29b93563`. Esta revisão altera somente documentação e organização do OpenSpec; não executa chamadas de escrita no Xano nem altera código, malha ou parâmetros.

## Arquivamento concluído

`corrigir-exclusividade-viagens` foi arquivada em `openspec/changes/archive/2026-11-11-corrigir-exclusividade-viagens/`. A data corresponde à conclusão funcional e ao reteste de 11/11; a revisão/movimentação ocorreu em 12/11. As nove tarefas estavam concluídas, os quatro artefatos completos e os três requisitos foram consolidados e comparados integralmente em `openspec/specs/exclusividade-viagens/spec.md`.

A correção foi publicada no Xano após backup e integrada documentalmente pelo PR #43. Na disputa HTTP autenticada 81/82, ambas as confirmações retornaram 200 e apenas a última permaneceu ativa após o commit. Isso não prova toda combinação de carga ou falha, conforme limites da evidência.

## Mudanças mantidas ativas

| Mudança | Motivo |
|---|---|
| `concorrencia-rotas` | O checklist geral ainda contém a integração HTTP de configuração realmente ausente, se exigida. Expiração real de token de teste, entradas inválidas, ausência de alternativa proporcional e exclusividade já têm evidências; não repetir essas tarefas como pendentes. |
| `orientacoes-embarque-baldeacao` | Implementação 26/26 concluída, mas o checklist determina arquivar primeiro `concorrencia-rotas`; o delta de Escopo do MVP depende dela. Preservar as limitações da coleta e os lados fictícios para demonstração. |
| `corrigir-pendencias-malha` | Faltam certificação/inclusão de retornos diretos do Expresso L10 e reteste administrativo HTTP de gravações simultâneas de trechos. |
| `integrar-status-operacional-multifonte` | Faltam token e amostra Direto dos Trens, condições de ativação pública, fuso CPTM e revisão de cobertura 6/7/13 e serviços especiais. |

## Configuração ausente: alcance da validação

A configuração nula e omitida foi validada em uma cópia exata do cálculo publicado, executada isoladamente no Xano com dados/relógio controlados e controle positivo de ocupação. O principal foi preservado nos casos sem configuração. **Não foi executada chamada HTTP ao endpoint público com o registro de configuração realmente ausente no banco.** O registro real 1/1% não foi removido nem alterado. As funções temporárias foram removidas e as nove tabelas e 26 documentos de produção permaneceram idênticos.

Não marcar a integração completa como realizada e não arquivar a mudança geral apenas pelo resultado isolado. Se a equipe dispensar esse ensaio de integração, registrar a decisão e seu motivo antes de encerrar a mudança. Ver [método e evidências](xano/sessao-expirada-configuracao-ausente-2026-11-11.md).

## Entrega

O arquivamento e esta revisão permanecem na cópia de trabalho isolada até a integração documental. A main e a pasta normal não são alteradas automaticamente por esta revisão. Validação estrita do OpenSpec e conferência de alterações documentais devem passar antes da entrega.
