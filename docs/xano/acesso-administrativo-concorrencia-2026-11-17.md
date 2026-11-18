# Acesso administrativo e concorrência — 17/11/2026

Base: main `b135aca8e2600cc546a10fbb3ef7eadff417755d` (PR #51). A revisão anterior confirmou passageiro bloqueado no painel, administrador com indicadores e estações, localização real no Chrome após permissão e renovação de Metrô/CPTM. Esta etapa investiga a instabilidade e audita as viagens; não modifica o Xano.

## Diagnóstico e correção local

O histórico nativo mostrou HTTP 200 para a conta administradora: leituras normalmente abaixo de um segundo, mas também 43,432, 57,682, 111,129 e 202,092 segundos. O timeout do cliente é 10 segundos e a chamada do navegador tem limite de 35 segundos. A evidência identifica latência observada, não prova a causa interna do fornecedor ou do ambiente. Não houve evidência de perda da concessão nessas chamadas; o painel voltou a carregar sem alterar permissão.

O cliente corrigido faz no máximo uma repetição de GET em timeout/falha de rede ou 502/503/504 sem Retry-After, com pausa de um segundo. 401/403/429, Retry-After, contrato inválido e todos os POST não são repetidos. O endpoint Xano revalida o acesso a cada tentativa. Falha persistente é apresentada como indisponibilidade do serviço, sem inferir falta de papel administrativo e sem exibir dados protegidos antes de resposta autorizada. O tempo de resposta externo continua fora do controle da aplicação; a recuperação limitada não garante sucesso durante lentidão prolongada.

## Registros reais auditados

Os registros 89 e 90 pertencem a usuários distintos, com 6,960 segundos entre confirmações. Ambos estavam não substituídos na exportação e suas janelas se sobrepuseram; não se afirma que ainda estejam ativos no momento da leitura posterior. As confirmações anteriores 86/87/88 da mesma conta foram substituídas por confirmações posteriores.

| Registro | Caminho observado | Tempo físico | Total estimado com margem | Baldeações |
|---|---|---|---|---|
| 89 | Linha 3 → Sé → Linha 1 | 1155 s | 1215 s (21 min arredondados) | 1 |
| 90 | Linha 3 → República → Linha 4 → Paulista/Consolação → Linha 2 | 1665 s | 1725 s (29 min arredondados) | 2 |

A função de busca e o validador de confirmação **exportados do Xano** foram executados localmente com o relógio reconstruído dos registros, as capacidades do cliente e a situação histórica das substituições. Foram reproduzidos integralmente os trechos, os padrões de trem, cada início previsto e `fim_janela`. Busca e registro usam a versão `ebe34d59abdefc843e976afe160630f9b8ba37c5ca5c66885a0c1656fab333bb`. A tabela não guarda versão em campo próprio; a confirmação deriva da reprodução com a função publicada, não da leitura de um campo inexistente.

Para a segunda busca, o principal tinha 1155 s. A alternativa acrescentou 510 s (8min30), abaixo de `min(540, 1155 × 45%) = 519,75 s`, com uma baldeação extra. A exposição prevista caiu de 885 para 350 s: redução de 60,45%, acima dos 40% mínimos. A margem pública foi 60 s uma única vez e não ampliou a ocupação. A preferência pelo Metrô e os limites permaneceram no cálculo publicado, sem alterações.

A auditoria executou primeiro o corpo exato e depois uma cópia local instrumentada para expor as medidas internas, conferindo respostas públicas idênticas. Nada foi instrumentado ou publicado no Xano. Essa reprodução complementa os registros HTTP reais; não constitui um novo teste HTTP nativo nem certifica toda combinação de carga.

## Preservação e validação

- Somente leituras no Xano; backup de código anterior obtido sem exportar variáveis de ambiente.
- Oito tabelas (malha, disponibilidade e configuração de lotação) conferidas antes/depois com hashes idênticos.
- Suíte direcionada: 134 testes e 22 subtestes aprovados.
- Suíte completa: 440 testes e 119 subtestes aprovados; um aviso de depreciação já existente do TestClient.
- Compilação Reflex `--dry`: concluída; sem atualização de dependências. O arquivo gerado de lock alterado pelo compilador foi restaurado ao conteúdo original.
- OpenSpec estrito: 16 itens aprovados, incluindo a mudança de recuperação.
- Instalação/reinício executados pelo usuário em 17/11; os dois arquivos alterados foram comparados por hash normalizado e correspondem à correção validada. A recarga da janela administrativa apresentou indicadores apurados às 22:18:39 e depois às 22:19:24 de 17/11. A atualização manual final ainda precisa ser concluída após novo login: em 18/11, a janela anônima estava em `/login`. Não se atribui o motivo do redirecionamento sem evidência adicional.

A pendência anterior de configuração ausente permanece validada por **HTTP local isolado**, não pelo runtime nativo do Xano. Nenhuma alteração da situação de estação, teste administrativo de escrita, concessão ou revogação foi realizada aqui. Os parâmetros demonstrativos 1 usuário/1% permaneceram iguais.

Evidências sanitizadas: [auditoria](evidencias/auditoria-concorrencia-2026-11-17.json) e [hashes](evidencias/preservacao-malha-2026-11-17.json). Dados brutos e credenciais não integram a entrega.

## Validação final em sessão real — 18/11/2026

Após novo login administrativo na janela anônima do Chrome, o painel carregou normalmente. A apuração inicial foi `18/11/2026 às 20:18:26`. O clique em **Atualizar indicadores** produziu nova apuração às **20:18:56**, sem erro de verificação de acesso, mantendo a sessão autorizada e a lista de estações.

Foram observadas 188 estações ativas, zero inativas, 17 linhas e 213 trechos cadastrados ativos. O critério demonstrativo continuou em 1 usuário/1%. Não foram acionados controles de ativação/inativação, concessão ou revogação. A leitura de zero viagens ativas é uma fotografia da apuração atual; não invalida as janelas históricas dos registros 89/90 já auditados.

A instalação dos dois arquivos corrigidos foi conferida por hash e o usuário reiniciou o servidor. O ensaio conclui a validação funcional da abertura e atualização manual na versão local corrigida; não reproduziu intencionalmente lentidão do fornecedor nem prova ausência de falhas futuras. As falhas transitórias e as recusas de autorização continuam cobertas pelos testes simulados documentados acima. A correção ainda não foi entregue à main.
