# Exceções datadas e encerramento — 04/11/2026

Trabalho local, sem gravação no Xano, ativação do experimento, reinício da aplicação, commit ou publicação. Nenhum minuto de margem foi aplicado. A instrução mais recente autoriza tratar a Linha 6 depois de concluir a cobertura anterior; ela não foi incorporada antecipadamente.

## Decisões sobre frequências

As estimativas-base da etapa anterior permanecem selecionadas para o laboratório: Linha 9 integral com intervalo de sete minutos em dias úteis, 11h30–15h30, e dez minutos nas demais faixas/dias. São hipóteses apoiadas em referências datadas e extrapolações identificadas, não uma grade atual medida. Não se exige documentação integral para usá-las como estimativas, mas tampouco se afirma precisão que as fontes não oferecem.

O [comunicado oficial de Finados](https://trilhos.motiva.com.br/linha-4-amarela/noticias/2026/outubro/motiva-trilhos-anuncia-operacao-especial-para-feriado-de-finados/) confirma a oferta das linhas 5/8/9 semelhante à de domingo em 02/11/2026. Não informa numericamente o intervalo da Linha 9; por isso não foi usado para atribuir caráter oficial aos dez minutos candidatos. O calendário da cópia já tratava a data como domingo/feriado, sem mudança de tempo nesse caso.

## Exceções executáveis na cópia

`docs/dados/tempos/excecoes-operacionais-candidatas.json` guarda início/fim absolutos, fonte, frequência e alcance. O novo `scripts/candidato_excecoes_operacionais.py` transforma somente a função copiada, mediante opção explícita do simulador.

| Data e faixa | Integral que atravessa o trecho afetado | Agregado limitado |
|---|---|---|
| 08/05, 12h30–15h | Intervalo candidato de 12 min | Osasco–Socorro, 6 min |
| 20/05, 11h30–15h30 | Intervalo candidato de 14 min | Osasco–Socorro, 7 min |
| 03/10, 21h até 04/10, 07h | Intervalo candidato de 20 min | Osasco–Jurubatuba, 10 min |

Fontes: [ViaMobilidade, 08/05](https://trilhos.motiva.com.br/viamobilidade8e9/noticias/2026/maio/viamobilidade-realiza-manutencoes-nas-linhas-8-e-9/), [20/05](https://trilhos.motiva.com.br/viamobilidade8e9/noticias/2026/maio/confira-as-manutencoes-programadas-nas-linhas-8-diamante-e-9-esm/) e [programação de 28/09 a 05/10](https://trilhos.motiva.com.br/viamobilidade8e9/noticias/2026/setembro/confira-as-manutencoes-programadas-das-linhas-8--diamante-e-9-es/).

O integral modela quem precisa atravessar a região de menor frequência. O agregado permite usar a frequência melhor somente até seu limite; não promete permanecer no mesmo trem até Varginha. Não é uma lista de partidas individuais nem prova de que cada trem termina no limite do agregado. No modelo, embarcar no agregado e depois prosseguir em outro padrão exige outra espera e troca estimada.

A regra verifica a data também no embarque calculado: começar a esperar antes da obra não permite reaproveitar uma frequência normal quando o embarque estimado já está dentro da exceção. Quem já está embarcado não recebe nova espera ao atravessar a faixa. A última espera iniciada durante a exceção pode avançar além de seu fim; é uma estimativa conservadora, sem fases individuais de partidas. Novos embarques após o fim voltam ao perfil normal. O período noturno de obra não abre estações por suposição: a abertura comercial original continua sendo exigida.

Essas três exceções são referências históricas simuladas. Não constituem calendário completo de todas as obras/incidentes, nem regras permanentes para os fins de semana futuros.

## Linha 17 perto do encerramento

A [página oficial de horários](https://www.metro.sp.gov.br/sua-viagem/horarios/) confirma funcionamento transitório de segunda a sábado, 06h–22h. O [comunicado de 01/10](https://www.metro.sp.gov.br/2026/10/01/linha-17-ouro-transporta-mais-de-25-mil-passageiros-no-primeiro-dia-com-horario-ampliado/) informa intervalo inferior a nove minutos. Nove minutos continua como intervalo candidato conservador; não foi convertido em grade de partidas a partir das 06h. Não foi localizada passagem do último trem por estação.

Decisão local: manter o cálculo nominal já existente e seu limite de chegada até 22h. Quando o mesmo percurso ultrapassaria o fechamento em uma sensibilidade com espera completa de nove minutos por novo embarque e deslocamento 20% mais lento, acrescentar aviso para confirmar o último trem na estação. Essa sensibilidade é uma hipótese de avaliação, não medição nem regra oficial de último embarque.

O aviso não aumenta o tempo informado, não altera o registro ou a ocupação e não aplica margem por trecho. Não há um corte universal às 21h45: sentido, percurso e troca no ramal são avaliados. Domingos continuam indisponíveis na cópia. Feriados de segunda a sábado seguem a disponibilidade já cadastrada, sem afirmação de calendário especial completo do operador.

## Antes e depois

Comparação contra o candidato da etapa anterior, em cópias locais. Tempos estimados, sem margem final:

| Consulta | Antes | Depois |
|---|---:|---:|
| Osasco → Varginha, 08/05 às 13h | 56min25s | 58min55s |
| Osasco → Varginha, 20/05 às 12h10 | 56min25s | 59min55s |
| Osasco → Varginha, 04/10 às 06h | 57min55s | 62min55s |
| Osasco → Socorro, 08/05 às 13h | 35min55s | 35min25s |
| Morumbi → Congonhas, dia útil às 21h45 | 14min30s | 14min30s, com aviso |
| Morumbi → Congonhas, dia útil às 21h50 | Sem rota nominal | Sem rota nominal |
| Morumbi → Washington Luís, às 21h30 | 23min20s | 23min20s, com aviso |

Os resultados após o fim das exceções e em um dia normal de novembro mantêm o perfil normal. Não se generalizaram aumentos de obras passadas para a operação atual.

## Verificação

- 880 execuções gerais de busca/concorrência; sem ciclos e sem os desvios excessivos verificados pelo auditor. Os hashes das tabelas de origem permaneceram iguais.
- 42 casos direcionados aprovados: datas, alcance, sentidos, início/fim, embarque atravessando a mudança, sábado, domingo, feriado e ramal.
- 35 viagens disponíveis tiveram registro reproduzido com fim de janela igual à busca. As 35 respostas passaram pela normalização e pelo contrato público local, preservando avisos.
- 24 regressões de frequência por dia/faixa, com 24 registros alinhados, aprovadas.

Resultados em `outputs/excecoes-encerramento-20261104/`, na pasta superior ao repositório. Geradores: `scripts/simular_estimativas_lacunas.py` com `--excecoes-operacionais`, `scripts/gerar_registro_calibrado.py`. Verificação específica: `scripts/validar_excecoes_operacionais.py`. A opção de exceções exige também preparação de esperas/baldeações e frequências por dia.

## Cobertura que permanece pendente

Esta etapa define como usar as estimativas selecionadas e como tratar as exceções conhecidas e a incerteza do último trem; não declara cobertura operacional global concluída. Permanecem conexões inferidas por plataforma/sentido, acessibilidade, demais calendários de exceção e simulação final integrada da entrega. Dados melhores de frequência e partidas podem substituir as hipóteses preservadas, sem tornar comprovação documental integral um requisito novo.

Publicação, margem única de 60 segundos no total e avanço da Linha 6 continuam sujeitos à ordem solicitada: concluir a cobertura anterior primeiro. Nada foi alterado no Xano.
