# Persistência de status — integração em 24/11/2026

## Estado atual

A tabela `status_operacional_fontes` (918028), o grupo `status_operacional` (441482), GET `snapshot` (4137646), POST `controle` (4137645) e a função privada `status_operacional/inicializar` foram instalados em 24/11 após backup e testes locais. Quatro fontes foram inicializadas vazias, desligadas e sem autorização de publicação. Não há status operacional real no snapshot enquanto a liberação das fontes estiver pendente.

A escrita usa a sessão administrativa já existente: conta ativa/verificada, versão da sessão e registro em `administradores`. Não foram criados usuários, tokens permanentes, segredos no Render ou agendadores. O histórico do POST é desativado para não guardar o conteúdo enviado. O endpoint Python do site continua exigindo seu cookie; a leitura Xano contém apenas condições não pessoais.

`METROFLOW_STATUS_XANO_URL` seleciona a leitura remota compartilhada. Nesse modo nenhuma fonte direta é construída, mesmo se uma flag local estiver ligada. O Render mantém todas as flags de coleta em 0. O leitor preserva valores/datas em HTTP 503, payload inválido ou 429, sem propagar a falha ao planejador. A precedência é DDT, CPTM, Metrô e Motiva, preferindo resposta válida atual sobre antiga.

O coletor opcional `python -m MetroFlow.status.publish_cache` lê o SQLite local com `mode=ro` e envia somente payloads já persistidos pelo cache. Exige URL HTTPS e login administrativo no terminal; senha e token não são salvos. `--sources` lista apenas fontes já liberadas e habilitadas no Xano. `--loop` espaça as fontes em um ciclo de cinco minutos; não consulta operadoras nem garante atualização se o computador local estiver desligado. O banco mantém o último retorno mesmo assim. A suspensão do Render não apaga o registro remoto.

Exemplo, após liberação da fonte: `python -m MetroFlow.status.publish_cache --url https://x8ki-letl-twmt.n7.xano.io/api:metroflow-status-operacional --cache .cache/line-status.sqlite3 --sources cptm --loop`. O iniciador local atual não foi alterado. Não ligar fontes nem atribuir operação normal para preencher ausência de dado.

Validação: suíte local com 487 testes e 119 subtestes, mais quatro testes posteriores do publicador, incluindo HTTPS local, retenção e seleção remota. HTTP nativo confirmou GET 200 com snapshot vazio e POST 401 sem sessão. A gravação/releitura e a retenção do JSON e das datas em falha foram confirmadas em uma função privada com um registro sintético desabilitado; registro e função foram removidos. A lambda não pôde executar no contexto de função da CLI; seu redutor continua validado localmente, não como teste nativo integral do protocolo de reserva. HTTP autenticado validou administrador recusado com 400 para fonte desligada e passageiro recusado com 403; o snapshot permaneceu vazio e nenhuma condição foi publicada. A reserva concorrente e a publicação positiva de fonte liberada ainda estão pendentes. Não afirmar que testes SQLite são PostgreSQL/Xano. A publicação da leitura na main/Render e a ativação de dados reais são etapas distintas.

## Histórico da preparação de 23/11 (superado nos pontos acima)

O texto abaixo documenta a proposta anterior, então exclusivamente local e desconectada. A identidade técnica e a flag de ambiente antes propostas foram substituídas pela concessão administrativa existente.

## Verificação do plano, somente em leitura

A CLI autenticada confirmou workspace 149130 e `extras.instance.package.name = build`, sem features adicionais declaradas. O cadastro oficial associa `plan=build` ao plano Free. A oferta pública consultada permite 100 mil registros e limita a API a 10 requisições a cada 20 segundos. Isso confirma a viabilidade de guardar até quatro registros adicionais, **sujeita à disponibilidade efetiva de espaço e registros**, que não foi medida nesta consulta. Nenhum conteúdo de usuários ou viagens foi baixado.

O campo interno `k8s.deployments.task.enabled=true` apareceu na resposta, mas indica serviço provisionado: não é prova de direito a tarefas agendadas. A oferta comercial coloca Background tasks em Essential. O painel interno abriu na tela de login, portanto não foi possível confirmar a tela de entitlement/agendamento desta conta. Não prometer cron gratuito a partir desse campo. A lista de tarefas não foi alterada; não houve tentativa de criar tarefa para descobrir a limitação.

Comandos de consulta usados: `xano workspace get -p default -w 149130 -o json` e `xano profile me -p default -o json`. Somente id do workspace, código do pacote e flags técnicas foram usados; token, credenciais, dados de cobrança e conteúdo bruto da conta não foram gravados no pacote.

Referências consultadas:

- [Free e cotas](https://www.xano.com/pricing/)
- [Cadastro oficial do Free com código build](https://app.xano.com/signup?cluster_id=1&plan=build)
- [Tarefas agendadas](https://www.xano.com/learn/background-tasks-cron-jobs/)

## O que está preparado

- `status_operacional_fontes.xs`: tabela independente com uma linha por fonte, chave única em `codigo`, flags de autorização/ativação, mapa de últimas condições e controle de coleta. Até quatro registros, sem histórico crescente e sem chaves estrangeiras para a malha.
- `semente-proposta.json`: quatro linhas vazias (CPTM, Metrô, Motiva e DDT), todas desautorizadas e desligadas. Não foi importada.
- `api_group.xs`: grupo `metroflow-status-operacional` com `active=false` e Swagger desativado.
- `controle_post.xs`: protocolo de reserva/publicação/falha, protegido por JWT de usuário técnico, conta ativa/verificada, versão de sessão, escopo `status_coletor`, ID configurado e flag `STATUS_XANO_ESCRITA_HABILITADA=1`. Nenhum token ou usuário técnico foi criado.
- `reduzir_status.js`: corpo exato da lambda incorporada ao POST, executado nos testes Node. Não chama fontes externas nem lê/grava tabelas da malha.
- `snapshot_get.xs`: somente leitura de informações não pessoais de fontes autorizadas/habilitadas, sem consulta externa. Retorna contrato `{version:1,sources:[{source,conditions}]}`. Se o grupo vier a ser ativado, esse GET será público; avaliar exposição/abuso e cota antes de publicar. Controle de coleta e IDs não são devolvidos.
- `MetroFlow/status/xano_snapshot.py`: cliente HTTP somente leitura, com uma instância compartilhada por servidor, cache de 60 segundos e pausa de 300 segundos em falhas, sem repetição imediata. Preserva observações anteriores e não renova suas datas. Ainda desconectado do endpoint atual e do Render.

Todos os arquivos .xs passaram na validação de sintaxe. Isso **não** valida permissões, PostgreSQL, JWT, transações, escopo ou comportamento em execução no Xano.

## Fluxo proposto

1. Coletor técnico pede reserva de uma fonte (`acao=reserve`). O Xano bloqueia somente a linha dedicada da fonte, relê o controle e concede uma geração se permitida.
2. A transação termina antes da consulta externa. O coletor usa o adaptador autorizado, sem executar essa coleta dentro de uma busca de trajeto.
3. Se receber resposta válida e armazenável, envia `acao=publish`, geração e condições normalizadas em lote. Se falhar, envia `acao=fail`, com o intervalo de espera aplicável, sem texto bruto de erro ou credenciais.
4. O servidor valida geração, lease de 60 segundos, fonte, linhas, situações, textos e horários. Atualiza apenas o mapa da fonte. Leituras continuam disponíveis sem chamar as origens.
5. O Reflex lê um snapshot agregado compartilhado; passageiros não disparam GET adicional ao Xano por cartão ou embarque.

Campos públicos de datas permanecem em segundos Unix, como no contrato atual. Controle interno e timestamps do Xano usam milissegundos. `updated_at` é o horário da informação na origem; `verified_at` pode avançar em uma resposta válida mesmo quando a situação não mudar. Em falha, nenhum deles é renovado.

Resposta parcial preserva a linha ausente como antiga. Resposta vazia ou inválida não vira operação normal. Não há TTL que apague o último retorno; validade é calculada separadamente. Dados `no-store`, `private` e `no-cache` não são persistidos, seguindo a política conservadora existente. O limite interno continua no máximo uma tentativa por cinco minutos e 12 por hora por fonte; isso não é autorização nem cota concedida pelas operadoras.

## Impacto na cota e coleta automática

Banco persistente não executa coletas sozinho. Se não houver agendamento nativo disponível, a alternativa inicial é um coletor único enquanto o Render estiver ativo. Ele conserva no Xano o último retorno para retomada, mas **não atualiza durante suspensão**. Coleta contínua sem usuários depende de um agendador cuja gratuidade e permissões ainda devem ser confirmadas. Nenhum coletor/agendador foi conectado nesta entrega.

Estimativa máxima ilustrativa para três fontes a cada cinco minutos: 25.920 ciclos em 30 dias; reserva e finalização consomem até 51.840 chamadas. Uma leitura agregada por minuto soma 43.200, total de até 95.040 chamadas mensais. O problema do Free é o pico de 10 chamadas/20 s, não uma cota mensal documentada. Escalonar as três fontes (por exemplo offsets 0/100/200 segundos) reduz picos; falhas e Retry-After reduzem a frequência. São estimativas, não benchmark ou garantia de ausência de impacto.

Como tudo compartilha a mesma cota de API do Xano, não é possível garantir impacto zero na busca apenas separando tabelas ou grupos. É necessário homologar sob carga com duas contas reais, tráfego administrativo e coleta espaçada; qualquer erro/429 do status deve afetar apenas seus indicadores. Não alterar a política de viagens para compensar limites.

## Publicação futura, não autorizada nesta etapa

- Confirmar autorização de coleta, armazenamento e exibição com Metrô/CPTM/Motiva ou usar API autorizada. Os termos da Motiva vedam mineração de dados e ferramentas similares; o regulamento 10023786 do Metrô prevê API por credenciamento. Nada nesta pasta concede permissão.
- Confirmar capacidade restante do banco e agendamento no painel/suporte. Não contratar plano ou presumir exceção de gratuidade.
- Fazer backup da configuração/esquema antes de qualquer criação; usar lista de alterações limitada a esta tabela e este grupo. Nunca enviar a pasta de rascunhos inteira com --sync.
- Criar e proteger identidade técnica, escopo no JWT emitido somente pelo servidor, rotação e configuração de segredos sem usuários passageiros/administradores comuns. Avaliar ocultação de pedidos e tokens no histórico Xano.
- Testar transação nativa de duas reservas, geração vencida, queda do coletor, revogação, snapshots, quota e limites de tempo antes de ligar o grupo.
- Integrar o leitor à fábrica e conectar o coletor **somente em mudança posterior**. A escolha deve manter a autenticação existente do endpoint Python e não cachear permissões de usuário.
- Só então atualizar o pacote Render, mantendo fontes desligadas enquanto não autorizadas.

O teste anterior de configuração ausente da concorrência continua sendo **HTTP local isolado, não runtime nativo do Xano**. Os novos testes desta preparação também são locais; não ampliam aquela evidência.

## Validação retomada em 23/11/2026

Base atualizada para main `03342d5` (PR #54), em cópia separada. O erro de sintaxe do leitor preparado foi corrigido; nenhum módulo da aplicação em uso passou a importá-lo. A suíte completa passou com **484 testes e 119 subtestes**, incluindo os testes de deploy e persistência; houve um aviso existente de dependência. A validação estrita do OpenSpec passou em 18 itens, e os quatro rascunhos XanoScript passaram na validação de sintaxe, sem publicação.

O laboratório adicional usa HTTPS real em `127.0.0.1`, certificado temporário validado por uma autoridade confiada somente pelo cliente de teste, e SQLite temporário. Conferiu cache compartilhado (20 leituras sem GET adicional), retenção durante HTTP 503, preservação das datas e leitura do mesmo retorno após reiniciar o servidor e o cliente no dia seguinte, então marcado como antigo. Não houve desativação da verificação TLS nem alteração de certificados do sistema. SQLite e o servidor de laboratório **não são o PostgreSQL nem o runtime nativo do Xano**; transação nativa, JWT, cotas e duas contas reais continuam pendentes.

O leitor continua desconectado da fábrica de status, do Render e das buscas. O grupo permanece com `active=false`, a semente com todas as fontes desligadas/desautorizadas e o controle de escrita fechado por padrão. Nenhuma tabela, endpoint, usuário técnico, agendamento ou segredo foi criado no Xano. O pacote Free consultado publicamente continua oferecendo até 100 mil registros e 10 chamadas/20 s; o agendamento gratuito desta conta não foi confirmado. Banco persistente guarda o último retorno, mas não garante coleta enquanto o serviço Render estiver suspenso.


Reteste autenticado concluído em 24/11: GET 200; sem sessão 401; administrador com fonte desligada 400; passageiro 403; snapshot preservado. Resultado sem identidades/credenciais na evidência versionada.
