## Why

Quando vários usuários seguem para o mesmo destino, os mesmos trechos concentram passageiros. Não há API de ocupação disponível, então a lotação precisa ser estimada como em uma pesquisa por amostragem: a proporção das viagens confirmadas no próprio MetroFlow que ocupam cada trecho indica se ele está lotado. Com essa estimativa, os próximos usuários recebem um trajeto que evita os trechos lotados.

## What Changes

- Permitir que o usuário confirme, por um botão no resultado do trajeto, que vai fazer a viagem apresentada.
- Registrar no Xano a viagem confirmada. Cada usuário tem no máximo uma viagem ativa; uma nova confirmação substitui a anterior, que deixa de contar imediatamente. Não há cancelamento manual.
- Estimar, no momento da busca, a ocupação de cada trecho ferroviário em cada sentido a partir das viagens ativas, considerando cada viagem somente no intervalo estimado em que ela passa pelo trecho.
- Considerar um trecho lotado quando ele atinge, ao mesmo tempo, um mínimo de usuários e um percentual do total de viagens ativas, ambos lidos de uma tabela de configuração no Xano.
- Quando o trajeto principal passa por um trecho lotado, substituir o resultado pelo caminho de menor tempo que evite os trechos lotados. Se esse caminho não existir, apresentar o trajeto principal.
- Manter a lotação apenas para uso interno: o usuário não vê a lotação nem é avisado da substituição.
- Atualizar o roadmap para registrar esta entrega.

## Fora do escopo

- Fontes oficiais ou em tempo real de ocupação.
- Exibição da lotação ou de qualquer aviso de substituição ao usuário.
- Cancelamento manual de viagem e informação de horário de partida pelo usuário.
- Limite de tempo extra para a rota alternativa e apresentação de várias opções de trajeto.
- Uso dos registros guardados após o fim da janela para outros fins (por exemplo, histórico do usuário da etapa P3).
- Estimativas reais de caminhada, espera e transferência (etapa P1).

## Capabilities

### New Capabilities

- `concorrencia-rotas`: Registra viagens confirmadas, estima a lotação de cada trecho ferroviário por sentido a partir da proporção de viagens ativas e substitui o trajeto quando ele passa por um trecho lotado.

### Modified Capabilities

- `busca-trajetos`: o escopo deixa de omitir a lotação estimada e a substituição do trajeto por alternativa, que passam a seguir `concorrencia-rotas`.

## Impact

Xano: nova tabela de viagens confirmadas, nova tabela de configuração, novo endpoint de confirmação e alteração do endpoint `trajetos/buscar`. Backend Python: novo endpoint local de confirmação com validação de sessão. Reflex: botão de confirmação no resultado. Documentação: roadmap, visão geral e modelo de domínio.
