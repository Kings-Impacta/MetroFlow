## Xano

- [x] Criar a tabela de viagens confirmadas com usuário, momento da confirmação, trechos em ordem com sentido e `tempo_estimado`, e indicação de substituição.
- [x] Criar a tabela de configuração com o mínimo de usuários e o percentual de lotação.
- [x] Criar o endpoint autenticado de confirmação que obtém o usuário da sessão, encerra a viagem ativa anterior e registra a nova.
- [x] Alterar `trajetos/buscar` para calcular a lotação somente nos trechos ferroviários, por trecho e sentido, desconsiderar a viagem ativa de quem busca e substituir o trajeto quando houver trecho lotado.
- [x] Garantir que a resposta pública não contenha lotação nem indicação de substituição.
- [x] Garantir que nenhuma resposta pública devolva registros de viagens confirmadas.

## Backend Python e Reflex

- [x] Criar o endpoint local de confirmação com revalidação de sessão e validação do corpo, sem expor tokens.
- [x] Confirmar automaticamente o trajeto após uma busca bem-sucedida, sem exibir botão adicional.

## Testes

- [x] Testar janela da viagem e intervalo por trecho sem a penalidade de baldeação.
- [x] Testar substituição da viagem ativa e saída imediata da contagem.
- [x] Testar reconfirmação do mesmo trajeto, que substitui a viagem e reinicia a janela.
- [x] Testar lotação com mínimo e percentual, isolados e combinados, incluindo valores iguais aos parâmetros, e sentidos independentes.
- [x] Testar que trechos de integração a pé e de serviços especiais não recebem ocupação, mas contam no tempo da janela e dos intervalos seguintes.
- [x] Testar exclusão da viagem ativa de quem busca.
- [x] Testar trajeto sem lotação, alternativa disponível e alternativa indisponível.
- [x] Testar confirmação sem sessão válida e ausência de dados de lotação na resposta.
- [x] Testar que a busca dispara uma única confirmação automática e a interface não exibe botão adicional.
- [x] Testar que nenhuma resposta pública devolve registros de viagens confirmadas.

## Documentação e validação

- [x] Atualizar o roadmap, a visão geral e o modelo de domínio com esta entrega.
- [x] Executar a suíte de testes e a validação estrita do OpenSpec e registrar os limites da validação.
- [x] Concluir a matriz com as evidências HTTP remotas de sessão/entradas/viagens e, para configuração ausente, a integração HTTP local isolada aceita pelo usuário em 12/11. Não declarar execução HTTP nativa do Xano para esse último caso. Ver `docs/xano/http-local-configuracao-ausente-2026-11-12.md`.

## Evidência real de 09/11/2026

- [x] Confirmar duas contas distintas, registro automático e substituição da viagem anterior com a calibração publicada.
- [x] Confirmar conflito temporal e alternativa por República dentro dos limites aprovados (registros 52/53, HTTP 200).
- [x] Validar configuração realmente ausente por HTTP local com SQLite descartável, cliente real e cálculo exportado: oito casos aprovados em 12/11, sem produção. A regra também foi executada no motor remoto; a camada HTTP nativa do Xano continua não testada, como limitação conhecida e não como execução alegada.
- [x] Verificar confirmações simultâneas do mesmo usuário por HTTP autenticado; falha 70/71 e 75/76 corrigida com bloqueio por conta, reteste 81/82 aprovado em 11/11. Ver `docs/xano/exclusividade-viagens-2026-11-11.md`.

Evidências e pendências classificadas em `docs/xano/fechamento-trajetos-concorrencia-2026-11-09.md`. Esse estado era o da revisão anterior; o fechamento pelo escopo HTTP local aceito está registrado na atualização de 12/11 ao final.

## Reteste de 11/11/2026

- [x] Auditar registros 67/68 de contas distintas e reproduzir calibração e limites com o código publicado: Linha 3/Sé/Linha 1 e Linha 11/Luz/Linha 1. Evidências em `docs/xano/reteste-main-status-concorrencia-2026-11-11.md`. Essa rodada não encerrava a matriz; a simultaneidade foi concluída em 81/82 e a configuração ausente posteriormente em HTTP local, com os limites explicitados ao final.

## Expiração e ausência de configuração em 11/11/2026

- [x] Confirmar expiração de token assinado de teste em HTTP real: aceito antes do vencimento e 401 depois em auth/me, busca e confirmação, sem mudar as 24 h do login normal.
- [x] Validar configuração nula e omitida no cálculo exato publicado, executado isoladamente no Xano, com controle positivo de ocupação e resultados completos iguais aos locais.

Evidência e limites em `docs/xano/sessao-expirada-configuracao-ausente-2026-11-11.md`. O item amplo de matriz remota não implica retirar a configuração de produção: a integração HTTP com o registro realmente ausente não foi executada. Token de versão de sessão anterior também não foi testado nesta rodada.

## Encerramento da pendência por HTTP local — 12/11/2026

O usuário solicitou execução local isolada para concluir o caso de configuração ausente. Os oito casos passaram por socket HTTP, com o cliente real, SQLite temporário e lambda exportada. O registro local foi realmente excluído e a rota principal foi mantida, enquanto o controle ocupado/configurado produziu alternativa. Nenhuma chamada ao Xano ou alteração em produção.

A aceitação do método local revisa o critério de integração desta pendência; não transforma o ensaio em HTTP nativo do Xano. Esse último permanece não executado, com limitação expressa em `docs/xano/http-local-configuracao-ausente-2026-11-12.md`. Nenhum teste de versão anterior de sessão, primeira viagem simultânea ou rollback sob carga foi acrescentado por este ensaio.
