# Incidente da tabela `trechos` — 26/10/2026

Registro do incidente no workspace Xano 149130, branch `v1`, fonte de dados
`live`. Os horários estão em UTC, com o horário de Brasília entre parênteses.
As evidências vêm do log de auditoria e do histórico de requisições da Metadata
API do Xano; nenhum token foi registrado.

## Resumo

Às 17:01:58 (14:01:58), uma alteração da tabela `trechos` pela Metadata API
substituiu o esquema por `id` e `created_at`. As colunas removidas levaram os
valores dos 207 registros da malha. Dois segundos antes, o endpoint
`POST trechos` havia perdido `auth = "usuarios"`. A autenticação e as colunas
foram restauradas no mesmo dia; **os valores dos trechos continuam perdidos** e
precisam ser reimportados.

## Linha do tempo

| Horário | Evento |
|---|---|
| 13:59 (10:59) | Leitura do workspace pelo Xano CLI para preparar a publicação de `concorrencia-rotas`; `trechos` íntegra. |
| 14:03 (11:03) | Duas simulações (`--dry-run`) sem alteração prevista em `trechos`. |
| 14:32 (11:32) | Outro cliente da Metadata API, na mesma conta, baixa o workspace. |
| 17:01:28 (14:01:28) | `PUT` do endpoint `POST trechos` recusado com `400`. |
| 17:01:56 (14:01:56) | Novo `PUT` do endpoint aceito; o endpoint fica sem autenticação. |
| 17:01:58 (14:01:58) | `PUT /table/882609` aceito; a tabela fica só com `id` e `created_at`. |
| 17:03 (14:03) | Consultas aos registros de `trechos`. |
| 17:09 (14:09) | Envio de vários documentos recusado com `400`. |
| 17:11 (14:11) | `PUT` do esquema completo de `trechos` recusado com `500`. |
| 17:27 (14:27) | Envio da publicação de `concorrencia-rotas` recusado com `400` ao tentar recriar as colunas de `trechos`; nada foi aplicado. |
| 18:07 (15:07) | A recolocação de `tempo_estimado` como coluna opcional devolveu `null` em todos os registros, confirmando a perda dos valores. |
| 18:12:54 (15:12:54) | `POST trechos` restaurado com a versão publicada antes do incidente, incluindo `auth = "usuarios"`. |
| 18:15:22 (15:15:22) | Colunas de `trechos` recriadas com a definição anterior, sem os índices únicos. |
| 18:17:06 (15:17:06) | Publicação de `concorrencia-rotas`: duas tabelas, `viagens/confirmar` e a nova versão de `trajetos/buscar`. |

## Causa provável

As duas alterações de 17:01 enviaram ao `PUT` da Metadata API a definição em
XanoScript no campo `xanoscript`. Para a tabela, essa definição continha todas
as colunas, mas o resultado foi um esquema vazio; para o endpoint, continha
`auth = "usuarios"`, mas a autenticação foi removida. O comportamento indica que
esse `PUT` não aplica o campo `xanoscript` e substitui o esquema e a
autenticação por valores padrão.

O conteúdo enviado sugere uma alteração em andamento: envolver a gravação de
`POST trechos` em `try_catch` para tratar colisões concorrentes e remover o
índice único composto `estacao_origem_id + estacao_destino_id + linha_id`,
mantendo o índice de `chave_integridade`. Essa alteração **não foi reaplicada**;
ela deve passar por uma mudança OpenSpec própria.

## Estado após a contenção

- `POST trechos` exige sessão novamente; chamadas sem token recebem `401`.
- A tabela `trechos` tem as colunas anteriores. Os 207 registros existem, mas
  com valores padrão (`0`, texto vazio, `ativo = true`), e por isso a busca não
  encontra trajetos.
- Os índices únicos de `chave_integridade` e da combinação origem, destino e
  linha **não existem**: com os valores padrão, todos os registros seriam
  iguais e a criação falharia.

## Pendências

1. Reimportar os 207 registros a partir da exportação de 08/10/2026 citada em
   [auditoria-integridade-2026-10-08.md](auditoria-integridade-2026-10-08.md),
   enviada por e-mail à conta do workspace, ou pedir ao suporte do Xano a
   recuperação dos dados. O repositório não contém cópia completa da malha;
   [alteracoes-malha-2026-09-18.md](alteracoes-malha-2026-09-18.md) registra
   apenas parte dos tempos.
2. Depois da reimportação, recriar os dois índices únicos e repetir a auditoria
   de integridade com `executar_backfill=false`.
3. Executar a validação pendente de
   [concorrencia-rotas](rascunhos/concorrencia-rotas/README.md) com uma sessão
   real.
4. Evitar alterações simultâneas no Xano a partir de ferramentas diferentes e
   não usar o campo `xanoscript` no `PUT` de tabelas e endpoints da Metadata
   API. Para publicar XanoScript, usar `xano workspace push` precedido de
   `--dry-run` sobre um `pull` recente.
