## Context

O projeto é atualmente um esqueleto de aplicação Reflex. A interface será construída em Reflex, enquanto autenticação, dados, APIs e regras principais serão fornecidos pelo Xano. O workspace confirmado é “Raphael's Workspace” (`149130`), ambiente `v1`, mas seu schema precisa ser inspecionado em modo somente leitura antes de qualquer alteração.

O MVP cobre o transporte ferroviário metropolitano de São Paulo, incluindo Metrô, CPTM e concessionárias. Um usuário deverá autenticar-se por e-mail antes de planejar uma viagem. O trajeto principal será definido pelo menor tempo total e, em caso de empate, pela menor quantidade de baldeações.

A motivação e o comportamento esperado estão descritos em `proposal.md` e `specs/busca-trajetos/spec.md`.

## Goals / Non-Goals

**Goals:**

- Definir uma fronteira simples entre a interface Reflex e o backend Xano.
- Exigir autenticação para planejar viagens, dependendo de uma mudança OpenSpec separada para autenticação por e-mail.
- Propor a entidade `operadores` e sua associação às linhas para representar Metrô, CPTM e concessionárias, condicionadas à inspeção e aprovação.
- Carregar estações disponíveis e consultar trajetos pela API do Xano.
- Centralizar no Xano a determinação do trajeto principal.
- Somar `tempo_estimado`, integer positivo em segundos, de todos os trechos percorridos.
- Desempatar caminhos de mesmo tempo total pela menor quantidade de mudanças de linha.
- Representar trechos físicos bidirecionais uma única vez.
- Derivar baldeações da mudança de linha, sem tabela própria.
- Retornar resultado normalizado com estações, trechos, linhas, operadores, tempo total e baldeações.
- Manter estados distinguíveis de autenticação, carregamento, sucesso, ausência de trajeto e erro.

**Non-Goals:**

- Implementar área administrativa.
- Implementar lotação ou rotas alternativas.
- Considerar lotação na escolha do trajeto.
- Acrescentar caminhada, espera ou transferência ao tempo total do primeiro MVP.
- Integrar horários ou condições em tempo real.
- Criar tabela específica de baldeações ou de tempos de transferência.
- Implementar ou especificar nesta mudança o histórico de trajetos planejados.
- Criar tabela, API ou recursos de histórico antes da mudança OpenSpec separada `historico-trajetos`.
- Alterar o schema ou os dados do Xano antes da revisão e aprovação da modelagem.
- Fixar detalhes visuais além das informações necessárias para cumprir a especificação.

## Decisions

### Usar o Xano como fonte de verdade

O Reflex SHALL consumir autenticação, estações e trajetos pelas APIs do Xano. O Xano manterá a malha ferroviária e executará o cálculo do trajeto; o frontend manterá o estado da interação, adaptará o contrato e apresentará o resultado.

Antes de qualquer alteração no Xano, seu schema existente deverá ser inspecionado e comparado com este modelo. Nenhuma tabela ou endpoint de autenticação será criado até a modelagem ser revisada e aprovada.

### Depender de autenticação por e-mail

A autenticação por e-mail faz parte do MVP como dependência funcional, mas será especificada e implementada em uma mudança OpenSpec separada. Esta mudança define apenas que o planejador e a chamada de consulta de trajeto SHALL estar disponíveis somente para usuário autenticado. A estrutura de usuários e os endpoints de autenticação existentes no Xano deverão ser inspecionados antes da mudança específica.

### Modelar operadores, linhas, estações e trechos

O modelo esperado preserva as estruturas confirmadas abaixo e propõe explicitamente `operadores` e `linhas.operador_id`, ambos condicionados à inspeção do Xano e à aprovação.

**`operadores`**

A entidade `operadores` identificará Metrô, CPTM e concessionárias, com a seguinte estrutura aprovada para o MVP:

- `id`
- `created_at`
- `nome`
- `codigo`
- `ativo`

- `nome`: `text`, required, not nullable, normalizado com `trim` e sem default.
- `codigo`: `text`, required, not nullable, normalizado com `trim`, sem default e unique.
- `ativo`: `boolean`, required, not nullable e default `true`.

A tabela e seus índices serão criados somente após backup, revisão do plano de alteração e autorização explícita. O campo `linhas.operador_id` será uma Table Reference required e not nullable para `operadores`. O frontend utilizará `operadores.nome` para a apresentação discreta do operador associado à linha, dispensando `nome_exibicao` no MVP.

**`estacoes`**

- `id`
- `created_at`
- `nome`
- `codigo`
- `ativa`

- `nome`: `text`, required, not nullable, normalizado com `trim` e sem default.
- `codigo`: `text`, required, not nullable, normalizado com `trim`, sem default e unique.
- `ativa`: `boolean`, required, not nullable e default `true`.

A configuração de `ativa` foi confirmada diretamente na interface do Xano com **Allow nullable values** desmarcado, **Default value** igual a `true`, **Required** marcado e **Column visibility** como `Visible`. A exportação do CLI como `bool ativa?=true` não representa integralmente a configuração **Required** usada pelo Database Link e não autoriza alteração do campo.

**`linhas`**

- `id`
- `created_at`
- `operador_id`
- `nome`
- `codigo`
- `cor`
- `ativa`

- `nome`: `text`, required, not nullable, normalizado com `trim` e sem default.
- `codigo`: `text`, required, not nullable, normalizado com `trim`, sem default e unique.
- `cor`: `text` opcional, normalizado com `trim`.
- `ativa`: `boolean`, required, not nullable e default `true`.
- `operador_id`: Table Reference required e not nullable para `operadores`, aprovada para a modelagem do MVP, mas ainda não existente no Xano. Sua criação dependerá de backup, revisão do plano de alteração e autorização explícita.

A configuração de `ativa` foi confirmada diretamente na interface do Xano com **Allow nullable values** desmarcado, **Default value** igual a `true`, **Required** marcado e **Column visibility** como `Visible`. A representação `bool ativa?=true` exportada pelo CLI não torna o campo opcional para o Database Link e não deverá ser modificada apenas para alterar essa representação.

Quando a proposta for aprovada e implementada, o frontend deverá exibir discretamente o operador associado, por exemplo, “Linha 8–Diamante — ViaMobilidade”.

**`estacoes_linhas`**

- `id`
- `created_at`
- `estacao_id`
- `linha_id`
- `ordem`

- `estacao_id`: Table Reference para `estacoes`, required e not nullable.
- `linha_id`: Table Reference para `linhas`, required e not nullable.
- `ordem`: `integer` positivo, required e not nullable.
- A combinação `estacao_id + linha_id` SHALL possuir unique composto.

**`trechos`**

- `id`
- `created_at`
- `estacao_origem_id`
- `estacao_destino_id`
- `linha_id`
- `tempo_estimado`
- `ativo`

- `estacao_origem_id`: Table Reference para `estacoes`, required e not nullable.
- `estacao_destino_id`: Table Reference para `estacoes`, required e not nullable.
- `linha_id`: Table Reference para `linhas`, required e not nullable.
- `tempo_estimado`: `integer` positivo em segundos, required e not nullable.
- `ativo`: `boolean`, required, not nullable e default `true`.

A configuração de `ativo` foi confirmada diretamente na interface do Xano com **Allow nullable values** desmarcado, **Default value** igual a `true`, **Required** marcado e **Column visibility** como `Visible`. A representação `bool ativo?=true` do CLI não expõe integralmente a configuração de entrada do Database Link e não indica pendência de schema.

As constraints de armazenamento e as configurações de entrada geradas pelo Database Link SHALL ser verificadas separadamente. Para estes três booleanos, a interface do Xano é a evidência da configuração de entrada; a exportação XanoScript permanece útil para estrutura e default, mas não deve ser interpretada isoladamente como prova de opcionalidade.

Um trecho físico será armazenado uma única vez e percorrível nos dois sentidos. As regras de integridade têm mecanismos distintos:

- origem igual ao destino SHALL ser rejeitada por validação;
- duplicata direta na mesma linha SHALL ser protegida por unicidade composta de `estacao_origem_id + estacao_destino_id + linha_id`;
- duplicata inversa na mesma linha SHALL ser impedida por normalização canônica dos extremos ou validação lógica equivalente, pois a unicidade composta direta não detecta a inversão.

Os nomes `estacao_origem_id` e `estacao_destino_id` SHALL ser preservados.

### Calcular o trajeto principal

O tempo total SHALL ser exclusivamente a soma de `tempo_estimado` dos trechos percorridos. Não haverá custo adicional de caminhada, espera ou transferência no primeiro MVP.

Quando dois ou mais caminhos tiverem o mesmo tempo total, será escolhido aquele com menor quantidade de baldeações. A quantidade de baldeações é o número de mudanças de linha entre trechos consecutivos e não altera o tempo total.

A arquitetura deverá permitir a inclusão futura de tempos reais de transferência sem exigir agora tabela específica ou antecipar seu formato de armazenamento.

#### Usar Dijkstra no primeiro MVP

O cálculo do trajeto principal será implementado com o algoritmo de Dijkstra. O estado da busca deverá considerar a estação e a linha atual para permitir a contagem correta das mudanças de linha.

O custo será comparado lexicograficamente como `(tempo_total, quantidade_de_baldeações)`: primeiro será escolhido o menor tempo total e, somente em caso de empate, a menor quantidade de baldeações.

Essa regra pode favorecer uma economia mínima de tempo ao custo de várias baldeações. Essa limitação é aceita no primeiro MVP. Após sua conclusão, uma mudança separada deverá avaliar uma tolerância de tempo ou uma penalidade por baldeação, usando a malha real e testes de experiência do usuário. A margem ou penalidade não será definida nesta mudança.

### Derivar baldeações

Não haverá tabela de pontos de baldeação. Uma baldeação será derivada quando a `linha_id` de um trecho for diferente da `linha_id` do trecho seguinte. O resultado normalizado deverá identificar a estação comum em que a mudança ocorre, a linha anterior e a linha seguinte.

### Normalizar o contrato da rota

O resultado deverá identificar:

- origem e destino;
- estações percorridas em ordem;
- trechos percorridos;
- linha e operador de cada trecho;
- baldeações derivadas;
- tempo total estimado em segundos;
- quantidade de baldeações.

O frontend poderá converter segundos para minutos apenas para exibição, sem alterar o valor canônico do contrato.

### Validar a busca e os estados da interface

O frontend deverá rejeitar origem ou destino ausentes e origem igual ao destino antes de chamar o Xano. O backend deverá repetir validações relevantes de autorização e integridade. A interface distinguirá `idle`, `loading`, `success`, `not_found` e `error`, além do estado não autenticado, e impedirá solicitações duplicadas durante o carregamento.

### Planejar o histórico em uma mudança futura

O histórico não faz parte da capability `busca-trajetos` desta mudança. Ele será especificado futuramente em uma mudança OpenSpec separada, conceitualmente denominada `historico-trajetos`, após a definição da tabela de usuários na mudança de autenticação.

As decisões de produto já estabelecidas para essa mudança futura são:

- o histórico representa viagens planejadas e não comprova que o usuário realizou a viagem;
- cada usuário verá somente os seus 10 trajetos planejados mais recentes;
- uma repetição consecutiva da mesma origem e destino não criará novo item;
- somente buscas concluídas com trajeto válido serão registradas;
- buscas inválidas, sem trajeto ou com erro não serão registradas;
- o usuário poderá excluir individualmente um item;
- o usuário poderá limpar todo o próprio histórico;
- selecionar um item recente executará novamente o cálculo com a malha atual;
- não será armazenada localização em tempo real;
- não será armazenada uma cópia completa e permanente dos trechos apenas para reutilização rápida;
- cada registro pertencerá ao usuário autenticado e nunca poderá ser acessado por outro usuário.

A modelagem preliminar, ainda não aprovada para criação, é:

**`historico_trajetos`**

- `id`;
- `created_at`;
- `user_id`: Table Reference para `user`, required e not nullable;
- `estacao_origem_id`: Table Reference para `estacoes`, required e not nullable;
- `estacao_destino_id`: Table Reference para `estacoes`, required e not nullable;
- `tempo_total_calculado`: `integer` em segundos;
- `quantidade_baldeacoes`: `integer` não negativo.

A definição exata de `user_id`, das regras de acesso por proprietário, da nulabilidade dos campos de resultado e dos índices dependerá da mudança separada de autenticação e da futura especificação `historico-trajetos`. Nenhuma tabela, API, função ou regra de autenticação do histórico será criada como parte desta mudança.

## Risks / Trade-offs

- **Schema Xano ainda não inspecionado:** comparar o modelo existente antes de propor qualquer migração.
- **Plano Free sem sandbox:** futuras alterações atingirão diretamente o workspace; exigir revisão, `dry-run` quando disponível e autorização explícita.
- **Unicidade bidirecional:** índices simples não detectam automaticamente a combinação inversa; aplicar normalização lógica e testes de integridade.
- **Dados inconsistentes:** validar referências, códigos, ordem e tempos antes de calcular rotas.
- **Unidade histórica dos tempos:** os trechos de IDs 1 a 5 foram cadastrados com valor `2` em minutos e deverão ser convertidos individualmente para `120` segundos, preservando todos os demais campos.
- **Transferência sem custo no MVP:** o resultado pode favorecer caminhos com mudanças rápidas; o desempate reduz apenas empates e a limitação deverá ser conhecida.
- **Crescimento da malha:** acompanhar desempenho do algoritmo no Xano para toda a rede metropolitana.
- **Rede lenta ou indisponível:** manter feedback e nova tentativa no frontend.

## Migration Plan

1. Inspecionar em modo somente leitura o schema, relacionamentos, índices, autenticação e APIs existentes no workspace `149130`, ambiente `v1`.
2. Comparar o schema encontrado com a modelagem aprovada e documentar divergências sem alterar o Xano.
3. Obter aprovação explícita para qualquer alteração no Xano.
4. Ajustar, somente após aprovação, operadores, estações, linhas, associações e trechos preservando dados existentes.
5. Aplicar a dependência da mudança OpenSpec separada de autenticação por e-mail e proteger os endpoints de planejamento.
6. Definir os contratos de listagem de estações e consulta de trajeto.
7. Implementar e testar o cálculo por tempo total e desempate por baldeações.
8. Implementar o adaptador e a interface Reflex.
9. Validar cenários automatizados e integrados.
10. Após concluir a definição de autenticação, criar uma mudança OpenSpec separada `historico-trajetos` para especificar histórico, propriedade por usuário, retenção dos 10 itens recentes, exclusões e recálculo com a malha atual.

Rollback: qualquer futura mudança deverá ter estratégia específica aprovada antes da aplicação. Não excluir dados, tabelas ou arquivos como mecanismo padrão de rollback.

## Open Questions

- Quais serão os formatos e URLs finais dos endpoints de desenvolvimento e produção? Essa definição será feita durante a criação das APIs e deverá ser configurada por ambiente, sem expor valores diretamente no código.
