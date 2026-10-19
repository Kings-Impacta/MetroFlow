## Garantias de armazenamento

- [x] Revisar os caminhos de gravação, backups e permissões visíveis; registrar os endpoints novos, as referências `Deleted table`, os caminhos administrativos que contornam o endpoint e a necessidade de uma exportação atual.
- [x] Publicar no endpoint de gravação a rejeição de origem igual ao destino, sem depender da validação da busca.
- [x] Publicar chave canônica e índice único para rejeitar duplicata inversa não direcionada na mesma linha, preservando serviços explicitamente direcionados.
- [x] Testar referências, tempo positivo, padrão de `ativo`, extremos iguais e duplicatas diretas e inversas.
- [x] Verificar concorrência, executar validação estrita do OpenSpec e registrar os limites observados.
