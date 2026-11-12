# Reteste da main, status e concorrência — 11/11/2026

## Escopo e evidências

Cliente em execução na main `4ba2317cd467ecf91310e873c7911f25d6503ff8`, entregue pelo [PR #41](https://github.com/Kings-Impacta/MetroFlow/pull/41), iniciado por `iniciar-status-local.ps1`. A busca da aba interna foi observada diretamente; o caminho da outra conta foi informado pelo usuário e depois confirmado na tabela `viagens_confirmadas` do Xano. A auditoria foi somente de leitura, sem alterar malha, endpoints ou configuração.

Os registros 67 e 68 pertencem a usuários distintos, com 15,824 segundos entre confirmações. Ambos contêm padrões de trem, início previsto, espera e custo de baldeação. A reprodução local do validador efetivamente exportado do Xano, com a referência reconstruída dos registros, reproduziu integralmente os trechos e `fim_janela` de ambas as viagens usando a versão `ebe34d59abdefc843e976afe160630f9b8ba37c5ca5c66885a0c1656fab333bb`. Busca e registro publicados usam essa mesma versão e não têm rascunho pendente. A tabela não guarda o identificador da versão como campo próprio; esta conclusão resulta da reprodução e dos padrões/horários persistidos, não de uma leitura de versão inexistente na tabela.

| Registro | Caminho | Tempo físico | Estimado com margem única | Baldeações |
|---|---|---|---|---|
| 67 | Linha 3 → Sé → Linha 1 → Paraíso | 19min45s | 20min45s (21 min na tela) | 1 |
| 68 | Linha 11 → Luz → Linha 1 → Paraíso | 27min05s | 28min05s (29 min na tela) | 1 |

A margem continua sendo 60 segundos uma única vez no total público. Não integra o relógio de ocupação.

## Concorrência reproduzida

A execução local do código exportado, com os dados consultados e as viagens anteriores ativas no instante das confirmações, selecionou os mesmos trechos gravados. Na segunda consulta, reconheceu 885 segundos de exposição prevista no principal e zero na alternativa: redução de 100% da exposição temporal modelada. Isso não representa medição da lotação dos trens.

- Acréscimo físico: 440 s (7min20s), ou 37,13% do principal.
- Limite da alternativa parcial: min(540 s, 45% de 1185 s) = 533,25 s; acréscimo aprovado.
- Baldeações: uma em cada caminho; nenhuma adicional, abaixo do máximo de uma extra.
- Redução mínima exigida: 40%; redução reproduzida: 100%.
- Configuração observada: mínimo de um usuário e percentual de 1%, mantidos para demonstração.

A política mantém a tentativa inicial de evitar todos os trechos ocupados sob a tolerância histórica menor entre 10 min e 25%, com piso de 2 min. A seleção seguinte por redução de exposição admite min(9 min, 45%) e pode também encontrar exposição zero, como neste teste. Não confundir as duas etapas.

A simulação adicional, exclusivamente local e com orçamento ampliado para diagnóstico, encontrou República → Linha 4 → Paulista–Consolação → Linha 2 com 1725 s físicos. São 540 s acima do principal, excedendo o limite percentual de 533,25 s por 6,75 s; também são 100 s acima da alternativa pela Luz, além da preferência de até 60 s pelo Metrô. Portanto, não escolher República foi coerente com as regras, sem necessidade de alterar limites.

## Status na versão da main

Foram observadas 12 linhas: Metrô 1/2/3/4/5/15/17, CPTM 10/11/12 e Motiva 8/9. A Linha 17 informou operação transitória e troca de trem em Campo Belo; não se presumiu normalidade. Linhas 6/7/13 e serviços especiais sem resposta própria permaneceram indisponíveis.

Sem acionar atualização manual, as coletas do Metrô e da CPTM avançaram de 16:01 para 16:06; a Motiva avançou para 16:07 e foi apresentada como desatualizada segundo a validade da origem. Os indicadores anteriores permaneceram visíveis durante a atualização, e a busca continuou disponível. A renovação da coleta não implica mudança da ocorrência nem garantia de dado atual. A retenção após falha prolongada continua comprovada pelo ensaio isolado anterior; não foi provocada falha nas fontes nesta rodada.

## Pendências revisadas

| Área | Pendência real |
|---|---|
| Status | Receber token Direto dos Trens, validar amostra, limites, datas e condições; confirmar condições antes de ativação pública. |
| Status | Completar 6/7/13 e serviços especiais apenas com resposta efetiva; confirmar o fuso de `dataGeracao` CPTM. |
| Operação | Coordenar coleta/cache entre máquinas antes de compartilhar uma credencial em vários servidores; o SQLite atual coordena processos do mesmo servidor. |
| Concorrência | Completar matriz HTTP autenticada de entradas inválidas/desconexas, sessão expirada, configuração ausente e ausência de alternativa. |
| Concorrência | Concluído no reteste posterior 81/82, após correção do bloqueio por conta; ver a atualização ao final. |
| Administração da malha | Repetir gravações simultâneas de trechos por HTTP autenticado; é outro tipo de concorrência. |
| Trajetos | Reavaliar necessidade e certificar tempos dos retornos diretos do Expresso L10 ainda abertos no checklist. |
| Produção | Definir parâmetros de ocupação com a equipe; 1/1% é demonstração. Manter horários, exceções e alcance operante da Linha 6 atualizados. |
| Processo | Sincronizar/arquivar mudanças OpenSpec somente quando seus itens restantes estiverem concluídos. Esta atualização documental é entregue junto dos três arquivamentos revisados. |

Não foi encontrada falha nova no cenário auditado. Isso não encerra a matriz de todas as rotas, condições de falha ou disputas simultâneas. Status permanece informativo e independente do cálculo e do registro.

As evidências restritas permanecem fora do repositório, em `outputs/auditoria-viagens-main-20261111/` da pasta de trabalho: exportações, reprodução, comparação ampliada e `calibracao-verificada.json`. Nenhuma credencial ou identidade das contas integra esta documentação.

A revisão de arquivamento posterior concluiu três mudanças; veja [revisão das mudanças ativas](../revisao-mudancas-ativas-2026-11-11.md). As mudanças com pendências reais e a dependência de orientações continuam abertas.

## Atualização posterior: exclusividade corrigida em 11/11

A disputa simultânea da mesma conta foi reproduzida, corrigida no Xano após backup e validada nos registros 81/82, com apenas uma viagem ativa após a disputa. A segunda conta manteve o principal quando não havia alternativa proporcional. Malha e parâmetros preservados. A matriz de configuração ausente e sessão naturalmente expirada permanece aberta. Veja [correção e evidências](exclusividade-viagens-2026-11-11.md).
