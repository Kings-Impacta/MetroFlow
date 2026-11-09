# Cobertura numérica dos tempos — 04/11/2026

Trabalho exclusivamente local. Nenhuma alteração no Xano, publicação, commit ou aplicação da margem. A Linha 6 permanece fora desta entrega.

## Estimativas preservadas

Os 178 sentidos restantes receberam candidatos: Linha 7 (32), Linha 8 (38), Linha 9 (40), Linha 10 (28), Linha 11 (2), Linha 12 (24) e Linha 17 (14). Somados aos 229 anteriores, são **407 sentidos com modelos numéricos**, sem aprovação automática para operação. Dados e hipóteses estão em `docs/dados/tempos/estimativas-sentidos-restantes.json`; o gerador é `scripts/estimar_sentidos_restantes.py`.

- Linha 12: [apresentação técnica da CPTM](https://anptrilhos.org.br/wp-content/uploads/2020/11/melhores-praticas-anptrilhos-2020-cptm-sergio-barbosa.pdf), tabela de junho de 2020 por intervalo, nos dois sentidos, total de 53 minutos. É referência histórica ao minuto, não medição de 2026.
- Linhas 8/9: [auditoria do TCE](https://www.tce.sp.gov.br/sites/default/files/portal/6.%20Fiscaliza%C3%A7%C3%A3o%20Operacional%20-%20Transporte%20sobre%20Trilhos%20-%20TC-021575.989.23-1.pdf), quadro 5: programação histórica de 53 minutos Júlio Prestes–Itapevi e 45 minutos Osasco–Grajaú. A auditoria critica inconsistências e mudanças de programação. Os valores posteriores de 65/60 minutos ficam como referência de sensibilidade, sem atribuição automática a outros terminais. A extensão até Varginha foi modelada separadamente; 45 minutos não foram atribuídos ao trajeto completo atual.
- Linha 10: [declaração atribuída à CPTM em 2022](https://www.abcdoabc.com.br/linha-10-turquesa-tera-novas-alteracoes-a-partir-desta-terca-feira-13/) sustenta cenário histórico de 43 minutos no núcleo Brás–Rio Grande da Serra. A extensão até Barra Funda usa estimativas separadas. Não é cronometragem atual.
- Linha 7: cenário físico de 57 km a 40 km/h assumidos, total 85min30s, distribuído geograficamente. Os 61 minutos de projeto não foram tratados como observação atual. Não há validação de velocidade por trecho.
- Linha 17: cenário físico de 6,7 km a 35 km/h assumidos, inspirado em referência técnica de monotrilho, sem afirmar velocidade comercial medida da Linha 17. Os nove minutos divulgados de intervalo entre trens não foram confundidos com duração da viagem. Os 690 segundos somam todos os sete enlaces físicos, incluindo o ramal; não representam um itinerário único.

Nas distribuições agregadas, coordenadas não representam geometria exata da via. Simetria, arredondamentos e tempos de parada estão identificados como hipóteses. Todos os novos candidatos permanecem com confiança baixa e sem classificação de medição.

## Baldeações e esperas

O acervo passou de 76 para **320 combinações direcionais candidatas**. Os 128 pares do inventário têm cobertura numérica: 126 por combinações e dois por corredores a pé explícitos, sem penalidade duplicada de caminhada. O arquivo `cobertura-baldeacoes-modeladas.json` explicita essa distinção.

As combinações adicionais são inferidas pela topologia e pela classe da troca. Não são 320 plataformas inspecionadas ou conexões físicas confirmadas. As 405 possibilidades de espera continuam candidatas, com limitações de faixa, dia e serviço preservadas.

## Comparação local

Comparação com o candidato anterior desta mesma pesquisa, não com tempos medidos. Totais abaixo incluem esperas e trocas modeladas, sem o minuto de margem. Casos isolados por linha verificam o custo do corredor; não afirmam que ele seja sempre a melhor opção entre todas as linhas.

| Corredor | Antes | Depois |
|---|---:|---:|
| Jundiaí → Barra Funda, Linha 7 | 35min | 88min30s |
| Júlio Prestes → Itapevi, Linha 8 | 40min30s | 55min30s |
| Osasco → Varginha, Linha 9 | 42min | 54min55s |
| Barra Funda → Rio Grande da Serra, Linha 10 | 40min | 61min |
| Brás → Calmon Viana, Linha 12 | 26min15s | 55min15s |
| Morumbi → Congonhas, Linha 17 | 16min30s | 14min30s |

Essas diferenças mostram o efeito de substituir tempos uniformes; não comprovam maior precisão de cada hipótese. No ensaio de sensibilidade, Jandira → Paraíso permaneceu pelas linhas 8, 3 e 1, com troca em Barra Funda e Sé: 64min09s, 70min20s e 76min31s ao variar somente os novos custos em −15%, valor central e +15%. Essa faixa não abrange necessariamente toda a incerteza das fontes históricas.

Validação: 880 execuções gerais; 22 casos direcionados; 18 simulações de sensibilidade; regressões de Guaianases (32), linhas parciais (18) e exceções (16), todas aprovadas. Verificações incluem ausência de estações repetidas, consistência da soma, cobrança de espera por embarque e respeito às exceções exercitadas. Os hashes das tabelas de origem permaneceram iguais. Resultados detalhados ficam em `outputs/cobertura-407-20261104/`, na pasta superior ao repositório.

## Pendências para concluir a entrega

1. Selecionar os valores-base após confrontar hipóteses conflitantes e sensibilidade. A Linha 17 exige atenção: o candidato mais curto passa a permitir viagem às 21h45 perto do encerramento; isso valida a aritmética do cenário, não garante embarque real.
2. Completar a coerência operacional das esperas, especialmente atendimentos parciais das linhas 7/8/9, dias, feriados e alcance por estação. Não generalizar avisos de obras de um dia para a operação permanente.
3. Rever conexões inferidas e situações de acessibilidade por sentido; estimativas fundamentadas são aceitas, sem exigir comprovação documental integral.
4. Alinhar busca, registro automático da viagem e ocupação da concorrência. O contrato legado de registro não deve manter custos de espera/troca diferentes dos usados na busca.
5. Só após essa cobertura e as simulações finais, acrescentar **60 segundos uma vez no total**, manter “Tempo estimado” e aviso de variação externa, preparar backup e publicar os ajustes coerentes. Não somar margem a cada componente nem usá-la para deslocar partidas.

Preencher os 407 sentidos conclui a cobertura numérica do deslocamento; não encerra essas pendências operacionais nem autoriza publicação antecipada.
