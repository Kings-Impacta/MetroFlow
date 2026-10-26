# Visão geral do MetroFlow

O MetroFlow é um projeto integrador para planejar viagens na rede de transporte ferroviário metropolitano de São Paulo. Sua entrega atual permite que uma pessoa autenticada escolha origem e destino e consulte um trajeto, com instruções de viagem e tempo estimado.

## Problema e público

A rede reúne linhas e operadores diferentes. Para planejar uma viagem, o usuário precisa identificar as estações percorridas, o sentido de cada linha e os pontos de baldeação sem consultar separadamente vários mapas. O projeto atende passageiros que desejam pesquisar um trajeto entre estações cadastradas.

## Escopo atual

- Cadastro com confirmação de e-mail, login, restauração da sessão e logout integrados ao Xano.
- Reenvio da confirmação e recuperação de senha por e-mail, com retorno ao login após a redefinição.
- Consulta autenticada das estações e do trajeto principal entre origem e destino.
- Exibição das linhas, operadores, sentidos, estações, trechos, baldeações e tempo estimado.
- Seleção do menor tempo calculado pelos trechos cadastrados mais 600 segundos por mudança de linha; em empate, menos baldeações.
- Tratamento de seleção inválida, sessão expirada, ausência de rota e indisponibilidade do serviço.

O projeto não oferece ainda lotação de fontes oficiais ou em tempo real, várias opções de trajeto nem estimativas reais de caminhada, espera ou transferência. As próximas entregas e sua ordem estão em [roadmap-pos-mvp.md](roadmap-pos-mvp.md).

## Em andamento

A mudança `concorrencia-rotas` registra automaticamente cada trajeto obtido com sucesso e usa as viagens ativas para estimar, de forma interna, a lotação de cada trecho. Quando o trajeto principal passa por um trecho lotado, a busca apresenta um caminho que o evita. Em 26/10/2026, o backend Python, a interface Reflex e os testes estão prontos, e as [tabelas e os endpoints do Xano](xano/rascunhos/concorrencia-rotas/README.md) foram publicados com parâmetros de lotação de teste. A validação completa com duas sessões reais ainda está pendente.

No mesmo dia, um [incidente na tabela `trechos`](xano/incidente-trechos-2026-10-26.md) apagou os valores da malha no Xano. Até a reimportação dos 207 trechos, a busca não encontra trajetos.

## Arquitetura e restrições

O frontend usa exclusivamente Reflex. O backend Python protege a sessão e normaliza as respostas da API. O Xano armazena a malha, autentica usuários e calcula o caminho. A [arquitetura](../ARCHITECTURE.md) descreve os módulos; o [modelo de domínio](domain-model.md) descreve os conceitos sem confundi-los com o esquema físico do banco.

Tokens e senhas não devem aparecer na interface, em URLs ou em logs. O token de sessão permanece em cookie HttpOnly. O planejamento exige uma sessão válida. Mudanças de contrato ou comportamento devem ser especificadas no OpenSpec e testadas antes de sua conclusão.

## Fontes de verdade

O código e os testes representam o comportamento implementado. `openspec/specs/` contém as especificações consolidadas das entregas concluídas; `openspec/changes/archive/` guarda o histórico dessas entregas, e novas mudanças ativas em `openspec/changes/` mostram o trabalho em andamento. No estado registrado em 26/10/2026, as mudanças ativas são `concorrencia-rotas` e `integrar-status-operacional-multifonte`. As observações do Xano estão em [docs/xano](xano/README.md), com limites de evidência explicitados. O [README](../README.md) reúne as instruções de instalação, execução e teste.
