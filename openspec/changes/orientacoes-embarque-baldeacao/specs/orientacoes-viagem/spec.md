## Purpose

Ajudar o passageiro dentro das estações com o lado de desembarque e uma observação
adicional, coletados e rastreáveis, apresentados junto às instruções de viagem sem
alterar o trajeto calculado.

## ADDED Requirements

### Requirement: Cadastro rastreável de orientações

O sistema SHALL manter cada orientação associada a uma estação, a uma linha e ao
sentido de chegada do trem nessa estação, identificados pelos mesmos nomes
apresentados no trajeto. A orientação SHALL ter como informação principal o lado de
desembarque e MAY ter uma observação adicional em texto livre com qualquer
informação relevante ao passageiro. Cada registro SHALL informar a fonte e a data de
coleta e SHALL conter o lado de desembarque, a observação ou ambos.

#### Scenario: Registro completo
- **WHEN** um registro informa estação, linha, sentido, fonte, data de coleta e lado de desembarque ou observação
- **THEN** o registro é aceito

#### Scenario: Registro só com observação
- **WHEN** um registro informa a observação, mas não o lado de desembarque
- **THEN** o registro é aceito e apresenta apenas a observação

#### Scenario: Registro sem fonte
- **WHEN** um registro com lado de desembarque ou observação não informa a fonte ou a data de coleta
- **THEN** o registro é rejeitado pela validação do cadastro e não é apresentado

#### Scenario: Registro sem orientação
- **WHEN** um registro não informa o lado de desembarque nem a observação
- **THEN** o registro é ignorado e não é apresentado

#### Scenario: Registro duplicado
- **WHEN** existe mais de um registro para a mesma estação, linha e sentido
- **THEN** a validação do cadastro aponta a duplicata e nenhum dos registros duplicados é apresentado

### Requirement: Valores válidos das orientações

O lado de desembarque SHALL ser "esquerdo", "direito" ou "ambos", considerando o
sentido de viagem do trem. A observação SHALL ser não vazia após remover espaços e
SHALL ter no máximo 200 caracteres.

#### Scenario: Lado de desembarque inválido
- **WHEN** um registro informa um lado de desembarque fora dos valores permitidos
- **THEN** o registro é descartado na normalização, sem afetar os demais

#### Scenario: Observação longa demais
- **WHEN** um registro informa uma observação com mais de 200 caracteres
- **THEN** o registro é descartado na normalização, sem afetar os demais

### Requirement: Ativação controlada das orientações

O sistema SHALL apresentar orientações por padrão, sem configuração adicional, e
SHALL permitir desativá-las explicitamente pela configuração do ambiente.
Desativada, a resposta do trajeto e as instruções de viagem SHALL ser idênticas às
anteriores a esta mudança.

#### Scenario: Funcionalidade ativa por padrão
- **WHEN** nenhuma configuração de ativação está definida e existem orientações para as etapas do trajeto
- **THEN** as orientações são associadas e apresentadas

#### Scenario: Funcionalidade desativada
- **WHEN** a desativação está configurada no ambiente
- **THEN** o trajeto e as instruções são apresentados sem orientações e sem campos novos na resposta

### Requirement: Associação das orientações às etapas do trajeto

O sistema SHALL associar a cada etapa ferroviária do trajeto a orientação da estação
onde o passageiro desce dessa etapa, considerando a linha e o sentido da etapa, seja
a descida no destino final ou em uma baldeação.

#### Scenario: Desembarque no destino
- **WHEN** a última etapa chega ao destino e existe orientação para essa estação, linha e sentido
- **THEN** o resultado apresenta essa orientação na etapa de desembarque

#### Scenario: Desembarque para baldeação
- **WHEN** uma etapa termina em baldeação e existe orientação para essa estação, linha e sentido
- **THEN** o resultado apresenta essa orientação na etapa de baldeação

#### Scenario: Sentido diferente
- **WHEN** existe orientação apenas para o sentido oposto ao da etapa
- **THEN** essa orientação não é apresentada

#### Scenario: Integração a pé
- **WHEN** a etapa é uma integração a pé entre estações
- **THEN** nenhuma orientação é associada a ela

### Requirement: Apresentação opcional nas instruções de viagem

O sistema SHALL apresentar as orientações associadas, em português, nos cartões de
"Como chegar" em que o passageiro desce do trem: baldeação, integração a pé
seguinte e desembarque final. O lado de desembarque SHALL aparecer em destaque e a
observação SHALL aparecer como informação adicional; qualquer campo ausente SHALL
ser omitido.

#### Scenario: Orientações disponíveis
- **WHEN** um trajeto tem orientações associadas
- **THEN** os cartões correspondentes mostram o lado de desembarque em destaque e a observação informada

#### Scenario: Orientações ausentes
- **WHEN** nenhuma orientação está cadastrada para as etapas do trajeto
- **THEN** os cartões são apresentados como antes desta mudança, sem espaços vazios ou textos de dado ausente

### Requirement: Planejamento independente das orientações

O sistema SHALL apresentar o trajeto mesmo quando as orientações estiverem
indisponíveis, inválidas ou expiradas, e SHALL não alterar a escolha do trajeto, os
trechos ou o tempo estimado com base nas orientações.

#### Scenario: Falha na leitura das orientações
- **WHEN** o cadastro de orientações está ausente, ilegível ou com conteúdo inválido
- **THEN** o trajeto é apresentado sem orientações e sem mensagem interna do serviço

#### Scenario: Tempo inalterado
- **WHEN** um trajeto recebe orientações
- **THEN** o tempo total, as estações, os trechos e as baldeações são os mesmos de um trajeto sem orientações

### Requirement: Proteção da consulta das orientações

O sistema SHALL apresentar as orientações somente dentro do resultado de um trajeto
consultado com sessão válida e SHALL não expor tokens, credenciais ou respostas
internas do Xano à interface, às URLs ou aos logs.

#### Scenario: Resposta pública
- **WHEN** o backend devolve um trajeto com orientações
- **THEN** a resposta contém apenas o lado de desembarque e a observação, sem fonte, data de coleta, identificadores internos de autenticação ou conteúdo bruto do Xano
