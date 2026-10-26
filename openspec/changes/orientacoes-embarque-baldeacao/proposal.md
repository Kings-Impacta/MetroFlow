## Why

As instruções de viagem dizem qual linha usar e em que sentido, mas não ajudam o
passageiro dentro da estação: em qual lado a porta abre e o que mais vale saber ao
descer, como o carro mais perto da escada ou o caminho da baldeação.
Não há API nem base aberta com esses dados para o Metrô, a CPTM e as
concessionárias, então eles precisam ser coletados, registrados com fonte e
publicados pelo próprio projeto.

## What Changes

- Manter no repositório um arquivo CSV versionado com orientações por estação,
  linha e sentido de chegada. A informação principal é o lado de desembarque; uma
  observação adicional em texto livre, de até 200 caracteres, registra qualquer
  outra dica relevante. Cada registro informa a fonte e a data de coleta.
- Ler e validar esse arquivo no backend Python, sem nenhuma alteração no Xano.
- Apresentar as orientações por padrão e permitir desligá-las com a variável de
  ambiente `METROFLOW_ORIENTACOES=0`; desligada, a aplicação se comporta
  exatamente como antes desta mudança.
- Associar, no backend, as orientações às etapas do trajeto e apresentá-las nos
  cartões de "Como chegar" do Reflex somente quando existirem.
- Preparar um piloto com as estações de baldeação e de destino da rota de
  demonstração Jandira → Paraíso, com os campos de orientação a preencher pela
  coleta em campo.

Fica fora desta mudança:

- qualquer alteração de tabelas, endpoints ou dados do Xano; migrar as orientações
  para o Xano será uma mudança futura;
- cobertura completa da malha; estações sem registro continuam com as instruções
  atuais;
- alteração do cálculo, da escolha do trajeto ou do tempo estimado;
- dados em tempo real, lotação, acessibilidade detalhada ou tempo de caminhada;
- tela administrativa de cadastro; a manutenção ocorre pelo arquivo CSV;
- coleta automática do HTML de sites das operadoras.

## Capabilities

### New Capabilities

- `orientacoes-viagem`: cadastro rastreável e apresentação opcional do lado de
  desembarque e de uma observação adicional nas instruções de viagem.

### Modified Capabilities

- `busca-trajetos`: o requisito "Escopo do MVP" passa a admitir as orientações
  opcionais da nova capacidade no resultado, sem alterar a escolha do trajeto.

## Impact

- **Xano:** nenhum impacto. Tabelas, endpoints e dados permanecem inalterados.
- **Backend Python:** modelo de domínio, leitura e validação do CSV, interruptor
  por variável de ambiente e associação das orientações às etapas; o contrato
  `POST /api/planning/route` ganha um campo opcional por trecho, ausente quando não há
  orientação ou a funcionalidade está desligada.
- **Reflex:** cartões de instrução exibem as orientações quando presentes.
- **Dados e documentação:** arquivo em `docs/dados/`, guia de coleta e atualização
  de `docs/api-planejamento-exemplos.md`, do modelo de domínio e da arquitetura.
- **Testes:** validação do arquivo, associação às etapas, interruptor ligado por padrão e desligado com `0`,
  arquivo ausente ou inválido sem bloquear o planejamento.
