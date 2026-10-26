## 1. Estado da confirmação

- [x] 1.1 Adicionar `trip_status` e `trip_message` ao `PlanningState` e zerá-los em `_clear_result`, que também incrementa `_trip_request_id`; verificar com teste de estado que uma nova busca, a troca de estações e o logout voltam o botão para `idle`.
- [x] 1.2 Fazer `confirm_trip` passar para `loading` e ignorar novos cliques em `loading` e `confirmed`; verificar com teste que o segundo clique não gera requisição.
- [x] 1.3 Tratar a resposta em `receive_trip_confirmation`: `confirmed` com `ok`, `error` com mensagem por status, `401` levando ao login e descarte de respostas com `request_id` antigo; verificar com testes para `204`, `400`, `422`, `502`, `503`, `0`, `401` e resposta antiga.

## 2. Botão no resultado

- [x] 2.1 Alterar `_confirm_trip_button` para exibir "Viagem confirmada" com ícone quando confirmado, indicar carregamento, desativar em `loading` e `confirmed` e mostrar a mensagem de erro abaixo do botão; verificar com teste de componente que o texto, `loading`, `disabled` e o alerta dependem do estado.
- [x] 2.2 Conferir que o resultado continua sem textos de lotação ou de substituição do trajeto; verificar com o teste de componente existente.

## 3. Documentação e validação

- [x] 3.1 Atualizar o modelo de domínio, a visão geral, o roadmap e o registro da mudança `concorrencia-rotas` (resposta à questão aberta do design) para descrever o retorno da confirmação; verificar por leitura que nenhum documento afirma que a interface não exibe aviso.
- [x] 3.2 Executar a suíte completa com `pytest`, `reflex compile --dry` e `openspec validate --all --strict`, e registrar os resultados.
  - 26/10/2026: `pytest` com 199 testes e 58 subtestes aprovados; `reflex compile --dry` concluído com sucesso; `openspec validate retorno-confirmacao-viagem --strict` válido.
  - `openspec validate --all --strict` reprova três especificações principais anteriores a esta mudança (`auditoria-sessao`, `integridade-trechos` e `validacao-planejamento`) porque o `Purpose` delas ainda é o texto provisório do arquivamento. Esta mudança não altera esses arquivos.
  - Os testes não cobrem a renderização no navegador nem a resposta real do Xano; esses pontos ficam na tarefa 3.3.
- [ ] 3.3 Validar no navegador, com sessão real, os estados "Confirmar viagem", carregamento, "Viagem confirmada" e erro, e conferir no Xano que um único registro foi criado por confirmação.
- [ ] 3.4 Arquivar esta mudança somente depois do arquivamento de `concorrencia-rotas`, porque a delta modifica um requisito que ainda não está em `openspec/specs/`.
