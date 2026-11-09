## Pesquisa e autorização

- [x] Registrar cobertura, contrato observado, riscos e lacunas das fontes avaliadas.
- [x] Definir precedência, cache e tratamento de indisponibilidade propostos.
- [ ] Configurar no backend a chave ARTESP que o usuário confirmou possuir e registrar os termos aceitos para o ambiente.
- [ ] Obter confirmação do Metrô para consumo e republicação do endpoint agregado.
- [ ] Obter confirmação da CPTM para os dados das linhas sob sua gestão.
- [ ] Catalogar valores e nulabilidade do contrato com amostras autorizadas.

## Backend

- [x] Criar o modelo normalizado de condição operacional.
- [x] Implementar adaptador ARTESP, autenticação, limites e cache compartilhado.
- [ ] Implementar adaptadores complementares somente após autorização.
- [x] Expor a condição pelo backend sem credenciais ou respostas internas.
- [x] Preservar a busca de trajetos quando todas as fontes estiverem indisponíveis.

## Interface

- [x] Apresentar status, descrição, fonte e atualização das linhas do trajeto.
- [x] Diferenciar dado atual, desatualizado e indisponível.
- [x] Manter os avisos informativos sem alterar a rota nesta entrega.

## Validação

- [x] Cobrir normalização, cache, limite, timeout e resposta inválida.
- [x] Cobrir precedência e divergência entre fontes.
- [x] Cobrir ausência parcial e total sem bloquear o planejamento.
- [x] Validar estado/componentes Reflex, compilar a interface e executar a suíte completa (231 testes e 55 subtestes). Não representa teste visual autenticado com fontes reais.
- [x] Executar validação estrita do OpenSpec (12 itens) e registrar limites restantes.

## Entrega inicial de 09/11

Adaptadores preparados com fontes desligadas por padrão. O agregado tem testes sintéticos, sem autorização ou ativação real. A ativação ARTESP e a amostra autenticada continuam pendentes. Guia e limites em `docs/status-operacional.md`.
