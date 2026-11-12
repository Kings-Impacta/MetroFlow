# Sessão expirada e configuração ausente — 11/11/2026

## Escopo

Validar a rejeição de sessão expirada e a regra de ausência de configuração, sem remover a configuração de produção nem alterar malha, login, parâmetros, registros de usuários ou viagens. Foram usadas duas funções temporárias privadas, executadas pela API administrativa do Xano, sem criar endpoints públicos. O histórico das funções ficou desativado e nenhum token foi retornado ou persistido nas evidências. As funções foram removidas ao término.

## Expiração: HTTP real aos endpoints publicados

Como não havia token antigo disponível, o teste emitiu no próprio Xano um token autenticado válido com 15 segundos de duração, usando a versão de sessão atual de uma conta já utilizada nos testes. Isso não modificou `auth/login`, cuja validade permaneceu 86400 s (24 horas), nem a configuração de usuários.

O mesmo token foi usado antes e depois de uma espera de 18 segundos, sem adulteração, mudança de relógio ou redefinição da versão de sessão. A verificação posterior ocorreu 19,604 s após a emissão registrada.

| Endpoint | Antes do vencimento | Depois do vencimento |
|---|---|---|
| `auth/me` | HTTP 200 | HTTP 401 |
| `trajetos/buscar` | HTTP 200, sessão aceita | HTTP 401 |
| `viagens/confirmar`, com lista vazia de trechos | HTTP 400, entrada inválida com sessão aceita | HTTP 401 |

A lista vazia evitou criar uma viagem no controle anterior ao vencimento; não se tratou de confirmação válida. O teste demonstra a expiração efetiva de um token assinado e o bloqueio dos endpoints reais. Não equivale a aguardar as 24 horas de um token emitido pelo login normal, testar versão anterior da sessão ou observar o redirecionamento do navegador nesta rodada. Esse redirecionamento possui evidência histórica própria do P0.

## Configuração ausente: cálculo isolado no Xano

Foi extraída, sem modificar seu corpo, a função lambda do endpoint de busca publicado. A mesma função foi executada no Xano por uma função temporária privada que recebeu dados de referência em memória; não houve consulta que removesse ou substituísse `configuracao_lotacao`.

Os quatro cenários usam a mesma malha de referência, o mesmo relógio controlado de 11/11 e um cenário de ocupação reconstruído a partir da viagem 67. A indicação de substituição dessa viagem foi ajustada somente na entrada de teste para representar seu estado histórico ativo. Os resultados foram comparados à execução local da mesma função, inclusive o contrato completo de resposta.

| Cenário | Resultado | Tempo físico |
|---|---|---|
| Referência sem ocupação, com configuração | Linha 3 → Sé → Linha 1 | 1185 s |
| Controle com ocupação e configuração | Linha 11 → Luz → Linha 1 | 1625 s |
| Ocupação e configuração nula | Mesmo trajeto e resposta completa da referência principal | 1185 s |
| Ocupação e configuração omitida | Mesmo trajeto e resposta completa da referência principal | 1185 s |

Os quatro resultados remotos foram idênticos aos locais. O controle positivo mudou a rota, demonstrando que o caso nulo não passou apenas porque faltava conflito. A margem pública de um minuto permaneceu fora do tempo físico.

Isso valida no motor remoto a regra de ausência de configuração, preservando o registro real 1/1%. **Não é uma chamada HTTP ao endpoint público com o registro de configuração realmente ausente no banco.** Essa integração completa não foi executada e continua explicitamente separada; caso necessária, deve ocorrer em ambiente isolado com dados próprios ou com mock de teste, sem apagar a configuração de produção.

## Preservação e evidências

Backup do workspace e hashes dos dados anteriores, fora do Git: `outputs/sessao-configuracao-20261111/`. Evidências sem credenciais: `resultado-expiracao.json`, `resultados-remotos-configuracao.json` e `conferencia-final.json`. Os scripts e entradas restritas não integram a entrega documental.

A conferência final confirmou os 26 documentos de produção idênticos aos anteriores e hashes idênticos das nove tabelas, incluindo viagens. Nenhuma viagem foi criada. As duas funções temporárias foram removidas e o conjunto original de funções foi restaurado. A remoção inicial excedeu o tempo de resposta; a ausência efetiva foi conferida por leitura posterior, sem presumir sucesso pelo timeout. O token de teste expirou e o login normal permaneceu em 86400 s.
