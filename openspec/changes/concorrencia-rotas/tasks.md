## Xano

- [x] Criar a tabela de viagens confirmadas com usuário, momento da confirmação, trechos em ordem com sentido e `tempo_estimado`, e indicação de substituição.
- [x] Criar a tabela de configuração com o mínimo de usuários e o percentual de lotação.
- [x] Criar o endpoint autenticado de confirmação que obtém o usuário da sessão, encerra a viagem ativa anterior e registra a nova.
- [x] Alterar `trajetos/buscar` para calcular a lotação somente nos trechos ferroviários, por trecho e sentido, desconsiderar a viagem ativa de quem busca e substituir o trajeto quando houver trecho lotado.
- [x] Garantir que a resposta pública não contenha lotação nem indicação de substituição.
- [x] Garantir que nenhuma resposta pública devolva registros de viagens confirmadas.

## Backend Python e Reflex

- [x] Criar o endpoint local de confirmação com revalidação de sessão e validação do corpo, sem expor tokens.
- [x] Adicionar o botão de confirmação ao resultado do trajeto, sem aviso após a confirmação e mantendo o botão disponível.

## Testes

- [x] Testar janela da viagem e intervalo por trecho sem a penalidade de baldeação.
- [x] Testar substituição da viagem ativa e saída imediata da contagem.
- [x] Testar reconfirmação do mesmo trajeto, que substitui a viagem e reinicia a janela.
- [x] Testar lotação com mínimo e percentual, isolados e combinados, incluindo valores iguais aos parâmetros, e sentidos independentes.
- [x] Testar que trechos de integração a pé e de serviços especiais não recebem ocupação, mas contam no tempo da janela e dos intervalos seguintes.
- [x] Testar exclusão da viagem ativa de quem busca.
- [x] Testar trajeto sem lotação, alternativa disponível e alternativa indisponível.
- [x] Testar confirmação sem sessão válida e ausência de dados de lotação na resposta.
- [x] Testar que a interface não exibe aviso após a confirmação e mantém o botão disponível.
- [x] Testar que nenhuma resposta pública devolve registros de viagens confirmadas.

## Documentação e validação

- [x] Atualizar o roadmap, a visão geral e o modelo de domínio com esta entrega.
- [x] Executar a suíte de testes e a validação estrita do OpenSpec e registrar os limites da validação.
- [ ] Validar no Xano, com uma sessão real e a malha reimportada, os casos listados em `docs/xano/rascunhos/concorrencia-rotas/README.md`.
