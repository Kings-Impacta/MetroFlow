- [x] Reproduzir a disputa remota e preservar os pares 70/71 e 75/76.
- [x] Conferir documentação oficial e sintaxe do bloqueio nativo.
- [x] Exportar workspace antes da edição e preservar hashes do backup.
- [x] Preparar correção restrita ao registro com revalidação após o bloqueio.
- [x] Guardar snapshots de dados e validar código e regressões pertinentes.
- [x] Conferir prévia com somente viagens/confirmar e publicar.
- [x] Reler endpoint e comprovar preservação da malha, parâmetros e busca.
- [x] Repetir confirmações simultâneas autenticadas e conferir HTTP, sobreposição, substituição e uma única viagem ativa.
- [x] Documentar resultado e limitações sem concluir a matriz remota não executada.

Resultado: registros 81/82, ambos HTTP 200 e sobrepostos; somente 82 ativa na leitura após a disputa. Releitura independente confirmou a substituição e hashes preservados. Evidência e limites em `docs/xano/exclusividade-viagens-2026-11-11.md`.

## Data e limite do arquivamento

Conclusão funcional e reteste: **11/11/2026**, registros 81/82; integração na main: PR #43. Revisão e movimentação para arquivo: **12/11/2026**. O diretório usa a data da conclusão, conforme critério solicitado pelo usuário. Os três requisitos foram consolidados em `openspec/specs/exclusividade-viagens/spec.md`. Este fechamento é exclusivo da correção de exclusividade e não encerra a matriz geral da concorrência. A configuração ausente foi validada apenas de forma isolada, sem retirar o registro real; ver `docs/xano/sessao-expirada-configuracao-ausente-2026-11-11.md`.
