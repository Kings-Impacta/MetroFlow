# Revisão OpenSpec — 12/11/2026

Base: main após PR #44, commit `778a9fd505e45a2d61ba4eeeabf9246b29b93563`. Esta revisão altera somente documentação e organização do OpenSpec; não executa chamadas de escrita no Xano nem altera código, malha ou parâmetros.

## Arquivamento concluído

`corrigir-exclusividade-viagens` foi arquivada em `openspec/changes/archive/2026-11-11-corrigir-exclusividade-viagens/`. A data corresponde à conclusão funcional e ao reteste de 11/11; a revisão/movimentação ocorreu em 12/11. As nove tarefas estavam concluídas, os quatro artefatos completos e os três requisitos foram consolidados e comparados integralmente em `openspec/specs/exclusividade-viagens/spec.md`.

A correção foi publicada no Xano após backup e integrada documentalmente pelo PR #43. Na disputa HTTP autenticada 81/82, ambas as confirmações retornaram 200 e apenas a última permaneceu ativa após o commit. Isso não prova toda combinação de carga ou falha, conforme limites da evidência.

## Estado histórico antes do teste HTTP local

| Mudança | Motivo |
|---|---|
| `concorrencia-rotas` | O checklist geral ainda contém a integração HTTP de configuração realmente ausente, se exigida. Expiração real de token de teste, entradas inválidas, ausência de alternativa proporcional e exclusividade já têm evidências; não repetir essas tarefas como pendentes. |
| `orientacoes-embarque-baldeacao` | Implementação 26/26 concluída, mas o checklist determina arquivar primeiro `concorrencia-rotas`; o delta de Escopo do MVP depende dela. Preservar as limitações da coleta e os lados fictícios para demonstração. |
| `corrigir-pendencias-malha` | Faltam certificação/inclusão de retornos diretos do Expresso L10 e reteste administrativo HTTP de gravações simultâneas de trechos. |
| `integrar-status-operacional-multifonte` | Faltam token e amostra Direto dos Trens, condições de ativação pública, fuso CPTM e revisão de cobertura 6/7/13 e serviços especiais. |

## Configuração ausente: alcance da validação

A configuração nula e omitida foi validada em uma cópia exata do cálculo publicado, executada isoladamente no Xano com dados/relógio controlados e controle positivo de ocupação. O principal foi preservado nos casos sem configuração. **Não foi executada chamada HTTP ao endpoint público com o registro de configuração realmente ausente no banco.** O registro real 1/1% não foi removido nem alterado. As funções temporárias foram removidas e as nove tabelas e 26 documentos de produção permaneceram idênticos.

Na revisão inicial, não era possível marcar a integração completa nem arquivar a mudança geral apenas pelo resultado isolado do motor. Se a equipe dispensar esse ensaio de integração, registrar a decisão e seu motivo antes de encerrar a mudança. Ver [método e evidências](xano/sessao-expirada-configuracao-ausente-2026-11-11.md).

## Entrega

O arquivamento e esta revisão permanecem na cópia de trabalho isolada até a integração documental. A main e a pasta normal não são alteradas automaticamente por esta revisão. Validação estrita do OpenSpec e conferência de alterações documentais devem passar antes da entrega.

## Atualização posterior: pendência validada localmente

Após esta revisão, o usuário solicitou HTTP local isolado para concluir a configuração ausente. Oito casos passaram sem chamadas remotas, com cliente real e registro removido no SQLite temporário. A integração HTTP nativa do Xano permanece não executada, mas deixou de ser bloqueio no escopo local aceito; não confundir os ambientes. Ver [execução e evidência](xano/http-local-configuracao-ausente-2026-11-12.md). A mudança de concorrência ainda não foi arquivada nesta etapa.

## Encerramento após PR #46 e revisão dos dois arquivamentos

Base desta etapa: main `ee3a48e9bcab66f2248b06defdc96bd2d30e645c`. As mudanças `concorrencia-rotas` (28/28) e `orientacoes-embarque-baldeacao` (26/26) foram revisadas e arquivadas localmente em 12/11/2026, nesta ordem, respeitando a dependência do delta de busca.

- Concorrência: `openspec/changes/archive/2026-11-12-concorrencia-rotas/`; conclusão do escopo aceito em 12/11, após oito casos HTTP locais.
- Orientações: `openspec/changes/archive/2026-10-26-orientacoes-embarque-baldeacao/`; a data preserva a última conclusão/validação funcional registrada em 26/10. A movimentação ocorreu em 12/11, após liberar a dependência documental.
- Especificações consolidadas: `concorrencia-rotas`, `orientacoes-viagem` e os requisitos afetados de `busca-trajetos`. Os deltas antigos foram corrigidos documentalmente para não reintroduzir alternativa sem limite, penalidade fixa universal ou cronograma sem esperas/baldeações. Foram preservados os limites e a preferência pelo Metrô já publicados; nenhuma regra de execução foi alterada.

**Configuração ausente: HTTP local isolado, não HTTP no runtime nativo do Xano.** O teste nativo permanece não executado e não é apresentado como aprovado. O escopo local foi aceito pelo usuário para encerrar esta pendência; ver [método e oito casos](xano/http-local-configuracao-ausente-2026-11-12.md).

O arquivamento de orientações conclui a implementação, não certifica os dados de demonstração. Permanecem cobertura parcial, associação por nomes e observações/lados sujeitos à coleta e confirmação em campo, conforme o registro histórico do piloto. Não foram alterados esses dados nesta revisão.

Permanecem ativas somente `corrigir-pendencias-malha` (17/19) e `integrar-status-operacional-multifonte` (15/19), pelos motivos registrados na tabela histórica acima. Não foram arquivadas tarefas incompletas. Nenhuma chamada de escrita no Xano, alteração de malha, parâmetros, código ou funcionamento do aplicativo foi realizada. Esta etapa permanece local até entrega posterior na main.

## Encerramento com escopo reduzido — 12/11/2026

Por decisão do usuário, `corrigir-pendencias-malha` e `integrar-status-operacional-multifonte` foram encerradas e arquivadas com o escopo já entregue, em `openspec/changes/archive/2026-11-12-corrigir-pendencias-malha/` e `openspec/changes/archive/2026-11-12-integrar-status-operacional-multifonte/`. As referências anteriores a mudanças ativas descrevem o estado antes desta decisão.

Os dois itens restantes da malha e os quatro de status foram **adiados, não executados nem aprovados**, e estão preservados em [melhorias futuras e limitações](melhorias-futuras-malha-status.md). As contagens originais eram 17/19 e 15/19; não foram convertidas em alegações de execução integral. As listas arquivadas distinguem tarefas executadas e itens retirados do compromisso atual. Não há mudanças ativas no OpenSpec após este encerramento; isso não significa ausência de melhorias ou restrições.

Foram consolidadas as capacidades `disponibilidade-malha` e `status-operacional-linhas`, alinhando referências históricas à calibração e à configuração local já entregues. Nenhuma alteração de código, funcionamento, malha, parâmetros, fontes ou configuração foi feita. O encerramento permanece local até entrega posterior na main.

A configuração ausente foi validada por **HTTP local isolado**, não por HTTP no runtime nativo do Xano, e não comprova o teste administrativo de gravações simultâneas de trechos. A ativação pública das fontes e a validação autorizada Direto dos Trens continuam fora do escopo encerrado.
