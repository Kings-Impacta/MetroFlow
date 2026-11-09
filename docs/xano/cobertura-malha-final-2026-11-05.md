# Encerramento da Linha 6 e cobertura da malha — 05/11/2026

A LinhaUni publica a janela das 10h às 15h em dias úteis, exceto feriados. A ARTESP registrou o encerramento às 15h03 em 03/11 e às 15h01 em 04/11. São horários de registro do estado da linha. O Cittamobi indica 14h45 como última saída de dia útil em cada terminal, em quadro de 03/11. O fim de faixa às 14h59 do GTFS fica preservado como metadado de frequência. Para a simulação foi escolhida a referência de 14h45. Ainda não foi localizada uma grade oficial por estação e sentido. [LinhaUni](https://www.linhauni.com.br/guia-do-passageiro) · [Histórico da ARTESP](https://ccm.artesp.sp.gov.br/metroferroviario/historico-status/) · [Cittamobi sentido Perdizes](https://linhas-preview.cittamobi.com.br/linha/transporte_publico-SaoPaulo-SPTRANS-METROL6-PERDIZES-e633f26a1924) · [Cittamobi sentido João Paulo I](https://linhas-preview.cittamobi.com.br/linha/transporte_publico-SaoPaulo-SPTRANS-METROL6-JOAOPAULOI-3195cfe79ade)

A estimativa soma os tempos de cada trecho a partir da saída do terminal. Os horários abaixo foram arredondados ao minuto para leitura. A reprodução usa os valores completos em segundos. A chegada estimada aos dois terminais é por volta das 14h57.

| Estação | Última partida estimada rumo a Perdizes | Rumo a João Paulo I |
|---|---:|---:|
| João Paulo I | 14h45 | Terminal de chegada |
| Freguesia do Ó | 14h47 | 14h54 |
| Santa Marina | 14h50 | 14h51 |
| Água Branca | 14h52 | 14h49 |
| Sesc-Pompeia | 14h55 | 14h47 |
| Perdizes | Terminal de chegada | 14h45 |

A simulação anterior só verificava se a espera média e o deslocamento cabiam até as 15h. O candidato agora rejeita novo embarque após a última passagem estimada. Quando a espera média ultrapassa a última passagem e o passageiro já chegou à plataforma, usa o horário do último trem candidato. O percurso continua limitado às 15h, preserva a permanência no mesmo trem e avisa sobre a incerteza perto do encerramento.

| Busca em dia útil | Antes | Depois |
|---|---|---|
| João Paulo I → Perdizes, 14h43 | Sem rota | 13 min 35 s, incluindo 2 min de espera |
| João Paulo I → Freguesia do Ó, 14h45min01s | Rota curta disponível | Sem embarque após a última saída estimada |
| Freguesia do Ó → João Paulo I, 14h53min20s | Sem rota | 3 min 15 s, incluindo 1 min de espera |
| João Paulo I → Perdizes, 12h | 18 min 05 s | 18 min 05 s |

A cobertura local da malha ativa foi fechada no nível de estimativa. O grafo carregou os 419 sentidos esperados com tempo positivo, incluindo 415 ferroviários e quatro a pé. Cada sentido ferroviário teve uma janela de embarque modelada nas amostras do dia útil. O conjunto preserva as 320 combinações de baldeação estimadas anteriormente e os dois corredores de caminhada explícitos do grafo, Paulista–Consolação e Água Branca L6–L7. A cobertura de cenários preserva as exceções já catalogadas. Horários operacionais podem mudar e os tempos modelados não são medições.

A comparação incluiu 25 cenários gerais da Linha 6, 32 de encerramento, 39 reproduções da cronologia do registro e dois cenários de concorrência na Linha 6. Na rede anterior, as 320 buscas e os 120 cenários de concorrência produziram os mesmos resultados. O Xano e a margem de 60 segundos ficaram fora desta etapa.

Dados e fontes em [linha6-operacao-assistida.json](../dados/tempos/linha6-operacao-assistida.json). Para reproduzir, o script `scripts/simular_linha6_assistida.py` recebe o candidato sem Linha 6, a pasta de saída e o candidato anterior com Linha 6. Os resultados ficam em `outputs/cobertura-malha-final-20261105/`.
