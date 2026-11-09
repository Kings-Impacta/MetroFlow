# Simulação local: preferência pelo Metrô — 09/11/2026

Estado: experimento local, não publicado. Nenhuma alteração no Xano.

A preferência atua apenas na escolha da alternativa de concorrência: admite um caminho inteiramente pelo Metrô até 60 segundos mais lento que a alternativa elegível original. Inclui linhas concedidas; não presume que o usuário já esteja embarcado. A busca inicial sem ocupação continua priorizando o menor tempo.

Preserva o acréscimo máximo de min(9 minutos, 45% do tempo principal), uma baldeação extra e redução mínima de 40% da exposição temporal em relação à rota principal. Mantém horários e disponibilidade do motor existente.

## Barra Funda → Paraíso

Reprodução local dos registros anonimizados de duas contas, com 18,242 segundos entre buscas. Os tempos abaixo já incluem uma única margem de 1 minuto sobre o total.

| Cenário | Caminho | Tempo estimado | Baldeações | Exposição modelada |
|---|---|---|---|---|
| Principal | Linha 3 → Sé → Linha 1 | 21min15s | 1 | 14min45s |
| Teto de 9 minutos, sem preferência | Linha 11 → Luz → Linha 1 | 29min35s | 1 | 0s |
| Teto de 9 minutos, com preferência | Linha 3 → República → Linha 4 → Paulista–Consolação → Linha 2 | 29min45s | 2 | 5min50s |

O caminho pelo Metrô custa 10 segundos adicionais frente à alternativa pela Luz e 8min30s frente ao principal. Reduz a exposição em 60,45% frente ao principal. A preferência aceita mais exposição que a alternativa pela Luz, desde que a redução mínima continue atendida. Exposição representa sobreposição calculada com os registros do teste, não uma medição de lotação real.

## Validação

- 320 buscas sem ocupação: resultados preservados.
- 404 cenários de concorrência: 5 escolhas alteradas; todos os casos alterados respeitaram os limites, usaram apenas linhas do Metrô e não repetiram estações.
- Limiares de preferência de 0 e 9 segundos mantiveram Luz; 10 e 60 segundos liberaram República no caso principal.
- Três controles preservados: viagem do próprio usuário, sentido inverso e viagem substituída.

Reprodução: `scripts/simular_preferencia_metro.py`. Evidências: `outputs/preferencia-metro-20261109/comparacao.json` e `candidato-metro.js`, no diretório pai deste checkout.

Limitação: simulação com a malha e os horários dos cenários guardados. Não substitui novo teste com duas contas no aplicativo após eventual aprovação e publicação. O teto de 9 minutos e esta preferência continuam candidatos locais.

Atualização: candidato publicado em 09/11 após autorização, conforme publicacao-preferencia-metro-2026-11-09.md. O conteúdo acima descreve o ensaio anterior à publicação.
