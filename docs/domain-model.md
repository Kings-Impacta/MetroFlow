# Modelo de domínio do MetroFlow

Este documento descreve os conceitos usados no planejamento de viagens. Os nomes de campos do Xano, detalhes de API e classes Python podem diferir deste modelo conceitual.

## Usuário e sessão

O **usuário** possui uma conta identificada por e-mail e pode planejar viagens enquanto sua conta e sessão forem válidas. A **sessão** representa a autenticação necessária para consultar estações e trajetos. Credenciais e tokens não integram o resultado público de uma busca.

## Estação

A **estação** é um ponto da malha selecionável como origem ou destino. Possui identificação, nome e código. Uma estação pode atender mais de uma linha, possibilitando uma baldeação. Sua presença no percurso não implica, por si só, uma troca de linha.

## Operador e linha

O **operador** identifica a organização responsável por uma linha. A **linha** reúne trechos e possui identificação, nome, código e, quando disponível, cor. Cada linha pertence a um operador. Uma estação pode participar de várias linhas e uma linha atende várias estações.

## Trecho

O **trecho** liga duas estações distintas em uma linha e possui tempo estimado positivo em segundos. Alguns percursos podem ter direção específica; quando aplicável, o sentido da viagem deve ser apresentado ao passageiro. Um trecho físico bidirecional é armazenado uma vez e pode ser percorrido nos dois sentidos. Trechos de integração a pé ou serviços especiais precisam ser distinguidos dos trechos ferroviários no resultado.

## Baldeação e trajeto

A **baldeação** ocorre quando trechos consecutivos usam linhas diferentes, em uma estação compartilhada. É derivada do percurso e não requer tabela própria. O **trajeto** liga uma origem a um destino diferentes, contém estações e trechos ordenados, baldeações derivadas e tempo total estimado.

O tempo total resulta da soma dos tempos dos trechos mais **600 segundos por mudança de linha**. O caminho principal minimiza esse total e usa a menor quantidade de baldeações como desempate.

## Viagem confirmada e lotação estimada

A **viagem confirmada** registra que o usuário vai fazer o trajeto apresentado. Guarda o usuário da sessão, o momento da confirmação e os trechos em ordem, com o sentido percorrido e o tempo estimado. Cada usuário tem no máximo uma viagem ativa: uma nova confirmação, mesmo do mesmo trajeto, substitui a anterior e reinicia a janela. Não há cancelamento manual. Os registros são mantidos depois do fim da janela, mas só ficam acessíveis no Xano.

A **janela** da viagem vai da confirmação até a soma dos tempos dos trechos, sem a penalidade de baldeação. Dentro dela, a viagem ocupa cada trecho somente no intervalo estimado em que passa por ele.

A **lotação estimada** compara, no momento da busca, quantas viagens ativas ocupam cada trecho ferroviário em cada sentido com o total de viagens ativas, sem contar a viagem de quem busca. Um trecho fica lotado quando atinge ao mesmo tempo um mínimo de usuários e um percentual, ambos configurados no Xano. Integrações a pé e serviços especiais não ficam lotados. Quando o trajeto principal passa por um trecho lotado, a busca apresenta o caminho de menor tempo que evita os trechos lotados ou, sem esse caminho, o próprio principal. A lotação é interna: não aparece para o usuário e não equivale a uma medição oficial de ocupação. O [registro da API](api-planejamento-exemplos.md) detalha a representação pública, e a [auditoria complementar do Xano](xano/auditoria-integridade-2026-10-08.md) registra as garantias de armazenamento verificadas e os limites operacionais restantes.
