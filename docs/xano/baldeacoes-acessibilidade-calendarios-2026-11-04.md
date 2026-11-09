# Baldeações, acessibilidade e calendários — 04/11/2026

Continuação local de `excecoes-e-encerramento-2026-11-04.md`. Nenhuma gravação no Xano, publicação ou commit. O cenário experimental permanece separado do uso normal; a margem de um minuto continua sem aplicação. Linha 6 somente após concluir a cobertura anterior.

## Acervo ampliado

`docs/dados/tempos/baldeacoes-acessibilidade-candidatas.json` preserva as **320 combinações direcionais**, dois corredores a pé e referências de infraestrutura para **27 estações de integração**. O inventário anterior de 128 pares continua como referência, sem reinterpretá-lo como 128 conexões físicas certificadas.

As páginas específicas de sete estações foram associadas ao acervo: Pinheiros, Osasco, Presidente Altino, Santo Amaro, Barra Funda, Brás e Tamanduateí. As demais entradas conservam referências gerais, sem presumir que uma descrição da rede confirme o percurso exato da baldeação. Todas mantêm disponibilidade dos equipamentos desconhecida e percurso autônomo não validado.

Fontes relevantes: [Pinheiros, Linha 4](https://trilhos.motiva.com.br/linha-4-amarela/estacoes/pinheiros/), [Pinheiros, Linha 9](https://trilhos.motiva.com.br/viamobilidade8e9/linha-9---esmeralda/pinheiros/), [Osasco](https://trilhos.motiva.com.br/viamobilidade8e9/linha-9---esmeralda/osasco/), [Presidente Altino](https://trilhos.motiva.com.br/viamobilidade8e9/linha-9---esmeralda/presidente-altino/), [Barra Funda](https://www.cptm.sp.gov.br/cptm/sua-viagem/linhas-e-estacoes/barra_funda), [Brás](https://www.cptm.sp.gov.br/cptm/sua-viagem/linhas-e-estacoes/bras) e [Tamanduateí](https://www.cptm.sp.gov.br/cptm/sua-viagem/linhas-e-estacoes/tamanduatei).

A [TIC informa adequações de acessibilidade](https://www.tictrens.com.br/sua-viagem/acessibilidade) em Campo Limpo Paulista, Perus, Várzea Paulista, Botujuru, Caieiras, Vila Clarice e Pirituba, além de atendimento assistido e táxi acessível nas estações sem acessibilidade. A lista de obras, isoladamente, não prova ausência de todos os recursos em cada estação. O modelo emite aviso para confirmar o acesso e não inventa duração fixa de táxi ou o representa como viagem ferroviária.

## Cenário de deslocamento com mobilidade reduzida

Foram guardados dois valores por combinação: tempo-base anterior e cenário de circulação mais lenta/assistida. A hipótese deste segundo cenário é 1,5 vez o tempo-base, com 120 segundos para dois movimentos assistidos presumidos de 60 segundos quando a mudança de nível é modelada. A hipótese é arredondada a 15 segundos. Em combinações curtas de plataforma, não se presume essa espera vertical adicional.

Esses parâmetros não são tempos medidos nem inventário de elevadores por plataforma. São um cenário de sensibilidade para comparar percursos; não certificam uma rota acessível. Não incluem acesso desde a rua nem saída final. A espera do trem continua calculada separadamente.

**Não é margem de erro por baldeação.** O minuto solicitado pelo usuário continua reservado uma única vez ao total, ainda não aplicado. O cenário assistido muda a estimativa física de circulação. Exemplos: plataforma candidata de 60 s passa a 90 s; troca-base de 300 s passa a 570 s; Pinheiros com base de 480 s passa a 840 s. O corredor Paulista–Consolação recebe o tempo estimado no próprio trecho a pé, sem outra penalidade de transferência na fronteira.

As versões dos cenários padrão e assistido são distintas. O registro recalcula o mesmo cenário da busca e preserva início de passagem e fim de janela. Nenhuma opção nova foi ativada na interface em execução.

## Calendários e plataformas

O [comunicado oficial da CPTM sobre Finados](https://www.cptm.sp.gov.br/cptm/!ut/p/z0/04_Sj9CPykssy0xPLMnMz0vMAfIjo8ziDSzMTIyM3Q2MPVz9XQzMQkMMg9xcjEICfc31gzOK9AuyHRUBqOhUBQ!!/?1dmy=&urile=wcm%3Apath%3A%2Fwcm%2Fconnect%2Fcptm_content%2Fcptm%2Fnoticias%2Fcptm-tera-alteracoes-na-circulacao-de-trens-no-feriado-prolongado-de-finados) acrescentou dois bloqueios à cópia:

| Data | Trecho | Regra local |
|---|---|---|
| 31/10, 08h–18h | Linha 10, Barra Funda–Luz | Bloquear passagem nos dois sentidos durante a intervenção |
| 02/11, 09h–16h | Linha 11, Tatuapé–Corinthians-Itaquera | Bloquear passagem e comparar alternativas, incluindo Linha 3 |

A verificação usa o intervalo previsto de passagem, não apenas o horário em que a consulta começou. Assim, uma busca às 08h59 não atravessa um trecho que estará fechado às 09h. Depois do fim, o trecho volta a ser oferecido. Não foi criada uma aresta fictícia de PAESE.

No primeiro evento, a fonte prevê alternância nas plataformas 6/7 para facilitar a conexão de quem chega pela Linha 7. Foi preservada uma hipótese de 120 segundos de circulação **somente** na combinação Água Branca → Barra Funda → Luz, das linhas 7 para 11, durante aquela janela. O sentido inverso e outras datas mantêm o modelo anterior. O passageiro deve confirmar a plataforma nos avisos; a alternância não garante o mesmo embarque em todas as composições.

Mudanças de plataforma em Tamanduateí, Ipiranga e Tatuapé foram guardadas como referências datadas, sem inventar duração específica onde o percurso não foi identificado. As regras estão em `calendario-baldeacoes-candidato.json`.

Também foi explicitada a restrição noturna de transferência entre metrô e outras operadoras: a operação piloto de quatro linhas não abre automaticamente seus bloqueios de integração na madrugada. A [página oficial de horários](https://www.metro.sp.gov.br/sua-viagem/horarios/) distingue funcionamento da estação e horário de transferência; o piloto permanece restrito às linhas e vigência já modeladas. O [comunicado de 29/10](https://www.metro.sp.gov.br/2026/10/29/veja-como-vai-funcionar-o-metro-durante-o-feriado-prolongado/) confirma oferta de dia útil no ponto facultativo de 30/10 e a operação de Finados; ponto facultativo não virou feriado automaticamente.

## Antes e depois

Tempos estimados, sem margem, comparados à etapa anterior. O cenário assistido representa outra hipótese de circulação, não uma correção da velocidade de todos os passageiros.

| Consulta | Antes | Padrão com calendário | Cenário assistido |
|---|---:|---:|---:|
| Brás → Estudantes, Finados às 10h | 77min30s | 92min, linhas 3 e 11 | 96min30s |
| Perus → Luz, 31/10 às 10h | 56min05s | 51min05s, linhas 7 e 11 | 52min05s |
| Pinheiros → Paraíso, dia útil às 07h30 | 21min50s | 21min50s | 26min20s |
| Paulista → Brigadeiro, dia útil às 07h30 | 9min15s | 9min15s | 13min45s |
| Perus → Luz, dia útil às 07h30 | 51min50s | 51min50s | 57min20s |

A primeira linha passa a contornar a interdição em vez de indicar o trecho fechado. A segunda usa a conexão por plataforma programada naquela data. O cenário que envolve Perus inclui aviso de necessidade de confirmar condições de acesso/apoio.

## Correção do validador local

As novas comparações revelaram que corredor a pé e trem com a mesma identificação de linha podiam ter padrões técnicos diferentes e gerar uma baldeação duplicada no domínio. `requires_train_change` agora preserva a ausência de troca adicional nesse caso, sem deixar de contar mudança real entre linhas ou trens parciais. Um teste de regressão cobre o corredor seguido de trem da Linha 4.

## Verificações

- 640 verificações de custo: 320 combinações reais de arestas em cada perfil, além da combinação datada de Barra Funda.
- 58 comparações de rota, com trechos isolados interditados e alternativas na rede, nos dois sentidos.
- 46 viagens disponíveis com resposta normalizada e registro alinhado; versões diferentes para os dois cenários.
- Oito cenários de concorrência com dois usuários simulados, mantendo exclusão da própria viagem e limites de tempo/trocas.
- 53 testes unitários aprovados, com 13 subtestes, incluindo o novo caso do corredor.
- 42 regressões das exceções anteriores, 35 registros e respostas normalizados, aprovados no cenário padrão.
- Auditoria geral: 880 execuções no padrão e 876 no cenário assistido, sem ciclos e sem os desvios excessivos verificados. A diferença de quatro execuções ocorre porque Barra Funda–Aeroporto passa a escolher somente serviço especial no cenário assistido; não há trecho regular a sobrecarregar nesses quatro ensaios. O comparador foi corrigido para casar consultas por par e ocorrência, sem deslocar a comparação quando essa quantidade muda.

Resultados em `outputs/baldeacoes-calendarios-20261104/` e `outputs/mobilidade-calendarios-20261104/`, na pasta superior ao repositório. Scripts: `estimar_baldeacoes_acessibilidade.py`, `candidato_baldeacoes_calendarios.py` e `validar_baldeacoes_calendarios.py`. Tabelas de origem preservadas por hash; nenhum script desta etapa grava no Xano.

## O que permanece aberto

Há cobertura numérica dos candidatos estudados, mas ainda não validação física de todos os percursos de integração. Vinte das 27 estações deste inventário têm apenas referência geral associada; a existência de uma página específica nas outras sete também não confirma a ligação completa entre plataformas. Disponibilidade de elevadores, acesso autônomo e tempos desde a rua/até a saída continuam desconhecidos. O calendário de eventos conhecido não cobre incidentes futuros.

Esses limites ficam registrados em vez de serem convertidos em tempos zero ou promessas de acessibilidade. Para a entrega, ainda falta decidir o tratamento operacional desses casos e realizar a revisão integrada final antes de publicar. Linha 6 segue condicionada à conclusão dessa cobertura anterior; nenhuma aprovação de publicação é presumida.
