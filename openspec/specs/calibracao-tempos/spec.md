# calibracao-tempos Specification

## Purpose
Definir estimativas rastreáveis de deslocamento, espera e transferência, uma margem única no total público e cronologia compartilhada entre busca e registro.

## Requirements

### Requirement: Cobertura rastreável antes da publicação
O sistema SHALL preservar referências e metodologia por componente. Estimativas concretas SHALL ser aceitas sem exigência de comprovação documental integral, identificadas como estimativas. A publicação SHALL depender de cobertura completa e simulações coerentes, com Linha 6 tratada por último e incluída somente no alcance parcial modelado e autorizado.

#### Scenario: Uma fonte contém somente duração agregada
- **WHEN** uma fonte informa o tempo total de uma linha sem tempos por parada
- **THEN** o acervo preserva a referência agregada e qualquer distribuição estimada exige metodologia explícita em vez de ser apresentada como medição

### Requirement: Margem separada e sem duplicação
O cálculo SHALL acrescentar exatamente 60 segundos uma única vez ao total-base do trajeto. Não SHALL aplicar margem individual por intervalo, estação, espera ou transferência, nem duplicá-la no cliente ou registro.

#### Scenario: Trajeto-base de quinze minutos
- **WHEN** o total-base é 900 segundos
- **THEN** o tempo estimado com margem é 960 segundos independentemente da quantidade de estações ou baldeações

#### Scenario: Corredor conecta duas linhas
- **WHEN** o passageiro atravessa Paulista–Consolação para mudar de linha
- **THEN** sua caminhada integra o total-base sem margem individual e o trajeto recebe apenas a reserva final única

### Requirement: Cronologia consistente de partidas e ocupação
Busca e registro de viagem SHALL usar a mesma versão de tempos-base. A margem final não SHALL deslocar horários de partida nem criar ocupação fictícia nos trechos.

#### Scenario: Serviço com partida marcada
- **WHEN** a estimativa final recebe a margem total
- **THEN** as partidas e intervalos físicos permanecem baseados na cronologia sem margem por componente

#### Scenario: Registro de padrão parcial
- **WHEN** uma busca seleciona um atendimento agregado limitado a um trecho central
- **THEN** a reprodução local do registro preserva esse padrão e recalcula espera, caminhada e início de cada trecho com as mesmas regras da busca, sem prometer continuação fora do alcance

#### Scenario: Referência de calibração incompatível
- **WHEN** o registro informa versão diferente, padrão inexistente ou cálculo com mais de trinta segundos
- **THEN** a reprodução local rejeita a viagem sem aproveitar tempos fornecidos pelo cliente

#### Scenario: Laboratório separado do contrato publicado
- **WHEN** o laboratório experimental está habilitado no cliente
- **THEN** sua configuração exige loopback, enquanto o contrato calibrado publicado é declarado explicitamente pelo cliente na API oficial e usa a mesma versão na busca e no registro

#### Scenario: Frequência muda durante a espera
- **WHEN** a espera estimada para embarque atravessa o limite para uma faixa de menor frequência
- **THEN** o cálculo usa a maior espera aplicável sem cobrá-la novamente em cada estação, e o registro reproduz o mesmo horário

#### Scenario: Obra tem início e término publicados
- **WHEN** uma exceção datada reduz a frequência em parte da Linha 9
- **THEN** a cópia local distingue o integral do agregado de alcance limitado, verifica a data também no embarque estimado e deixa de oferecer a exceção em novos embarques após sua vigência

#### Scenario: Conexão da Linha 17 próxima do encerramento
- **WHEN** o percurso cabe na cronologia nominal até 22h mas um cenário de espera completa e percurso mais lento ultrapassaria esse horário
- **THEN** a rota local informa a dependência do último trem sem alterar sua duração ou ocupação, e não oferece uma viagem cujo cálculo nominal já ultrapassa o limite

#### Scenario: Trecho ferroviário interditado
- **WHEN** o intervalo de passagem previsto cruza uma interdição oficial datada
- **THEN** a simulação local exclui esse trecho nos dois sentidos e compara alternativas disponíveis sem transformar PAESE em trecho ferroviário ou repetir estações

#### Scenario: Circulação com mobilidade reduzida
- **WHEN** o laboratório avalia o cenário de deslocamento assistido
- **THEN** o custo de circulação é estimado separadamente da espera pelo trem, o registro usa a mesma versão e o resultado não promete acessibilidade ou disponibilidade de elevadores

#### Scenario: Corredor e trem compartilham identificação da linha
- **WHEN** um corredor a pé e o trecho ferroviário seguinte têm a mesma identificação de linha e padrões técnicos distintos
- **THEN** essa diferença técnica não cria outra baldeação na validação do resultado

### Requirement: Apresentação como tempo estimado
A interface SHALL identificar o tempo como estimado e informar que pode variar conforme operação, lotação e condições externas.

#### Scenario: Busca com resultado
- **WHEN** o passageiro visualiza um trajeto
- **THEN** a duração é identificada como “Tempo estimado” sem promessa de chegada exata

### Requirement: Alternativa parcial com desvio limitado
Quando a alternativa totalmente livre não couber nos limites publicados, a busca SHALL poder selecionar um percurso parcialmente ocupado que reduza em pelo menos 40% o tempo previsto em trechos ocupados. O acréscimo SHALL ficar dentro do menor valor entre 540 segundos e 45% do tempo-base principal, com no máximo uma baldeação adicional. A margem pública de 60 segundos SHALL ficar fora dessa comparação.

#### Scenario: República reduz a exposição com acréscimo de oito minutos
- **WHEN** o principal tem 1155 segundos, uma baldeação e 885 segundos de exposição, e o caminho por República tem 1635 segundos, duas baldeações e 350 segundos de exposição
- **THEN** a alternativa por República é elegível e seu total público é 1695 segundos

#### Scenario: Desvio excede o limite ou reduz pouco a exposição
- **WHEN** um percurso excede o limite de tempo, acrescenta mais de uma baldeação ou reduz menos de 40% da exposição
- **THEN** a regra parcial não seleciona esse percurso

### Requirement: Preferência limitada por percurso do Metrô
Entre alternativas elegíveis por concorrência, o sistema SHALL preferir percurso inteiramente pelo Metrô até 60 segundos acima da alternativa original, preservando min(540 segundos, 45%) de acréscimo sobre o principal, no máximo uma baldeação extra e redução mínima de 40% da exposição. Essa preferência não SHALL presumir o trem em que o usuário já está.

#### Scenario: Alternativa por República excede o orçamento
- **WHEN** o principal tem 1185 segundos, a alternativa pela Luz tem 1625 segundos e exposição zero, e República tem 1725 segundos
- **THEN** mantém a alternativa pela Luz, pois República excede 45% sobre o principal e fica mais de 60 segundos acima da alternativa original
