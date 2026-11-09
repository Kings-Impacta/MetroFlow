# Complementação com fontes independentes e comunidade

Consulta: 01/11/2026. Estudo local; sem acesso de escrita ao Xano, publicação de endpoints, mudança da aplicação ou envio à main. A Linha 6 permanece excluída.

## O que dá para aproveitar

| Fonte consultada | Informação aproveitável | Limite de uso |
| --- | --- | --- |
| [Relatos sobre baldeações, março de 2026](https://www.reddit.com/r/saopaulo/comments/1rjqzgi/baldea%C3%A7%C3%B5es/) | Diferenciar conexões curtas de Pinheiros e Santa Cruz; Paraíso varia com o sentido; posicionamento no trem influencia Presidente Altino | Discussão qualitativa, com humor e discordâncias. Votos não são amostra estatística nem cronômetro |
| [Experiências em Pinheiros e Santa Cruz](https://www.reddit.com/r/saopaulo/comments/1ocuiqz/) | Relatos de muitos lances de escada e passarela; um participante estima aproximadamente dez minutos em Pinheiros | Observação individual, sem controle de dia, sentido, fila ou acessibilidade. Não adotar como média medida |
| [Bresser-Mooca → São Joaquim](https://www.reddit.com/r/saopaulo/comments/1ry0dio/d%C3%BAvida_sobre_um_trajeto_no_metr%C3%B4/) | Há relato de 12 minutos desde o embarque, com troca na Sé, e descrição de conexão curta | Outros participantes sugerem margem maior. Não converter o total em tempos individuais por trecho |
| [Paulista–Consolação](https://www.reddit.com/r/saopaulo/comments/1i8vxfe/) | Passageiros distinguem corredor em fluxo livre e congestionamento no pico | Há exageros e comentários humorísticos. Descartar números sem medição verificável; aproveitar a necessidade de faixa por horário |
| [Rome2Rio: Jandira → Barra Funda](https://www.rome2rio.com/pt/s/Jandira/Barra-Funda-distrito-de-S%C3%A3o-Paulo) | Verificação externa da ligação direta | A consulta retorna 1h45. Não esclarece medição e pode reutilizar dados de horários já inconsistentes. Não é confirmação independente dos tempos do GTFS |
| [Metrô: Linha 3 e estações](https://www.metro.sp.gov.br/sua-viagem/linhas-estacoes/linha-3-vermelha/) | Referência oficial de topologia e integrações | Não fornece cronometragem de cada baldeação |

Conclusão: relatos ajudam a escolher o que medir, distinguir sentidos e montar testes de sensibilidade. Ainda não sustentam uma tabela completa de tempos reais. Estimativas de aplicativos podem compartilhar a mesma origem; duas telas com o mesmo número não significam duas medições independentes. Incidentes e obras pontuais não devem virar duração permanente de trecho.

## Simulação isolada

Utilitário: `scripts/simular_calibracao_comunidade.py`. Entrada: exportação de leitura de 01/11 usada na auditoria oficial. O utilitário não tem chamadas de rede; copia os dados para outra pasta e executa localmente a função de busca exportada. Só a cópia experimental recebe ajustes. A referência deve reproduzir exatamente o relatório anterior ou o ensaio falha.

Os números abaixo são **hipóteses de engenharia para sensibilidade**, não médias extraídas dos relatos e não parâmetros aprovados:

| Perfil | Sé L1↔L3 e Ana Rosa L1↔L2 | Pinheiros L4↔L9 e Santa Cruz L1↔L5 | Corredor Paulista–Consolação | Deslocamento regular |
| --- | --- | --- | --- | --- |
| Referência | 10 min | 10 min | 3 min | Cadastro atual |
| Trocas menores | 3 min | 8 min | 5 min | Cadastro atual |
| Trocas congestionadas | 8 min | 15 min | 10 min | Cadastro atual |
| Deslocamento +20% | 3 min | 8 min | 5 min | Cadastro atual × 1,2 |

Outras trocas conservam o parâmetro atual. Paraíso não foi simplificado para um tempo único novo: falta identificar e medir cada conexão por sentido. Esperas especiais, horários, limites de concorrência e trocas dos ramais foram preservados. Os perfis são cenários fixos, não implementação de pico por horário; todos são confrontados com os mesmos cinco horários do ensaio anterior, inclusive fechamento e madrugada.

O corredor mantém a representação e eventuais penalidades de troca do algoritmo atual. Assim, o valor de caminhada na tabela não equivale automaticamente ao tempo completo de uma rota que chega ao corredor por uma linha e continua por outra. Uma calibração definitiva precisa separar caminhada, espera e dupla contagem de penalidades.

São 398 casos por perfil (290 buscas e 108 cenários de concorrência). A ocupação sintética é reconstruída para cada perfil conforme os horários de passagem; não representa passageiros reais nem mantém artificialmente os mesmos intervalos quando o tempo muda. O ensaio verifica estações repetidas e desvios acima do dobro do principal, mas não prova optimalidade global ou precisão dos tempos. Resultados completos: pasta irmã do worktree `outputs/simulacao-comunidade-20261101`, arquivo `comparacao.json`.

## Resultado antes/depois do ensaio

Foram executados 1.592 cenários (quatro perfis × 398), com reprodução exata da referência, nenhuma estação repetida nas buscas e alternativas e nenhum desvio acima do dobro do principal. Não se trata de 1.592 viagens observadas. Os números de caminhos alterados abaixo incluem mudança de trecho/linha mesmo quando a lista de estações permanece igual.

| Perfil experimental | Buscas com resultado alterado, entre 290 | Caminhos alterados | Resultados de concorrência alterados, entre 108 |
| --- | --- | --- | --- |
| Trocas menores | 48 | 17 | 22 |
| Trocas congestionadas | 39 | 11 | 16 |
| Deslocamentos +20% | 188 | 11 | 108 |

Exemplos sem ocupação, às 12h10 de 29/10/2026. **Depois** significa apenas perfil local de trocas menores; não é tempo real aprovado:

| Trajeto | Antes | Depois simulado | Caminho |
| --- | --- | --- | --- |
| Barra Funda → Paraíso | 28 min | 21 min | Mantém Vermelha → Azul, troca na Sé |
| Jandira → Paraíso | 68 min | 61 min | Mantém Diamante → Vermelha → Azul |
| Vila Prudente → Tucuruvi | 46 min | 45 min | Verde → Turquesa → Azul passa a Verde → Azul pela Ana Rosa |
| Capão Redondo → Paraíso | 46 min | 44 min | Lilás → Verde pela Chácara Klabin passa a Lilás → Azul pela Santa Cruz |
| Consolação → Paulista | 3 min | 5 min | Mantém corredor a pé |

A mudança para Santa Cruz merece cautela: os relatos a descrevem como trabalhosa e o teste mostra que reduzir o seu custo pode torná-la preferida. Isso demonstra sensibilidade, não uma melhoria comprovada. Na hipótese congestionada, a rota continua pela Chácara Klabin. Tampouco basta diminuir tempos de troca para concluir que a Amarela → Verde será a alternativa mais rápida entre Barra Funda e Paraíso: ela não se tornou principal nesses exemplos.

Em concorrência sintética, Barra Funda → Paraíso mudou de Turquesa → Azul, 30 min, para manter Vermelha → Azul, 21 min, no perfil de trocas menores. A decisão depende da tolerância de desvio e da ocupação prevista recalculada: o objetivo não é forçar alternância se o desvio não compensa. Não houve teste com duas contas ou gravação de viagens reais nesta etapa.

## Critérios para converter hipótese em calibração

- Registrar partida e chegada em cada estação consecutiva; distinguir tempo embarcado, parada, caminhada e espera.
- Registrar estação, linhas e sentidos de origem/destino da troca; horário, dia, condições de acessibilidade, fila e falhas de escadas.
- Repetir observações em dias distintos e nas duas direções; calcular mediana, dispersão e tamanho da amostra, sem misturar situações de falha com operação habitual.
- Usar vídeos contínuos com relógio ou marcas de tempo como observação auditável, se disponíveis; não inferir velocidade de vídeos acelerados ou editados.
- Comparar fontes com procedência conhecida e confirmar divergências. Antes da aplicação, revisar os itinerários alterados e os cenários de concorrência, e recalcular o registro da viagem com os mesmos custos.

A calibração real continua pendente até haver observações suficientes. Nada neste estudo deve ser enviado ao Xano sem a validação acordada com o usuário.
