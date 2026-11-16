## 1. Conferência do Xano e novas tabelas

- [x] 1.1 Baixar o workspace atual com `xano workspace pull` para uma pasta temporária e conferir o esquema de `usuarios` e o código de `auth/me`; verificar que incluir `administrador` na resposta é uma alteração aditiva e, se houver divergência, interromper e revisar `design.md`.
- [x] 1.2 Criar em `docs/xano/rascunhos/portal-administrativo/` a tabela `administradores`, com `usuario_id` único, e o grupo `administracao`, com canonical `metroflow-administracao`; verificar que os arquivos existem e que nenhum altera tabela já publicada.
- [x] 1.3 Criar na mesma pasta a tabela `estacoes_situacao_historico`, com estação, nova situação, usuário e momento; verificar que ela não é referenciada por nenhuma resposta pública.

## 2. Endpoints no Xano

- [x] 2.1 Escrever `GET admin/indicadores` com as verificações de sessão e de administrador e os indicadores definidos em `design.md`, mantendo uma única `|lambda:` no arquivo, como exige `tests/unit/planning/xano_lambda.py`; verificar pela tarefa 2.2.
- [x] 2.2 Criar `tests/unit/admin/test_xano_indicadores.py` executando a função com Node.js e verificar que passam os casos de janela, viagem substituída, duas viagens do mesmo usuário, uso recente de 7 dias, virada do dia em São Paulo, volume com substituídas, ranking com origem e destino, empate e menos de cinco estações.
- [x] 2.3 Adicionar testes de `trechos_lotados` e verificar sentidos independentes, integração a pé, serviço especial, configuração ausente ou inválida (`null`), usuários distintos, intervalo pelo cronograma calibrado (`inicio_previsto_em`) e pelo cálculo de registros antigos, como na função publicada de `trajetos/buscar` conferida em 16/11/2026.
- [x] 2.4 Adicionar teste que percorre a resposta dos indicadores e verificar que não há `usuario_id`, e-mail nem registro de viagem.
- [x] 2.5 Escrever `GET admin/estacoes`, com as mesmas verificações, devolvendo todas as estações com situação e linhas; verificar pela leitura do rascunho que nenhum filtro por `ativa` foi aplicado e pela tarefa 3.4 no ambiente real.
- [x] 2.6 Escrever `POST admin/estacoes/situacao`, com as mesmas verificações, gravando em `db.transaction` somente `ativa` e o histórico, sem gravar quando a situação não muda e usando `$auth.id`; verificar pela leitura do rascunho e pela tarefa 3.4.
- [x] 2.7 Preparar a versão de `auth/me` que acrescenta `administrador`, partindo do arquivo baixado na tarefa 1.1; verificar por comparação que a única diferença é o novo campo e sua consulta.

## 3. Publicação no Xano

- [x] 3.1 Baixar novamente o workspace, copiar os arquivos e executar `xano workspace push --dry-run` em comando separado; verificar que a lista contém somente as operações esperadas e obter a aprovação explícita da equipe antes de enviar.
- [x] 3.2 Publicar com `xano workspace push` após a aprovação, sem usar `PUT` da Metadata API, e baixar novamente; verificar que as cópias publicadas correspondem aos rascunhos e atualizar a pasta com os `guid` atribuídos.
- **Adiado, não executado nesta entrega:** 3.3 Inserir no Xano as linhas dos primeiros administradores, definidos pela equipe; verificar que `auth/me` devolve `administrador = true` para eles e `false` para os demais.
- **Adiado, não executado nesta entrega:** 3.4 Validar com sessões reais, sem registrar tokens: 401 sem sessão, 403 sem concessão, sucesso de administrador, revogação com efeito imediato, situação repetida sem novo histórico e histórico gravado na alteração; usar uma estação de baixo impacto, reativá-la ao final e conferir que nenhuma estação ficou inativa por causa do teste.

## 4. Backend Python

- [x] 4.1 Consultar os skills `reflex-docs`, `setup-python-env` e `reflex-process-management` e executar a suíte existente no ambiente do projeto; verificar e registrar o resultado inicial.
- [x] 4.2 Criar `MetroFlow/admin/` com as camadas `domain`, `application`, `infrastructure` e `presentation` e os modelos de indicadores e estações; verificar em `tests/unit/admin/test_models.py` a rejeição de contagens negativas, ranking acima de cinco e `trechos_lotados` inconsistente com o critério.
- [x] 4.3 Implementar `XanoAdminClient` com `XANO_ADMIN_API_BASE_URL`, distinguindo 401 de 403; verificar em `tests/unit/admin/test_xano_client.py`, com transporte simulado, contrato, erros, indisponibilidade e resposta inválida.
- [x] 4.4 Implementar os casos de uso com porta para o cliente Xano e ordenação das estações por nome; verificar em `tests/unit/admin/test_services.py`.
- [x] 4.5 Criar o roteador `/api/admin` e incluí-lo em `MetroFlow/MetroFlow.py`; verificar em `tests/unit/admin/test_api.py` os códigos 401, 403, 400, 404, 502 e 503, `Cache-Control: no-store`, rejeição de campos extras, mensagens genéricas e ausência de token nas respostas.
- [x] 4.6 Expor a indicação de administrador em `/api/auth/me`, aceitando somente `true`, e manter `/api/auth/login` inalterado; atualizar a asserção exata de `tests/unit/auth/test_api.py` e verificar os casos de campo ausente, não booleano, `true` e `false`.

## 5. Interface Reflex

- [x] 5.1 Levar a indicação de administrador ao `AuthState` e limpá-la no logout e em sessão inválida; verificar em `tests/unit/auth/test_state.py`.
- [x] 5.2 Criar `AdminState` com as cargas separadas de indicadores e estações, descarte de respostas antigas, 401 para `/login` com limpeza dos dados e 403 como acesso restrito; verificar em `tests/unit/admin/test_state.py`, incluindo que uma falha nos indicadores não bloqueia as estações e não mantém valores antigos como atuais.
- [x] 5.3 Implementar pesquisa sem distinção de acentos e filtro por situação; verificar em teste que `se` encontra `Sé`, que o filtro funciona e que nenhum resultado exibe a mensagem correspondente.
- [x] 5.4 Implementar o fluxo de alteração; verificar em teste que inativar abre confirmação com nome e linhas, cancelar não envia requisição, ativar não pede confirmação, a tela usa a situação devolvida, a falha preserva a situação e o sucesso apura de novo os indicadores.
- [x] 5.5 Criar a página `/admin`, registrá-la em `MetroFlow/MetroFlow.py` com restauração de sessão e cargas no `on_load` e apresentar indicadores, critério de lotação, ranking, momento da apuração, botão de atualizar e estados de carregamento, restrito e erro em português; verificar em `tests/unit/admin/test_pages.py` e compilando a aplicação.
- [x] 5.6 Acrescentar ao cabeçalho o link condicional para o painel; verificar em teste que aparece somente para administradores.

## 6. Documentação

- [x] 6.1 Atualizar `docs/domain-model.md` com administrador e situação da estação e `ARCHITECTURE.md` com o módulo `admin` e o fluxo de autorização; verificar que estado atual e pendências estão diferenciados.
- [x] 6.2 Atualizar `docs/roadmap-pos-mvp.md`, retirando a etapa P6 da espera, `docs/project-overview.md` e `README.md` com `XANO_ADMIN_API_BASE_URL`; verificar que os links relativos funcionam.
- [x] 6.3 Registrar em `docs/xano/README.md` e no README de `docs/xano/rascunhos/portal-administrativo/` as tabelas, os endpoints, como conceder o papel e o resultado da publicação; verificar que nenhum token ou dado pessoal foi incluído.

## 7. Validação e fechamento

- [x] 7.1 Executar a suíte completa e `openspec validate portal-administrativo --strict --no-interactive`; registrar a quantidade de testes e o resultado.
  - 16/11/2026: 400 testes e 119 subtestes passaram, com 1 aviso de depreciação do `TestClient`; `reflex compile --dry` concluiu sem erros. `portal-administrativo` passou na validação estrita. `openspec validate --all --strict` acusa `auditoria-sessao`, `integridade-trechos` e `validacao-planejamento` por `Purpose` provisório; as mesmas três falhas ocorrem na `origin/main` e não fazem parte desta mudança.
- **Adiado, não executado nesta entrega:** 7.2 Validar com `reflex run` e sessões reais: visitante sem sessão, usuário comum e administrador; inativar uma estação de baixo impacto, comprovar que a busca a retira da seleção e dos caminhos, reativá-la e conferir os indicadores, registrando que tokens não aparecem na interface, nas URLs e nos logs.
- [x] 7.3 Registrar os limites da validação em `docs/xano/rascunhos/portal-administrativo/README.md`, incluindo o que os testes locais não cobrem: atomicidade real de `db.transaction`, alterações simultâneas de administradores e comportamento sob o limite de requisições.
- [x] 7.4 Antes de arquivar, verificar que nenhuma outra mudança ativa altera `Escopo do MVP` e que o delta desta mudança parte do texto consolidado atual de `openspec/specs/busca-trajetos/spec.md`.

## Encerramento

Por decisão explícita do usuário, em 16/11/2026, esta mudança foi arquivada com o escopo implementado, testado e publicado. Os três itens marcados como adiados não foram executados: a concessão dos primeiros administradores, a validação no Xano com sessões reais e o teste ponta a ponta com `reflex run`. Nenhuma caixa de tarefa não realizada foi marcada como concluída. A verificação feita sem token confirmou só a recusa com `401`; ela não substitui as sessões reais. O roteiro desses testes está em `docs/xano/rascunhos/portal-administrativo/README.md`.
