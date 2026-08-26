## Context

O estado atual do projeto é um esqueleto de aplicação Reflex, sem a capacidade de consulta de trajetos implementada. Conforme a proposta, a interface será construída em Reflex e os dados, APIs e regras principais da busca serão fornecidos pelo Xano.

O MVP deverá permitir que o usuário selecione uma estação de origem e uma estação de destino e receba o trajeto principal entre elas. O trajeto principal será definido pelo menor tempo estimado de percurso e, em caso de empate, pela menor quantidade de baldeações.

A motivação e o comportamento esperado estão descritos em `proposal.md` e `specs/buscar-trajetos/spec.md`.

## Goals / Non-Goals

**Goals:**

- Definir uma fronteira simples entre o estado da interface Reflex e o backend Xano.
- Permitir carregar as estações disponíveis por meio da API.
- Enviar origem e destino selecionados para consulta.
- Centralizar no Xano a lógica responsável pela determinação do trajeto principal.
- Considerar como trajeto principal aquele com menor tempo estimado de percurso.
- Em caso de empate no tempo estimado, priorizar o trajeto com menor quantidade de baldeações.
- Retornar ao frontend um resultado normalizado para apresentação.
- Representar o trajeto como uma sequência ordenada de estações e trechos, associados às respectivas linhas e pontos de baldeação.
- Manter estados distinguíveis de carregamento, sucesso, ausência de trajeto e erro.

**Non-Goals:**

- Implementar nível de lotação.
- Gerar ou apresentar rotas alternativas.
- Considerar lotação como critério para escolha do trajeto.
- Integrar horários ou condições em tempo real nesta primeira versão.
- Definir autenticação, administração da malha metroviária ou edição de dados no Xano.
- Fixar detalhes visuais além das informações necessárias para cumprir a especificação.

## Decisions

### Usar o Xano como fonte de verdade e camada de lógica da rota

A aplicação Reflex SHALL consumir as estações e solicitar trajetos pela API do Xano.

O Xano será responsável por manter os dados da malha metroviária e executar a lógica necessária para determinar o trajeto principal. O frontend manterá apenas o estado da interação e a apresentação do resultado.

Essa decisão evita duplicar a malha e as regras de negócio no cliente e permite que futuras funcionalidades, como lotação e rotas alternativas, sejam incorporadas sem alterar a responsabilidade principal do frontend.

Alternativa considerada: manter a malha e calcular trajetos no frontend. Foi descartada porque criaria duplicação de dados e lógica e aumentaria o risco de divergência entre o backend e a interface.

### Critério para definição do trajeto principal

O Xano deverá avaliar os trajetos disponíveis entre origem e destino.

O trajeto principal será aquele com menor tempo estimado total.

Quando dois ou mais trajetos possuírem o mesmo tempo estimado, será escolhido o que tiver menor quantidade de baldeações.

Para permitir esse cálculo, os trechos da rede deverão possuir as informações necessárias para determinar seu tempo estimado de percurso.

### Normalizar o resultado em estações e trechos

O contrato de resposta deverá identificar:

- origem;
- destino;
- estações percorridas em ordem;
- trechos percorridos;
- linha utilizada em cada trecho;
- pontos de baldeação;
- tempo total estimado;
- quantidade de baldeações.

Cada trecho deverá informar a linha utilizada e as estações relacionadas.

As baldeações deverão ser identificadas quando houver mudança de linha durante o percurso e disponibilizadas explicitamente no resultado normalizado.

Alternativa considerada: retornar apenas uma lista plana de estações e linhas. Foi descartada porque torna ambíguo onde ocorre a troca de linha e dificulta a apresentação consistente do trajeto.

### Validar a busca antes da chamada externa

A camada de estado do frontend deve rejeitar origem ou destino ausentes e a seleção da mesma estação antes de chamar o Xano.

O botão de consulta deverá refletir o estado de carregamento para evitar solicitações duplicadas.

Alternativa considerada: deixar todas as validações somente para a API. Foi descartada porque aumenta chamadas desnecessárias e não fornece feedback imediato ao usuário.

### Tratar estados da consulta como contrato de UI

A interface deverá distinguir os estados:

- `idle`
- `loading`
- `success`
- `not_found`
- `error`

O resultado anterior não deverá permanecer apresentado como se correspondesse à nova seleção enquanto uma nova consulta estiver em andamento.

Alternativa considerada: utilizar apenas uma mensagem genérica de erro. Foi descartada porque não diferencia ausência legítima de trajeto de indisponibilidade do serviço.

## Risks / Trade-offs

- **Contrato Xano ainda não definido:** documentar os campos mínimos de entrada e saída antes da implementação e criar um adaptador para que a interface não dependa diretamente do formato bruto da API.
- **Dados inconsistentes de linhas, estações ou tempos:** validar a resposta recebida e tratar resultados incompletos como erro, sem apresentar uma rota enganosa.
- **Estimativas de tempo incompletas:** garantir que os trechos necessários para o cálculo do trajeto possuam um valor de tempo estimado válido.
- **Rede lenta ou indisponível:** exibir estado de carregamento, permitir nova tentativa e manter a interface responsiva.
- **Modelo de baldeação variar entre linhas:** centralizar a regra em uma única camada e cobrir trajetos de uma e de múltiplas linhas nos testes.
- **Crescimento da malha:** acompanhar o desempenho do cálculo no Xano e revisar a estratégia caso o volume de estações e conexões aumente significativamente.

## Migration Plan

1. Definir o modelo de dados necessário para estações, linhas, conexões e tempos estimados.
2. Definir e validar no Xano os endpoints de listagem de estações e consulta de trajeto.
3. Implementar no Xano a regra de determinação do trajeto principal.
4. Implementar o adaptador da API e o modelo normalizado no frontend Reflex.
5. Conectar os controles de seleção e os estados da tela ao adaptador.
6. Validar os cenários da especificação em testes automatizados e em execução integrada com o Xano.
7. Confirmar que o resultado retornado respeita menor tempo estimado e, em caso de empate, menor quantidade de baldeações.

Rollback: remover a entrada do fluxo de busca e desativar os endpoints consumidores sem alterar os dados existentes da rede.

## Open Questions

- Qual será o formato final e a URL dos endpoints Xano para os ambientes de desenvolvimento e produção?
- Qual será o formato exato das tabelas e relacionamentos de estações, linhas e conexões no Xano?
- Como será armazenado o tempo estimado de cada trecho?
- A lista de estações será carregada de uma só vez ou haverá busca/paginação no endpoint?
- Qual abordagem será utilizada no Xano para calcular o menor caminho de forma eficiente?