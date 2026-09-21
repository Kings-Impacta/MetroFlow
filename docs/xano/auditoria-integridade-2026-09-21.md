# Auditoria de integridade do Xano — 21/09/2026

Auditoria somente leitura realizada no workspace `149130`, branch `v1`, data source `live`. Nenhuma tabela, campo, índice, endpoint ou registro foi alterado.

## Evidências confirmadas

- `estacoes` (`882606`, 182 registros): `nome` e `codigo` são obrigatórios, não anuláveis e normalizados com `trim`; `codigo` possui índice único; `ativa` é não anulável e obrigatória.
- `linhas` (`882607`, 16 registros): `nome` e `codigo` são obrigatórios, não anuláveis e normalizados com `trim`; `codigo` possui índice único; `operador_id` é uma Table Reference obrigatória e não anulável.
- `estacoes_linhas` (`882608`, 219 registros): as duas referências são obrigatórias e não anuláveis; `ordem` é obrigatória, não anulável e tem mínimo `1`; existe índice único composto por `estacao_id + linha_id`.
- `trechos` (`882609`, 207 registros): referências obrigatórias e não anuláveis; `tempo_estimado` é inteiro obrigatório, não anulável e tem mínimo `1`; `ativo` é obrigatório e não anulável; existe índice único composto por `estacao_origem_id + estacao_destino_id + linha_id`.
- `usuarios` (`885320`, 4 registros): `email` é obrigatório, normalizado com `trim` e `lower` e possui índice único; `senha` usa o tipo password, mínimo de oito caracteres, é obrigatória, sensível e interna; `ativo` é obrigatório e não anulável.
- `POST /trajetos/buscar` (`4035909`) exige autenticação, rejeita origem igual ao destino na entrada, valida que as estações existem e estão ativas, carrega a malha e rejeita resultado vazio.

## Divergências encontradas

1. `linhas.ativa` está não anulável, porém **Required** está desmarcado na configuração de entrada do Xano. O modelo aprovado exige **Required**.
2. O índice de `trechos` impede apenas duplicata direta. Ele não impede o mesmo trecho com origem e destino invertidos na mesma linha.
3. A rejeição de origem igual ao destino está comprovada no endpoint de busca, mas não há constraint ou trigger comprovado no armazenamento de `trechos`.

## Correção proposta no Xano

- habilitar **Required** em `linhas.ativa`;
- adicionar validação de armazenamento para rejeitar `estacao_origem_id == estacao_destino_id`;
- adicionar validação canônica ou lógica equivalente para rejeitar duplicata inversa na mesma linha.

Essas alterações remotas exigem backup e autorização específica antes da execução, conforme a modelagem aprovada. Até lá, os itens 2.2, 2.7, 2.9, 8.1 e 8.3 permanecem abertos.
