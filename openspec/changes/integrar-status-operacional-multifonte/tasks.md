## Implementação entregue

- [x] Preparar adaptadores Metrô, CPTM e Motiva com cobertura explícita e fontes desligadas por padrão.
- [x] Preparar API Direto dos Trens com credencial somente no backend, sem ativação sem token.
- [x] Manter status independente de busca, calibração, registro e concorrência.
- [x] Compartilhar cache/reserva entre usuários e preservar limite e backoff das fontes.
- [x] Conservar último retorno e datas em falhas prolongadas, consultas em andamento e respostas parciais/vazias.
- [x] Respeitar política de armazenamento, sem transformar informação vencida em atual.
- [x] Mostrar indicadores compactos no resumo e em cada embarque, com repetição automática única e layout responsivo.
- [x] Ajustar transporte do Metrô preservando TLS e as outras fontes.
- [x] Confirmar consultas reais e renovação automática das sete linhas do Metrô no cliente reiniciado.
- [x] Conferir busca interna e relato do teste de duas contas com caminhos distintos.
- [x] Excluir o coletor experimental bloqueado, caches e credenciais do pacote de entrega.
- [x] Incluir iniciador portátil para uso local com três fontes.

## Entrega

- [x] Validar a versão final baseada na main: 276 testes/86 subtestes, compilação e 12 itens OpenSpec.
- [x] Preparar pacote e fluxo de entrega com exigência dos checks tests/openspec e conferência do commit antes do merge, sem alteração no Xano.

A publicação foi concluída pelo PR #41, com checks tests/openspec aprovados na main.

- [x] Confirmar na main a renovação automática das três fontes e auditar os registros 67/68 no Xano, reproduzindo calibração, cronologia e limites da alternativa; ver `docs/xano/reteste-main-status-concorrencia-2026-11-11.md`.

## Pendências externas e operação pública

- [ ] Receber token Direto dos Trens e validar resposta autorizada, limites, datas e condições de uso.
- [ ] Confirmar condições para ativação em serviço público; a configuração local não equivale a hospedagem pública.
- [ ] Confirmar fuso de dataGeracao CPTM; enquanto ausente, usar apenas coleta local como referência de validade.
- [ ] Revisar cobertura 6/7/13 e serviços especiais após obter a API, sem inferir normalidade.
