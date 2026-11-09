# Simulação de limites da concorrência — 08/11/2026

O cenário recomendado para validação permite uma alternativa parcialmente ocupada quando ela reduz pelo menos 40% do tempo previsto em trechos ocupados, acrescenta no máximo uma baldeação e respeita o menor limite entre 8 minutos e 45% do tempo principal. A política de alternativas totalmente livres conserva o comportamento publicado. A margem final de 60 segundos entra somente na estimativa exibida.

| Perfil | Resultado no conflito real | Mudanças em 404 cenários de ocupação |
|---|---|---:|
| Publicado | Linha 3 → Sé → Linha 1 | Referência |
| Parcial, 45%, teto 7 min, redução mínima 40% | Principal mantido | 42 |
| Parcial, 45%, teto 8 min, redução mínima 40% | Linha 3 → República → Linha 4 → Paulista/Consolação → Linha 2 | 73 |
| Parcial, 45%, teto 10 min, redução mínima 40% | Mesmo caminho por República | 79 |

| Componente do caso real | Antes | Candidato de 8 min |
|---|---:|---:|
| Tempo físico | 19 min 15 s | 27 min 15 s |
| Tempo estimado com margem única | 20 min 15 s | 28 min 15 s |
| Baldeações | 1 | 2 |
| Tempo previsto em trechos ocupados | 14 min 45 s | 5 min 50 s |

A redução de exposição no caso real é de 60,45%. A primeira parte entre Barra Funda e República continua compartilhada. A alternativa pela Luz, de 44 min 20 s com a margem final, continua fora dos limites.

Cada perfil foi comparado com 320 buscas sem ocupação e 404 cenários de ocupação. Todas as buscas sem ocupação conservaram a resposta. No candidato de 8 minutos, as 73 mudanças respeitaram o teto de tempo e a baldeação adicional, sem ciclos. A menor redução de exposição entre essas mudanças foi 44,1%. A exclusão da própria viagem, o sentido inverso e viagens substituídas foram verificados adicionalmente. A métrica é ocupação estimada a partir das viagens do aplicativo.

A simulação usa os registros reais anonimizados de 08/11 e a cópia publicada da malha. O código candidato e os resultados estão em `outputs/limites-concorrencia-20261108`. Os arquivos são exclusivos de laboratório e exigem regeneração coordenada da versão de busca e registro antes de qualquer publicação. Não houve alteração no Xano.

No reteste real de 09/11, os registros de 14h39min55,076s e 14h40min13,318s pertencem a contas distintas. As buscas e confirmações responderam HTTP 200, usando a nova versão 570d9ed67e4c9df0cd179e4f6e2cb99ca57a0df5dd2843e53e8d61778c2e3407. Ambas receberam Linha 3 até Sé e Linha 1 até Paraíso.

A reprodução reconheceu os nove trechos ocupados. Nesse horário de segunda-feira, o principal tinha 1215 s de tempo físico, enquanto o corredor por República tinha 1725 s, duas trocas e exposição de 350 s. O acréscimo de 510 s excedeu o teto de 480 s por 30 s. A alternativa pela Linha 11 e Luz tinha 1715 s e excedeu o teto por 20 s. Assim, os novos limites foram respeitados, mas nenhuma alternativa foi selecionada neste par. A estimativa pública do principal é 1275 s e a de República seria 1785 s, incluindo a margem única.
