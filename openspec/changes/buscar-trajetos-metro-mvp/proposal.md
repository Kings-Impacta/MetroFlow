## Why

O MetroFlow precisa oferecer uma primeira experiência útil e autenticada para planejar viagens na rede de transporte ferroviário metropolitano de São Paulo. O MVP estabelece o fluxo essencial de busca do trajeto principal entre estações do Metrô, da CPTM e das concessionárias antes de adicionar informações de lotação, rotas alternativas ou tempos reais de transferência.

## What Changes

- Exigir uma sessão autenticada para planejar uma viagem; a autenticação por e-mail será especificada e implementada em uma mudança OpenSpec separada.
- Permitir que o usuário autenticado selecione uma estação de origem e uma estação de destino da malha ferroviária metropolitana disponível.
- Buscar o trajeto principal pelo menor tempo total estimado, calculado pela soma de `tempo_estimado` dos trechos e por uma penalidade fixa de 600 segundos por mudança de linha.
- Em caso de empate no tempo total, priorizar o trajeto com menor quantidade de baldeações.
- Exibir as estações percorridas, as linhas, seus operadores ou concessionárias e os pontos em que ocorre mudança de linha.
- Representar baldeações como informação derivada da mudança de linha, sem tabela específica.
- Representar cada trecho físico bidirecional uma única vez, impedindo duplicatas no mesmo sentido ou no sentido inverso.
- Definir estados de autenticação, seleção incompleta, consulta em andamento, resultado encontrado e ausência de trajeto válido.
- Excluir deste MVP dados de lotação, rotas alternativas e tempos reais ou específicos de caminhada, espera e transferência.

## Capabilities

### New Capabilities

- `busca-trajetos`: Permite que um usuário autenticado selecione origem e destino e consulte o trajeto principal na rede de transporte ferroviário metropolitano, incluindo estações, linhas, operadores e baldeações derivadas.

### Modified Capabilities

Nenhuma.

## Impact

- Frontend Reflex: dependência de uma sessão autenticada, proteção do planejador, controles de seleção e apresentação dos estados e do resultado.
- Xano: armazenamento da malha e disponibilização de estações, linhas, associações estação-linha e trechos por meio de APIs; a entidade `operadores` e sua associação com linhas são alterações propostas, condicionadas à inspeção e aprovação.
- Modelo de domínio: proposta de operadores associados às linhas, estações, associações ordenadas entre estações e linhas e trechos físicos bidirecionais armazenados uma única vez.
- Regra de rota: soma dos tempos estimados dos trechos com 600 segundos por mudança de linha; em empate, menor quantidade de mudanças.
- Testes: autenticação obrigatória, integridade da modelagem, cálculo da rota, apresentação e estados sem resultado.
- Fora do escopo: área administrativa, lotação, rotas alternativas, tempos reais ou específicos por estação para caminhada, espera e transferência, e implementação do histórico. O histórico será tratado futuramente em uma mudança OpenSpec separada, conceitualmente denominada `historico-trajetos`, armazenará somente viagens planejadas de usuários autenticados e permitirá replanejamento rápido utilizando a malha atual.
