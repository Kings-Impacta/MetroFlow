## Preparação
- [x] Ler estado, documentação e proposta anterior.
- [x] Conferir grades oficiais e guardar exportação atual.

## Implementação
- [x] Implementar horários, espera e disponibilidade prevista no cálculo.
- [x] Implementar desempate determinístico e continuidade no mesmo trem.
- [x] Integrar contrato detalhado e legado, registro e lotação.
- [x] Atualizar instruções e documentação com limites das estimativas.

## Validação
- [x] Testar dias, horários, feriados, última partida e disponibilidade futura.
- [x] Comparar rotas reais antes/depois e preservar cenários regulares.
- [x] Testar contratos, registro, concorrência e compilar Reflex.
- [x] Validar OpenSpec/XanoScript, prévia, publicação e releitura sem alterar tabelas.

## Revisão para arquivamento em 11/11/2026

Escopo concluído e publicado; os testes de entrega e a auditoria dos registros 67/68 são descritos em `docs/xano/reteste-main-status-concorrencia-2026-11-11.md`. Pendências de validação remota geral e de dados adicionais permanecem nas mudanças próprias, sem serem marcadas como concluídas aqui.

## Datas de conclusão e atualização

- Última atualização versionada anterior à revisão de arquivamento: **09/11/2026**, commit `6f0a998` (PR #39), que contém o fechamento e as evidências de publicação/validação. Esta é a data usada no diretório de arquivo por solicitação do usuário.
- Revisão documental e movimentação física para `archive`: **11/11/2026**. Essa revisão não é uma nova data de implementação ou publicação. Correções documentais de limites e contexto feitas na revisão não foram retrodatadas.
- A publicação e releitura do cálculo de espera foram concluídas em **29/10/2026**; o cliente calibrado foi integrado em **05/11/2026** e o fechamento documental posterior é de **09/11/2026**. Fonte: `docs/xano/espera-partidas-2026-10-28.md` e histórico do Git.
