## Why

O MetroFlow precisa apresentar as condições das linhas sem depender da disponibilidade de uma fonte externa para calcular ou registrar viagens. A espera pelo token Direto dos Trens e as falhas transitórias dos quadros públicos exigem cobertura explícita e preservação do último retorno.

## What Changes

- Integrar os quadros oficiais do Metrô e Motiva e o JSON CPTM, com configuração explícita no backend.
- Preparar Direto dos Trens como principal futura, sem consultas protegidas enquanto o token não estiver configurado.
- Compartilhar cache e limite de tentativas por fonte; conservar dados anteriores e suas datas em falhas ou respostas parciais.
- Mostrar indicadores compactos no resumo e nos embarques, mantendo detalhes em `/status`.
- Ajustar o transporte do Metrô sem alterar as outras fontes, TLS, busca, tempos ou concorrência.
- Incluir um iniciador local portátil para a configuração validada de três fontes.

## Capabilities

### New Capabilities

- `status-operacional-linhas`: consulta e apresentação informativa, com fonte, horário e validade.

### Modified Capabilities

Nenhuma regra de escolha ou registro de trajetos é modificada.

## Impact

O módulo de status, sua apresentação e testes são atualizados. Nenhuma credencial, cache local, arquivo de treinamento ou alteração no Xano integra esta entrega. Todas as fontes permanecem desativadas por padrão; o iniciador local as habilita somente no processo que inicia. A API Direto dos Trens aguarda token e validação autorizada.

## Decisão final de escopo — 12/11/2026

Entrega encerrada com escopo reduzido, por autorização do usuário. As pendências não executadas foram retiradas do compromisso atual e preservadas como melhorias futuras em `docs/melhorias-futuras-malha-status.md`; consulte também as limitações no checklist. O texto anterior preserva a proposta e as decisões históricas, não representa certificação de todas as hipóteses nem garantia de disponibilidade pública. Esta revisão é somente documental.
