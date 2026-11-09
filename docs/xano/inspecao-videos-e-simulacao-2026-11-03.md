# Inspeção de vídeos e simulação local — 03/11/2026

Continuação da coleta iniciada em 01/11. Sem gravação, consulta autenticada ou publicação no Xano nesta etapa; sem alteração do aplicativo ou envio à main. Referência das simulações: exportação de leitura de 01/11/2026, não uma confirmação do estado remoto em 03/11. Linha 6 permanece fora do ensaio e por último.

## Evidência nova e grau de validação

Foi possível acessar o YouTube pelo navegador e conferir três vídeos por marcos visuais e transcrição automática. Isso resolve parte do bloqueio anterior de acesso, mas **não constitui inspeção contínua de toda a gravação**. A reprodução Normal no player foi conferida em República; não comprova que o arquivo original não foi acelerado ou editado. Datas de publicação foram lidas na descrição expandida; datas de gravação continuam desconhecidas.

| Vídeo e publicação | Marcos observados | Aproveitamento |
| --- | --- | --- |
| [República: L4 → L3, Dicas SP, 20/02/2024](https://www.youtube.com/watch?v=LTaWTSs3Mis) | 00:40 ainda na saída do trem; 00:45 na plataforma da Amarela; 01:15 no percurso intermediário; 02:20 descendo para a Vermelha; 02:30 no piso da plataforma | Intervalo de mídia de 105 s entre 00:45 e 02:30. Uma observação, sem espera pelo próximo trem. Não é média atual comprovada |
| [Paulista → Consolação, Dicas SP, 13/02/2024](https://www.youtube.com/watch?v=xg9cJLb44Ds) | 00:30 já em deslocamento antes das escadas; 00:50 na escada; 02:00 no acesso do corredor; 04:05 junto à plataforma da Verde | Segmento parcial de mídia de 215 s. Não mede a saída de todas as portas/plataformas nem autoriza remover outras penalidades de troca |
| [Pinheiros: L4 → L9, Brasileiro pelo Mundo, 04/09/2026](https://www.youtube.com/watch?v=lTeWTJGTVQA) | Início na Linha 4; 01:50 em circulação interna; narração acompanha escadas, comentários e posterior espera na Linha 9 | Contexto recente sobre acesso e caminho. Os 15min37 do arquivo não são duração de baldeação. A descrição inverte a direção do título e a narração confunde destinos antes de corrigir; não importar orientações automaticamente |

Os tempos são diferenças no relógio do vídeo, não cronometragens independentes em campo. Permanecem pendentes verificação contínua de cortes/velocidade original e amostras adicionais. Os dois registros de 2024 são mais recentes que os relatos de 2018 usados antes, mas ainda não certificam a operação de 2026. O vídeo de 2026 não forneceu tempo limpo de caminhada. Não houve novo tempo embarcado atual validado por vídeo.

Foram preservados nove candidatos adicionais no catálogo, inclusive vídeos de Pinheiros, Luz e viagem ao aeroporto. Uma tentativa posterior de abrir o vídeo do aeroporto expirou; ele permanece como pista não inspecionada. Acervo total: 25 links candidatos, seis observações históricas e três inspeções de vídeo. Não foram republicadas transcrições integrais nem vídeos; os arquivos de acervo contêm links e anotações próprias.

## Simulação e limites

`scripts/simular_observacoes_video.py` gera três cópias locais da função exportada e executa o algoritmo original, com horários e regras de concorrência preservados:

1. Referência, sem ajustes.
2. República: substitui a penalidade de 600 s por 105 s apenas na troca L4 → L3 em República. É um teste exploratório com caminhada observada; não inclui uma nova estimativa de espera regular. Não transferir esse total para produção antes de separar e completar espera/caminhada.
3. República e corredor: acrescenta a substituição de 180 por 215 s apenas em Paulista → Consolação. É um ensaio do segmento parcial; as penalidades existentes permanecem, e o sentido inverso conserva 180 s. Não aplicar 215 s como baldeação completa.

Não foram somados os valores antigos das hipóteses comunitárias nem o ajuste histórico da Linha 12: são ensaios separados para permitir atribuir as diferenças à evidência nova. O teste de caminhada não publica um registro de viagem com regras diferentes; nenhuma gravação real é efetuada.

A bateria anterior não exercitava a troca L4 → L3 em República. A primeira execução foi interrompida pela verificação de cobertura e não gerou comparação aprovada. Foi adicionado `--pares-videos` ao auditor local com Luz ↔ Marechal Deodoro, Paulista ↔ Brás e Pinheiros ↔ Marechal Deodoro. Sem a opção, os casos anteriores permanecem como antes.

O ensaio ampliado executou **1.320 cenários**: três perfis com 320 buscas e 120 cenários sintéticos de concorrência cada. As 290 buscas originais foram reproduzidas sem diferenças no perfil de referência. Nenhuma estação repetida nas buscas ou alternativas; nenhum desvio acima do dobro do principal; arquivos de entrada preservados por SHA-256; corredor inverso verificado sem alteração. Esses controles não validam a precisão dos tempos nem todas as regras operacionais possíveis.

| Perfil | Buscas alteradas / 320 | Respostas de concorrência alteradas / 120 |
| --- | --- | --- |
| República 105 s | 9 | 10 |
| República e segmento do corredor 215 s | 15 | 12 |

Exemplos às 12h10 de 29/10/2026, sem ocupação, com os dados exportados de 01/11:

| Trajeto | Referência | Ensaio combinado | Itinerário |
| --- | --- | --- | --- |
| Luz → Marechal Deodoro | 16 min | 7min45 | Mantém Amarela → Vermelha |
| Paulista → Brás | 18 min | 13min45 | Amarela → Turquesa passa a Amarela → Vermelha |
| Pinheiros → Marechal Deodoro | 26 min | 17min45 | Mantém Amarela → Vermelha |
| Paulista → Consolação | 3 min | 3min35 | Segmento a pé no sentido observado |
| Paulista → Brigadeiro | 17 min | 17min35 | Mantém a penalidade atual após o corredor |

**Não apresentar esses totais como previsão de viagem atual.** Os demais deslocamentos ainda têm aproximações e a espera regular não foi calibrada. A diferença de 8min15 em República vem da substituição de uma penalidade genérica por um tempo de mídia de caminhada; não é economia comprovada para todos os passageiros. O custo de Paulista → Brigadeiro também ilustra a necessidade de separar componentes antes de mexer em penalidades.

Resultado completo: pasta irmã do worktree `outputs/observacoes-video-20261103-ampliado/comparacao.json`, com casos e arquivos por perfil. O acervo permanente fica em `docs/dados/tempos/inspecoes-video.csv` e `videos-candidatos.csv`, com estados e limitações. A calibração real permanece aberta, com prioridade para continuidade dos vídeos, direção/plataforma, amostras por faixa horária e espera regular.
