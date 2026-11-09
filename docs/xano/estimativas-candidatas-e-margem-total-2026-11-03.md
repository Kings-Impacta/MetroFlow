# Estimativas candidatas e margem única no total

Esclarecimento do usuário em 03/11/2026: aceitar estimativas concretas com método e referências, sem exigir validação documental integral. A margem será **um minuto no trajeto inteiro**, nunca por estação, espera ou baldeação. Exemplo obrigatório: base de 15 min → estimativa de 16 min. Não aplicada nesta etapa, porque a cobertura ainda está incompleta.

## Avanço nas lacunas

Foram guardados 11 candidatos em `docs/dados/tempos/estimativas-lacunas.json`. Nove correspondem a sentidos que estavam entre as 16 lacunas individuais. Dois são ajustes de consistência de Itapevi ↔ Santa Rita, que já tinham referência GTFS.

| Intervalo candidato | Base estimada, sem margem | Método e limite |
| --- | --- | --- |
| Itapevi ↔ Santa Rita | 2min45 | Distribuição por distância do total secundário de 12 minutos da extensão |
| Santa Rita ↔ Ambuitá | 6min45 | Mesmo modelo geográfico; não é cronometragem |
| Ambuitá ↔ Amador Bueno | 2min30 | Mesmo modelo; tempos de ida e volta assumidos simétricos |
| Tamanduateí ↔ São Caetano | 2min30 | Complemento de total histórico de 9 min, comparado à observação do outro intervalo |
| São Caetano ↔ Santo André | 6min30 | Relato de viagem no antigo Expresso L10+ usado como referência de serviço comparável; retorno estimado por simetria |
| Consolação → Paulista | 5 min | Caminhada assumida a 1,2 m/s para aproximadamente 300 m mais 50 s de circulação/transição |

São modelos de confiança baixa com parâmetros explícitos. A distribuição de um total entre paradas agora é permitida como estimativa identificada; continua proibido apresentá-la como medição. O modelo geográfico usa coordenadas das paradas do GTFS e a coordenada publicada de Ambuitá. A soma dos três intervalos da extensão permanece 12 minutos; distância geodésica não reproduz curvas de via, aceleração e paradas.

Fontes preservadas:

- [Características da Linha 8](https://pt.wikipedia.org/wiki/Linha_8_do_Trem_Metropolitano_de_S%C3%A3o_Paulo): total secundário de 12 minutos, com trechos do artigo desatualizados. Serve de âncora aproximada, sem garantia de atualidade.
- [Localização de Ambuitá](https://pt.wikipedia.org/wiki/Esta%C3%A7%C3%A3o_Ambuit%C3%A1) e coordenadas do GTFS já guardado: base do rateio geográfico.
- [COMMU: viagem de São Caetano a Santo André](https://www.commu.site/blog/2019/04/06/cptm_flexibilizacao/): observação de 6min30 em 2019 no Expresso L10+. O serviço difere do expresso atual; a estimativa não cria atendimento em São Caetano no contrafluxo.
- [Diário do Grande ABC](https://www.dgabc.com.br/Noticia/2864077/cptm-analisa-modelo-de-trem-expresso-que-atenda-maua): referência histórica de cerca de nove minutos no total do Expresso L10. Combinar amostras distintas produz inferência, não medição de uma viagem.
- [UOL: reportagem sobre o corredor](https://noticias.uol.com.br/cotidiano/ultimas-noticias/2011/11/01/esteiras-rolantes-da-estacao-paulista-do-metro-deixam-usuarios-a-pe-em-horarios-de-pico.amp.htm): distância aproximada de 300 m. Velocidade e circulação adicional são parâmetros do modelo, não valores medidos pela reportagem.

Os tempos de 90 s + 90 s do cadastro do Expresso L10 não foram adotados como verdade; os candidatos aumentam seu total para nove minutos. É importante confrontar também o parador e a disponibilidade: os tempos regulares genéricos podem tornar o parador artificialmente mais rápido. Nenhuma alteração foi publicada.

## Comparação local

`scripts/simular_estimativas_lacunas.py` executou 880 cenários: 320 buscas e 120 casos sintéticos de concorrência por perfil, referência e candidato. As 290 buscas antigas foram reproduzidas sem diferenças na referência. No candidato, 12 buscas e oito resultados de concorrência mudaram. Nenhuma estação repetida nem alternativa acima do dobro do principal nos controles executados. Os dados originais foram preservados por hash.

Exemplos ao meio-dia do ensaio (12h10 de 29/10), usando a exportação de 01/11:

| Trajeto | Referência | Candidato sem margem |
| --- | --- | --- |
| Júlio Prestes → Amador Bueno | 54 min | 60 min |
| Amador Bueno → Júlio Prestes | 54 min | 60 min |
| Consolação → Paulista | 3 min | 5 min |
| Brigadeiro → Paulista | 17 min | 19 min |

Os totais ainda contêm outros custos provisórios, inclusive a penalidade de dez minutos após o corredor. Não são previsões finais de toda a rede. A margem única não foi aplicada nem a esse candidato. Os candidatos do Expresso L10 precisam de cenários específicos por sentido e faixa, pois a bateria não comprova que todas as suas arestas foram escolhidas.

Relatório completo na pasta irmã do worktree: `outputs/estimativas-lacunas-20261103/comparacao.json`. Os ensaios antigos de hipóteses, vídeos e relato histórico continuam separados, sem serem reclassificados.

## Cobertura restante e interface

O inventário regenerado contém 389 sentidos com referências anteriores, 11 com candidatos modelados e sete ainda sem referência externa individual, todos do Expresso Aeroporto. A classificação registra estimativa disponível, não aprovação para publicar. As 405 possibilidades de embarque ainda exigem seleção de espera por faixa/dia/serviço; as 128 trocas candidatas exigem decisão de conexão e tempos de caminhada, sem obrigação de documentação formal de cada uma.

A interface local já diz “Tempo estimado” e avisa que a duração pode variar conforme operação, lotação e condições externas. Esse aviso não constitui garantia nem elimina a necessidade de estimativas coerentes. A margem final de 60 s, a inclusão definitiva no projeto e a publicação no Xano aguardam completar a cobertura e simular. Linha 6 permanece adiada.

Verificação local: componente de resultado construído com sucesso; 21 testes de estado e três subtestes aprovados; OpenSpec estrito com 12 itens aprovados; comparações do candidato concluídas. A compilação completa do Reflex não concluiu: houve falhas de acesso ao registro de dependências durante a inicialização e a execução foi interrompida. Não afirmar que a compilação integral ou a interface em um navegador foram validadas nesta etapa. Nenhum servidor da apresentação foi reiniciado.
