# Medições parciais, vídeos candidatos e reprodução histórica

Pesquisa de 01/11/2026. Xano e aplicação inalterados; sem publicação ou envio à main. Linha 6 por último. Acervo reutilizável em `docs/dados/tempos/`, dentro do projeto, com observações CSV, links de vídeo e manifesto de fontes. Os arquivos não são carregados pelo aplicativo.

## Avanço e limites

Foram preservados seis relatos de deslocamento com horários ou duração e 16 links candidatos a vídeo. O [relato com comentários de passageiros](https://www.essemundoenosso.com.br/trem-pro-aeroporto-de-guarulhos-como-e-e-como-usar/) contém um registro datado de 02/12/2018: Tatuapé → Engenheiro Goulart entre 18h20 e 18h32. Outros registros abrangem percursos agregados, úteis como referências históricas sem desmembramento arbitrário. Há ainda [relato de 31 minutos no Expresso antigo a partir da Luz](https://passageirodeprimeira.com/como-ir-de-trem-para-o-aeroporto-de-guarulhos/), mantido fora dos parâmetros atuais.

Essa evidência é mais concreta que uma hipótese sem fonte, mas ainda é uma observação individual antiga. A viagem do autor do primeiro relato não pode ser datada pela atualização da página. O comentário da Linha 13 tem numeração de linha incorreta na chegada, registrada como ressalva no CSV. Não foi inferida duração do percurso inverso nem caminhada a partir de intervalos que incluem espera.

O [catálogo UrbanRail](https://www.urbanrail.net/cab-rides/YOUTUBE%20VIDEOS%20CAB%20RIDES%20METRO.pdf), páginas 12–13 do PDF, permitiu identificar quinze candidatos ferroviários, além do vídeo associado ao relato. São pistas de busca, não observações primárias validadas. Os players consultados não abriram e não houve inspeção visual. Foram guardadas suspeitas de aceleração e inconsistências entre datas e terminais. Nenhum tempo de baldeação foi medido em vídeo nesta etapa. Faltam vídeos acessíveis com continuidade, eventos e velocidade verificáveis para substituir os tempos das baldeações.

## Comparação local reproduzível

`scripts/simular_medicao_parcial.py` executa a busca exportada em cópias isoladas. O único ajuste experimental é 720 s no trecho 171 da Linha 12, Tatuapé → Engenheiro Goulart. Na referência ele usa 120 s. Trata-se da reprodução de uma observação de 2018, **não de uma recomendação de atualização para 2026**.

Foram executados 796 cenários: 398 de referência e os mesmos 398 no candidato (290 buscas e 108 casos de concorrência por perfil). A referência reproduziu exatamente a auditoria anterior. Foram alteradas seis buscas e quatro respostas de concorrência; nenhuma estação repetida, nenhum desvio acima do dobro do principal. O ensaio também confirmou a preservação dos casos Engenheiro Goulart → Brás e dos arquivos de entrada por comparação de SHA-256.

Exemplos às 12h10 de 29/10/2026:

| Percurso | Cadastro atual | Reprodução histórica parcial | Itinerário |
| --- | --- | --- | --- |
| Brás → Engenheiro Goulart | 4 min | 14 min | Mantém Linha 12 |
| Barra Funda → Aeroporto-Guarulhos | 38 min | 48 min | Mantém Turquesa → Safira → Jade |
| Engenheiro Goulart → Brás | 4 min | 4 min | Volta preservada por falta de observação |

Esses resultados não validam o tempo total das viagens: os demais trechos mantêm estimativas e esperas regulares incompletas. A referência de Brás → Engenheiro Goulart relatada pelo autor é de 20 minutos, em outra viagem. Não se subtraiu essa amostra para inventar a duração Brás → Tatuapé. A discrepância fica preservada para pesquisa posterior.

Na primeira comparação de concorrência afetada, Barra Funda → Aeroporto mantém Coral → Safira → Jade e passa de 38 para 48 minutos no candidato. Os casos de ocupação são sintéticos, reconstruídos segundo os custos de cada perfil; não houve registro de viagens ou teste de contas reais.

Os relatórios completos estão na pasta irmã do worktree `outputs/medicoes-parciais-20261101`, com `comparacao.json`, referências e resultados por cenário. Os relatórios anteriores de hipóteses permanecem separados e não foram reclassificados como medições.

## Continuidade do acervo

Preservar qualquer observação útil mesmo que não cubra a linha toda. Classificar por data, sentido, tipo de evidência, precisão, confiabilidade e pendência. Dados históricos servem para verificação e investigação, sem substituir automaticamente a operação atual. Antes de aplicar: confirmar vigência, ampliar amostras, medir baldeações plataforma a plataforma, separar espera e caminhada, e simular busca e registro da viagem com custos compatíveis. A calibração atual permanece em aberto.
