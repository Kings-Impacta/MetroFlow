# Espera, disponibilidade e desempate — 28/10/2026

O cálculo compara horários previstos de chegada: deslocamento cadastrado + espera conhecida + 600 segundos por baldeação. Verifica o serviço no instante previsto de cada embarque, inclusive conexões futuras. Em igualdade de chegada, prefere menos embarques especiais, depois menos baldeações; a ordem final é determinística. A regra de lotação continua podendo escolher uma alternativa ao caminho principal.

## Fontes e regras

O catálogo reproduz as grades dos PDFs oficiais da CPTM para [Expresso Aeroporto](https://www.cptm.sp.gov.br/dx/api/dam/v1/collections/05321fd9-3791-4689-a8ac-9e2adde39c4b/items/bdfdcc63-cee4-43a2-bb91-70dd75adae0d/renditions/b3fca1ea-5b3c-4133-8c87-e1f7ac3efac0?binary=true) e [Expresso Linha 10](https://www.cptm.sp.gov.br/dx/api/dam/v1/collections/05321fd9-3791-4689-a8ac-9e2adde39c4b/items/996297d1-45bf-4a2c-adb2-23cf38c61c9a/renditions/9bb7e05d-a547-40da-9b30-181dc8154c8d?binary=true), conferidos nesta data. Não se acrescentou a partida de domingo às 13h30 ausente da grade publicada. A última partida à meia-noite pode concluir o percurso no dia seguinte; isso não permite embarcar numa conexão já fechada.

O Expresso Linha 10 usa grades distintas por sentido e somente dias úteis não feriados. Não foram inventados tempos para os retornos diretos sem parada em São Caetano: o cadastro atual só permite modelar as viagens com essa parada.

A [publicação do Metrô de 29/09/2026](https://www.metro.sp.gov.br/2026/09/29/metro-amplia-horario-da-linha-17-ouro-a-partir-desta-quarta-feira-30/) informa Linha 17 de segunda a sábado, 6h–22h, intervalo médio de 9 minutos e troca obrigatória em Brooklin Paulista para Washington Luís. Usamos espera média de 270 segundos a cada novo embarque, inclusive no ramal, sem simular um horário exato de trem.

Os [horários do Metrô](https://www.metro.sp.gov.br/pt_BR/sua-viagem/horarios/) e [Linha 7](https://www.tictrens.com.br/sua-viagem/informacoes-uteis) fundamentam as janelas regulares. O piloto de madrugada de sábado para domingo é limitado às linhas 1, 2, 3 e 15 e à vigência até janeiro/2027. O modelo regular utiliza abertura geral de 4h40 para Metrô e 4h para trens, com limite conservador de novo embarque às 0h fora do piloto; não representa o último embarque específico de cada estação. Permanecer no mesmo trem permite concluir um percurso iniciado antes do fechamento.

O calendário considera feriados nacionais, estaduais e municipais de São Paulo, inclusive os móveis. Feriados específicos dos demais municípios e operações excepcionais precisam de informação adicional. A consulta não aguarda mais de duas horas por um novo embarque.

## Contrato e registro

`suporta_espera_partidas=true` retorna `calculado_em`, `tempo_espera_segundos` e a espera de cada trecho. Clientes anteriores recebem essa espera incorporada ao tempo do trecho, mantendo a igualdade do total. O Reflex atualizado mostra a espera no resumo e antes do embarque.

A confirmação automática envia a referência da busca; o servidor aceita no máximo 30 segundos, recalcula as durações e partidas sem confiar nos tempos recebidos e salva o início previsto de cada trecho. A lotação só conta ocupação durante o deslocamento, preservando as regras anteriores para registros antigos. Não foram alterados tabelas, registros da malha, autenticação ou configuração de concorrência nesta entrega.

## Comparações reproduzíveis

`scripts/validar_espera_partidas.py` usa a exportação real com relógio controlado, sem criar viagens: 160 comparações em dez horários/dias e 16 pares, incluindo domingo, feriado, abertura e fechamento. As 11 referências ao meio-dia mantêm trechos e totais.

Passaram 168 testes distintos de planejamento e 19 subtestes, incluindo os contratos do cliente, apresentação da espera, referência da busca no registro, lotação, confirmação e regressões anteriores da malha. A compilação seca do Reflex, a validação dos dois XanoScripts e a validação estrita dos dez itens OpenSpec também passaram. A validação da interface nesta entrega foi por testes de estado e compilação, sem substituir uma sessão autenticada no navegador.

| Cenário controlado | Antes | Depois |
| --- | --- | --- |
| Barra Funda → Aeroporto às 12h10 | Expresso, 35 min, ignorava a espera | Regular Turquesa/Safira/Jade, 38 min estimados; Expresso aguardaria 50 min antes dos 35 min de deslocamento |
| Barra Funda → Aeroporto às 12h59 | Expresso, 35 min | Expresso, 36 min, incluindo 1 min de espera; continua vencendo o regular |
| Morumbi → Congonhas às 12h10 | 12 min | 16 min 30 s, incluindo 4 min 30 s de espera média |
| Morumbi → Washington Luís às 12h10 | 22 min | 31 min, incluindo duas esperas médias e a troca já contabilizada |
| Morumbi → Congonhas às 21h55 | Oferecia chegada depois das 22h | Não oferece esse serviço para essa partida |
| Luz → Jandira com Turquesa ocupada | Coral + Diamante, 48 min no cenário | Coral + Diamante, 48 min; preserva alternativa regular |

Esses valores usam as durações atuais do cadastro; não são medições de viagem real. A espera dos trens regulares, sem grade ou frequência disponível, permanece desconhecida. Passagens intermediárias dos expressos são estimadas somando durações cadastradas e não incluem paradas medidas. Os tempos provisórios do Expresso Linha 10 continuam exigindo medição/documentação. Alertas e atrasos em tempo real dependem da futura integração das fontes operacionais.

## Arquivos

As fontes, a data de verificação e os limites estão em `rascunhos/espera-partidas/horarios.json`; o auxiliar temporal é compartilhado entre busca e confirmação. `scripts/gerar_espera_partidas.py` gera somente os dois endpoints a partir de uma exportação. O relatório privado de comparação e a exportação anterior permitem auditoria sem guardar tokens no repositório.

## Publicação e releitura

Os dois endpoints foram publicados no workspace 149130, branch `v1`, após prévia limitada a esses arquivos. Na conferência concluída em 29/10/2026, a exportação dos 26 documentos mostrou alterações somente em busca e confirmação; os dois corpos de cálculo correspondem aos candidatos validados, desconsiderando apenas a quebra de linha final removida pelo Xano. As oito tabelas relidas permaneceram idênticas à exportação anterior, incluindo os 207 trechos e suas 207 chaves únicas, sem o registro inválido 215. As 160 comparações foram repetidas com o código relido da publicação e passaram.

As alterações do cliente Reflex e da documentação permanecem locais na branch `fix/pendencias-malha-restaurada`, sem commit, push ou merge nesta entrega. Para exibir a espera separadamente, é necessário executar o cliente atualizado; o endpoint mantém compatibilidade com o cliente anterior incorporando a espera no tempo do trecho.
