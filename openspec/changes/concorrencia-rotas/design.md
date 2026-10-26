## Context

O MetroFlow calcula no Xano o trajeto principal de menor tempo (soma de `tempo_estimado` mais 600 segundos por mudança de linha; em empate, menos baldeações). Hoje nenhuma busca é registrada e não existe fonte de ocupação. A estimativa proposta compara a proporção de viagens confirmadas no app que ocupam cada trecho, como uma amostra da demanda real.

## Goals / Non-Goals

- Estimar a lotação por trecho e sentido usando somente viagens confirmadas no app.
- Desviar os próximos usuários de trechos lotados sem expor a estimativa.
- Manter cálculo e dados no Xano e o backend Python como camada de sessão, validação e normalização.
- Não apresentar a estimativa como medição oficial de ocupação.
- Não alterar a regra do trajeto principal quando nenhum trecho dele estiver lotado.

## Decisions

### Viagem confirmada e janela

A confirmação registra a viagem apresentada no resultado, com o usuário, o momento da confirmação e os trechos em ordem, com seu sentido e `tempo_estimado`. A janela da viagem começa na confirmação e termina na confirmação mais a soma de `tempo_estimado` dos trechos, sem a penalidade de 600 segundos. Uma viagem é ativa enquanto o instante atual estiver dentro da janela e ela não tiver sido substituída. Uma nova confirmação do mesmo usuário encerra imediatamente a viagem ativa anterior. Os registros são mantidos após o fim da janela, mas deixam de contar. Confirmar novamente o mesmo trajeto é tratado como nova confirmação: substitui a viagem ativa e reinicia a janela.

### Intervalo em cada trecho

O intervalo estimado de uma viagem em um trecho começa na confirmação mais a soma de `tempo_estimado` dos trechos anteriores e termina somando o `tempo_estimado` do próprio trecho. A penalidade de baldeação não entra nesse cálculo.

### Lotação

Somente trechos ferroviários entram na estimativa. Trechos cujo `tipo` não é `ferroviario`, como a integração a pé (`transferencia`), e trechos com `servico_id` preenchido não recebem ocupação e nunca são considerados lotados. O `tempo_estimado` deles continua contando na janela da viagem e no início dos intervalos dos trechos seguintes.

No momento da busca, a ocupação de um trecho em um sentido é a quantidade de viagens ativas cujo intervalo nesse trecho e sentido contém o instante atual. O percentual é essa ocupação dividida pelo total de viagens ativas. A viagem ativa do próprio usuário que busca não entra na ocupação nem no total. O trecho é lotado quando a ocupação é maior ou igual ao mínimo de usuários e o percentual é maior ou igual ao limite, ambos lidos da tabela de configuração.

### Substituição do trajeto

O Xano calcula o trajeto principal pela regra atual. Se algum trecho dele, no sentido percorrido, estiver lotado, o Xano recalcula com a mesma regra excluindo os trechos lotados naquele sentido e retorna esse caminho no lugar do principal. Sem caminho válido nessas condições, o Xano retorna o trajeto principal. A resposta pública não contém lotação nem indicação de substituição.

### Integração

O Reflex exibe o botão de confirmação no resultado. O backend Python expõe um endpoint local de confirmação que revalida a sessão como em `/api/planning/route`, valida o corpo e chama o novo endpoint autenticado do Xano. O usuário da viagem é obtido da sessão no Xano, nunca de um campo enviado pela interface. Após a confirmação, a interface não exibe aviso e mantém o botão disponível. A mudança `retorno-confirmacao-viagem` substituiu essa decisão: o botão indica o envio, fica desativado com "Viagem confirmada" após o registro e, em caso de falha, exibe uma mensagem e volta a ficar disponível.

### Retenção dos registros

Os registros de viagens confirmadas são mantidos sem prazo de exclusão e ficam acessíveis somente no Xano. Nenhuma resposta pública, inclusive a da confirmação, devolve registros de viagens.

## Risks / Trade-offs

- Com poucos usuários, a amostra não representa a demanda real; o mínimo de usuários evita que poucas viagens marquem um trecho como lotado.
- Usar o instante da busca, e não o momento em que o usuário passará pelo trecho, pode desviar com base em uma situação que já mudou quando ele chegar.
- Sem limite de tempo extra, a rota alternativa pode ser bem mais longa que a principal, e o usuário não sabe o motivo da troca.
- Desviar todos os próximos usuários para o mesmo caminho alternativo pode deslocar a lotação para ele.
- Guardar viagens indefinidamente retém dados de deslocamento associados a usuários; o acesso restrito ao Xano reduz, mas não elimina, esse risco.
- Sem aviso após a confirmação, o usuário não sabe se ela foi registrada, e reconfirmar o mesmo trajeto reinicia a janela.

## Open Questions

- O que a interface mostra quando a confirmação falha por erro do serviço, já que não há aviso de sucesso? Respondida na mudança `retorno-confirmacao-viagem`: uma mensagem de erro abaixo do botão, que volta a ficar disponível.
