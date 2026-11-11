# Fechamento de trajetos e concorrência — 09/11/2026

Estado histórico de 09/11. Para o estado atual, consulte o [reteste na main de 11/11](reteste-main-status-concorrencia-2026-11-11.md), incluindo status e pendências.

## Resultado confirmado

O teste real Barra Funda → Paraíso gravou as viagens 52 e 53 para contas distintas, com 8,666 segundos entre confirmações. Ambos os registros retornaram HTTP 200, enviaram a versão publicada `ebe34d59abdefc843e976afe160630f9b8ba37c5ca5c66885a0c1656fab333bb` e tiveram horário calculado e trechos confrontados com o banco.

| Conta por ordem de registro | Caminho | Tempo estimado com margem única |
|---|---|---|
| Primeira | Linha 3 → Sé → Linha 1 | 21min15s |
| Segunda | Linha 3 → República → Linha 4 → Paulista–Consolação → Linha 2 | 29min45s |

A reprodução do conflito com o código publicado selecionou os mesmos trechos da segunda viagem: 885 s de exposição no principal e 350 s na alternativa, redução de 60,45%. O acréscimo físico foi 8min30s, com uma baldeação extra. A configuração 1 usuário/1% continua intencional para demonstração. Isso não mede lotação oficial.

Busca e registro compartilham a versão e o relógio físico. O total público recebe apenas 60 s de margem. A publicação preservou autenticação, parâmetros e GUIDs. Veja [evidências da publicação](publicacao-preferencia-metro-2026-11-09.md).

## Pendências revisadas

A revisão abaixo confronta os checklists e evidências locais; não representa uma nova auditoria online de todas as linhas nem novo teste de cada caso remoto.

| Item | Estado e consequência |
|---|---|
| Restauração da malha, integração do cliente e espera de serviços | Concluídos nas entregas posteriores; marcações antigas corrigidas. |
| Cobertura estimada de trechos, esperas e baldeações | Entrega modelada concluída: 419 sentidos, incluindo Linha 6 parcial; não confundir com tempos medidos ou todas as obras futuras. |
| Alternativa calibrada com duas contas | Concluída para Barra Funda → Paraíso. Não garante rota alternativa para toda combinação: pode não haver opção elegível. |
| Matriz remota completa da concorrência | Ainda sem evidência completa: entradas inválidas/desconexas, sessão expirada, configuração ausente, sem alternativa. Há testes locais; falta encerrar a matriz autenticada histórica no Xano. Não bloqueia desenvolvimento informativo de status. |
| Duas confirmações simultâneas do mesmo usuário | Ainda precisa teste autenticado para confirmar a garantia de uma única viagem ativa na transação. O teste de duas contas não cobre essa disputa. Deve ser validado antes de ampliar uso em produção. |
| Criações administrativas simultâneas de trechos | Reteste HTTP autenticado ainda listado na mudança de pendências da malha. Separado da concorrência de passageiros e não bloqueia leitura informativa de status. |
| Retornos diretos do Expresso L10 | Certificação/inclusão adicional ainda aberta no checklist antigo. A modelagem vigente contempla o serviço com estimativas e disponibilidade; não afirmar que novos retornos já foram cadastrados. Reavaliar fonte, necessidade e impacto em mudança própria. Não bloqueia status. |
| Limites de demonstração 1/1% | Mantidos por decisão do usuário; definir valores de produção com a equipe antes de uso real amplo. Não trocar automaticamente nesta revisão. |
| Atualização de horários, exceções e Linha 6 | Manutenção contínua das estimativas e do alcance operante. Não oferecer conexões futuras nem prometer última partida exata por estação. |
| Integração documental e encerramento OpenSpec | O fechamento de 09/11 foi entregue no PR #39 e a integração de status no PR #41. Sincronizar/arquivar somente mudanças com critérios concluídos; permanecem itens remotos e externos abertos. |

## Integração de status e reteste posterior

A preparação descrita originalmente nesta seção foi superada: adaptadores, cache, limites, atualização automática, retenção, interface e testes foram entregues na main pelo PR #41. A configuração local usa Metrô/CPTM/Motiva; Direto dos Trens ainda aguarda token. As condições de ativação pública e a cobertura restante continuam pendentes. Consulte o [guia vigente](../status-operacional.md) e o [reteste de 11/11](reteste-main-status-concorrencia-2026-11-11.md).

Status não modifica cálculo, horários ou ocupação. Usar alertas no cálculo exigirá decisão e validação próprias.
