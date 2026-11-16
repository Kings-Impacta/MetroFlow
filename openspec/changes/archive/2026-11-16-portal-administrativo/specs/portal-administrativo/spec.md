## Purpose

Oferece aos administradores do MetroFlow um painel de controle para ativar e inativar estações e acompanhar, por meio de indicadores agregados, o uso do sistema e a situação da malha.

## ADDED Requirements

### Requirement: Papel de administrador

O sistema SHALL considerar administrador somente o usuário autenticado com concessão registrada no Xano. A validade da sessão e a concessão SHALL ser verificadas no Xano a cada operação administrativa. A aplicação SHALL não oferecer meio de conceder ou revogar o papel.

#### Scenario: Administrador com sessão válida

- **WHEN** um administrador com sessão válida solicita uma operação administrativa
- **THEN** o sistema executa a operação

#### Scenario: Usuário autenticado sem concessão

- **WHEN** um usuário com sessão válida e sem concessão solicita uma operação administrativa
- **THEN** o sistema rejeita a operação como acesso negado, não devolve dados administrativos e mantém a sessão do usuário

#### Scenario: Concessão revogada

- **WHEN** a concessão é removida no Xano enquanto o administrador mantém uma sessão válida
- **THEN** a operação administrativa seguinte é rejeitada como acesso negado

#### Scenario: Sessão inválida

- **WHEN** uma operação administrativa é solicitada sem token ou com token inválido, expirado ou de versão de sessão anterior
- **THEN** o sistema rejeita a operação como não autorizada, sem executá-la

#### Scenario: Conta inativa ou não verificada

- **WHEN** uma operação administrativa é solicitada por uma conta com concessão, mas inativa ou sem e-mail verificado
- **THEN** o sistema rejeita a operação como não autorizada, sem executá-la

### Requirement: Acesso à página do painel

O sistema SHALL oferecer o painel na rota `/admin` e SHALL não apresentar indicadores nem controles antes de confirmar a autorização. O acesso ao painel SHALL aparecer na navegação somente para administradores.

#### Scenario: Visitante sem sessão

- **WHEN** uma pessoa sem sessão válida abre `/admin`
- **THEN** a interface a direciona ao login sem apresentar dados administrativos

#### Scenario: Usuário sem concessão

- **WHEN** um usuário autenticado sem concessão abre `/admin`
- **THEN** a interface informa que o acesso é restrito a administradores e não apresenta indicadores nem controles

#### Scenario: Sessão expirada com o painel aberto

- **WHEN** a sessão expira enquanto o painel está aberto e o administrador solicita uma atualização ou alteração
- **THEN** a operação é bloqueada, os dados apresentados são descartados e a interface direciona ao login

#### Scenario: Navegação do administrador

- **WHEN** um administrador navega autenticado pela aplicação
- **THEN** o cabeçalho apresenta o acesso ao painel

#### Scenario: Navegação dos demais usuários

- **WHEN** um visitante ou usuário sem concessão navega pela aplicação
- **THEN** o cabeçalho não apresenta o acesso ao painel

### Requirement: Proteção dos dados administrativos

As respostas administrativas SHALL não conter tokens, senhas, hashes nem respostas internas do Xano e SHALL ser marcadas como não armazenáveis em cache. Erros SHALL ser apresentados com mensagens genéricas. Entradas com campos não previstos ou valores inválidos SHALL ser rejeitadas sem efeito.

#### Scenario: Resposta bem-sucedida

- **WHEN** uma operação administrativa é concluída
- **THEN** a resposta é marcada como não armazenável em cache e contém somente os dados públicos previstos

#### Scenario: Falha no serviço externo

- **WHEN** o Xano está indisponível ou devolve erro
- **THEN** o sistema apresenta uma mensagem genérica, sem conteúdo interno da falha

#### Scenario: Resposta externa inválida

- **WHEN** o Xano devolve uma resposta fora do contrato esperado
- **THEN** o sistema não apresenta os dados como válidos e informa que não foi possível concluir a operação

#### Scenario: Entrada inválida

- **WHEN** uma alteração é enviada com campo não previsto, identificador inválido ou situação não booleana
- **THEN** o sistema rejeita a solicitação sem alterar nenhuma estação

### Requirement: Listagem de estações

O painel SHALL listar todas as estações cadastradas, ativas e inativas, com nome, código, situação e linhas atendidas, em ordem alfabética de nome. O painel SHALL permitir pesquisa por nome ou código, sem distinção de maiúsculas e acentos, e filtro por situação.

#### Scenario: Estação inativa na lista

- **WHEN** existe uma estação inativa
- **THEN** ela aparece na lista identificada como inativa

#### Scenario: Pesquisa sem acento

- **WHEN** o administrador pesquisa `se`
- **THEN** a lista inclui a estação `Sé`

#### Scenario: Filtro por situação

- **WHEN** o administrador seleciona o filtro de estações inativas
- **THEN** a lista apresenta somente as estações inativas

#### Scenario: Pesquisa sem resultado

- **WHEN** nenhuma estação corresponde à pesquisa e ao filtro
- **THEN** o painel informa que nenhuma estação foi encontrada

### Requirement: Alteração da situação de uma estação

O administrador SHALL poder ativar e inativar uma estação pelo painel. A inativação SHALL exigir confirmação que identifique a estação e as linhas atendidas e avise que a estação sairá da seleção de origem e destino e que nenhum trajeto passará por ela, interrompendo as linhas naquele ponto. A ativação SHALL não exigir confirmação. A alteração SHALL afetar somente a situação da estação, e a interface SHALL apresentar a situação devolvida pelo sistema.

#### Scenario: Inativação confirmada

- **WHEN** o administrador solicita a inativação de uma estação ativa e confirma
- **THEN** o sistema inativa a estação e o painel a apresenta como inativa

#### Scenario: Inativação cancelada

- **WHEN** o administrador solicita a inativação e cancela a confirmação
- **THEN** nenhuma alteração é enviada e a estação permanece ativa

#### Scenario: Ativação

- **WHEN** o administrador solicita a ativação de uma estação inativa
- **THEN** o sistema ativa a estação sem pedir confirmação e o painel a apresenta como ativa

#### Scenario: Situação já aplicada

- **WHEN** a situação solicitada já é a situação atual da estação, por exemplo após a ação de outro administrador
- **THEN** a operação é concluída com a situação atual, sem criar nova alteração

#### Scenario: Estação inexistente

- **WHEN** a alteração é solicitada para uma estação que não existe
- **THEN** o sistema informa o erro e não altera nenhuma estação

#### Scenario: Falha na alteração

- **WHEN** a alteração não pode ser concluída
- **THEN** o painel mantém a situação anterior da estação e informa a falha

#### Scenario: Demais dados preservados

- **WHEN** a situação de uma estação é alterada
- **THEN** nome, código, vínculos com linhas e trechos da estação permanecem inalterados

### Requirement: Viagens em andamento na inativação

A inativação de uma estação SHALL não encerrar, alterar nem notificar viagens em andamento.

#### Scenario: Viagem passa por estação inativada

- **WHEN** uma estação é inativada e existe viagem em andamento que passa por ela
- **THEN** a viagem permanece ativa até o fim da sua janela e continua contando nos indicadores e na lotação estimada

### Requirement: Registro das alterações de situação

O sistema SHALL registrar no Xano, na mesma operação da alteração, a estação, a nova situação, o administrador da sessão e o momento. Esses registros SHALL ser acessíveis somente no Xano.

#### Scenario: Alteração registrada

- **WHEN** a situação de uma estação é alterada
- **THEN** o registro contém a estação, a nova situação, o administrador da sessão e o momento da alteração

#### Scenario: Falha ao registrar

- **WHEN** o registro da alteração não pode ser gravado
- **THEN** a situação da estação permanece como estava

#### Scenario: Administrador do registro

- **WHEN** uma alteração é registrada
- **THEN** o administrador é obtido da sessão autenticada e não de um dado enviado pela interface

#### Scenario: Registro sem exposição

- **WHEN** o painel é apresentado ou uma alteração é concluída
- **THEN** a resposta não contém os registros de alteração

### Requirement: Indicadores de uso

O painel SHALL apresentar: **rotas ativas**, a quantidade de viagens em andamento; **usuários em viagem agora**, a quantidade de usuários distintos com viagem em andamento; **uso recente**, a quantidade de usuários distintos com ao menos uma viagem registrada nos últimos 7 dias; e **contas habilitadas**, a quantidade de contas ativas com e-mail verificado. Uma viagem SHALL estar em andamento quando não foi substituída e o instante da apuração está dentro da sua janela. Cada usuário SHALL contar com no máximo uma viagem em andamento.

#### Scenario: Viagem dentro da janela

- **WHEN** uma viagem não substituída tem o instante da apuração dentro da sua janela
- **THEN** ela conta em rotas ativas e seu usuário conta em usuários em viagem agora

#### Scenario: Viagem encerrada ou substituída

- **WHEN** a janela de uma viagem terminou ou a viagem foi substituída
- **THEN** ela não conta em rotas ativas nem em usuários em viagem agora

#### Scenario: Duas viagens simultâneas do mesmo usuário

- **WHEN** há mais de uma viagem em andamento do mesmo usuário
- **THEN** somente a mais recente conta em rotas ativas

#### Scenario: Várias viagens recentes do mesmo usuário

- **WHEN** um usuário registrou várias viagens nos últimos 7 dias
- **THEN** ele conta uma única vez em uso recente

#### Scenario: Viagem fora do período de uso recente

- **WHEN** a viagem mais recente de um usuário foi registrada há mais de 7 dias
- **THEN** ele não conta em uso recente

#### Scenario: Conta pendente ou inativa

- **WHEN** uma conta está inativa ou sem e-mail verificado
- **THEN** ela não conta em contas habilitadas

### Requirement: Indicadores da malha

O painel SHALL apresentar a quantidade de estações ativas, de estações inativas, de linhas ativas e de trechos ativos. Uma linha SHALL contar como ativa quando ela e seu operador estiverem ativos. Um trecho SHALL contar como ativo quando ele, sua linha e o operador dela estiverem ativos, independentemente da situação das estações em suas pontas.

#### Scenario: Estação inativada

- **WHEN** uma estação é inativada
- **THEN** a contagem de estações ativas diminui em um e a de inativas aumenta em um na apuração seguinte

#### Scenario: Linha de operador inativo

- **WHEN** uma linha ativa pertence a um operador inativo
- **THEN** ela não conta em linhas ativas

#### Scenario: Trecho ligado a estação inativa

- **WHEN** um trecho ativo tem uma estação inativa em uma das pontas
- **THEN** ele continua contando em trechos ativos

### Requirement: Volume de viagens

O painel SHALL apresentar a quantidade de viagens registradas no dia corrente, no horário de São Paulo, e nos últimos 7 dias. Viagens substituídas SHALL contar nesse volume.

#### Scenario: Viagem substituída

- **WHEN** uma viagem registrada hoje foi substituída por outra
- **THEN** as duas contam no volume do dia

#### Scenario: Virada do dia

- **WHEN** uma viagem foi registrada às 23h59 de ontem, no horário de São Paulo
- **THEN** ela não conta no volume de hoje e conta no volume dos últimos 7 dias

### Requirement: Ranking de estações

O painel SHALL apresentar as cinco estações mais usadas como origem ou destino nas viagens registradas nos últimos 7 dias, com a quantidade de usos, em ordem decrescente de usos e, em empate, em ordem alfabética de nome. Cada viagem SHALL contar um uso para sua origem e um uso para seu destino. Estações inativas SHALL permanecer elegíveis.

#### Scenario: Contagem por viagem

- **WHEN** uma viagem vai da estação A à estação B passando pela estação C
- **THEN** A e B recebem um uso cada e C não recebe uso

#### Scenario: Empate

- **WHEN** duas estações têm a mesma quantidade de usos
- **THEN** a de nome alfabeticamente anterior aparece primeiro

#### Scenario: Menos de cinco estações com uso

- **WHEN** menos de cinco estações têm uso no período
- **THEN** o painel apresenta somente essas estações

#### Scenario: Sem viagens no período

- **WHEN** não há viagens registradas nos últimos 7 dias
- **THEN** o painel informa que ainda não há dados para o ranking

### Requirement: Trechos lotados no painel

O painel SHALL apresentar a quantidade de trechos lotados no instante da apuração, com o critério de mínimo de usuários e percentual vigente. Cada combinação de trecho e sentido SHALL contar separadamente. O cálculo SHALL seguir o critério de lotação de `concorrencia-rotas`, considerando todas as viagens em andamento. Quando a configuração estiver ausente ou inválida, o indicador SHALL ser apresentado como indisponível. O indicador SHALL ser apresentado somente a administradores.

#### Scenario: Trecho lotado nos dois sentidos

- **WHEN** um trecho atinge o critério nos dois sentidos
- **THEN** o indicador conta duas ocorrências

#### Scenario: Nenhum trecho lotado

- **WHEN** nenhum trecho atinge o critério
- **THEN** o painel apresenta zero e o critério vigente

#### Scenario: Configuração ausente ou inválida

- **WHEN** a configuração de lotação não existe ou contém valores fora dos limites
- **THEN** o indicador é apresentado como indisponível, e não como zero

#### Scenario: Passageiro não vê a lotação

- **WHEN** um usuário sem concessão usa a aplicação
- **THEN** nenhuma tela ou resposta destinada a ele contém o indicador ou o critério de lotação

### Requirement: Indicadores somente agregados

Os indicadores SHALL conter somente contagens, nomes e códigos de estações e o critério de lotação. Eles SHALL não conter identificadores de usuários, e-mails nem registros individuais de viagem.

#### Scenario: Resposta dos indicadores

- **WHEN** um administrador consulta os indicadores
- **THEN** a resposta não contém identificador de usuário, e-mail ou registro de viagem

### Requirement: Atualização dos indicadores

O painel SHALL apurar os indicadores ao abrir, por solicitação do administrador e após cada alteração concluída, e SHALL apresentar o momento da última apuração. Uma falha nos indicadores SHALL não impedir o uso da lista de estações, e valores anteriores SHALL não ser apresentados como atuais depois de uma falha.

#### Scenario: Abertura do painel

- **WHEN** um administrador abre o painel
- **THEN** os indicadores são apurados e o momento da apuração é apresentado

#### Scenario: Atualização manual

- **WHEN** o administrador solicita a atualização
- **THEN** os indicadores são apurados novamente e o momento da apuração muda

#### Scenario: Após uma alteração

- **WHEN** a situação de uma estação é alterada com sucesso
- **THEN** os indicadores são apurados novamente

#### Scenario: Falha nos indicadores

- **WHEN** a apuração dos indicadores falha e a lista de estações está disponível
- **THEN** o painel informa que os indicadores estão indisponíveis e mantém a lista de estações utilizável
