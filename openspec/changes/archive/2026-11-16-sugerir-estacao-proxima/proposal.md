## Why

Para começar uma consulta, o passageiro precisa saber o nome da estação de onde vai
partir e digitá-lo. Quem está na rua, sem conhecer bem a região, nem sempre sabe qual
é a estação mais próxima. O navegador já permite, com autorização do usuário,
conhecer a posição aproximada do aparelho e usá-la para sugerir essa estação.

## What Changes

- Exibir no planejador o aviso "Encontrar a estação mais próxima de você?", com os
  botões "Usar minha localização" e "Agora não".
- Ao tocar em "Usar minha localização", pedir ao navegador a permissão de
  localização. Com a permissão concedida, preencher a origem com a estação
  cadastrada mais próxima e exibir "Estação mais próxima: ~N m (distância em linha
  reta)".
- Calcular a estação mais próxima no próprio navegador. A posição do usuário não é
  enviada ao backend nem ao Xano, não é guardada e não aparece em logs.
- Manter no repositório um arquivo CSV versionado com as coordenadas das estações,
  cada uma com fonte e data de coleta, lido e validado pelo backend Python. A
  primeira carga cobre as 188 estações da malha: as 10 cujas coordenadas já estão
  nos estudos de tempo e as demais do OpenStreetMap.
- Acrescentar latitude e longitude opcionais à lista de estações entregue ao
  planejador. Sem coordenadas, o aviso não aparece.
- Ligar a funcionalidade por padrão e permitir desligá-la com
  `METROFLOW_LOCALIZACAO=0`. Desligada, o planejador se comporta exatamente como
  antes desta mudança.

Fica fora desta mudança:

- qualquer alteração de tabelas, endpoints ou dados do Xano;
- mapa, lista das estações próximas, rota a pé e status das linhas próximas;
- acompanhamento da posição durante a viagem;
- pedido de permissão automático ao abrir a página; ele só ocorre após o toque;
- garantia de cobertura de estações cadastradas no futuro; estações sem coordenada
  não são sugeridas;
- alteração da busca, do cálculo, da concorrência ou do registro da viagem;
- publicação do aplicativo em HTTPS para uso fora do `localhost`.

## Capabilities

### New Capabilities

- `localizacao-estacao-proxima`: sugestão opcional, por meio da localização do
  navegador, da estação cadastrada mais próxima como origem do planejamento.

### Modified Capabilities

Nenhuma. A seleção de origem e destino de `busca-trajetos` continua igual; a sugestão
apenas preenche a origem pelo mesmo mecanismo de escolha manual.

## Impact

- **Xano:** nenhum impacto. Tabelas, endpoints e dados permanecem inalterados.
- **Backend Python:** leitura e validação do CSV de coordenadas, interruptor por
  variável de ambiente e campos opcionais `latitude` e `longitude` em
  `GET /api/planning/stations`.
- **Reflex:** aviso com dois botões no planejador, script de localização executado
  no navegador e texto da distância abaixo da origem.
- **Dados e documentação:** arquivo `docs/dados/coordenadas-estacoes.csv` e
  atualização do README, da arquitetura e do modelo de domínio.
- **Testes:** validação do CSV, associação por nome, interruptor, campos opcionais
  na lista de estações, script de localização com navegador simulado e estado do
  planejador.
