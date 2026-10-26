## Why

A mudança `concorrencia-rotas` definiu que a interface não exibe aviso após a confirmação e mantém o botão disponível. Na validação com sessões reais, em 26/10/2026, os usuários não conseguiram distinguir uma confirmação registrada de uma falha. Também confirmaram a mesma viagem várias vezes, e cada nova confirmação reiniciou a janela da viagem anterior. A própria mudança registrou esse risco e deixou em aberto o que mostrar quando a confirmação falha.

## What Changes

- Enquanto a confirmação é enviada, o botão "Confirmar viagem" fica desativado e indica carregamento.
- Após a confirmação registrada, o botão fica desativado e passa a exibir "Viagem confirmada" até que outro resultado seja apresentado.
- Quando a confirmação falha por um motivo que não seja a sessão expirada, a interface exibe uma mensagem de erro e o botão volta a ficar disponível.
- A sessão expirada continua levando ao login.
- Uma nova busca, a troca de estações ou o logout descartam o retorno de uma confirmação ainda pendente e liberam o botão para o novo resultado.
- A lotação estimada e a substituição do trajeto continuam fora da interface.

## Fora do escopo

- Alterações nos endpoints do Xano e no endpoint local `/api/planning/trip`, cujo contrato permanece o mesmo.
- Cancelamento manual de viagem e indicação da viagem ativa depois de recarregar a página ou em outra sessão.
- Exibição da lotação ou de qualquer aviso de substituição do trajeto.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `concorrencia-rotas`: o requisito "Confirmação de viagem" deixa de proibir o aviso após a confirmação e passa a exigir o retorno no botão e a mensagem de erro em caso de falha. A especificação desta capacidade está na mudança `concorrencia-rotas`, ainda não arquivada.

## Impact

Reflex: estado do planejador (`PlanningState`) e botão de confirmação no resultado do trajeto. Testes de estado e de componentes do planejamento. Documentação: modelo de domínio, visão geral e registro da mudança `concorrencia-rotas`. Sem impacto no backend Python, no Xano ou no contrato das APIs.
