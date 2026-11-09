# Calibração de tempos: verificação de fontes oficiais

Consulta em 01/11/2026. Pesquisa e simulação locais, sem alterar tabelas, publicar endpoints ou enviar alterações à main. **A calibração de tempos reais ainda não está concluída.** Linha 6 excluída da análise, conforme prioridade definida.

## Evidências e limites

- [SPTrans — desenvolvedores](https://www.sptrans.com.br/desenvolvedores/): GTFS estático obtido no [download oficial](https://www.sptrans.com.br/umbraco/Surface/PerfilDesenvolvedor/BaixarGTFS?memberName=sptrans). Arquivo recebido em 01/11/2026, SHA-256 `a948ac3b23507ac456d94a1c40dde94740d057c82b7648ee8ec861bd2be9e1ac`. A atualização do pacote não comprova a atualização de cada linha.
- Após excluir a Linha 6, foram examinados 15 padrões ferroviários e 30 viagens em dois sentidos. Em todos os padrões, os tempos entre paradas consecutivas são uniformes. Isso não comprova tempos medidos e exige confirmação da metodologia antes de substituir os valores atuais.
- Exemplos do pacote: Linha 7 com 480 s por intervalo; Linha 8 com 420 s; Linha 1 com 112 s; Linha 3 com 190 s. Não foram adotados como calibração real. A Linha 8 também omite Ambuitá.
- Não há `transfers.txt` nem `pathways.txt` no pacote: ele não fornece durações de caminhada por integração. Também não há `calendar_dates.txt` para exceções de calendário.
- A Linha 17 no GTFS usa janelas de 9h às 16h e intervalos antigos. O [comunicado do Metrô de 29/09/2026](https://www.metro.sp.gov.br/2026/09/29/metro-amplia-horario-da-linha-17-ouro-a-partir-desta-quarta-feira-30/) informa operação de segunda a sábado, 6h–22h, intervalo médio de 9 minutos e troca em Brooklin Paulista para Washington Luís. Preservar essa fonte mais específica e recente.
- Os quadros oficiais de intervalos da CPTM, disponíveis nos PDFs públicos abaixo, informam frequência programada por faixa e dia, não duração entre estações nem espera observada. Na Linha 10, o intervalo menor de pico é restrito a Barra Funda–Mauá; não deve ser aplicado automaticamente ao percurso inteiro. Na Linha 13, os intervalos também variam em dias úteis, sábados, domingos e feriados. Não houve alteração de esperas nesta etapa.
- O [planejador da TIC Trens](https://www.tictrens.com.br/sua-viagem/planeje-sua-viagem) confirmou o itinerário Jandira → Barra Funda → Sé → Paraíso, pelas linhas 8, 3 e 1 nas consultas efetuadas, mas a resposta obtida não forneceu tempos. Não usar esse resultado como medição de duração.

Quadros CPTM consultados:

- [Linha 10 — intervalos programados](https://www.cptm.sp.gov.br/dx/api/dam/v1/collections/05321fd9-3791-4689-a8ac-9e2adde39c4b/items/b6e68f57-4f4f-444d-b483-075f910e2c1b/renditions/4298df26-497c-47fd-a480-0b1812d6bb66?binary=true).
- [Linha 13 — intervalos programados](https://www.cptm.sp.gov.br/dx/api/dam/v1/collections/05321fd9-3791-4689-a8ac-9e2adde39c4b/items/a5767f09-3864-4b2a-930b-627adfd84220/renditions/f9c0493c-46d2-4224-8a80-c24dd88b2529?binary=true).

## Validação do estado atual

Exportação de leitura do Xano nesta consulta: 207 trechos, 190 ferroviários regulares, dos quais 188 ainda usam 120 segundos. Logo, o estado atual também contém aproximações e não deve ser apresentado como tempo real.

Executada a auditoria existente com 58 pares, cinco horários, 290 buscas sem ocupação e 108 cenários de concorrência. Resultado: nenhuma estação repetida nos casos sem lotação; nenhuma alternativa acima de duas vezes a duração principal. Esses controles não comprovam que as durações são reais ou que toda alternativa é adequada ao passageiro.

Exemplos às 12h10 de 29/10/2026, simulados com a exportação atual:

| Trajeto | Resultado atual | Estimativa atual |
| --- | --- | --- |
| Barra Funda → Paraíso | Vermelha → Azul | 28 min |
| Jandira → Paraíso | Diamante → Vermelha → Azul | 68 min |
| Consolação → Paulista | Integração a pé | 3 min |

Não existe comparação de correção aplicada antes/depois nesta etapa: os novos dados não passaram pela avaliação de adequação para calibração e os custos foram preservados. Não apresentar a repetição do resultado atual como melhoria de precisão.

## Próximos dados necessários

1. Tempos programados e, se disponíveis, observados entre estações consecutivas, por sentido, serviço, faixa horária e tipo de dia, com vigência e metodologia.
2. Caminhada por integração entre plataformas, distinguindo acesso comum e acessível; separar caminhada, desembarque e espera pelo próximo trem para evitar dupla contagem.
3. Frequências e padrões de atendimento completos, inclusive serviços parciais, ramais, feriados e partidas finais. Os quadros de intervalos encontrados podem apoiar uma etapa própria de estimativa de espera, identificada como programada.
4. Com dados aprovados, produzir candidato isolado e comparar as mesmas buscas e cenários de concorrência antes de qualquer atualização no Xano.
5. Linha 6 por último, fora desta etapa.

Nenhuma solicitação foi enviada às operadoras. Os arquivos de pesquisa e relatórios ficam em `../outputs/calibracao-oficial-20261101` em relação à raiz deste worktree, fora dos arquivos de execução da aplicação. O utilitário `scripts/auditar_gtfs_ferroviario.py` permite repetir a inspeção de um ZIP local sem acessar ou alterar o Xano.
