# Linhas adicionais, alcance dos trens e integrações

Continuação em 04/11/2026, somente local. Nenhuma alteração no Xano, nenhuma margem aplicada, nenhum commit ou envio. Linha 6 permanece fora desta etapa.

## Percursos adicionais preservados

Foram acrescentados 50 sentidos candidatos em `docs/dados/tempos/estimativas-linhas-adicionais.json`:

- Linha 11: 30 sentidos entre Luz e Estudantes, preservando o total histórico de 63 minutos anunciado pela CPTM em 2022. A extensão Barra Funda–Luz fica fora dessa âncora. Fontes: [histórico da operadora](https://www.cptm.sp.gov.br/cptm/Institucional/nossa-historia/) e [comunicado de aniversário de 2022](https://cptm.sp.gov.br/noticias/Pages/CPTM-completa-30-anos-com-conquistas-e-projetos-para-o-futuro.aspx).
- Linha 15: 20 sentidos entre Vila Prudente e Jardim Colonial, com âncora modelada de 1.490 segundos: extensão de 14,5 km dividida pela velocidade comercial de projeto de 35 km/h e arredondada a cinco segundos. Fontes: [características de projeto](https://www.metro.sp.gov.br/obras/linha-15-prata/caracteristicas/) e [relatório integrado de 2024](https://ri.metrosp.com.br/wp-content/uploads/2025/03/RI-2024-Metro-de-Sao-Paulo.pdf).

Ambos são cenários, não medições atuais. O gerador associa as estações à sequência ferroviária do GTFS, calcula distância geodésica entre elas e distribui o total com uma parcela fixa de 20 segundos e o saldo proporcional à distância. A parcela é parâmetro de distribuição, não parada cronometrada; não aumenta o total. Há arredondamento a cinco segundos com preservação da soma. Curvas de via, manobras, aceleração e diferenças de sentido ainda não foram medidas. A simetria é hipótese explícita.

O corredor Paulista → Consolação também recebeu cenário completo de cinco minutos, coerente com o candidato inverso. O segmento de vídeo de 215 segundos começa com a caminhada em andamento; não foi reinterpretado como medição completa. O inventário agora distingue **73 sentidos com candidatos modelados e 334 com referências ainda a avaliar**, entre 407 sentidos. Referência ou candidato não equivale a aprovação operacional.

## Linha 10: ordem física e padrões

A associação de estações da cópia coloca Brás–Rio Grande da Serra nas posições 1–13, Luz em 14 e Barra Funda em 15. Usar diretamente a diferença dessas posições troca a identificação do sentido em Brás numa viagem contínua. O candidato resolve a ordem física localmente: Barra Funda → Luz → Brás → … → Mauá → … → Rio Grande da Serra. O cadastro remoto permanece intacto.

`padroes-l10-candidatos.json` preserva fonte, caminho e limitações. Com o [quadro oficial de intervalos](https://www.cptm.sp.gov.br/dx/api/dam/v1/collections/05321fd9-3791-4689-a8ac-9e2adde39c4b/items/b6e68f57-4f4f-444d-b483-075f910e2c1b/renditions/4298df26-497c-47fd-a480-0b1812d6bb66?binary=true), já guardado no acervo:

- O serviço integral usa 12 minutos de intervalo no pico, com espera média de seis minutos.
- Uma opção agregada até Mauá usa seis minutos de intervalo, com espera média de três minutos. Ela representa os trens disponíveis no tronco; não afirma que todo trem termina em Mauá. O sentido informa “Mauá ou Rio Grande da Serra”.
- O agregado não pode continuar automaticamente além de Mauá. Prosseguir exige novo embarque com custo candidato de troca de cinco minutos e espera do integral; a busca também considera embarcar diretamente no integral desde o começo.
- A opção agregada só admite novo embarque no pico útil, excluindo feriados. A disponibilidade é verificada também depois da espera: uma consulta às 08h29 não promete embarque agregado às 08h32, depois do fim da faixa.
- Permanecer no mesmo perfil não cobra espera em cada estação, nem em Brás. Um trem já embarcado não desaparece quando termina a faixa de pico.

Isso é um modelo de alcance e frequência média. Não há grade individual ou fase conhecida de alternância dos trens. Não se pode afirmar qual composição será a próxima. A mudança de padrão e suas instruções ainda precisam integrar o contrato de busca e registro antes de publicar.

## Esperas e baldeações

O [quadro oficial da Linha 12](https://www.cptm.sp.gov.br/dx/api/dam/v1/collections/05321fd9-3791-4689-a8ac-9e2adde39c4b/items/6b5636e0-3384-43bf-8941-6d1f8e43b8e3/renditions/aa6a03df-e9fc-4190-89db-e4a8781b8555?binary=true) substitui no ensaio a repetição diária do GTFS por faixas próprias de dias úteis, sábados, domingos e feriados. São intervalos programados, sem data de vigência explícita extraída. Os valores e sua origem estão em `referencias-intervalos.json` e `esperas-candidatas.json`.

`plataformas-candidatas.json` passou de oito para 20 combinações: oito em Paraíso, oito em Ana Rosa e quatro de Amarela para Vermelha em República. Em Ana Rosa, mantêm-se três minutos do modelo anterior, agora por sentido, com apoio da [descrição oficial de plataformas centrais e mezanino](https://www.metro.sp.gov.br/sua-viagem/linhas-estacoes/linha-1-azul/estacao-ana-rosa/). Em República, o cenário de 150 segundos usa o marco histórico de vídeo de 105 segundos como referência e admite circulação adicional; não é medição de quatro plataformas. [Metrô](https://www.metro.sp.gov.br/sua-viagem/linhas-estacoes/linha-3-vermelha/estacao-republica/) e [Motiva](https://trilhos.motiva.com.br/linha-4-amarela/estacoes/republica/) confirmam a integração e a geometria geral. O sentido inverso conserva o modelo anterior.

Paulista–Consolação já é uma aresta de caminhada. No candidato, essa caminhada conta uma vez; foi retirada a penalidade genérica adicional na sua entrada/saída. A espera do trem seguinte continua separada. A quantidade e a lista de baldeações continuam registrando a troca mesmo quando a penalidade adicional é zero, para não apagar a instrução ao passageiro. O total de caminhada não pode ser confundido com o minuto de margem, ainda não aplicado.

## Comparação com o candidato anterior

Antes: `../outputs/excecoes-plataformas-20261104/candidato`. Depois: `../outputs/linhas-parciais-final-20261104/candidato`. Tempos abaixo são totais do modelo, incluindo esperas, sem margem. Linhas isoladas nos testes de alcance; não representam obrigatoriamente a melhor rota da rede inteira.

| Consulta | Antes | Depois |
|---|---:|---:|
| Barra Funda → Mauá, pico | 40 min | 31 min |
| Barra Funda → Rio Grande da Serra, pico | 46 min | 40 min |
| Mauá → Rio Grande da Serra, pico | 12 min | 12 min |
| Barra Funda → Mauá, entrepico | 36 min | 32 min |
| Oscar Freire → Brigadeiro, por Paulista–Consolação | 21min30s | 13min30s |
| Brigadeiro → Oscar Freire, pelo corredor | 23min30s | 13min30s |
| Luz → Estudantes, somente Linha 11 | 33min30s | 66min30s |
| Vila Prudente → Jardim Colonial, somente Linha 15 | 27min30s | 32min20s |
| Brás → Tatuapé, somente Linha 12, domingo | 5 min | 19min30s |

A redução da Linha 10 decorre também de eliminar uma espera artificial em Brás, não de uma nova medição da velocidade do trem. O aumento da Linha 11 corrige a comparação exploratória que usava dois minutos iguais em quase todos os intervalos; o total de 63 minutos é histórico. Na Linha 15, 24min50s são deslocamento modelado e 7min30s são a espera mantida neste horário. Essa espera ainda precisa de calibração própria.

Validação: 880 execuções amplas antes/depois, com 214 buscas e 120 cenários de concorrência alterados; sem ciclos nem desvios acima do dobro no conjunto exercitado. Foram acrescentados 18 testes direcionados de Linha 10, fim do pico, corredor, âncoras das linhas 11/15 e perfis da Linha 12. A revisão de 16 exceções anterior também foi executada no candidato. Esses números não comprovam precisão real de todas as durações.

## O que permanece pendente

Tempos específicos das linhas 1, 2, 3, 4, 5, 7, 8-tronco, 9, 10 e 12 ainda exigem estimativas mais bem ancoradas; referências uniformes não foram adotadas em massa. O modelo da Linha 11 precisa incorporar o alcance dos parciais até Guaianases, identificado no quadro oficial e preservado em `fontes-adicionais.csv`. As seis combinações de Paraíso ainda conservam custo genérico. Demais integrações, acessibilidade e faixas sem perfil próprio continuam abertas.

Foi guardado também o RAP da Linha 5: seu quadro de 33min40s inclui **Jardim Ângela**, portanto não foi usado como duração da linha atual Capão Redondo–Chácara Klabin. Dados de extensão futura e ocorrências pontuais não foram convertidos em tempos atuais.

Busca, cronologia de ocupação e registro precisam compartilhar os padrões e custos antes de publicação. Cobertura operacional continua incompleta. Somente após completar a cobertura e simular será acrescentado um minuto uma única vez ao total, preservando “Tempo estimado” e a indicação de variação por condições externas.
