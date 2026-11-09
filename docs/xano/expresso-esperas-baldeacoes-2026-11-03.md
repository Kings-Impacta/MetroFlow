# Expresso Aeroporto, esperas e baldeações — ensaio local

## Estado em 03/11/2026

Nenhuma alteração no Xano. Nenhuma margem numérica aplicada. Linha 6 adiada. As estimativas foram preservadas para continuidade, sem aprovação automática para publicação.

Os sete sentidos restantes do Expresso Aeroporto receberam candidatos:

| Sentido | Minutos candidatos |
|---|---:|
| Barra Funda → Luz | 8 |
| Luz → Guarulhos-Cecap | 22 |
| Guarulhos-Cecap → Aeroporto | 5 |
| Aeroporto → Guarulhos-Cecap | 5 |
| Guarulhos-Cecap → Brás | 18 |
| Brás → Luz | 4 |
| Luz → Barra Funda | 8 |

Cada percurso completo soma 35 minutos, sem espera. O [estudo técnico de 2025 apresentado na Semana de Tecnologia](https://semanadetecnologia.com.br/31semana/files/artigos/915_artigo_acessoaeroferroviario.pdf) sustenta a ordem de grandeza do **total**. A divisão entre estações reutiliza os pesos do cadastro restaurado, documentados em `correcao-malha-2026-10-28.md`; não representa sete novas medições independentes. Confiança baixa e método registrados no JSON.

O inventário passou a ter 389 sentidos com referência e 18 com estimativa modelada, sem sentido numericamente vazio. Isso não significa que os tempos atuais de todos os trechos tenham sido calibrados: há referências GTFS uniformes e conflitos que ainda exigem seleção coerente dos valores-base.

## Esperas e trocas preservadas

- `docs/dados/tempos/esperas-candidatas.json`: 405 possibilidades de embarque. Serviços com grade usam a próxima partida; regulares usam metade do intervalo como aproximação, uma vez por embarque. Linha 10 e Linha 13 têm perfis por tipo de dia; outros perfis GTFS ainda têm calendário provisório. A extensão Itapevi–Amador Bueno está separada.
- `docs/dados/tempos/baldeacoes-candidatas.json`: 128 pares candidatos de linhas, com valores por classe de conexão e faixas de sensibilidade. Não são 128 caminhadas medidas nem conexões físicas integralmente confirmadas. Caminhada e espera permanecem componentes separados.
- `docs/dados/tempos/estimativas-lacunas.json`: 18 candidatos de percurso, incluindo os sete acima. Fontes e limitações permanecem junto aos valores.

## Simulações antes e depois

Executado `scripts/simular_estimativas_lacunas.py` com `--incluir-esperas-baldeacoes`, usando cópias locais. As tabelas copiadas dos serviços especiais também receberam os tempos candidatos, mantendo os horários intermediários coerentes com seus percursos.

Resultado: **880 execuções**, 211 buscas com resultado alterado e 120 casos de concorrência alterados. Não foram detectados ciclos nem alternativas acima do limite de dobro do tempo no conjunto exercitado. Isso verifica o ensaio, não garante a qualidade de toda combinação de estações.

Exemplo às 07h30: Barra Funda → Paraíso manteve Vermelha → Azul e mudou de 28 para 22min30s. A redução decorre principalmente de trocar a penalidade fixa de troca por um custo candidato menor; não comprova esse tempo na operação real.

Cinco verificações específicas passaram:

| Caso | Espera | Total sem margem |
|---|---:|---:|
| Linha 13, dia útil | 6 min | 10 min |
| Linha 13, domingo | 17min30s | 21min30s |
| Linha 13, feriado | 17min30s | 21min30s |
| Itapevi → Amador Bueno, mesmo trem | 15 min uma vez | 27 min |
| Expresso, consulta às 12h59 para partida às 13h | 1 min | 36 min |

Esses totais pertencem ao modelo experimental; o percurso regular da Linha 13 ainda conserva tempos-base do cadastro e não deve ser divulgado como calibrado.

Resultados reproduzíveis em `../outputs/estimativas-combinadas-coerentes-20261103/`, relativo à raiz do trabalho. Scripts: `estimar_lacunas_tempos.py`, `estimar_esperas_baldeacoes.py`, `candidato_esperas_baldeacoes.py`, `simular_estimativas_lacunas.py` e `validar_esperas_candidatas.py`.

## Pendências antes de publicar

Resolver os calendários provisórios do GTFS, a vigência dos intervalos históricos da extensão da Linha 8, os trens parciais da Linha 10 e a aproximação de intervalos na operação noturna. Selecionar tempos-base de percurso onde o cadastro ainda usa valores uniformes. Desdobrar trocas relevantes por plataforma/sentido, acessibilidade e corredores para evitar cobrança duplicada de caminhada. Validar busca e registro/concorrência com os mesmos custos e ampliar os casos de fechamento e últimas partidas.

Somente depois da cobertura operacional e das simulações: acrescentar **60 segundos uma única vez ao total**, manter a indicação **Tempo estimado** e a informação de variação por condições externas, preparar cópia de segurança e publicar de forma coerente. Não acrescentar margem por estação, embarque ou baldeação.
