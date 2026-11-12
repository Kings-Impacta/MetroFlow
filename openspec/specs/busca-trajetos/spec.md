# busca-trajetos Specification

## Purpose
Permitir que um usuário autenticado planeje uma viagem na rede de transporte ferroviário metropolitano de São Paulo e compreenda o trajeto principal, as estações, linhas, operadores e baldeações necessárias.

## Requirements

### Requirement: Autenticação obrigatória para planejar viagens

O sistema SHALL permitir o planejamento de viagens somente a usuários autenticados. A autenticação por e-mail é uma dependência funcional do MVP e será especificada em uma mudança OpenSpec separada.

#### Scenario: Usuário não autenticado
- **WHEN** uma pessoa sem sessão autenticada tenta acessar ou executar o planejamento de viagem
- **THEN** o sistema não consulta o trajeto e solicita autenticação por e-mail

#### Scenario: Usuário autenticado
- **WHEN** um usuário com sessão válida acessa o planejador
- **THEN** o sistema permite selecionar estações e solicitar um trajeto

#### Scenario: Sessão inválida durante a consulta
- **WHEN** o serviço rejeita a consulta por sessão ausente, inválida ou expirada
- **THEN** o sistema não apresenta resultado protegido e direciona o usuário para autenticação

### Requirement: Cobertura da malha ferroviária metropolitana

O sistema SHALL estar preparado para representar estações e linhas do Metrô, da CPTM e das concessionárias, associando cada linha ao seu operador.

#### Scenario: Linha operada por concessionária
- **WHEN** uma linha é apresentada em uma opção ou em um trajeto
- **THEN** o sistema apresenta discretamente seu operador ou concessionária, como em “Linha 8–Diamante — ViaMobilidade”

### Requirement: Integridade da modelagem da malha

O sistema SHALL preservar `estacoes`, `linhas`, `estacoes_linhas`, `trechos` e `operadores` conforme a modelagem aprovada, incluindo a referência obrigatória `linhas.operador_id`.

#### Scenario: Campos de estação
- **WHEN** uma estação é cadastrada ou atualizada
- **THEN** `nome` é text required not nullable com trim e sem default, `codigo` é text required not nullable com trim e unique, e `ativa` é boolean required not nullable com default true

#### Scenario: Campos de linha
- **WHEN** uma linha é cadastrada ou atualizada
- **THEN** `nome` é text required not nullable com trim, `codigo` é text required not nullable com trim e unique, `cor` é text opcional com trim, e `ativa` é boolean required not nullable com default true

#### Scenario: Operador associado à linha
- **WHEN** uma linha é cadastrada ou consultada
- **THEN** ela possui um operador referenciado por `linhas.operador_id`, e `operadores.codigo` possui unicidade

#### Scenario: Estação associada a uma linha
- **WHEN** uma estação é associada a uma linha
- **THEN** `estacao_id` e `linha_id` são Table References required not nullable, `ordem` é integer positivo required not nullable e a combinação `estacao_id + linha_id` possui unique composto

#### Scenario: Tempo estimado de trecho
- **WHEN** um trecho é cadastrado ou atualizado
- **THEN** as três referências do trecho são Table References required not nullable, `tempo_estimado` é integer positivo em segundos required not nullable e `ativo` é boolean required not nullable com default true

#### Scenario: Trecho repetido no mesmo sentido
- **WHEN** já existe na mesma linha um trecho com a mesma origem e o mesmo destino
- **THEN** a unicidade composta de `estacao_origem_id + estacao_destino_id + linha_id` rejeita a duplicata direta

#### Scenario: Percurso nos dois sentidos
- **WHEN** existe um trecho válido armazenado entre duas estações
- **THEN** o cálculo pode percorrê-lo em ambos os sentidos sem um segundo cadastro

### Requirement: Seleção de estações de origem e destino

O sistema SHALL permitir que o usuário autenticado selecione origem e destino entre as estações ativas disponíveis.

#### Scenario: Estações disponíveis
- **WHEN** o usuário autenticado acessa o planejador
- **THEN** o sistema apresenta controles para escolher origem e destino entre as estações ativas

#### Scenario: Seleção incompleta
- **WHEN** o usuário tenta solicitar uma rota sem selecionar origem ou destino
- **THEN** o sistema não solicita um trajeto e informa que ambas devem ser selecionadas

#### Scenario: Origem e destino iguais
- **WHEN** o usuário seleciona a mesma estação como origem e destino
- **THEN** o sistema não solicita um trajeto e informa que elas devem ser diferentes

### Requirement: Consulta do trajeto principal

O sistema SHALL consultar caminhos entre origem e destino e retornar resultado somente quando houver caminho válido.

#### Scenario: Consulta bem-sucedida
- **WHEN** o usuário autenticado solicita uma rota entre estações diferentes e conectadas
- **THEN** o sistema apresenta o trajeto principal retornado

#### Scenario: Consulta em andamento
- **WHEN** uma solicitação está sendo processada
- **THEN** o sistema indica carregamento e impede solicitações concorrentes para a mesma busca

#### Scenario: Ausência de trajeto
- **WHEN** o serviço informa que não há caminho válido
- **THEN** o sistema informa que nenhum trajeto foi encontrado e não apresenta resultado incompleto

#### Scenario: Falha no serviço
- **WHEN** o serviço não responde ou retorna erro
- **THEN** o sistema informa a falha e permite nova tentativa

### Requirement: Definição do trajeto principal

O sistema SHALL escolher o caminho com menor tempo total estimado, calculado pelos deslocamentos, esperas e baldeações específicos do contrato calibrado, respeitando a disponibilidade no momento do embarque. Em empate, SHALL preferir menos serviços especiais e depois menos baldeações. A margem pública única de 60 segundos SHALL não alterar a seleção. O contrato legado SHALL conservar 600 segundos por mudança de linha.

#### Scenario: Soma do tempo dos trechos
- **WHEN** um caminho possui múltiplos trechos
- **THEN** seu tempo total é a soma calibrada dos deslocamentos, esperas e baldeações, com 60 segundos acrescidos apenas ao total público

#### Scenario: Trajetos com tempos diferentes
- **WHEN** existem caminhos com tempos totais diferentes
- **THEN** o sistema seleciona o de menor tempo total

#### Scenario: Trajetos com o mesmo tempo
- **WHEN** existem caminhos com o mesmo tempo total
- **THEN** o sistema prefere menos serviços especiais e depois menor quantidade de baldeações

#### Scenario: Penalidade fixa de transferência no primeiro MVP
- **WHEN** a consulta usa o contrato legado e o caminho contém uma ou mais mudanças de linha
- **THEN** o sistema acrescenta 600 segundos por mudança ao tempo total usado na seleção e apresentado ao usuário

#### Scenario: Trajeto sem transferência
- **WHEN** todos os trechos do caminho permitem continuar no mesmo trem
- **THEN** nenhum tempo de transferência é acrescentado

### Requirement: Baldeações derivadas

O sistema SHALL derivar uma baldeação quando houver mudança de linha ou troca obrigatória de trem entre serviços consecutivos e SHALL fazer isso sem tabela específica de baldeações.

#### Scenario: Trajeto sem baldeação
- **WHEN** todos os trechos do trajeto permitem continuar no mesmo trem
- **THEN** o sistema informa zero baldeações

#### Scenario: Trajeto com baldeação
- **WHEN** a linha de um trecho difere da linha do trecho seguinte
- **THEN** o sistema identifica a estação comum ou a integração a pé explicitamente cadastrada como ponto de baldeação e informa as linhas envolvidas

### Requirement: Apresentação do trajeto

O sistema SHALL apresentar estações em ordem, trechos, linhas com seus operadores, baldeações derivadas, tempo total estimado e quantidade de baldeações.

#### Scenario: Conversão do tempo para exibição
- **WHEN** o frontend apresenta o tempo total ao usuário
- **THEN** ele pode converter segundos para minutos sem alterar o valor canônico recebido

#### Scenario: Nova busca
- **WHEN** uma nova consulta é iniciada após um resultado anterior
- **THEN** o resultado anterior deixa de ser apresentado como correspondente à nova seleção

### Requirement: Escopo do MVP

O sistema SHALL considerar deslocamentos, esperas, disponibilidade de serviços e tempos específicos de caminhada e baldeação conforme as capacidades de calibração e espera de partidas. A penalidade fixa de 600 segundos SHALL ficar restrita ao contrato legado. O tempo público SHALL ser estimado, com margem única de 60 segundos sobre o total, fora da ocupação. O sistema SHALL não oferecer área administrativa. A lotação estimada e a substituição do trajeto SHALL seguir `concorrencia-rotas`, sem apresentação da lotação ao usuário. O resultado MAY incluir as orientações opcionais de desembarque definidas em `orientacoes-viagem`, sem alterar a escolha, os trechos ou o tempo estimado.

#### Scenario: Resultado do MVP

- **WHEN** um trajeto é apresentado
- **THEN** o resultado contém um único trajeto principal ou alternativa elegível conforme `concorrencia-rotas`, com as informações opcionais disponíveis

#### Scenario: Orientações não alteram o cálculo

- **WHEN** existem orientações cadastradas para estações do trajeto
- **THEN** a escolha do trajeto e o tempo total seguem as regras de busca, calibração, espera de partidas e `concorrencia-rotas`, independentemente das orientações
