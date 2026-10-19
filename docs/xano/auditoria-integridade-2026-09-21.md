# Auditoria de integridade do Xano — 21/09/2026

Auditoria realizada no workspace `149130`, branch `v1`, data source `live`. Antes da correção, foram solicitadas exportações CSV completas das tabelas `linhas` e `trechos`; o Xano informou que os links ficarão disponíveis por e-mail durante 12 horas.

## Evidências confirmadas

- `estacoes` (`882606`, 182 registros): `nome` e `codigo` são obrigatórios, não anuláveis e normalizados com `trim`; `codigo` possui índice único; `ativa` é não anulável e obrigatória.
- `linhas` (`882607`, 16 registros): `nome` e `codigo` são obrigatórios, não anuláveis e normalizados com `trim`; `codigo` possui índice único; `operador_id` é uma Table Reference obrigatória e não anulável.
- `estacoes_linhas` (`882608`, 219 registros): as duas referências são obrigatórias e não anuláveis; `ordem` é obrigatória, não anulável e tem mínimo `1`; existe índice único composto por `estacao_id + linha_id`.
- `trechos` (`882609`, 207 registros): referências obrigatórias e não anuláveis; `tempo_estimado` é inteiro obrigatório, não anulável e tem mínimo `1`; `ativo` é obrigatório e não anulável; existe índice único composto por `estacao_origem_id + estacao_destino_id + linha_id`.
- `usuarios` (`885320`, 4 registros): `email` é obrigatório, normalizado com `trim` e `lower` e possui índice único; `senha` usa o tipo password, mínimo de oito caracteres, é obrigatória, sensível e interna; `ativo` é obrigatório e não anulável.
- `POST /trajetos/buscar` (`4035909`) exige autenticação, rejeita origem igual ao destino na entrada, valida que as estações existem e estão ativas, carrega a malha e rejeita resultado vazio.

## Correção aplicada

`linhas.ativa` estava não anulável e com default `true`, mas sem **Required** na configuração de entrada. **Required** foi habilitado e a configuração foi reaberta para confirmar o estado salvo.

## Limitações encontradas em 21/09/2026

Esta seção preserva o estado observado na data da auditoria. As duas limitações
abaixo foram superadas posteriormente por um endpoint de gravação autenticado,
uma chave canônica e um índice único, conforme a
[auditoria complementar de 08/10/2026](auditoria-integridade-2026-10-08.md).

1. O índice de `trechos` impede apenas duplicata direta. Ele não impede o mesmo trecho com origem e destino invertidos na mesma linha.
2. A rejeição de origem igual ao destino está comprovada no endpoint de busca, mas não existe constraint na tabela.

O painel de Database Triggers exibiu somente **Upgrade now**. Os filtros de entrada disponíveis para campos inteiros oferecem `min` e `max`, sem comparação entre dois campos ou consulta de registros existentes. Portanto, o plano atual não oferece um mecanismo de tabela capaz de implementar corretamente essas duas proteções.

Não foi adicionada uma coluna manual ou validação parcial naquela revisão, pois isso criaria uma falsa garantia de integridade. A solução posterior adotou o caminho então proposto: um endpoint de gravação validado, com chave canônica e proteção por índice único. Os testes de extremos iguais, duplicatas direta e inversa e concorrência foram concluídos em 19/10/2026.
