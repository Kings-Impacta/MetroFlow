# Comparação dos rascunhos Xano — 13/09/2026

Os três arquivos locais de `xano/api/planejamento/` são rascunhos históricos.
Eles não são uma exportação fiel do ambiente remoto nem arquivos prontos para
importação, push ou sincronização com o Xano.

Destino documental proposto: `docs/xano/rascunhos/planejamento/`, preservando o
conteúdo original de cada arquivo. O código usado pela aplicação Python não
depende desses arquivos `.xs`.

## Origem da comparação

Inspeção somente em leitura da sessão autenticada de Raphael's Workspace,
workspace 149130, branch v1, fonte de dados live, grupo planejamento 431173.

- [Grupo planejamento](https://x8ki-letl-twmt.n7.xano.io/workspace/149130-0/api/431173/dashboard)
- [GET estacoes, ID 4035908](https://x8ki-letl-twmt.n7.xano.io/workspace/149130-0/api/431173/query/4035908)
- [POST trajetos/buscar, ID 4035909](https://x8ki-letl-twmt.n7.xano.io/workspace/149130-0/api/431173/query/4035909)

O texto remoto foi lido pelo botão XanoScript de cada endpoint e copiado do editor
para comparação. Não foram usados Save, Run, Publish, importação ou alteração de
dados. Isso é uma captura do código exibido na interface, não um backup de banco
ou exportação oficial com identificadores, metadados e versões publicadas.

## Resultado por arquivo

| Arquivo original | Resultado |
|---|---|
| `api_group.xs` | Nome, descrição e canonical correspondem ao grupo e à URL já observados na interface. Não houve exportação completa dos metadados do grupo. |
| `estacoes_get.xs` | Autenticação em `usuarios`, filtros de ativos, campos e função que monta a resposta coincidem. O local contém `sort = {nome: "asc"}`; o texto remoto não contém `sort`. Portanto, não assumir ordem alfabética no remoto. |
| `trajetos_buscar_post.xs` | Métodos, dois inputs, autenticação, validações, filtros e função de cálculo coincidem nos pontos comparados. Existem diferenças de representação descritas abaixo; não são arquivos textualmente iguais. |

As strings completas de `lambda` foram extraídas do local e das capturas do
editor e comparadas literalmente: iguais para estações (326 caracteres) e para
trajetos (2544 caracteres).

Diferenças adicionais observadas:

- O remoto explicita `return = {type: "list"}` nas consultas; o rascunho omite.
- O rascunho explicita `type: "inner"` nas junções; o texto remoto omite esse
  atributo. Esta revisão não atribui uma semântica padrão à omissão: a garantia
  de equivalência das junções depende da definição efetiva no Xano.
- Na validação de estações ativas, o remoto usa `$origem.ativa && $destino.ativa`;
  o rascunho compara ambos com `true`. São equivalentes sob o contrato de campos
  booleanos válido; a revisão não revalidou o schema do banco.
- Há diferenças de aspas em identificadores, posição de `where`/`eval`, listas,
  espaçamento e quebra de linha.
- Nem os rascunhos nem o texto desses editores contêm GUIDs. A ausência de GUID
  no editor não demonstra que uma exportação oficial também os omita.

Não foi alterada a ordenação no Xano para fazer o remoto coincidir com o rascunho.
Caso a interface exija ordem alfabética, a decisão deve ser implementada e testada
explicitamente na integração futura.

## Limites e pendências

A identidade das funções não prova o algoritmo em todos os grafos. Continuam
pendentes os testes de desempate, consulta inversa, ausência de caminho e cenários
de erro apontados no registro de validação do projeto.

O endpoint remoto usa `notfound` tanto para estação inexistente quanto para
ausência de caminho, confirmando no código exibido a ambiguidade já apontada no
cliente Python, que transforma qualquer HTTP 404 de busca em `None`.

Uma futura gestão de código Xano como fonte versionada de implantação exigirá
uma exportação oficial identificada, comparação de metadados e um fluxo próprio
de revisão. Os rascunhos nesta pasta são documentação histórica.

## Integridade dos arquivos originais

SHA-256 calculado sobre os bytes originais antes da movimentação local:

| Arquivo | SHA-256 |
|---|---|
| `api_group.xs` | `24459B23C9FD9979B4DAB8D4AD34747E2DC086FF17FBDF6AF02E779760735C0F` |
| `estacoes_get.xs` | `48A2B67116312455A841D9343BD31062F5B926B904D06C572D79F1A23CE208BE` |
| `trajetos_buscar_post.xs` | `22600C330C4E54E88FF0777F5E8C517616A1D49C00C9D85B5DF75106939E8E6F` |

Esses hashes documentam os arquivos locais lidos. Não são hashes do backend
remoto. O Git pode normalizar finais de linha ao armazenar arquivos textuais.
