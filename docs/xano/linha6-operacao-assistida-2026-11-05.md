# Linha 6 Laranja em operação assistida — 05/11/2026

A Prefeitura registra o início do atendimento em 03/07/2026 nas estações João Paulo I, Freguesia do Ó, Santa Marina, Água Branca, Sesc-Pompeia e Perdizes. A LinhaUni informa operação gratuita das 10h às 15h, de segunda a sexta, exceto feriados. O embarque nas demais linhas é tarifado. [Prefeitura de São Paulo](https://prefeitura.sp.gov.br/w/linha-6-laranja-inaugura-nova-fase-para-a-brasil%C3%A2ndia-e-aproxima-a-zona-norte-do-centro-de-s%C3%A3o-paulo) · [Guia da LinhaUni](https://www.linhauni.com.br/guia-do-passageiro)

Em Água Branca, a simulação distingue os acessos das linhas 6 e 7. O percurso externo usa a Avenida Santa Marina. A referência da obra descreve menos de 100 m na rua e a LinhaUni registra 47,8 m de profundidade para a estação do metrô. A estimativa de 7 min entre plataformas combina 90 s na rua, 210 s de circulação vertical e 120 s de acessos e orientação. A confirmação de abertura da passagem interna ainda está pendente. As conexões futuras com a Linha 4 em Higienópolis-Mackenzie e a Linha 1 em São Joaquim ficam no inventário de projeto. [Ficha da estação](https://www.linhauni.com.br/linha-6-laranja?unidade-construtiva=estacao-agua-branca) · [Percurso atual e obra](https://www.metrocptm.com.br/construcao-de-conexao-entre-linhas-6-e-7-em-agua-branca-tem-empresa-contratada/) · [Projeto de integração da TIC Trens](https://www.tictrens.com.br/noticias/tic-trens-vai-modernizar-estacao-agua-branca-que-se-tornara-o-principal-hub-de-mobilidade-paulista-2602)

A operação inaugural divulgou cerca de 13 min de intervalo. O GTFS da SPTrans coletado em 01/11 registra 15 min e 8 min uniformes entre cada par de estações. Esses offsets totalizam 40 min para o trecho e ficam guardados como referência de baixa confiança para duração. A simulação usa as coordenadas do GTFS e estima cada trecho pela distância em linha reta multiplicada por 1,10, velocidade de 35 km/h e 25 s de parada e manobra. São hipóteses nos dois sentidos, sem cronometragem. [Casa Civil](https://www.casacivil.sp.gov.br/sec_casa_civil/noticias/metrolinha6) · [Agência Brasil](https://agenciabrasil.ebc.com.br/geral/noticia/2026-07/linha-6-laranja-do-metro-de-sp-inicia-operacao-nesta-sexta-feira) · [GTFS da SPTrans](https://www.sptrans.com.br/desenvolvedores/)

| Trecho | Distância em linha reta | Estimativa por sentido |
|---|---:|---:|
| João Paulo I – Freguesia do Ó | 933 m | 2 min 15 s |
| Freguesia do Ó – Santa Marina | 1.389 m | 3 min 05 s |
| Santa Marina – Água Branca | 802 m | 2 min |
| Água Branca – Sesc-Pompeia | 894 m | 2 min 10 s |
| Sesc-Pompeia – Perdizes | 867 m | 2 min 05 s |

| Simulação às 12h de 05/11, em ambos os sentidos | Antes | Depois |
|---|---|---:|
| João Paulo I ↔ Perdizes | Sem rota no modelo | 18 min 05 s |
| Perdizes ↔ Palmeiras-Barra Funda | Sem rota no modelo | 25 min 40 s |
| Água Branca L6 ↔ Água Branca L7, plataforma a plataforma | Sem ligação no modelo | 7 min |

A espera média da Linha 6 é metade do intervalo e entra uma vez por embarque. Com intervalo de 15 min, o percurso completo sobe para 19 min 05 s. O cenário é conservador perto do fechamento e exige conclusão de cada trecho da Linha 6 até as 15h. A última partida real por estação e sentido segue sem grade confirmada. A referência operacional deve ser revisada quando o regime assistido mudar. A simulação bloqueia dias e horários fora da janela e datas anteriores à abertura.

O relatório reproduz 25 cenários direcionados, 17 cronologias de registro e 16 comparações de regressão. A Linha 6 tem uma única ligação com a malha ferroviária neste cenário. Com outra viagem ocupando o mesmo percurso entre terminais, o laboratório conserva o caminho por ausência de alternativa ferroviária válida. O trabalho ficou em cópia local, sem publicação no Xano e sem a margem final de 1 minuto.

Dados em [linha6-operacao-assistida.json](../dados/tempos/linha6-operacao-assistida.json). O script `scripts/simular_linha6_assistida.py` recebe a pasta do candidato anterior e a pasta de saída. O resultado fica em `outputs/linha6-assistida-20261105/simulacao-linha6.json`.


A [revisão de encerramento e cobertura integrada](cobertura-malha-final-2026-11-05.md) complementa este relatório histórico. O script passou a receber um terceiro argumento, com o candidato anterior da Linha 6 para a comparação de encerramento.
