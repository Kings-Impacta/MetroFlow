## Why

A API Trilhos da ARTESP deixou de cobrir as linhas geridas diretamente pelo Metrô e
pela CPTM. O MetroFlow precisa informar claramente a condição das linhas de um
trajeto sem apresentar cobertura parcial como se representasse toda a rede e sem
depender de coleta frágil de páginas HTML.

## What Changes

- Integrar condições operacionais por adaptadores de fontes autorizadas.
- Usar a ARTESP como fonte primária da malha delegada.
- Complementar as demais linhas somente com fonte oficial cujo uso por terceiros
  esteja confirmado.
- Normalizar fonte, situação, descrição, horários, validade e disponibilidade.
- Aplicar cache compatível com os limites de cada origem.
- Exibir condição indisponível ou desatualizada sem bloquear o planejamento.
- Manter a condição operacional apenas informativa nesta entrega, sem mudar o
  algoritmo de escolha do trajeto.

## Capabilities

### New Capabilities

- `status-operacional-linhas`: consulta e apresentação rastreável da condição das
  linhas usadas no planejamento.

### Modified Capabilities

Nenhuma. A busca atual permanece com a mesma regra de cálculo.

## Impact

A mudança adicionará adaptadores externos no backend, cache, um contrato interno de
condição operacional, apresentação no Reflex e testes de normalização e falha. A
implementação remota fica condicionada à chave da ARTESP e à confirmação dos termos
das fontes complementares.
