## Why

O MetroFlow não tem área administrativa: ativar ou inativar uma estação exige editar a tabela `estacoes` diretamente no painel do Xano, sem controle de quem pode fazer a alteração e sem registro de quem a fez. A equipe também não consegue acompanhar o uso do sistema sem consultar tabelas manualmente, embora as viagens registradas desde a mudança `concorrencia-rotas` já permitam medir esse uso.

A área administrativa estava em espera no roadmap (etapa P6). Esta mudança a retoma como um painel de controle restrito a administradores.

## What Changes

- Introduzir o conceito de **administrador**, verificado no Xano a cada operação. A concessão é feita manualmente no Xano.
- Criar a página `/admin`, com o painel de controle, visível e utilizável somente por administradores.
- Listar todas as estações, ativas e inativas, com pesquisa e filtro por situação.
- Permitir ativar e inativar estações pelo painel. Inativar pede confirmação e avisa que a estação sai da seleção e que nenhum trajeto passará por ela, o que interrompe as linhas naquele ponto.
- Registrar quem alterou a situação de cada estação e quando.
- Apresentar indicadores agregados:
  - **uso:** rotas ativas (viagens em andamento), usuários em viagem agora, usuários com uso nos últimos 7 dias e contas habilitadas;
  - **malha:** estações ativas e inativas, linhas ativas e trechos ativos;
  - **volume:** viagens registradas hoje e nos últimos 7 dias;
  - **ranking:** as cinco estações mais usadas como origem ou destino nos últimos 7 dias;
  - **lotação:** trechos lotados agora, com o critério vigente ao lado.
- Informar na consulta da sessão atual se o usuário é administrador, para que a interface mostre o acesso ao painel.

## Fora do escopo

- Tela para conceder ou revogar o papel de administrador; a concessão permanece no Xano.
- Gerenciamento de linhas, trechos, operadores, usuários ou parâmetros de lotação pelo painel.
- Alteração do cálculo de `trajetos/buscar`. Uma estação inativa continua fora do grafo; a modalidade "trem passa sem parar" não faz parte desta entrega.
- Encerramento ou aviso às viagens em andamento que passam por uma estação inativada.
- Exibição de usuários individuais, e-mails ou registros de viagem; os indicadores são somente agregados.
- Atualização automática dos indicadores, medição de "usuários online" e consulta do histórico de alterações na interface.
- Séries temporais, gráficos históricos e exportação de dados.

## Capabilities

### New Capabilities

- `portal-administrativo`: acesso restrito a administradores, página do painel, listagem e alteração da situação das estações, registro das alterações e indicadores agregados de uso, malha, volume, ranking e lotação.

### Modified Capabilities

- `autenticacao-usuario`: a consulta da sessão atual passa a informar se o usuário autenticado é administrador.
- `busca-trajetos`: o escopo deixa de proibir a área administrativa e passa a registrar explicitamente que nenhum trajeto seleciona ou atravessa uma estação inativa.

## Impact

- **Xano:** novas tabelas `administradores` e `estacoes_situacao_historico`, novo grupo de API `administracao` com três endpoints e novo campo `administrador` na resposta de `auth/me`. `trajetos/buscar` e as tabelas da malha não mudam de esquema.
- **Backend Python:** novo módulo `MetroFlow/admin/`, com domínio, aplicação, infraestrutura e apresentação, e endpoints locais em `/api/admin/*`. O módulo `auth` passa a expor a indicação de administrador em `/api/auth/me`.
- **Reflex:** nova página `/admin`, novo estado e link condicional no cabeçalho.
- **Configuração:** nova variável opcional `XANO_ADMIN_API_BASE_URL`.
- **Documentação:** roadmap, visão geral, modelo de domínio, arquitetura, README e registro da publicação em `docs/xano/`.
- **Dependências:** nenhuma nova.
