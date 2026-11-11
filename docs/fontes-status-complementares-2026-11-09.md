# Fontes complementares de status — 09/11/2026

Avaliação solicitada pelo usuário durante a preparação do adaptador do quadro do Metrô. Nenhuma fonte nova foi ativada e nenhum endpoint do Xano foi alterado.

## CPTM: serviço JSON usado pelo próprio site

A página `https://www.cptm.sp.gov.br/cptm` contém chamada GET para `https://api.cptm.sp.gov.br/AppCPTM/v1/Linhas/ObterStatus`, sem chave no código consultado. A requisição direta de 09/11 respondeu HTTP 200. O array retornado trouxe somente as linhas **10, 11 e 12**, com campos `linhaId`, `dataGeracao`, `descricao`, `tipo` e `status`. A `dataGeracao` da amostra foi `2026-11-09T16:11:20`, sem deslocamento de fuso explícito.

A página filtra registros com `tipo == 'C'`. Não inferir que o endpoint cobre toda a rede, nem oferecer status para a Linha 13 a partir dessa amostra. Há resultados de busca antigos com o portal anterior e datas de 2025; eles não comprovam a operação atual. A data da amostra direta foi guardada separadamente dos resultados em cache do buscador.

É um candidato prioritário para complementar as linhas 10/11/12 sem interpretar o HTML. Ainda falta confirmar contrato de uso/republicação, periodicidade, limites, estabilidade e significado/fuso de `dataGeracao`; depois preparar adaptador separado e testar nulabilidade, erros e validade. O retorno público sem autenticação é evidência técnica de acesso, não uma licença geral de republicação.

## Direto dos Trens: agregador independente com API documentada

O site declara coletar automaticamente dados de fontes oficiais e não possuir vínculo com as companhias. Sua API OpenAPI é publicada em `https://static.diretodostrens.com.br/swagger/api.json`; servidor `https://www.diretodostrens.com.br/api`.

`GET /status` retorna os últimos estados de todas as linhas, em array. O contrato indica atualização no backend a cada 60 segundos e campos `codigo`, `criado`, `id`, `situacao`, `descricao` opcional e `modificado` opcional. A lista efetiva de linhas não é enumerada no esquema; cobertura só pode ser confirmada por amostra autorizada, sem confundir o texto de apresentação com dados recebidos.

O endpoint exige token único, solicitado a **api@diretodostrens.com.br**, com descrição do projeto. A documentação encoraja projetos pessoais/acadêmicos, informa operação best-effort, exige respeito aos cabeçalhos de cache e restringe uso comercial sem autorização. Não foi enviada solicitação em nome do usuário nem feita chamada protegida.

A autenticação documentada usa parâmetro `token` na query string. Isso requer tratamento específico para impedir exposição em logs, traces e mensagens, e deve ser conciliado com a regra atual do projeto de não expor credenciais em URLs. Preferir solicitar suporte a cabeçalho de autenticação ao responsável antes de integrar. Nenhum token foi obtido, inserido em URL ou utilizado nesta pesquisa.

## Cobertura observada e próximos passos

| Fonte | Cobertura comprovada nesta análise | Estado |
|---|---|---|
| Quadro oficial do Metrô | 1, 2, 3, 4, 5, 15, 17 na captura guardada | Adaptador local preparado, desativado |
| JSON do site CPTM | 10, 11, 12 na resposta direta | Candidato oficial, sem adaptador novo nesta etapa |
| Direto dos Trens | Rede de vários operadores declarada; códigos reais ainda não conferidos | API documentada, token e condições específicas pendentes |
| ARTESP | Sem credencial válida; portal mostrou capacidade esgotada | Não ativar com chave recusada |

Entre as fontes oficiais diretas Metrô + CPTM examinadas, faltam 6/7/8/9/13. Essa não é uma ausência de cobertura do Direto dos Trens: o catálogo público do agregador inclui essas linhas. Seu consumo automatizado continua dependente do token solicitado e da validação da resposta; serviços especiais permanecem separados.

Guardar snapshot de referência não equivale a coletor ativo. Evidências desta pesquisa estão em `outputs/fontes-status-complementares-20261109`, fora do código do aplicativo. A busca e a concorrência continuam independentes dessas fontes.

Fontes: [Direto dos Trens](https://www.diretodostrens.com.br/), [documentação da API](https://static.diretodostrens.com.br/swagger/), [site CPTM](https://www.cptm.sp.gov.br/cptm) e [serviço JSON observado](https://api.cptm.sp.gov.br/AppCPTM/v1/Linhas/ObterStatus).


## Complemento oficial Motiva — linhas 8 e 9

O usuário indicou `https://trilhos.motiva.com.br/viamobilidade8e9/situacao-das-linhas/`. A página é da operadora e apresenta abas independentes para Linha 8-Diamante e Linha 9-Esmeralda, com data/hora, situação e descrição, além do histórico. A leitura direta respondeu HTTP 200 sem chave ARTESP.

No HTML há painéis `role="tabpanel"` associados ao título de cada linha em `data-cmp-data-layer`, com itens `block-post-list-container__post-item`, `post-time`, `post-title` e `post-description`. É possível preparar um parser isolado, separando a última atualização de cada linha das entradas históricas. Não inferir estado de ambas as linhas a partir do primeiro item global nem tratar a data da ocorrência como uma confirmação recente de coleta.

A consulta direta de 09/11 encontrou o primeiro item da Linha 8 com Atividade Programada em 09/11 às 10h09min46s, e o da Linha 9 com Operação Normal em 09/11 às 04h00min08s. O extrato do buscador apresentou versão diferente da Linha 8; por isso o snapshot direto foi preservado e a resposta não usa o buscador para afirmar a condição atual. Essas observações são amostras daquele momento, não um feed ativo.

Não foi localizado nesta leitura um contrato público de API para terceiros, licença de republicação ou frequência garantida. A página oficial pode complementar os dados das linhas 8/9, mas é necessário confirmar as condições de uso e manter cache, limite de acesso e tratamento de mudanças estruturais antes de ativação. Não há motivo para obter chave ARTESP para ler esse HTML público, mas isso não substitui a confirmação das condições de uso.

Com as coberturas observadas do quadro do Metrô (1/2/3/4/5/15/17), do JSON CPTM (10/11/12) e desta página Motiva (8/9), as lacunas de fontes oficiais diretas examinadas ficam em **6, 7 e 13**. O Direto dos Trens contempla essas linhas e passa a ser considerado o complemento planejado para elas. Essa união indica viabilidade de cobertura, não integrações já ativadas. Serviços especiais permanecem separados.

Nenhum adaptador Motiva foi implementado ou ativado nesta avaliação. Snapshots e resumo estão em `outputs/fontes-status-complementares-20261109/motiva-8e9.html` e `motiva-resumo.json`, fora do aplicativo. Fonte: [situação das linhas 8 e 9 — Motiva](https://trilhos.motiva.com.br/viamobilidade8e9/situacao-das-linhas/).


## Revisão detalhada do Swagger Direto dos Trens

O usuário informou que já solicitou acesso e aguarda retorno. A URL do Swagger foi consultada sem parâmetros de rastreamento; a especificação OpenAPI 3.1.2, versão de contrato 1.0.0, foi guardada novamente em `outputs/fontes-status-complementares-20261109/direto-api-revisao.json`.

| Endpoint | Uso possível | Acesso declarado |
|---|---|---|
| `GET /status` | Uma coleta agregada dos últimos estados, suficiente para o painel inicial | Token |
| `GET /status/codigo/{linha}` | IDs de registros recentes de uma linha | Token |
| `GET /status/codigo/{linha}/{ano}` | IDs históricos de uma linha em um ano | Token |
| `GET /status/id/{id}` | Detalhe de registro cujo ID já é conhecido | Sem exigência de token declarada nesta operação; acesso não testado |

Não enumerar IDs nem usar a operação de detalhe como substituto da coleta autorizada. O painel inicial não precisa consultar histórico em cada busca de usuário.

O estado agregado exige `codigo`, `criado`, `id` e `situacao`; `descricao` e `modificado` são opcionais. A data `criado` é da ocorrência, e `modificado` não deve ser interpretado automaticamente como verificação recente da fonte. O esquema descreve data/hora, mas amostras autorizadas precisam confirmar fuso, formatos efetivos e situações possíveis. A descrição pode ter até 1500 caracteres; qualquer limite interno menor precisa de truncamento explícito e testado.

A documentação informa atualização do backend a cada 60 segundos. Isso não define uma cota de chamadas nem autoriza uma requisição por usuário: o cache deve obedecer aos cabeçalhos retornados e às condições do token. Não reutilizar automaticamente a cota ARTESP como se fosse um limite publicado desta origem.

A exigência de autenticação é `apiKey` na query `token`. A configuração de transporte continua pendente de conciliação com a proteção de credenciais em URLs/logs; perguntar ao responsável se aceita cabeçalho e quais limites/atribuição se aplicam ao projeto. Embora o esquema não enumere as linhas, o catálogo público do site inclui 6/7/13. A primeira amostra autorizada validará o retorno efetivo da API, não a existência dessas linhas no site. Nenhuma chamada protegida ou tentativa de adivinhar token/IDs foi realizada.


## Correção da classificação de cobertura do Direto dos Trens

Após apontamento do usuário, foi relido o JavaScript público referenciado pela própria página (`https://www.diretodostrens.com.br/js/index.min.js`). O catálogo de linhas inclui explicitamente **6: Laranja, 7: Rubi e 13: Jade**, além de 1/2/3/4/5/8/9/10/11/12/15/17. A cobertura exibida/declarada pelo site deve ser considerada no planejamento da integração. A redação anterior confundia a ausência de amostra autenticada com falta de cobertura e foi corrigida.

Estado atual: Direto dos Trens é o complemento planejado para 6/7/13 e pode oferecer redundância para as demais linhas cadastradas. O acesso solicitado pelo usuário continua pendente. A validação com token verificará o conteúdo efetivamente retornado, datas, situações, nulabilidade e cache. Não é preciso continuar classificando essas três linhas como fontes ainda não localizadas. Nada foi ativado, e nenhuma chamada protegida foi feita.
