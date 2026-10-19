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

O tempo total resulta da soma dos tempos dos trechos mais **600 segundos por mudança de linha**. O caminho principal minimiza esse total e usa a menor quantidade de baldeações como desempate. O [registro da API](api-planejamento-exemplos.md) detalha a representação pública, e a [auditoria complementar do Xano](xano/auditoria-integridade-2026-10-08.md) registra as garantias de armazenamento verificadas e os limites operacionais restantes.
