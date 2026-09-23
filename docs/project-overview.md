# Visão geral do MetroFlow

O MetroFlow é um projeto integrador para planejar viagens na rede de transporte ferroviário metropolitano de São Paulo. Sua entrega atual permite que uma pessoa autenticada escolha origem e destino e consulte um trajeto, com instruções de viagem e tempo estimado.

## Problema e público

A rede reúne linhas e operadores diferentes. Para planejar uma viagem, o usuário precisa identificar as estações percorridas, o sentido de cada linha e os pontos de baldeação sem consultar separadamente vários mapas. O projeto atende passageiros que desejam pesquisar um trajeto entre estações cadastradas.

## Escopo atual

- Cadastro, login, restauração da sessão e logout integrados ao Xano.
- Consulta autenticada das estações e do trajeto principal entre origem e destino.
- Exibição das linhas, operadores, sentidos, estações, trechos, baldeações e tempo estimado.
- Seleção do menor tempo calculado pelos trechos cadastrados mais 600 segundos por mudança de linha; em empate, menos baldeações.
- Tratamento de seleção inválida, sessão expirada, ausência de rota e indisponibilidade do serviço.

O projeto não oferece ainda lotação, alternativas de trajeto, recuperação de senha nem estimativas reais de caminhada, espera ou transferência. As próximas entregas e sua ordem estão em [roadmap-pos-mvp.md](roadmap-pos-mvp.md).

## Arquitetura e restrições

O frontend usa exclusivamente Reflex. O backend Python protege a sessão e normaliza as respostas da API. O Xano armazena a malha, autentica usuários e calcula o caminho. A [arquitetura](../ARCHITECTURE.md) descreve os módulos; o [modelo de domínio](domain-model.md) descreve os conceitos sem confundi-los com o esquema físico do banco.

Tokens e senhas não devem aparecer na interface, em URLs ou em logs. O token de sessão permanece em cookie HttpOnly. O planejamento exige uma sessão válida. Mudanças de contrato ou comportamento devem ser especificadas no OpenSpec e testadas antes de sua conclusão.

## Fontes de verdade

O código e os testes representam o comportamento implementado. `openspec/specs/` contém as especificações consolidadas de autenticação e busca de trajetos; `openspec/changes/archive/` guarda as entregas concluídas, e as mudanças ainda ativas em `openspec/changes/` mostram o trabalho pendente. As observações do Xano estão em [docs/xano](xano/README.md), com limites de evidência explicitados. O [README](../README.md) reúne as instruções de instalação, execução e teste.
