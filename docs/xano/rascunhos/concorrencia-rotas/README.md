# XanoScript da mudança `concorrencia-rotas`

Estado em 26/10/2026: **publicado** no workspace 149130, branch `v1`, pelo
Xano CLI (`xano workspace push`). Os arquivos desta pasta são cópias obtidas
com `xano workspace pull` logo após a publicação, já com o `guid` atribuído pelo
Xano. O nome da pasta foi mantido porque os testes automatizados leem as funções
de cálculo (`|lambda:"…"`) destes arquivos e as executam com Node.js.

| Arquivo | Conteúdo |
|---|---|
| `viagens_confirmadas.xs` | Tabela das viagens confirmadas: usuário, confirmação, fim da janela, trechos em ordem e indicação de substituição. |
| `configuracao_lotacao.xs` | Tabela com `minimo_usuarios` e `percentual_lotacao`; a busca lê o registro `id = 1`. |
| `viagens_confirmar_post.xs` | `POST viagens/confirmar`, autenticado, no grupo `planejamento`. |
| `trajetos_buscar_post.xs` | `POST trajetos/buscar` publicado, com lotação e substituição do trajeto. |

A captura de 18/09/2026 em `../planejamento/trajetos_buscar_post.xs` é histórica:
não contém as precondições de sessão do P4 nem a lotação.

## Regras implementadas nas funções

- A confirmação recebe somente `id`, `estacao_origem_id` e `estacao_destino_id`
  de cada trecho. O Xano confere se o trecho está ativo, se o sentido existe no
  cadastro (trechos direcionados só no sentido gravado) e se os trechos são
  consecutivos. `tempo_estimado`, `tipo` e `servico_id` são copiados do cadastro.
- A janela vai da confirmação até a confirmação mais a soma de `tempo_estimado`,
  sem os 600 segundos por baldeação. A viagem é ativa enquanto
  `confirmada_em <= agora < fim_janela` e não foi substituída.
- O intervalo de cada trecho é `[início, início + tempo_estimado)`, em que o
  início soma o tempo dos trechos anteriores, inclusive integrações a pé.
- Só trechos com `tipo = ferroviario` e sem `servico_id` recebem ocupação.
- A viagem de quem busca fica fora da ocupação e do total. Se houver mais de uma
  viagem ativa do mesmo usuário (por exemplo, duas confirmações simultâneas),
  conta apenas a mais recente.
- Um trecho fica lotado em um sentido quando `ocupação >= minimo_usuarios` e
  `ocupação × 100 >= percentual_lotacao × total`.
- Sem o registro de configuração, com `minimo_usuarios < 1` ou com
  `percentual_lotacao` fora de `(0, 100]`, nenhum trecho é considerado lotado.
- Se o trajeto principal usa um trecho lotado, a busca repete o cálculo sem
  todos os trechos lotados naqueles sentidos e devolve esse caminho, sem limite
  de tempo extra. Sem caminho, devolve o principal. A resposta tem a mesma forma
  nos dois casos.
- As verificações de sessão de `viagens/confirmar` são as mesmas publicadas em
  `trajetos/buscar` (usuário ativo, e-mail verificado e
  `$auth.extras.versao_sessao`), com erro `unauthorized`.

## Publicação de 26/10/2026

1. A simulação (`--dry-run`) sobre o workspace baixado na hora listou somente a
   criação das duas tabelas e de `viagens/confirmar` e a atualização de
   `trajetos/buscar`. O envio aplicou essas quatro operações.
2. A cópia obtida após o envio difere do arquivo enviado apenas na formatação
   aplicada pelo Xano. As funções de cálculo publicadas são idênticas às
   testadas.
3. O registro `id = 1` de `configuracao_lotacao` foi criado com
   `minimo_usuarios = 1` e `percentual_lotacao = 1`, **valores de teste**: com
   eles, qualquer outra viagem ativa já torna o trecho lotado. A equipe deve
   definir os valores definitivos.
4. Chamadas sem token a `viagens/confirmar` e `trajetos/buscar` foram recusadas
   com `401`.

A publicação coincidiu com o [incidente da tabela `trechos`](../../incidente-trechos-2026-10-26.md).
Enquanto a malha não for reimportada, a busca não encontra trajetos e a
validação abaixo não pode ser concluída.

## Validação pendente no Xano

Os testes locais não cobrem o comportamento do ambiente remoto. Após a
reimportação da malha, repetir com uma sessão real, sem registrar o token:

| Caso | Resultado esperado |
|---|---|
| Confirmação válida | `{"confirmada": true}` e um registro com `substituida = false` |
| Nova confirmação do mesmo usuário | registro anterior com `substituida = true` e `substituida_em` preenchido |
| Trecho inexistente, desconexo ou em sentido proibido | `inputerror`, sem registro |
| Sessão expirada ou de versão anterior | rejeição sem registro |
| Busca sem viagens ativas | mesmo trajeto da versão anterior |
| Trecho do trajeto principal lotado, com alternativa | resposta com o caminho alternativo e sem campos novos |
| Trecho lotado sem alternativa | trajeto principal |
| Configuração ausente | trajeto principal |

Também é preciso conferir se o `db.transaction` impede duas viagens ativas para
o mesmo usuário em confirmações simultâneas. A busca já considera somente a
viagem mais recente de cada usuário.
