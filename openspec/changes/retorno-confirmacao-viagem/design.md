## Context

O botão "Confirmar viagem" chama `PlanningState.confirm_trip`, que envia os trechos do resultado ao endpoint local `/api/planning/trip` por `rx.call_script`. O endpoint responde `204` em caso de sucesso, `401` para sessão inválida, `400` para viagem recusada e `502` ou `503` para falhas do serviço. Hoje `receive_trip_confirmation` só trata o `401`; os outros resultados não alteram a tela. Ver proposal.md para a motivação.

## Goals / Non-Goals

**Goals:**

- Mostrar o andamento e o resultado da confirmação usando somente o estado Reflex e o status HTTP já devolvido pelo endpoint local.
- Impedir confirmações repetidas do mesmo resultado, que reiniciariam a janela da viagem.

**Non-Goals:**

- Alterar o backend Python, o Xano ou o corpo das respostas.
- Recuperar a viagem ativa ao recarregar a página.

## Decisions

### Estado da confirmação no `PlanningState`

Adicionar `trip_status` (`idle`, `loading`, `confirmed`, `error`) e `trip_message`. `confirm_trip` só envia a requisição com resultado de sucesso e `trip_status` em `idle` ou `error`, e passa o estado para `loading`. A resposta muda para `confirmed` quando `ok` é verdadeiro e para `error`, com mensagem, nos demais casos, exceto `401`, que continua chamando `_unauthenticated`.

Alternativa considerada: um único booleano de confirmado. Ele não distingue envio em andamento de falha, e a interface precisa dos dois para desativar o botão e exibir o erro.

### Mensagens por status

| Status | Mensagem |
|---|---|
| `400` | "Não foi possível confirmar esta viagem. Busque o trajeto novamente." |
| `422` | Mesma mensagem do `400`, pois o corpo é montado pelo próprio resultado. |
| Demais, inclusive `0` (rede ou tempo esgotado) | "Não foi possível confirmar a viagem agora. Tente novamente." |

As mensagens são definidas na interface, como na busca de trajetos, e não reproduzem o `detail` recebido, para que nenhum texto interno chegue à tela.

### Respostas de resultados anteriores

`_clear_result` incrementa `_trip_request_id` e volta `trip_status` para `idle`. Uma nova busca, a troca ou inversão das estações e o logout já passam por `_clear_result`. `receive_trip_confirmation` descarta respostas cujo `request_id` difere do atual, como `receive_route` faz com `_request_id`. Assim, uma confirmação que termina depois de uma nova busca não marca o novo resultado como confirmado.

### Botão

O botão mantém o mesmo lugar no resultado. O texto vem de `rx.cond`: "Viagem confirmada", com ícone de confirmação, quando `trip_status` é `confirmed`, e "Confirmar viagem" nos demais casos. `loading` acompanha o estado `loading`; `disabled` vale para `loading` e `confirmed`. No estado confirmado, as cores seguem o selo verde "TRAJETO ENCONTRADO" para diferenciar do botão de ação. A mensagem de erro aparece logo abaixo, em um `rx.callout` vermelho com `role="alert"`, e o texto do botão é anunciado por uma região `aria-live="polite"`.

### Especificação

A delta modifica o requisito "Confirmação de viagem" da capacidade `concorrencia-rotas`, que ainda não está em `openspec/specs/`. A validação estrita aceita a delta, mas o arquivamento exige a especificação principal. Por isso, esta mudança só pode ser arquivada depois de `concorrencia-rotas`.

## Risks / Trade-offs

- [O botão desativado esconde a reconfirmação do mesmo trajeto, prevista em `concorrencia-rotas`] → Uma nova busca libera o botão, e a reconfirmação continua possível sem reiniciar a janela por engano.
- [O estado confirmado não sobrevive ao recarregamento da página] → Fora do escopo. O registro continua no Xano e uma nova confirmação apenas substitui a viagem ativa.
- [Respostas `204` sem corpo] → O estado considera somente `ok` e `status`, pois `request_script` já devolve `data: null` quando não há JSON.

## Migration Plan

Mudança apenas na interface. Para colocar em uso, basta publicar a nova versão do Reflex; para reverter, voltar ao commit anterior. Não há alteração de dados.
