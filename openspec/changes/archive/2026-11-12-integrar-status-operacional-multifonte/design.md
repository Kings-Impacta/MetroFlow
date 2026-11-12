## Contexto e escopo

A entrega é informativa e independente do planejamento. O endpoint autenticado `/api/planning/line-status` normaliza dados públicos; a busca e o registro automático não consultam fontes de status. Tokens de sessão continuam em cookie HttpOnly.

## Fontes e configuração

- Metrô: quadro incorporado no site oficial, observado com linhas 1, 2, 3, 4, 5, 15 e 17.
- CPTM: JSON público observado com 10, 11 e 12; 13 só é aceita quando efetivamente retornada.
- Motiva: última ocorrência de cada aba das linhas 8 e 9. Vincular abas e painéis por identificadores acessíveis e selecionar a maior data, sem inferir pela cor ou posição.
- Direto dos Trens: adaptador preparado para a API autenticada, desativado sem flag e token; não coletar o site nem reutilizar credenciais internas.

As fontes são desligadas por padrão. `iniciar-status-local.ps1` habilita somente Metrô/CPTM/Motiva no processo local e restaura as variáveis ao sair. ARTESP e Azure não participam da fábrica atual. A precedência é DDT, CPTM, Metrô, Motiva: preferir informação atual; sem ela, conservar o último dado com identificação própria. Linhas 6/7/13 e serviços especiais sem resposta permanecem indisponíveis; não herdar situação de serviços regulares.

## Cache e retenção

SQLite persistente compartilhado entre usuários e processos do mesmo servidor, com reserva transacional antes da rede. Uma tentativa a cada cinco minutos e no máximo 12 por hora por fonte, política interna conservadora, não cota contratual. Respeitar Cache-Control, Age, Retry-After e ausência de permissão de gravação.

Validade vencida não significa proibição de armazenamento. Conservar a última observação armazenável até novo retorno válido, mantendo horários originais. Respostas vazias, futuras, duplicadas ou inválidas não substituem o último retorno. Em resposta parcial, atualizar somente as linhas retornadas e marcar as anteriores ausentes como desatualizadas. no-store/no-cache/private impedem gravar a nova observação, mas não apagam uma observação anterior cujo armazenamento era permitido.

Sem dado anterior, apresentar indisponibilidade; nunca fabricar normalidade. A consulta em andamento não apaga cartões. Falha do banco ou da fonte não é propagada ao planejamento. Várias máquinas exigem cache/coletor central antes de compartilhar uma credencial.

## Transporte e credenciais

Todas as chamadas usam HTTPS com validação de certificado, sem redirects. Credenciais DDT ficam exclusivamente no backend, em transporte dedicado à origem fixa, sem logger de URLs autenticadas; o cache usa hash da credencial, não o token.

O diagnóstico do Metrô reproduziu timeout de leitura com cinco segundos. IPv6 foi mais lento na comparação observada, mas também houve timeout IPv4; não se atribui a falha exclusivamente à família de rede. Somente o Metrô usa saída IPv4, conexão de cinco segundos, leitura de quinze por operação e orçamento de vinte segundos verificado durante a recepção. Não fixar IP remoto nem alterar IPv6 no sistema. Motiva e CPTM preservam seus limites. Não repetir imediatamente GET em falha; registrar apenas fonte e categoria segura do erro.

## Interface

O resumo lista linhas únicas na ordem do percurso, alinhado à direita das métricas. Cada embarque mostra apenas sua linha. Número/nome, bolinha e texto indicam o último estado: verde normal, amarelo restrição, vermelho interrupção, cinza encerramento/desconhecido/indisponível. A cor não é o único sinal.

Por decisão do usuário, o indicador compacto não inclui sufixo de idade. Validade, fonte e datas continuam no estado e no painel detalhado. Sem código no contrato legado, mostrar o nome recebido sem inferir status. Caminhadas não recebem indicador ferroviário. Um único ciclo por painel relê o backend a cada minuto e é cancelado ao desmontar; respostas antigas são descartadas. Não há uma consulta extra por indicador.

## Validação e limites

A implementação local foi testada com consultas reais, falha prolongada simulada, reinício e leituras concorrentes do cache. Em 11/11, a aba logada mostrou coletas Metrô às 11:35, 11:40 e 11:46, com atualização automática observada. A busca interna seguiu pela Sé/Linha 1 e o usuário confirmou outra conta pelas linhas 4/2. Não houve auditoria adicional de IDs ou sobreposição diretamente no Xano nessa rodada.

O coletor experimental do site Direto dos Trens foi bloqueado por verificação interativa e não integra esta entrega. A API autenticada continua pendente de token e condições aplicáveis. A validação não promete disponibilidade contínua de terceiros nem lotação oficial.

## Decisão final de escopo — 12/11/2026

Entrega encerrada com escopo reduzido, por autorização do usuário. As pendências não executadas foram retiradas do compromisso atual e preservadas como melhorias futuras em `docs/melhorias-futuras-malha-status.md`; consulte também as limitações no checklist. O texto anterior preserva a proposta e as decisões históricas, não representa certificação de todas as hipóteses nem garantia de disponibilidade pública. Esta revisão é somente documental.
