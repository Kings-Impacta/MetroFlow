# Entrega da malha calibrada — 05/11/2026

O cliente atualizado declara suporte à calibração na API oficial. A estimativa pública continua com a margem única de 60 segundos. A busca e a confirmação candidatas compartilham versão, regras de embarque, custos de troca e tempos previstos. A confirmação continua validando a sessão e registrando a viagem na transação existente. Clientes anteriores continuam com a resposta e o registro legados.

O pacote do cliente parte da revisão `bd945d8` e contém somente o código de planejamento e os testes relacionados. Está em `outputs/entrega-malha-completa-20261105/cliente-calibracao.patch`. O terminal autenticado do usuário publicou o pacote no PR #37 após a integração e o GitHub CLI da sessão retornarem erros de acesso.

Antes da ativação, foi exportado o backup `outputs/backup-xano-malha-completa-20261105` com 26 documentos XanoScript e as oito tabelas da malha e configuração. Os 34 hashes SHA-256 foram conferidos. O plano local registra 20 inserções da Linha 6. Os tempos dos 407 sentidos anteriores entram no cálculo calibrado por direção, preservando a base usada pelo contrato legado. A Linha 6 acrescenta dez sentidos ferroviários e dois a pé. Ao criar os registros, devem ser usados os IDs retornados pelo Xano para regenerar a versão final antes da ativação.

As simulações verificaram 377 buscas calibradas, 320 comparações legadas, 254 registros com a mesma cronologia da busca e 120 cenários de concorrência com usuários simulados. Foram rejeitados versão inválida, registro vencido e ausência de padrões. O cliente passou em 240 testes e 39 subtestes. A prévia do Xano apresentou três alterações: listagem de estações, busca de trajetos e confirmação de viagens. Os três arquivos XanoScript passaram na validação. O teste com contas reais permanece pendente.

## Publicação no Xano

O cliente foi entregue no [PR #37](https://github.com/Kings-Impacta/MetroFlow/pull/37), commit `326ddd1`. Os 11 arquivos correspondem ao pacote validado. A malha calibrada foi publicada no workspace 149130, branch v1. A releitura dos 26 documentos mostrou mudanças somente na listagem, na busca e na confirmação.

A Linha 6 foi cadastrada com o operador e as estações inativos. O limite de requisições interrompeu a primeira passagem depois de três trechos. A retomada conferiu os registros anteriores e os IDs já gravados antes de criar os três trechos restantes. A validação com os IDs reais passou antes da ativação. Depois da ativação, a releitura das oito tabelas confirmou os 20 novos registros e preservou o conteúdo anterior. O grafo calibrado usa os 419 sentidos, com margem única de 60 segundos no tempo estimado exibido.

Versão da calibração `7bd1cf949c7ac3cd20eed0b7acd0c4f99d5aaf15130e5366ac6e3671bea95169`. O pacote final, o diário de IDs e a releitura estão em `outputs/entrega-malha-completa-20261105`. O código relido repetiu as 377 buscas, os 254 registros e os 120 cenários simulados de concorrência. Os três endpoints recusaram requisições sem sessão com HTTP 401. O teste com duas contas reais continua pendente.


## Compatibilidade da confirmação

Em 05/11, duas buscas reais de Barra Funda para Paraíso retornaram HTTP 200, mas as confirmações legadas retornaram HTTP 400. O histórico mostrou pedidos com nove trechos e sem campos de calibração. A seleção do contrato foi ajustada para tratar os valores vazios dos opcionais como ausência de referência, e a confirmação legada usa o relógio do servidor quando o horário opcional está vazio. Uma referência preenchida continua exigindo versão, padrões e validade temporal.

Os dois pedidos reais anonimizados foram reproduzidos em memória. Seis variações de valores padrão foram aceitas e duas referências inválidas foram rejeitadas. O XanoScript foi validado e a releitura confirmou alteração apenas em `POST viagens/confirmar`. O backup e as amostras anonimizadas estão em `outputs/correcao-registro-legado-20261105`.

No reteste real de 05/11, a confirmação respondeu HTTP 200 para duas contas distintas. Às 20h48min06s, o Xano gravou Barra Funda → Paraíso pela Linha 3 até Sé e depois pela Linha 1. Às 20h48min18s, gravou a busca da outra conta pela Linha 10 até Luz e depois pela Linha 1. Os registros são do contrato legado. O teste com o cliente calibrado continua separado.

## Reteste com duas contas calibradas em 08/11/2026

O Xano registrou Barra Funda → Paraíso às 19h24min40s e às 19h29min03s, para usuários distintos. Busca e confirmação responderam HTTP 200. As duas confirmações enviaram a versão `7bd1cf949c7ac3cd20eed0b7acd0c4f99d5aaf15130e5366ac6e3671bea95169`. Os registros contêm padrões de trem calibrados, 90 s de espera e 180 s de troca. O total físico é 1155 s e a estimativa pública com margem é 1215 s.

As duas viagens usaram a Linha 3 até Sé e a Linha 1 até Paraíso. A diferença de 262,97 s entre as buscas resultou em zero trechos com sobreposição prevista no mesmo sentido. Assim, manter o principal é coerente com a concorrência por ocupação temporal. Este par confirmou registro e cronologia calibrados, mas não exerceu um conflito real que exigisse alternativa.

No teste de 08/11 às 19h38min18,745s e 19h38min26,080s, duas contas distintas registraram viagens calibradas com sucesso. As duas confirmações enviaram a versão publicada e responderam HTTP 200. O intervalo entre registros foi de 7,335 s. Houve sobreposição positiva nos nove trechos do mesmo sentido, de 63 a 128 s por trecho. Ambas receberam Linha 3 até Sé e Linha 1 até Paraíso. Portanto, o registro calibrado e o conflito temporal foram confirmados, mas nenhuma alternativa foi selecionada neste teste. A causa precisa ser confrontada com o filtro de lotação e os limites de desvio antes de concluir que há falha de cálculo.

## Diagnóstico do conflito real de 08/11

A reprodução da segunda busca, com a viagem da primeira conta e a configuração real, reconheceu uma outra viagem ativa e nove trechos ocupados. A exposição foi de 885 s. O principal teve 1155 s e uma baldeação. A tolerância de 25% foi de 288,75 s, permitindo até 1443,75 s e duas baldeações.

O corredor Linha 3 → República → Linha 4 → Paulista/Consolação → Linha 2 teve 1635 s e duas baldeações, ainda compartilhando os três primeiros trechos ocupados. Sua duração excedeu o limite por 191,25 s. A melhor alternativa totalmente livre encontrada, pela Luz, teve 2600 s e uma baldeação, incluindo a espera do serviço naquele domingo. A busca de redução parcial de exposição, que exige não aumentar tempo e trocas, manteve o principal.

O comportamento observado corresponde aos limites de produto publicados. O diagnóstico não justifica ampliar limites nem forçar uma alternativa. A reprodução é uma simulação com registros reais anonimizados. Os resultados e o detalhe dos corredores estão em `outputs/diagnostico-concorrencia-20261108`.

Atualização de 09/11/2026: a cobertura e a publicação calibradas foram concluídas, e o reteste real com duas contas confirmou a alternativa por República. As pendências anteriores de cliente calibrado e conflito real foram superadas por esse teste. Consulte `publicacao-preferencia-metro-2026-11-09.md` e `fechamento-trajetos-concorrencia-2026-11-09.md`; os diagnósticos anteriores acima permanecem históricos.
