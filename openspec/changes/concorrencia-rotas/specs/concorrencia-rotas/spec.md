## ADDED Requirements

### Requirement: Confirmação de viagem

O sistema SHALL permitir que o usuário autenticado confirme, por um botão no resultado do trajeto, que vai fazer a viagem apresentada, e SHALL registrar no Xano o usuário, o momento da confirmação e os trechos em ordem com seu sentido e `tempo_estimado`. Após a confirmação, a interface SHALL não exibir aviso e SHALL manter o botão disponível.

#### Scenario: Confirmação bem-sucedida

- **WHEN** o usuário autenticado aciona o botão de confirmação no resultado do trajeto
- **THEN** o sistema registra a viagem apresentada como viagem ativa desse usuário

#### Scenario: Sessão inválida na confirmação

- **WHEN** a confirmação é solicitada sem sessão válida
- **THEN** o sistema não registra a viagem e direciona o usuário para autenticação

#### Scenario: Usuário da viagem

- **WHEN** uma viagem é registrada
- **THEN** o usuário associado é obtido da sessão autenticada e não de um dado enviado pela interface

#### Scenario: Interface após a confirmação

- **WHEN** a viagem é registrada
- **THEN** a interface não exibe aviso de confirmação e o botão continua disponível

### Requirement: Uma viagem ativa por usuário

O sistema SHALL manter no máximo uma viagem ativa por usuário. Uma nova confirmação SHALL substituir a viagem ativa anterior, que deixa de contar imediatamente. O sistema SHALL não oferecer cancelamento manual.

#### Scenario: Nova confirmação com viagem ativa

- **WHEN** um usuário com viagem ativa confirma outra viagem
- **THEN** a viagem anterior deixa de contar na lotação no mesmo momento e a nova passa a ser a viagem ativa

#### Scenario: Reconfirmação do mesmo trajeto

- **WHEN** um usuário com viagem ativa confirma novamente o mesmo trajeto
- **THEN** a viagem anterior é substituída e a janela recomeça no momento da nova confirmação

### Requirement: Janela da viagem

A janela da viagem SHALL começar no momento da confirmação e terminar nesse momento somado à soma de `tempo_estimado` dos trechos, sem a penalidade de baldeação. Após o fim da janela, a viagem SHALL deixar de contar e o registro SHALL ser mantido.

#### Scenario: Fim da janela

- **WHEN** o instante atual ultrapassa o fim da janela de uma viagem
- **THEN** a viagem deixa de ser ativa e seu registro continua armazenado

#### Scenario: Baldeação não altera a janela

- **WHEN** a viagem confirmada contém mudanças de linha
- **THEN** a duração da janela não inclui os 600 segundos por mudança

### Requirement: Intervalo estimado em cada trecho

O sistema SHALL considerar que uma viagem ativa ocupa cada trecho, no sentido percorrido, somente no intervalo que começa na confirmação somada ao `tempo_estimado` dos trechos anteriores e termina somando o `tempo_estimado` do próprio trecho.

#### Scenario: Trecho ainda não alcançado

- **WHEN** o instante atual é anterior ao intervalo estimado da viagem em um trecho
- **THEN** a viagem não conta na ocupação desse trecho

#### Scenario: Trecho já percorrido

- **WHEN** o instante atual é posterior ao intervalo estimado da viagem em um trecho
- **THEN** a viagem não conta na ocupação desse trecho

### Requirement: Trechos considerados na lotação

Somente trechos ferroviários SHALL entrar na estimativa de lotação. Trechos de integração a pé e de serviços especiais SHALL não receber ocupação e SHALL nunca ser considerados lotados, mas o `tempo_estimado` deles SHALL continuar contando na janela da viagem e no início dos intervalos dos trechos seguintes.

#### Scenario: Integração a pé

- **WHEN** viagens ativas passam por um trecho de integração a pé
- **THEN** esse trecho não é considerado lotado, qualquer que seja a quantidade de viagens

#### Scenario: Serviço especial

- **WHEN** viagens ativas passam por um trecho de serviço especial
- **THEN** esse trecho não é considerado lotado, qualquer que seja a quantidade de viagens

#### Scenario: Tempo de trechos não ferroviários

- **WHEN** uma viagem contém um trecho de integração a pé antes de um trecho ferroviário
- **THEN** o `tempo_estimado` da integração a pé é somado ao início do intervalo do trecho ferroviário seguinte

### Requirement: Ocupação estimada por trecho e sentido

No momento da busca, o sistema SHALL calcular a ocupação de cada trecho em cada sentido como a quantidade de viagens ativas cujo intervalo nesse trecho e sentido contém o instante atual, e o percentual como essa ocupação dividida pelo total de viagens ativas. A viagem ativa do usuário que busca SHALL ser desconsiderada na ocupação e no total.

#### Scenario: Viagem ativa de quem busca

- **WHEN** o usuário que busca possui viagem ativa
- **THEN** essa viagem não entra na ocupação nem no total usados na busca

### Requirement: Critério de lotação

Um trecho SHALL ser considerado lotado em um sentido quando, ao mesmo tempo, a ocupação for maior ou igual ao mínimo de usuários e o percentual for maior ou igual ao limite, ambos definidos na tabela de configuração do Xano.

#### Scenario: Sentidos independentes

- **WHEN** um trecho está lotado em um sentido
- **THEN** o outro sentido do mesmo trecho é avaliado separadamente

#### Scenario: Percentual atingido sem mínimo de usuários

- **WHEN** um trecho atinge o percentual mas não o mínimo de usuários
- **THEN** o trecho não é considerado lotado

#### Scenario: Mínimo atingido sem percentual

- **WHEN** um trecho atinge o mínimo de usuários mas não o percentual
- **THEN** o trecho não é considerado lotado

#### Scenario: Valores iguais aos parâmetros

- **WHEN** a ocupação de um trecho é igual ao mínimo de usuários e o percentual é igual ao limite
- **THEN** o trecho é considerado lotado

#### Scenario: Parâmetros configuráveis

- **WHEN** o mínimo de usuários ou o percentual é alterado na tabela de configuração
- **THEN** as buscas seguintes usam os novos valores sem alteração de código

### Requirement: Substituição do trajeto por lotação

Quando o trajeto principal passar por um trecho lotado no sentido percorrido, o sistema SHALL apresentar no lugar dele o caminho de menor tempo que evite os trechos lotados nos sentidos em que estão lotados, sem limite de tempo extra. Se esse caminho não existir, o sistema SHALL apresentar o trajeto principal.

#### Scenario: Trajeto principal sem trecho lotado

- **WHEN** nenhum trecho do trajeto principal está lotado no sentido percorrido
- **THEN** o sistema apresenta o trajeto principal

#### Scenario: Alternativa disponível

- **WHEN** o trajeto principal passa por um trecho lotado e existe caminho que evita os trechos lotados
- **THEN** o sistema apresenta somente esse caminho alternativo

#### Scenario: Alternativa indisponível

- **WHEN** o trajeto principal passa por um trecho lotado e não existe caminho que evite os trechos lotados
- **THEN** o sistema apresenta o trajeto principal

### Requirement: Lotação de uso interno

O sistema SHALL não apresentar ao usuário a lotação estimada nem indicar que o trajeto apresentado substituiu o principal, e a resposta pública da busca SHALL não conter esses dados.

#### Scenario: Resultado substituído

- **WHEN** o sistema apresenta um caminho alternativo por lotação
- **THEN** o resultado tem a mesma forma de um trajeto principal, sem aviso nem dados de lotação

### Requirement: Retenção e acesso aos registros

Os registros de viagens confirmadas SHALL ser mantidos sem prazo de exclusão e SHALL ser acessíveis somente no Xano, sem resposta pública que os devolva.

#### Scenario: Registro sem exposição

- **WHEN** o usuário confirma uma viagem ou busca um trajeto
- **THEN** a resposta não contém registros de viagens confirmadas
