## Why

O MetroFlow precisa oferecer uma primeira experiência útil para consultar como chegar de uma estação de metrô a outra. Este MVP estabelece o fluxo essencial de busca de trajetos antes de adicionar informações de lotação ou rotas alternativas.

## What Changes

- Adicionar uma capacidade de busca em que o usuário seleciona uma estação de origem e uma estação de destino.
- Buscar um trajeto principal entre as estações selecionadas, considerando o melhor caminho disponível de acordo com os critérios definidos para o MVP.
- Exibir as estações percorridas, as linhas utilizadas e os pontos em que ocorre baldeação.
- Definir estados de seleção incompleta, consulta em andamento, resultado encontrado e ausência de trajeto válido.
- Excluir deste MVP dados de lotação e rotas alternativas; esses recursos serão especificados em mudanças futuras.

## Capabilities

### New Capabilities

- `busca-trajetos`: Permite selecionar origem e destino e consultar e visualizar o trajeto principal de metrô, incluindo estações, linhas e baldeações.

### Modified Capabilities

Nenhuma.

## Impact

- Frontend Reflex: nova tela ou fluxo de consulta, controles de seleção e apresentação do resultado e dos estados da busca.
- Xano: armazenamento e disponibilização dos dados de estações, linhas, conexões e demais informações necessárias para a busca de trajetos por meio de APIs.
- Modelo de domínio: representação consistente de estações, linhas, trechos e pontos de transferência.
- Testes: cobertura dos critérios de seleção, consulta, apresentação do trajeto e estados sem resultado.
- Fora do escopo: cálculo ou exibição de lotação e geração de rotas alternativas.