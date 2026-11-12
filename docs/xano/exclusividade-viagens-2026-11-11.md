# Exclusividade de confirmação por usuário — 11/11/2026

## Falha reproduzida

Duas rodadas HTTP autenticadas, com solicitações sobrepostas, retornaram duas confirmações HTTP 200 e deixaram pares de viagens ativas para a mesma conta: 70/71 e 75/76. A confirmação sequencial posterior encerrou as duplicatas pelo fluxo normal. Isso revelou que atomicidade da transação, sem bloqueio de registro estável, não serializava a leitura seguida da inserção.

## Correção publicada e backup

O endpoint `viagens/confirmar POST` adquire `db.get usuarios` com `lock = true`, dentro de `db.transaction`, antes de consultar as viagens a substituir. O registro de usuário existe mesmo sem viagem anterior. Duas confirmações da mesma conta disputam esse bloqueio; contas distintas usam registros diferentes. Nenhum campo de usuário é alterado. Commit ou rollback libera o bloqueio automaticamente.

Após a espera, o endpoint relê estado, verificação e versão da sessão, atualiza o instante da confirmação e verifica novamente a idade máxima de 30 s da referência de busca. Só depois substitui viagens anteriores e insere a nova. Cálculo, padrões, cronologia de embarque e margem pública permanecem iguais.

Fonte oficial: [bloqueio de Get Record dentro de transação](https://docs.xano.com/the-function-stack/functions/database-requests/get-record).

Backup anterior à publicação, fora do Git: `outputs/correcao-exclusividade-20261111/backup-workspace` (26 documentos), hashes, nove tabelas de referência/viagens e metadados dos dois endpoints em `backup-dados`. A prévia indicou atualização exclusiva do endpoint de registro. O patch versionado desta alteração está em [patches/exclusividade-viagens-2026-11-11.patch](patches/exclusividade-viagens-2026-11-11.patch).

## Conferências após publicação

- Releitura integral dos 26 documentos: somente `viagens/confirmar POST` alterado.
- Todas as funções lambda de cálculo/validação são idênticas às anteriores; o novo controle está na seção transacional.
- Contratos de entrada, resposta, autenticação, cache e identificadores preservados; sem rascunho pendente.
- Tabelas de estações, linhas, vínculos, trechos, operadores, serviços, disponibilidades e configuração de lotação com hashes idênticos aos anteriores.
- XanoScript válido; 13 itens OpenSpec aprovados; 36 testes e 18 subtestes de API/cliente passaram, com aviso já existente do TestClient.

O CLI emitiu avisos de referências não resolvidas no envio seletivo, apesar de os objetos existirem. A releitura integral confirmou as operações `db.*`, os nomes de tabelas, o bloqueio nativo e o código candidato preservados, sem placeholders. Isso não substitui a execução autenticada.

## Reteste real

**Reteste autenticado aprovado após a publicação.** O registro válido criou a viagem 80. Duas requisições sobrepostas partiram no mesmo instante medido pelo executor, responderam HTTP 200 e criaram 81/82. A leitura imediatamente após a disputa encontrou somente 82 ativa. A consulta independente posterior ao Xano confirmou que `substituida_em` de 81 coincide exatamente com `confirmada_em` de 82: 1794446378214 ms. A viagem 80 foi substituída pela primeira da disputa. Diferentemente das duas rodadas anteriores, não sobraram duas viagens ativas.

A segunda conta confirmou também o comportamento de trecho ocupado sem alternativa proporcional: manteve o trecho 206, sem criar desvio exagerado. O encerramento sequencial terminou com somente a viagem curta 84 da conta testada, sujeita à expiração normal. As viagens 81/82 foram posteriormente substituídas pelo fluxo normal, sem exclusão de histórico.

A conferência independente após o teste confirmou novamente hashes idênticos das oito tabelas de malha/configuração. A versão de calibração permaneceu `ebe34d59abdefc843e976afe160630f9b8ba37c5ca5c66885a0c1656fab333bb`. Evidências restritas: `reteste-autenticado-aprovado.json` e `conferencia-final-reteste.json` na pasta externa do backup. O teste positivo cobre esta disputa real; não é prova exaustiva de toda carga, rollback, expiração durante bloqueio ou contas sem histórico. Os testes negativos do relatório foram reaproveitados da rodada anterior e não são novas execuções após a correção.

A matriz remota de sessão naturalmente expirada e configuração ausente continua separada. A configuração não foi retirada nem alterada para fabricar esse cenário. O patch não resolve pendências administrativas de gravação de trechos nem altera preferência pelo Metrô, concorrência de passageiros, tempos ou serviços.

## Atualização posterior: expiração e configuração ausente

A expiração foi testada em HTTP real com token assinado de curta duração, sem alterar o login normal; auth/me, busca e confirmação rejeitaram o mesmo token com 401 após vencer. A regra de configuração nula/omitida passou em execução isolada do cálculo exato no Xano, sem retirar o registro real. Essa execução não substitui integração HTTP com registro ausente no banco de produção. Ver [método, resultados e limites](sessao-expirada-configuracao-ausente-2026-11-11.md).

## Arquivamento documental

A revisão de 12/11 concluiu o arquivamento da correção usando a data funcional de 11/11. Especificação consolidada: `openspec/specs/exclusividade-viagens/spec.md`. O arquivamento não encerra a matriz geral de concorrência; configuração ausente continua identificada como validação isolada. Ver [revisão OpenSpec](../revisao-openspec-2026-11-12.md).
