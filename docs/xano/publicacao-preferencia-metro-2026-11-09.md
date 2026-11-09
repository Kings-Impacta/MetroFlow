# Publicação da preferência pelo Metrô — 09/11/2026

Estado em 09/11/2026: publicado no Xano e validado com duas contas reais; registros 52 e 53. Consulte o reteste ao final.

## Correção da entrega

A tentativa anterior usou o campo `xanoscript` no PUT de metadados. A chamada retornou sucesso, mas a exportação manteve a versão anterior. A comparação detectou a diferença no identificador de calibração do registro. Não foi um erro na regra de seleção. A entrega corrigida usou `xano workspace pull`, prévia `--dry-run` e `workspace push` transacional dos dois endpoints juntos, preservando os GUIDs do pull recente.

A prévia indicou exclusivamente `trajetos/buscar POST` e `viagens/confirmar POST`. Nenhuma tabela, registro ou configuração de lotação integrou a publicação. Backup dos endpoints e nove tabelas de referência preservado em `outputs/publicacao-preferencia-metro-20261109/backup`, na pasta pai deste checkout; pull completo em `pull-recente`.

## Regra publicada

- Alternativa parcial: acréscimo máximo de min(540 segundos, 45% do tempo físico principal).
- No máximo uma baldeação adicional e redução mínima de 40% da exposição temporal.
- Entre alternativas elegíveis, preferência por caminho inteiramente pelo Metrô até 60 segundos acima da alternativa escolhida sem preferência.
- A busca inicial sem ocupação continua pelo menor tempo; horários de operação continuam aplicáveis.
- A margem de 60 segundos continua somente no tempo estimado público total, sem prolongar a ocupação física.

Busca e registro usam a versão `ebe34d59abdefc843e976afe160630f9b8ba37c5ca5c66885a0c1656fab333bb`.

## Conferência após publicação

A exportação dos dois endpoints contém lambdas idênticas às candidatas validadas, sem rascunho pendente. ID, nome, verbo, autenticação, entradas, cache e GUID foram preservados. A execução local do código efetivamente exportado reproduziu Barra Funda → República → Linha 4 → Paulista–Consolação → Linha 2 → Paraíso: 28min45s físicos, 29min45s estimados. O registro aceitou a mesma versão e cronologia e rejeitou versão incorreta e referência com mais de 30 segundos.

Os ensaios anteriores cobriram 320 buscas sem ocupação e 404 cenários de concorrência. O OpenSpec passou nos 12 itens em validação estrita. Evidências pós-publicação: `outputs/publicacao-preferencia-metro-20261109/conferencia-final/validacao.json`.

Na conferência inicial, o reteste real ainda estava pendente. Ele foi concluído depois, conforme a seção abaixo; a validação em memória e a evidência real permanecem distinguidas.

## Reteste real concluído às 15h05 de 09/11

Os registros 52 e 53 pertencem a usuários distintos e foram confirmados com 8,666 segundos de diferença. Ambos os POST de registro retornaram HTTP 200 e enviaram a versão publicada `ebe34d59abdefc843e976afe160630f9b8ba37c5ca5c66885a0c1656fab333bb`. O horário calculado e a sequência de trechos enviados coincidem com os registros persistidos.

A primeira viagem usou Linha 3 → Sé → Linha 1, com tempo físico de 20min15s e estimado de 21min15s. A segunda usou Linha 3 → República → Linha 4 → Paulista–Consolação → Linha 2 → Paraíso, com tempo físico de 28min45s e estimado de 29min45s. A reprodução com o código exportado e a primeira viagem ativa selecionou exatamente os trechos da segunda: exposição principal de 885 s e alternativa de 350 s, redução de 60,45%. Acréscimo de 510 s e uma baldeação adicional, dentro dos limites publicados. Os registros antigos das mesmas contas foram substituídos normalmente.

A pendência de reteste real descrita acima está concluída para esse cenário. Evidência resumida sem identidades: `outputs/reteste-preferencia-metro-20261109/resultado.json`, na pasta pai deste checkout. Nenhuma alteração no Xano foi realizada durante esta conferência.
