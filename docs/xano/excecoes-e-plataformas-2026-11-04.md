# Exceções de horários e plataformas — continuação local

Estado em 04/11/2026. Sem alteração no Xano, sem margem aplicada e com Linha 6 adiada. Este documento complementa o ensaio de 03/11; não substitui suas evidências nem aprova cobertura completa.

## Mudanças nos candidatos

**Operação noturna:** o modelo anterior reutilizava a frequência da última faixa diurna e podia deixar sem embarque o intervalo entre 04h e 04h40. O candidato passou a separar a madrugada de sábado para domingo, até 04h40, nas linhas do piloto. Usa intervalo estimado de 25 minutos, ponto médio dos 20–30 minutos divulgados na implantação, resultando em espera média de 12min30s por embarque. A abertura e o vencimento continuam limitados pelo calendário do helper, sem estender o piloto automaticamente.

A [prorrogação oficial de setembro de 2026](https://www.metro.sp.gov.br/2026/09/25/metro-estende-operacao-24-horas-nos-fins-de-semana-ate-janeiro-de-2027/) confirma as linhas e o término em 31/01/2027. A [publicação governamental de implantação](https://www.bibliotecajuridica.sp.gov.br/linha-operadas-pelo-metro-comecam-a-funcionar-24-horas-aos-sabados/) informa a faixa de intervalos. O valor de 25 minutos é uma aproximação, não medição atual. Dados e fontes ficam em `esperas-candidatas.json`, campo `madrugada_piloto`.

**Linha 13 regular:** quatro sentidos que somavam apenas quatro minutos por percurso completo no cadastro receberam um cenário de 17 minutos de deslocamento. O [documento de projeto da CPTM](https://www.cptm.sp.gov.br/a-companhia/obras-modern/Documents/Apresenta%C3%A7%C3%A3o%20Linha%2013%20-%20Completa.pdf), localizado no índice da busca, informa esse total estimado; a abertura direta redirecionou ao portal, portanto o documento integral e sua vigência não foram confirmados. A divisão candidata é 12 minutos Engenheiro Goulart–Cecap e cinco minutos Cecap–Aeroporto, com simetria assumida. É referência histórica de projeto, não tempo atual cronometrado. Não confundir duração do percurso com intervalo entre trens. Guardada em `estimativas-lacunas.json`, que agora contém 22 candidatos.

**Paraíso:** `plataformas-candidatas.json` distingue oito combinações de chegada/saída por sentido. Duas combinações recíprocas Jabaquara ↔ Vila Madalena usam caminhada candidata de 60 segundos no ensaio; as seis restantes conservam os 300 segundos anteriores enquanto se desdobra o percurso vertical. A [página oficial](https://www.metro.sp.gov.br/pt_BR/sua-viagem/linhas-estacoes/linha-1-azul/estacao-paraiso/) confirma a geometria geral e a integração; o [relato comunitário](https://www.reddit.com/r/saopaulo/comments/1df5exq) identifica a troca na mesma plataforma entre Azul sentido Jabaquara e Verde sentido Vila Madalena. Reciprocidade e duração são inferências explícitas. Não usar estes números como estimativa acessível validada. O código local lê as regras do arquivo, considerando linha e estação anterior e seguinte, sem reduzir todas as trocas de Paraíso.

## Antes e depois: testes direcionados

Comparação com o candidato combinado anterior de 03/11, sem margem:

| Consulta | Antes | Depois |
|---|---:|---:|
| Engenheiro Goulart → Aeroporto, útil 12h10 | 10 min | 23 min |
| Mesmo percurso, domingo/feriado 12h10 | 21min30s | 34min30s |
| Marechal Deodoro → Santa Cecília, domingo 02h | Frequência diurna reutilizada | 14min30s, incluindo 12min30s de espera |
| Mesmo percurso, domingo 04h10 | Sem resultado no candidato anterior | 14min30s |
| Vergueiro → Brigadeiro, útil 12h10 | 11 min | 7 min |

Vergueiro → Brigadeiro manteve a passagem por Paraíso, com espera total de dois minutos; só a caminhada candidata caiu de cinco para um minuto. Esses totais expressam o modelo, não garantias operacionais.

Passaram 16 testes direcionados: dias úteis, domingos e feriados na Linha 13; madrugada dentro e fora do piloto; piloto expirado; Linha 4 fechada à noite; grade dominical do Aeroporto sem inventar 13h30; feriado com grade horária conservada; Expresso L10 no pico e indisponível no entrepico, sábado e feriado; troca por sentido em Paraíso. Quinze testes isolam uma linha para verificar a regra sem mascará-la por uma rota alternativa; o caso de Paraíso pesquisa a malha inteira. Não interpretar indisponibilidade do serviço isolado como ausência de qualquer rota na rede.

Também foi repetida a comparação ampla de 880 execuções, incluindo concorrência, sem ciclos ou desvios acima do dobro nos casos exercitados. A contagem ampla e os testes específicos são conjuntos separados; os testes específicos cobrem mudanças que a amostra ampla não necessariamente exercita.

Reprodução: `scripts/estimar_lacunas_tempos.py`, `scripts/estimar_esperas_baldeacoes.py`, `scripts/mapear_cobertura_tempos.py`, `scripts/simular_estimativas_lacunas.py --incluir-esperas-baldeacoes`, `scripts/validar_excecoes_calibracao.py`. Artefatos finais em `../outputs/excecoes-plataformas-20261104/`, relativo à raiz de trabalho; comparação direcionada contra `../outputs/estimativas-combinadas-coerentes-20261103/candidato`.

## Pendências que continuam abertas

- Tempos uniformes das outras linhas: referências GTFS preservadas não demonstram tempos reais distintos por intervalo. O cenário histórico da Linha 13 resolve uma hipótese de comparação, não calibra toda a malha.
- Linha 10: permanece frequência conservadora para não oferecer como direto um trem parcial de Mauá; falta representar o padrão parcial e seu alcance na escolha do embarque.
- Expresso Aeroporto em feriados: resumo de operador e grade detalhada divergem; preservar grade conservadora, sem fabricar partidas. Teste aprovado verifica consistência com essa decisão, não resolve a divergência externa.
- Esperas regulares em fins de semana e feriados ainda usam aproximações GTFS onde não há perfil específico. Confirmar vigência da extensão da Linha 8 e testar sensibilidade noturna entre 20 e 30 minutos.
- Outras plataformas, seis combinações de Paraíso, acessibilidade, espera por elevador e eventual dupla cobrança do corredor Paulista–Consolação continuam sem fechamento.
- Busca e registro/concorrência precisam compartilhar os mesmos valores e versão antes de qualquer publicação. Cobertura operacional permanece incompleta.

Margem futura: acrescentar 60 segundos uma única vez no total final, mantendo “Tempo estimado” e informação de variação por condições externas. Nenhuma margem por trecho, espera ou baldeação.
