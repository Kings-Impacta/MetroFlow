# Modelo de domínio do MetroFlow

Este documento descreve os conceitos usados no planejamento de viagens. Os nomes de campos do Xano, detalhes de API e classes Python podem diferir deste modelo conceitual.

## Usuário e sessão

O **usuário** possui uma conta identificada por e-mail e pode planejar viagens enquanto sua conta e sessão forem válidas. A **sessão** representa a autenticação necessária para consultar estações e trajetos. Credenciais e tokens não integram o resultado público de uma busca.

## Estação

A **estação** é um ponto da malha selecionável como origem ou destino. Possui identificação, nome e código. Uma estação pode atender mais de uma linha, possibilitando uma baldeação. Sua presença no percurso não implica, por si só, uma troca de linha.

A estação tem uma **situação**, ativa ou inativa. Uma estação inativa não aparece na seleção, não é aceita como origem ou destino e nenhum trajeto passa por ela, então as linhas que a atendem ficam interrompidas naquele ponto. Inativar não altera nome, código, vínculos com linhas nem trechos, e não encerra viagens em andamento.

## Operador e linha

O **operador** identifica a organização responsável por uma linha. A **linha** reúne trechos e possui identificação, nome, código e, quando disponível, cor. Cada linha pertence a um operador. Uma estação pode participar de várias linhas e uma linha atende várias estações.

## Trecho

O **trecho** liga duas estações distintas em uma linha e possui tempo estimado positivo em segundos. Alguns percursos podem ter direção específica; quando aplicável, o sentido da viagem deve ser apresentado ao passageiro. Um trecho físico bidirecional é armazenado uma vez e pode ser percorrido nos dois sentidos. Trechos de integração a pé ou serviços especiais precisam ser distinguidos dos trechos ferroviários no resultado.

## Baldeação e trajeto

A **baldeação** ocorre quando trechos consecutivos usam linhas diferentes, em uma estação compartilhada, ou exigem troca de trem no ramal da Linha 17 em Brooklin Paulista ou na extensão da Linha 8 em Itapevi. É derivada do percurso e não requer tabela própria. O **trajeto** liga uma origem a um destino diferentes, contém estações e trechos ordenados, baldeações derivadas e tempo total estimado. Não inclui voltas pela mesma estação para aguardar a reabertura de uma conexão.

No contrato calibrado publicado, o tempo físico soma deslocamentos por sentido, espera no embarque e custos estimados de circulação interna por combinação de linhas/plataformas, incluindo trocas obrigatórias de trem. A referência fixa de 600 segundos por baldeação pertence ao contrato legado. Os custos calibrados são estimativas rastreáveis, não medições exatas. A apresentação acrescenta 60 segundos apenas uma vez ao total, com indicação de tempo estimado; a margem não participa de partidas nem da ocupação. O caminho principal minimiza o horário previsto de chegada, verificando a disponibilidade no momento de cada embarque; em empate, prefere menos embarques em serviços especiais e, depois, menos baldeações. Alternativas por República/Paulista e Pinheiros participam da mesma comparação. Permanecer no mesmo trem não acrescenta outra espera. A espera de serviços regulares sem informação de frequência permanece desconhecida, não equivale a zero na operação real.

## Viagem confirmada e lotação estimada

A **viagem ativa** é registrada automaticamente quando uma busca apresenta um trajeto válido. Guarda o usuário da sessão, o momento do registro e os trechos em ordem, com o sentido percorrido e o tempo estimado. Cada usuário tem no máximo uma viagem ativa: uma nova busca bem-sucedida, mesmo do mesmo trajeto, substitui a anterior e reinicia a janela. Não há confirmação ou cancelamento manual. Os registros são mantidos depois do fim da janela, mas só ficam acessíveis no Xano.

A **janela** dos novos registros inclui os deslocamentos, as esperas conhecidas e as baldeações. O servidor recalcula os horários a partir do cadastro e da hora da busca, aceita essa referência por até 30 segundos e guarda o início previsto de cada trecho. Dentro da janela, a viagem ocupa cada trecho somente durante o deslocamento estimado; esperar pelo trem ou fazer a baldeação não ocupa antecipadamente o próximo trecho. Registros antigos sem esses horários continuam sendo interpretados pelo contrato anterior até expirarem.

A **lotação estimada** compara a sobreposição entre o intervalo previsto de passagem da nova viagem e as viagens ativas no mesmo trecho e sentido, sem contar a própria viagem. O mínimo de usuários, o percentual e o denominador global de viagens ativas são preservados. Integrações a pé e serviços especiais não ficam lotados. A alternativa deve evitar a ocupação sem exceder a tolerância de produto: menor entre 10 minutos e 25% do tempo principal, com piso de tolerância de 2 minutos, e no máximo uma troca adicional. Sem opção inteiramente livre dentro desses limites, admite redução parcial mínima de 40% da exposição, com acréscimo máximo de min(540 segundos, 45% do tempo físico principal) e uma baldeação extra. Na seleção da alternativa por concorrência, prefere caminho inteiramente pelo Metrô até 60 segundos acima da alternativa elegível original, mantendo os mesmos limites. Inclui linhas concedidas e permite caminhadas explícitas. Essa preferência não presume em qual trem o passageiro já está. Sem alternativa elegível, mantém o principal. O teste real de 09/11 confirmou a alternativa por República; ver [publicação e reteste](xano/publicacao-preferencia-metro-2026-11-09.md). A estimativa é interna, não uma medição oficial de ocupação. Os parâmetros de demonstração do Xano permanecem intencionalmente inalterados.

Um **aviso de acesso** informa possível novo pagamento ou necessidade de confirmar a gratuidade em integrações por horário. Não bloqueia uma rota por suposição quando há conflito entre fontes oficiais, nem promete gratuidade sem confirmação.

## Administrador e painel de controle

O **administrador** é um usuário autenticado com concessão registrada no Xano. A concessão e a revogação são feitas no próprio Xano; a aplicação não oferece tela para isso. A autorização é conferida no Xano a cada operação administrativa, então a revogação vale na operação seguinte. A sessão informa à interface se o usuário é administrador apenas para mostrar o acesso ao painel.

No **painel de controle**, o administrador ativa e inativa estações. Inativar exige confirmação, porque interrompe as linhas naquele ponto; cada alteração registra a estação, a nova situação, o administrador e o momento. O painel também apresenta **indicadores agregados**, que nunca identificam usuários nem viagens individuais:

- **Uso:** rotas ativas (viagens em andamento), usuários em viagem agora, usuários com viagem nos últimos 7 dias e contas habilitadas. Como cada usuário tem no máximo uma viagem ativa, os dois primeiros números coincidem.
- **Malha:** estações ativas e inativas, linhas ativas e trechos ativos. Um trecho continua contando como ativo mesmo com uma estação inativa na ponta.
- **Volume:** viagens registradas no dia, no horário de São Paulo, e nos últimos 7 dias. As viagens substituídas também contam.
- **Ranking:** as cinco estações mais usadas como origem ou destino nos últimos 7 dias.
- **Lotação:** trechos lotados no instante da apuração, pelo mesmo critério da busca e com o critério vigente ao lado. Sem configuração válida, o indicador fica indisponível.

Uma viagem registrada mede uma busca bem-sucedida, não uma viagem realizada.

## Orientação de estação

A **orientação** é uma dica para o passageiro na estação onde ele desce de uma etapa, seja no destino ou em uma baldeação. A informação principal é o lado de desembarque; uma observação adicional em texto livre registra qualquer outra dica relevante, como o carro mais perto da escada ou o caminho da baldeação. Ela é identificada pela estação, pela linha e pelo sentido de chegada do trem. Cada orientação registra a fonte e a data de coleta. Ela não altera o trajeto, os trechos ou o tempo estimado e, quando não existe, o trajeto é apresentado sem ela.

## Estação mais próxima

A **coordenada da estação** é a latitude e a longitude de uma estação, com fonte e data de coleta, cadastradas em `docs/dados/coordenadas-estacoes.csv`. A primeira carga, de 16/11/2026, cobre as 188 estações da malha.

A **sugestão de origem** usa a localização do navegador, autorizada pelo usuário, para escolher a estação com coordenada mais próxima em linha reta, num raio de até 5 km. A sugestão só preenche a origem, que pode ser trocada como uma escolha manual. A distância exibida é aproximada e não representa o caminho a pé. A posição do usuário fica no navegador e não é armazenada. A sugestão não altera a busca, o tempo estimado nem o registro da viagem.

## Exclusividade da confirmação validada em 11/11/2026

O registro usa bloqueio transacional do usuário autenticado antes de consultar e substituir viagens anteriores. Após adquirir o bloqueio, revalida sessão e prazo da referência; o usuário não é modificado. No teste HTTP sobreposto 81/82, ambas as confirmações tiveram sucesso e somente a última permaneceu ativa após a disputa. Cálculo, cronologia, margem e parâmetros não mudaram. Veja [correção e limites da evidência](xano/exclusividade-viagens-2026-11-11.md).
