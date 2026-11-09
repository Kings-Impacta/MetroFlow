## ADDED Requirements

### Requirement: Disponibilidade de serviços
O sistema SHALL consultar serviços e janelas cadastradas na busca e confirmação,
usando o fuso America/Sao_Paulo, sem modificar trechos regulares sem serviço.

#### Scenario: Serviço fechado
- **WHEN** a consulta ocorre fora das janelas válidas de um serviço
- **THEN** seus trechos não participam da busca e uma confirmação não registra esses trechos

#### Scenario: Linha 17 no sábado
- **WHEN** a consulta ocorre no sábado entre 06h e 22h
- **THEN** os trechos ativos do serviço da Linha 17 estão disponíveis

#### Scenario: Dia ou horário inválido
- **WHEN** a janela está inativa, ausente ou malformada
- **THEN** ela não habilita o serviço

#### Scenario: Calendário fora de vigência
- **WHEN** um serviço que não opera em feriados exige calendário desconhecido
- **THEN** ele não é habilitado por suposição

#### Scenario: Feriados recorrentes no ano seguinte
- **WHEN** a consulta ocorre em 2027 dentro da vigência calculada
- **THEN** dias úteis ordinários continuam habilitados e Sexta-feira Santa/Corpus
  Christi são calculados para o ano da consulta, sem copiar as datas de 2026

#### Scenario: Expresso L10 por sentido
- **WHEN** a consulta ocorre às 05h45 de um dia útil sem feriado
- **THEN** o serviço com parada em São Caetano está habilitado de Santo André para
  Tamanduateí, e ainda não está habilitado no sentido contrário

### Requirement: Preservação da malha
O sistema SHALL manter tempos, referências e unicidade canônica após a correção,
com direções completas e operador independente para a Linha 7.

#### Scenario: Rota de referência
- **WHEN** a busca Jandira–Paraíso ocorre sem lotação e sem serviço especial necessário
- **THEN** permanece pela Linha 8, Linha 3 e Linha 1 com 4080 segundos

#### Scenario: Brás no Expresso
- **WHEN** o retorno do aeroporto passa por Brás
- **THEN** o sentido indica Palmeiras–Barra Funda

#### Scenario: Gravação duplicada
- **WHEN** duas gravações usam a mesma chave canônica
- **THEN** o índice impede duplicação e o endpoint devolve erro controlado

### Requirement: Ramal da Linha 17
O sistema SHALL representar Washington Luís ligada a Brooklin Paulista e informar
a troca obrigatória de trem entre o ramal e o tronco da mesma Linha 17.

#### Scenario: Morumbi para Washington Luís
- **WHEN** o serviço está disponível e o destino é Washington Luís
- **THEN** o caminho chega a Brooklin Paulista pelo tronco, troca de trem uma vez
  e segue ao ramal, sem passar pelo Aeroporto de Congonhas

#### Scenario: Washington Luís para Congonhas
- **WHEN** o serviço está disponível e a viagem liga Washington Luís a Congonhas
- **THEN** passa por Brooklin Paulista com uma troca de trem na mesma linha

#### Scenario: Viagem iniciada em Brooklin Paulista
- **WHEN** a origem é Brooklin Paulista e o destino é Washington Luís
- **THEN** existe uma etapa direta no ramal sem baldeação anterior ao embarque

### Requirement: Alternativas pelo tempo calculado
O sistema SHALL permitir alternativas por República/Paulista ou Pinheiros,
comparando tempos de trechos e transferências e preservando a regra de concorrência.

#### Scenario: Alternativa mais rápida
- **WHEN** os tempos cadastrados tornam Vermelha–Amarela–Verde mais rápida que a Sé
- **THEN** essa alternativa vence a busca sem exigir uma regra de preferência

#### Scenario: Rota principal lotada
- **WHEN** há caminho que evita o trecho lotado da principal
- **THEN** a busca escolhe a alternativa de menor tempo entre os caminhos disponíveis
