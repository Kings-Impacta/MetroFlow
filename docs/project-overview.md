# Visão geral do MetroFlow

O MetroFlow é um projeto integrador para planejar viagens na rede de transporte ferroviário metropolitano de São Paulo. Sua entrega atual permite que uma pessoa autenticada escolha origem e destino e consulte um trajeto, com instruções de viagem e tempo estimado.

## Problema e público

A rede reúne linhas e operadores diferentes. Para planejar uma viagem, o usuário precisa identificar as estações percorridas, o sentido de cada linha e os pontos de baldeação sem consultar separadamente vários mapas. O projeto atende passageiros que desejam pesquisar um trajeto entre estações cadastradas.

## Escopo atual

- Cadastro com confirmação de e-mail, login, restauração da sessão e logout integrados ao Xano.
- Reenvio da confirmação e recuperação de senha por e-mail, com retorno ao login após a redefinição.
- Consulta autenticada das estações e do trajeto principal entre origem e destino.
- Exibição das linhas, operadores, sentidos, estações, trechos, baldeações e tempo estimado.
- Seleção pelo tempo estimado de chegada, incluindo esperas conhecidas e trocas de trem; em empate, prefere serviços regulares e menos baldeações. A concorrência usa ocupação prevista e limites de desvio, descritos no modelo de domínio.
- Tratamento de seleção inválida, sessão expirada, ausência de rota e indisponibilidade do serviço.

O projeto oferece status operacional informativo, mas não lotação oficial em tempo real, várias opções simultâneas, grades oficiais completas de frequência regular ou tempos medidos de todas as transferências. As esperas conhecidas dos serviços especiais são estimativas baseadas nas fontes documentadas. As próximas entregas e sua ordem estão em [roadmap-pos-mvp.md](roadmap-pos-mvp.md).

## Estado em 09/11/2026

O cliente calibrado foi integrado à main pelo PR #37 e a mensagem de indisponibilidade por horário pelo PR #38. A busca registra automaticamente a viagem. O Xano usa a malha calibrada de 419 sentidos, incluindo a operação parcial modelada da Linha 6, com estimativas de embarque e baldeação e margem única de um minuto no total público.

A concorrência foi validada com duas contas distintas nos registros 52 e 53, separados por 8,666 segundos: a primeira recebeu Linha 3 → Sé → Linha 1 (21min15s estimados), e a segunda Linha 3 → República → Linha 4 → Paulista–Consolação → Linha 2 (29min45s). A versão de busca e registro coincidiu; a alternativa reduziu 60,45% da exposição prevista. Os parâmetros de lotação 1/1% continuam intencionais para demonstração e não representam lotação oficial.

A integração informativa de status operacional foi entregue posteriormente na main pelo PR #41. O [fechamento e as pendências](xano/fechamento-trajetos-concorrencia-2026-11-09.md) distinguem manutenção, verificações ainda não cobertas e os requisitos próprios dessa integração.

## Arquitetura e restrições

O frontend usa exclusivamente Reflex. O backend Python protege a sessão e normaliza as respostas da API. O Xano armazena a malha, autentica usuários e calcula o caminho. A [arquitetura](../ARCHITECTURE.md) descreve os módulos; o [modelo de domínio](domain-model.md) descreve os conceitos sem confundi-los com o esquema físico do banco.

Tokens e senhas não devem aparecer na interface, em URLs ou em logs. O token de sessão permanece em cookie HttpOnly. O planejamento exige uma sessão válida. Mudanças de contrato ou comportamento devem ser especificadas no OpenSpec e testadas antes de sua conclusão.

## Fontes de verdade

O código e os testes representam o comportamento implementado. `openspec/specs/` contém as especificações consolidadas das entregas concluídas; `openspec/changes/archive/` guarda o histórico dessas entregas, e novas mudanças ativas em `openspec/changes/` mostram o trabalho em andamento. As mudanças ativas e seus checklists ficam em `openspec/changes/`; documentos datados preservam o estado histórico, que pode ter sido superado pelo fechamento de 09/11/2026. As observações do Xano estão em [docs/xano](xano/README.md), com limites de evidência explicitados. O [README](../README.md) reúne as instruções de instalação, execução e teste.


## Integração informativa inicial de status

A integração informativa inicial de status está implementada em entrega separada: fontes desativadas por padrão, cache compartilhado e falhas sem bloquear busca/registro. A preparação atual usa Direto dos Trens como principal e CPTM como complemento, com Metrô reservado e desativado. Aguarda-se token e amostra autorizada; ARTESP/Azure ficam fora da configuração atual. Veja [guia de status](status-operacional.md).


## Entrega de status em 11/11/2026

A configuração local validada usa Metrô, CPTM e Motiva, com 12 linhas observadas e preservação do último retorno. O iniciador portátil fica na raiz do projeto. A API Direto dos Trens aguarda token. Fontes continuam desativadas por padrão e não participam do cálculo nem do registro de viagens. Consulte o guia de status para a configuração e os limites atuais.

O [reteste da main de 11/11](xano/reteste-main-status-concorrencia-2026-11-11.md) confirmou renovação automática das três fontes e os registros calibrados 67/68, com alternativa pela Luz e limites respeitados. O documento reúne as pendências atuais.
