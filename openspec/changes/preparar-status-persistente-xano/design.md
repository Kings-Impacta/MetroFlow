## Arquitetura implementada em 24/11/2026

Uma tabela exclusiva `status_operacional_fontes` guarda até quatro fontes em JSON, sem vínculos com malha, usuários de viagens ou configuração de lotação. O snapshot retorna somente condições públicas das fontes autorizadas e habilitadas. A escrita repete validação de conta ativa/verificada, versão de sessão e concessão existente em `administradores`; não cria conta técnica nem segredo no Render. O histórico do controle é desativado.

O POST usa transação: edita a linha exclusiva para obter bloqueio, relê o controle, executa o redutor e persiste o resultado. A reserva concede geração e lease de 60 segundos, com intervalo mínimo de cinco minutos e máximo de 12 por hora/fonte. Falhas não removem condições. O protocolo completo de duas reservas nativas ainda precisa de homologação; não confundir o teste SQLite/Node com PostgreSQL.

`METROFLOW_STATUS_XANO_URL` seleciona leitor compartilhado em processo, com leitura a cada minuto e pausa em falha/429. O modo remoto não constrói fontes diretas. O primeiro pedido pode aguardar o timeout de até dois segundos, mas somente no endpoint de status; busca e registro não importam nem chamam o leitor. Uma indisponibilidade mantém o último retorno em memória; após reiniciar o servidor, a próxima leitura recupera o registro persistido no Xano.

O publicador local lê o cache SQLite em modo somente leitura. Esse cache já exclui respostas não persistíveis (`no-store`, `private`, `no-cache`). Envia apenas retornos efetivos, com datas originais, autenticado com login administrativo feito no terminal e validado por `auth/me`. Credenciais ficam em memória. Retorno antigo não se torna atual por ter sido reenviado; a validade considera a data da observação/verificação. Sem retorno não presume operação normal.

## Operação sem custo adicional

Não criar plano, disco ou agendador pago. O publicador é opcional no computador do responsável, espaçando as fontes num ciclo de cinco minutos. Sem o coletor local, não há atualização, mas o último retorno continua no Xano. O site não precisa que esse computador esteja ligado para ler o que já foi salvo. Ainda não foi ativada fonte sem liberação de armazenamento/exibição.

## Evidência e limites

Suíte completa local: 487 testes e 119 subtestes; depois foram acrescentados os testes do publicador. OpenSpec: 18 itens. Xano nativo: tabela/grupo/endpoints instalados após backup, snapshot HTTP 200 vazio e escrita HTTP 401 sem sessão. A função de homologação confirmou gravação/releitura de JSON e manutenção de valores/datas após atualizar o controle de falha; o registro sintético esteve desabilitado e foi removido junto com a função privada. A execução de lambda não é aceita no contexto de função da CLI, portanto o redutor é comprovado localmente, não integralmente por esse ensaio nativo. Oito tabelas protegidas mantiveram hashes idênticos. O teste anterior de configuração ausente continua HTTP local isolado.

O reteste HTTP autenticado foi concluído: administrador recebeu 400 para fonte desativada, passageiro recebeu 403 e o snapshot permaneceu vazio. Isso não substitui publicar uma condição de fonte liberada nem disputar duas reservas nativas.
