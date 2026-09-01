## Purpose

Permitir que um usuário autenticado planeje uma viagem na rede de transporte ferroviário metropolitano de São Paulo e compreenda o trajeto principal, as estações, linhas, operadores e baldeações necessárias.

## ADDED Requirements

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

O sistema SHALL preservar `estacoes`, `linhas`, `estacoes_linhas` e `trechos` conforme a modelagem aprovada. A entidade `operadores` e a Table Reference `linhas.operador_id` são propostas condicionadas à inspeção do Xano e à aprovação explícita.

#### Scenario: Campos de estação
- **WHEN** uma estação é cadastrada ou atualizada
- **THEN** `nome` é text required not nullable com trim e sem default, `codigo` é text required not nullable com trim e unique, e `ativa` é boolean required not nullable com default true

#### Scenario: Campos de linha
- **WHEN** uma linha é cadastrada ou atualizada
- **THEN** `nome` é text required not nullable com trim, `codigo` é text required not nullable com trim e unique, `cor` é text opcional com trim, e `ativa` é boolean required not nullable com default true

##### Scenario: Operador aprovado para linha
- **WHEN** a alteração de modelagem receber backup, revisão e autorização explícita para aplicação no Xano
- **THEN** o sistema cria `operadores` com `id`, `created_at`, `nome`, `codigo` e `ativo`, exige `codigo` único e adiciona `linhas.operador_id` como Table Reference required e not nullable

#### Scenario: Estação associada a uma linha
- **WHEN** uma estação é associada a uma linha
- **THEN** `estacao_id` e `linha_id` são Table References required not nullable, `ordem` é integer positivo required not nullable e a combinação `estacao_id + linha_id` possui unique composto

#### Scenario: Tempo estimado de trecho
- **WHEN** um trecho é cadastrado ou atualizado
- **THEN** as três referências do trecho são Table References required not nullable, `tempo_estimado` é integer positivo em segundos required not nullable e `ativo` é boolean required not nullable com default true

#### Scenario: Trecho com extremos iguais
- **WHEN** se tenta cadastrar um trecho com `estacao_origem_id` igual a `estacao_destino_id`
- **THEN** uma validação rejeita a operação

#### Scenario: Trecho repetido no mesmo sentido
- **WHEN** já existe na mesma linha um trecho com a mesma origem e o mesmo destino
- **THEN** a unicidade composta de `estacao_origem_id + estacao_destino_id + linha_id` rejeita a duplicata direta

#### Scenario: Trecho repetido no sentido inverso
- **WHEN** já existe na mesma linha um trecho entre as mesmas estações com origem e destino invertidos
- **THEN** normalização canônica dos extremos ou validação lógica equivalente rejeita a duplicata inversa

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

O sistema SHALL escolher o caminho com menor tempo total, calculado exclusivamente pela soma de `tempo_estimado` dos trechos, em segundos. Em empate, SHALL escolher o caminho com menor quantidade de mudanças de linha.

#### Scenario: Soma do tempo dos trechos
- **WHEN** um caminho possui múltiplos trechos
- **THEN** seu tempo total é a soma dos valores de `tempo_estimado` desses trechos

#### Scenario: Trajetos com tempos diferentes
- **WHEN** existem caminhos com tempos totais diferentes
- **THEN** o sistema seleciona o de menor tempo total

#### Scenario: Trajetos com o mesmo tempo
- **WHEN** existem caminhos com o mesmo tempo total
- **THEN** o sistema seleciona o que possui menor quantidade de baldeações

#### Scenario: Transferência no primeiro MVP
- **WHEN** o caminho contém uma ou mais mudanças de linha
- **THEN** nenhum custo de caminhada, espera ou transferência é acrescentado ao tempo total

### Requirement: Baldeações derivadas

O sistema SHALL derivar uma baldeação quando houver mudança de linha entre trechos consecutivos e SHALL fazer isso sem tabela específica de baldeações.

#### Scenario: Trajeto sem baldeação
- **WHEN** todos os trechos do trajeto usam a mesma linha
- **THEN** o sistema informa zero baldeações

#### Scenario: Trajeto com baldeação
- **WHEN** a linha de um trecho difere da linha do trecho seguinte
- **THEN** o sistema identifica a estação comum como ponto de baldeação e informa as linhas envolvidas

### Requirement: Apresentação do trajeto

O sistema SHALL apresentar estações em ordem, trechos, linhas com seus operadores, baldeações derivadas, tempo total estimado e quantidade de baldeações.

#### Scenario: Conversão do tempo para exibição
- **WHEN** o frontend apresenta o tempo total ao usuário
- **THEN** ele pode converter segundos para minutos sem alterar o valor canônico recebido

#### Scenario: Nova busca
- **WHEN** uma nova consulta é iniciada após um resultado anterior
- **THEN** o resultado anterior deixa de ser apresentado como correspondente à nova seleção

### Requirement: Escopo do MVP

O sistema SHALL omitir lotação, rotas alternativas e custos adicionais de transferência e SHALL não oferecer área administrativa.

#### Scenario: Resultado do MVP
- **WHEN** um trajeto é apresentado
- **THEN** o resultado contém somente as informações necessárias ao trajeto principal definido nesta especificação
