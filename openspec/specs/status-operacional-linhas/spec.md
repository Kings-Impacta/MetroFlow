# status-operacional-linhas Specification

## Purpose
Apresentar status informativo das linhas com fontes e datas rastreáveis, preservando o último retorno permitido e a independência do planejamento em falhas externas.

## Requirements

### Requirement: Condição operacional rastreável

O sistema SHALL representar a condição operacional com código da linha, situação
normalizada, rótulo e descrição da origem, fonte, instante da coleta, instante da
origem quando disponível e estado de validade.

#### Scenario: Condição atual disponível

- **WHEN** uma fonte autorizada retorna uma condição válida dentro de sua validade
- **THEN** o sistema associa a condição à linha pelo código e informa fonte e atualização

#### Scenario: Resposta sem horário da origem

- **WHEN** a fonte retorna condição válida sem informar seu próprio horário
- **THEN** o sistema preserva o instante da coleta e não inventa um horário da origem

### Requirement: Fontes explícitas no escopo local

O sistema SHALL manter Direto dos Trens preparado como principal futura, desativado sem token e configuração explícita. A entrega local SHALL permitir habilitar Metrô, CPTM e Motiva pelo iniciador existente, com cobertura somente das linhas efetivamente retornadas. Todas as fontes SHALL permanecer desativadas por padrão. Quando habilitada e validada, a precedência SHALL ser Direto dos Trens, CPTM, Metrô e Motiva. A validação autenticada Direto dos Trens e a ativação pública estão fora da entrega encerrada, conforme `docs/melhorias-futuras-malha-status.md`. Flags antigas ARTESP/Azure não SHALL iniciar consultas nesta configuração. Nenhuma fonte SHALL ser ativada implicitamente pela presença de outra credencial.

#### Scenario: Principal e complemento têm informação atual
- **WHEN** ambas retornam condições atuais para a mesma linha
- **THEN** o sistema apresenta Direto dos Trens, com fonte e horário próprios, e registra divergência sem conteúdo sensível quando existir

#### Scenario: Principal não tem dado atual
- **WHEN** a principal falha ou só tem valor desatualizado e a CPTM tem dado atual da linha
- **THEN** o sistema apresenta a condição CPTM com sua atribuição, sem alterar o trajeto

#### Scenario: Token ainda não recebido
- **WHEN** o usuário aguarda o token e nenhuma fonte foi explicitamente habilitada
- **THEN** não há chamada à principal, reserva ou fontes antigas, e a consulta devolve indisponibilidade sem bloquear busca e registro

### Requirement: Cache compatível com a origem

O sistema SHALL compartilhar o cache entre usuários e respeitar a frequência máxima
e os limites documentados por cada fonte.

#### Scenario: Consulta dentro da validade do cache

- **WHEN** outro usuário solicita uma condição ainda válida no cache
- **THEN** o sistema reutiliza o valor sem consumir nova chamada externa

### Requirement: Indisponibilidade explícita

O sistema SHALL distinguir condição atual, desatualizada e indisponível e SHALL
continuar permitindo o planejamento quando a condição operacional não puder ser
obtida.

#### Scenario: Todas as fontes falham

- **WHEN** as fontes excedem o tempo limite, retornam erro ou resposta inválida
- **THEN** o sistema mantém o último retorno válido como desatualizado com sua data original; sem retorno anterior, informa indisponibilidade, preservando a busca de trajeto

#### Scenario: Cache ultrapassa a validade

- **WHEN** existe um último valor conhecido, mas sua validade terminou
- **THEN** o sistema o identifica como desatualizado e não o apresenta como condição atual

#### Scenario: Falha prolongada ou consulta em andamento

- **WHEN** existe último retorno válido e uma atualização demora, falha, retorna vazio ou omite uma linha
- **THEN** o sistema conserva o último retorno dessa linha e sua data, inclusive após uma hora, marcando desatualizado quando necessário e sem apagar os cartões durante a consulta

#### Scenario: Recuperação da fonte

- **WHEN** chega um novo retorno válido
- **THEN** somente as linhas retornadas são substituídas, com a data dessa nova coleta, preservando as demais e sem alterar busca ou concorrência

### Requirement: Credenciais protegidas

O sistema SHALL manter chaves externas exclusivamente no backend e SHALL impedir que
elas apareçam na interface, URLs, respostas públicas ou logs.

#### Scenario: Consulta autenticada Direto dos Trens

- **WHEN** o backend consulta a origem fixa pelo protocolo documentado com token
- **THEN** o navegador recebe somente dados normalizados, e a requisição interna autenticada não aparece em URLs públicas, respostas, logs ou mensagens de exceção

### Requirement: Uso informativo

O sistema SHALL apresentar a condição operacional como informação e SHALL preservar
a regra atual de escolha do trajeto nesta entrega.

#### Scenario: Linha do trajeto apresenta ocorrência

- **WHEN** a linha escolhida possui condição diferente de operação normal
- **THEN** o sistema apresenta o aviso sem recalcular ou substituir automaticamente o trajeto

### Requirement: Quadro oficial preparado sem ativação implícita

O sistema SHALL manter o adaptador HTML do quadro do Metrô desativado por padrão e independente das flags ARTESP e agregado. A ativação pública SHALL permanecer pendente de confirmação das condições de uso. A fonte SHALL ser identificada explicitamente e nenhuma condição SHALL alterar a busca ou o registro de viagem.

#### Scenario: Usuário configura apenas ARTESP
- **WHEN** existe uma chave ARTESP mas não há autorização configurada para o quadro
- **THEN** o backend não consulta o HTML do Metrô nem envia a chave ARTESP a esse site

#### Scenario: Estrutura do quadro muda
- **WHEN** não existem linhas reconhecíveis ou uma linha reconhecida perde a situação obrigatória
- **THEN** a coleta falha e o cache conserva somente seu último dado com validade desatualizada, sem fabricar normalidade

#### Scenario: Fonte alternativa apresenta dado atual
- **WHEN** uma fonte autorizada prioritária está indisponível ou desatualizada e outra fonte autorizada tem condição atual para a mesma linha
- **THEN** o sistema apresenta a condição atual com a identificação da fonte utilizada e preserva os limites de validade

### Requirement: Política de cache da resposta preservada

O cache SHALL respeitar os cabeçalhos da origem e manter a reserva de tentativas separada do corpo da resposta.

#### Scenario: Origem proíbe armazenamento
- **WHEN** uma resposta indica no-store, no-cache ou private
- **THEN** a condição não é persistida no cache compartilhado e novas consultas não ignoram o intervalo mínimo de tentativas

#### Scenario: Origem define validade curta
- **WHEN** max-age ou s-maxage termina antes da próxima tentativa permitida
- **THEN** o último valor não é apresentado como atual durante esse intervalo

### Requirement: Indicadores compactos no trajeto

O sistema SHALL mostrar a situacao das linhas usadas por meio de bolinha colorida e texto, no resumo junto ao tempo estimado e em cada instrucao de embarque, sem quadros detalhados no fim do resultado.

#### Scenario: Trajeto com varias linhas
- **WHEN** o trajeto utiliza uma ou varias linhas, inclusive numa alternativa por concorrencia
- **THEN** o resumo lista cada linha usada uma unica vez na ordem do percurso, com seu status, e cada embarque apresenta apenas o status da respectiva linha

#### Scenario: Fonte ausente ou retorno antigo
- **WHEN** uma linha nao tem retorno ou possui somente ultimo retorno desatualizado
- **THEN** o indicador mostra o último status recebido, ou indisponibilidade se não houver retorno, sem sufixo de idade no texto compacto; o estado e a página detalhada preservam validade e datas, sem bloquear busca ou registro

#### Scenario: Integracao a pe
- **WHEN** uma instrucao descreve caminhada em vez de embarque em trem
- **THEN** ela nao recebe um status ferroviario por inferencia

### Requirement: Transporte isolado do quadro Metrô

O sistema SHALL usar o ajuste de conexão IPv4 somente no adaptador Metrô, preservando HTTPS e validação de certificado, sem alterar configurações de rede do sistema, as outras fontes ou o cálculo de trajetos.

#### Scenario: Origem demora para responder

- **WHEN** o quadro Metrô demora para enviar a resposta HTTP
- **THEN** a conexão admite até cinco segundos e a leitura admite até quinze segundos por operação, com orçamento de leitura de vinte segundos verificado durante a recepção; em falha conserva o último retorno e respeita o próximo ciclo, sem repetir imediatamente o GET
