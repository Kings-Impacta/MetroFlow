## Pesquisa e autorização

- [x] Registrar cobertura, contrato observado, riscos e lacunas das fontes avaliadas.
- [x] Definir precedência, cache e tratamento de indisponibilidade propostos.
- [ ] Obter chave da API Trilhos e registrar os termos aceitos para o ambiente.
- [ ] Obter confirmação do Metrô para consumo e republicação do endpoint agregado.
- [ ] Obter confirmação da CPTM para os dados das linhas sob sua gestão.
- [ ] Catalogar valores e nulabilidade do contrato com amostras autorizadas.

## Backend

- [ ] Criar o modelo normalizado de condição operacional.
- [ ] Implementar adaptador ARTESP, autenticação, limites e cache compartilhado.
- [ ] Implementar adaptadores complementares somente após autorização.
- [ ] Expor a condição pelo backend sem credenciais ou respostas internas.
- [ ] Preservar a busca de trajetos quando todas as fontes estiverem indisponíveis.

## Interface

- [ ] Apresentar status, descrição, fonte e atualização das linhas do trajeto.
- [ ] Diferenciar dado atual, desatualizado e indisponível.
- [ ] Manter os avisos informativos sem alterar a rota nesta entrega.

## Validação

- [ ] Cobrir normalização, cache, limite, timeout e resposta inválida.
- [ ] Cobrir precedência e divergência entre fontes.
- [ ] Cobrir ausência parcial e total sem bloquear o planejamento.
- [ ] Validar a interface no Reflex e executar a suíte pertinente.
- [ ] Executar a validação estrita do OpenSpec e registrar limites restantes.
