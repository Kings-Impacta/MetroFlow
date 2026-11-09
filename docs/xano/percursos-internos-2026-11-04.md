# Percursos internos das baldeações — 04/11/2026

Diretriz incorporada: o funcionamento dos elevadores é informação adicional e **não bloqueia a cobertura dos trajetos**. O foco é o caminho entre plataformas/linhas e seu tempo estimado. Não houve gravação no Xano, publicação, commit ou aplicação da margem de um minuto.

## Cobertura numérica revisada

`docs/dados/tempos/percursos-internos-candidatos.json` guarda as 320 combinações por linha, sentido de chegada, sentido de saída e estações adjacentes, além dos dois corredores Paulista–Consolação. Abrange 27 estações de integração. Todas receberam um modelo de percurso interno; 106 tiveram seu valor numérico revisto, preservando o valor anterior. Não se afirma levantamento físico integral ou cronometragem atual de cada combinação.

A revisão distingue circulação ferroviária no mesmo complexo, conexão trem–metrô, ligação profunda por distribuidor, combinação candidata de plataforma compartilhada e corredor explícito a pé. Onde faltam medições, os componentes continuam hipóteses de desembarque/orientação, circulação e mudança de nível. Não são tempos de espera pelo trem nem margem de erro por componente.

| Ligação candidata | Antes | Novo modelo |
|---|---:|---:|
| Barra Funda, trens metropolitanos entre si | 7 min | 3 min: 30 s de orientação + 90 s de circulação + 60 s de distribuição |
| Barra Funda, trem–Linha 3 | 7 min | 5 min: 60 s + 150 s + 90 s |
| Brás/Luz, trens metropolitanos entre si | 7 min | 4 min: 60 s + 90 s + 90 s |
| Linha 10–Expresso Linha 10 no mesmo complexo, em Santo André/São Caetano/Tamanduateí | 7/5 min | 3 min: 30 s + 90 s + 60 s |

Os componentes são estimativas de circulação, sem afirmar distância medida ou plataforma exata. Não foi aplicada uma redução geral a toda troca: ligações profundas ao metrô, corredores longos e ramais preservam seu tratamento. A configuração temporária de plataforma em Barra Funda mantém precedência sobre o modelo permanente.

## Fontes e decisões de percurso

- [Barra Funda, Metrô](https://www.metro.sp.gov.br/sua-viagem/linhas-estacoes/linha-3-vermelha/estacao-barra-funda/): mezanino sobre plataformas em superfície. Isso fundamenta distinguir transferência ferroviária interna da ligação ao metrô, sem fornecer duração medida.
- [Brás, CPTM](https://www.cptm.sp.gov.br/cptm/noticias/estacao-bras-recebe-atendimentos-gratuitos-de-orientacao-sobre-educacao-financeira): confirma a existência do mezanino ferroviário, não a distância entre todos os pares de plataformas.
- [Luz, Linha 4](https://trilhos.motiva.com.br/linha-4-amarela/estacoes/luz/) e [Pinheiros, Linha 4](https://trilhos.motiva.com.br/linha-4-amarela/estacoes/pinheiros/): geometrias profundas; a circulação ferroviária não foi confundida com a conexão subterrânea. A profundidade não foi transformada diretamente em tempo ou distância de caminhada.
- [Paraíso](https://www.metro.sp.gov.br/sua-viagem/linhas-estacoes/linha-1-azul/estacao-paraiso/) e [Ana Rosa](https://www.metro.sp.gov.br/sua-viagem/linhas-estacoes/linha-1-azul/estacao-ana-rosa/): distribuição por plataformas e níveis. Em Paraíso, as duas combinações candidatas rápidas anteriores foram preservadas; não se estendeu essa vantagem às outras seis. Ana Rosa mantém o modelo via distribuidor.
- [Chácara Klabin, Linha 2](https://www.metro.sp.gov.br/sua-viagem/linhas-estacoes/linha-2-verde/estacao-chacara-klabin/), [Chácara Klabin, Linha 5](https://trilhos.motiva.com.br/linha-5-lilas/estacoes/chacara-klabin/) e [Santa Cruz](https://trilhos.motiva.com.br/linha-5-lilas/estacoes/santa-cruz/): integração confirmada. Sem nova medida de percurso, conservaram-se as estimativas, em vez de reduzi-las só pela existência da ligação.
- [Santo Amaro, maio de 2025](https://diariodotransporte.com.br/2025/05/13/viamobilidade-inicia-testes-da-nova-passarela-entre-as-linhas-5-lilas-e-9-esmeralda-em-santo-amaro/): referência útil de nova passarela com liberação parcial no sentido Chácara Klabin. Foi guardada sem generalizar sua vigência e configuração para os dois sentidos.

O acervo anterior, inclusive relatos e vídeos parciais, permanece preservado. As páginas e descrições arquitetônicas não foram apresentadas como medições de baldeação. Estado de equipamentos não participa da seleção de tempo desta etapa.

## Simulações antes e depois

Comparação contra o candidato da etapa de baldeações/calendários. Dia útil, 07h30; tempos estimados sem margem:

| Consulta | Antes | Depois | Caminho selecionado depois |
|---|---:|---:|---|
| Jandira → Paraíso | 72min50s | 70min50s | Linha 8 → Linha 3 → Linha 1 |
| Luz → Jandira | 63min20s | 59min20s | Linha 11 → Linha 8 |
| Perus → Luz | 51min50s | 47min50s | Linha 7 → Linha 11 |
| Barra Funda → Paraíso | 19min15s | 19min15s | Linha 3 → Linha 1 |
| Mauá → Paraíso | 45min05s | 45min05s | Linha 10 → Linha 2 |

Os três corredores alternativos solicitados também foram simulados separadamente, com as mesmas estimativas e disponibilidade:

| Origem → Paraíso | Vermelha–Azul | Vermelha–Amarela–Verde | Via Pinheiros–Amarela–Verde |
|---|---:|---:|---:|
| Jandira | 70min50s | 79min20s | 79min20s |
| Barra Funda | 19min15s | 27min45s | 66min25s |

Partindo de Barra Funda, a terceira opção inclui retornar pela Linha 8 para alcançar a Linha 9, o que explica a diferença nesse caso. Ela é mais pertinente para quem já vem pela Linha 8 antes de chegar a Barra Funda. As alternativas não foram proibidas nem escolhidas pelo número de estações; participam da comparação por tempo total. Os valores deste cenário não afirmam qual caminho será mais rápido em toda situação real.

Na concorrência simulada, uma consulta no sentido Paraíso → Jandira aceitou alternativa de 78min50s para um principal de 70min50s, dentro dos limites existentes. Outros casos mantiveram o principal quando não havia desvio adequado. Não se força uma troca só porque duas pessoas consultaram.

## Verificações

- 880 execuções gerais; sem ciclos e sem os desvios excessivos verificados pelo auditor; tabelas de origem preservadas por hash.
- 640 verificações de custo: todas as 320 combinações, antes e depois.
- Duas verificações adicionais da precedência da plataforma temporária de Barra Funda e de seu término.
- 28 comparações de rota, 28 respostas normalizadas e 28 registros com fim de janela igual ao tempo da busca.
- Oito cenários de concorrência com usuários simulados distintos, exclusão da própria viagem e limites de tempo/trocas.
- 42 regressões das exceções anteriores, com 35 viagens disponíveis normalizadas e registradas, aprovadas.

Artefatos em `outputs/percursos-internos-20261104/`, na pasta superior ao repositório. Dados gerados por `scripts/estimar_percursos_internos.py`; aplicação exclusivamente na cópia por `scripts/candidato_percursos_internos.py`; comparação por `scripts/validar_percursos_internos.py`.

## Linha 6: levantamento iniciado depois da cobertura numérica anterior

Foi iniciado o levantamento oficial, guardado em `docs/dados/tempos/linha6-levantamento-inicial.json`. A [LinhaUni](https://www.linhauni.com.br/linha-6-laranja?unidade-construtiva=estacao-brasilandia) apresenta 15 estações projetadas, 15,3 km e duração anunciada de 23 minutos para o projeto completo. Foram preservados os 14 intervalos e as três conexões projetadas, sem inventar tempos atuais dividindo os 23 minutos igualmente.

As [perguntas frequentes](https://www.linhauni.com.br/perguntas-frequentes) descrevem previsão de entrega parcial em 2026 e total em 2027; o [comunicado de 03/11](https://www.linhauni.com.br/comunidade/desvio-de-trafego-estacao-joao-paulo-i-2812) ainda trata de obras e desvio viário. Essas fontes não estabeleceram, neste levantamento, alcance e horário de passageiros por trecho suficientes para inserir a linha nos itinerários atuais. O indicador genérico “Operação Encerrada” também não resolve essa questão.

Portanto, a pesquisa da Linha 6 começou, mas nenhuma conexão projetada foi liberada no grafo. O próximo passo dessa parte é separar o trecho efetivamente atendido ao passageiro do projeto futuro. A publicação conjunta da calibração e a aplicação do minuto final continuam sem execução, aguardando revisão integrada da entrega; funcionamento de elevadores não será usado como bloqueio dessa revisão.
