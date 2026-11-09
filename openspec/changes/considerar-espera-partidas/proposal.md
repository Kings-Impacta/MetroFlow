## Why

Serviços com partidas espaçadas empatam com trens regulares porque a busca não
inclui espera. A disponibilidade é verificada apenas no instante da consulta,
permitindo conexões que fecham antes da chegada do passageiro.

## What Changes

- Calcular chegada, transferência e espera por embarque, mantendo o trem nas
  estações intermediárias sem cobrar uma nova espera.
- Usar grades oficiais por sentido e dia para Expresso Aeroporto e Expresso L10;
  passagens intermediárias são estimadas pelos tempos cadastrados.
- Usar a metade do intervalo publicado da Linha 17 como espera média estimada,
  sem apresentar uma previsão exata de partida.
- Priorizar menor tempo total, depois menos embarques em serviços especiais,
  depois menos baldeações; desempate final determinístico.
- Verificar o funcionamento na chegada à conexão, incluindo feriados, encerramento,
  datas operacionais e limite de espera de duas horas por embarque.
- Decompor espera na resposta para o cliente atualizado e incorporá-la ao tempo
  do trecho para clientes anteriores, preservando a soma esperada pelo contrato.
- Recalcular os horários no registro da viagem, sem aceitar tempos enviados pelo
  navegador, e alinhar a lotação com os instantes previstos dos trechos.

## Capabilities

### Added Capabilities
- `espera-partidas`: cálculo temporal de trajetos e disponibilidade prevista.

## Impact

Dois endpoints Xano, contrato Python e instruções Reflex. Sem reimportar trechos,
substituir esquema, alterar chaves ou parâmetros da demonstração de concorrência.
