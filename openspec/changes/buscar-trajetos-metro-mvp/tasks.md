## 1. Inspeção e aprovação do Xano

- [x] 1.1 Inspecionar em modo somente leitura o workspace “Raphael's Workspace” (`149130`), ambiente `v1`, incluindo tabelas, campos, relacionamentos, índices, autenticação e APIs existentes.
- [x] 1.2 Comparar o schema encontrado com a modelagem aprovada e documentar divergências sem alterar dados ou recursos.
- [x] 1.3 Apresentar qualquer proposta de alteração do Xano e obter autorização explícita antes de aplicar mudanças.
- [x] 1.4 Registrar limitações do plano Free e definir uma estratégia segura de revisão e `dry-run`, quando disponível.

## 2. Dados e estrutura no Xano

- [x] 2.1 Preservar `estacoes` com `id`, `created_at`, `nome`, `codigo` e `ativa`; manter `nome` text required not nullable com `trim` e sem default, `codigo` text required not nullable com `trim` e unique, e `ativa` boolean required not nullable com default `true`, já confirmado diretamente na interface do Xano.
- [x] 2.2 Preservar em `linhas` os campos confirmados `id`, `created_at`, `nome`, `codigo`, `cor` e `ativa`; manter `nome` text required not nullable com `trim`, `codigo` text required not nullable com `trim` e unique, `cor` text opcional com `trim`, e `ativa` boolean required not nullable com default `true`, já confirmado diretamente na interface do Xano.
- [x] 2.3 Após backup, revisão e autorização explícita, criar `operadores` com `id`, `created_at`, `nome`, `codigo` e `ativo`, adicionar unique em `codigo` e adicionar `linhas.operador_id` como Table Reference required e not nullable.
- [x] 2.4 Preservar `estacoes_linhas` com `id`, `created_at`, `estacao_id`, `linha_id` e `ordem`; exigir Table References required not nullable, `ordem` integer positivo required not nullable e unique composto de `estacao_id + linha_id`.
- [x] 2.5 Preservar `trechos` com `id`, `created_at`, `estacao_origem_id`, `estacao_destino_id`, `linha_id`, `tempo_estimado` e `ativo`; manter referências required not nullable, tempo integer positivo em segundos required not nullable e `ativo` boolean required not nullable com default `true`, já confirmado diretamente na interface do Xano.
- [x] 2.6 Converter, após backup e autorização explícita, exclusivamente `tempo_estimado` dos trechos IDs 1 a 5 de `2` minutos para `120` segundos, sem alterar outros campos ou registros.
- [x] 2.7 Rejeitar origem igual ao destino por validação.
- [x] 2.8 Proteger duplicata direta na mesma linha por unique composto de `estacao_origem_id + estacao_destino_id + linha_id`.
- [ ] 2.9 Impedir duplicata inversa na mesma linha por normalização canônica dos extremos ou validação lógica equivalente.
- [x] 2.10 Tratar cada trecho válido como bidirecional e armazenado uma única vez.
- [x] 2.11 Não criar tabela de baldeações; derivar mudanças de linha a partir dos trechos do caminho.
- [ ] 2.12 Inserir dados de teste somente após aprovação, cobrindo Metrô, CPTM e concessionárias, trajetos de uma linha e trajetos com mudanças de linha.

## 3. Dependência de autenticação

- [x] 3.1 Criar uma mudança OpenSpec separada para especificar e implementar autenticação por e-mail.
- [ ] 3.2 Nesta mudança, documentar apenas a dependência de uma sessão autenticada, sem criar tabelas ou endpoints de autenticação.
- [x] 3.3 Proteger o planejamento de viagens e a consulta de trajeto para permitir somente usuários autenticados.
- [x] 3.4 Definir respostas para sessão ausente, inválida e expirada.
- [ ] 3.5 Não implementar autenticação como parte desta mudança.

## 4. Lógica de busca no Xano

- [x] 4.1 Implementar no Xano a busca de caminhos com Dijkstra, usando o estado `(estação, linha atual)` e percorrendo cada trecho ativo em ambos os sentidos sem duplicar registros.
- [x] 4.2 Calcular o tempo total exclusivamente pela soma de `tempo_estimado` dos trechos.
- [x] 4.3 Não acrescentar custo de caminhada, espera ou transferência no primeiro MVP.
- [x] 4.4 Derivar a quantidade e os pontos de baldeação pela mudança de `linha_id` entre trechos consecutivos.
- [x] 4.5 Selecionar primeiro o menor tempo total e, somente em empate, a menor quantidade de baldeações.
- [x] 4.6 Manter a arquitetura extensível para tempos reais de transferência futuros sem criar tabela específica agora.

## 5. APIs do Xano

- [x] 5.1 Criar e documentar, após aprovação, endpoint autenticado de listagem de estações ativas.
- [x] 5.2 Criar e documentar, após aprovação, endpoint autenticado de consulta por estação de origem e destino.
- [x] 5.3 Retornar origem, destino, estações ordenadas, trechos, linhas, operadores, baldeações derivadas, tempo total em segundos e quantidade de baldeações.
- [ ] 5.4 Definir exemplos JSON para sucesso, ausência de trajeto, parâmetros inválidos, autenticação inválida e falha do serviço.

## 6. Integração e modelo de domínio no Reflex

- [ ] 6.1 Instalar e verificar os skills obrigatórios `reflex-docs`, `setup-python-env` e `reflex-process-management` antes de editar código Reflex.
- [ ] 6.2 Seguir integralmente `setup-python-env` para validar Python, `uv`, ambiente virtual e Reflex.
- [x] 6.3 Criar adaptadores para autenticação, estações e trajetos sem expor à interface o formato bruto do Xano.
- [x] 6.4 Criar modelos normalizados de estação, linha, operador, trecho, baldeação derivada e resultado.
- [ ] 6.5 Implementar os estados não autenticado, `idle`, `loading`, `success`, `not_found` e `error`.
- [x] 6.6 Validar origem e destino antes da chamada externa.

## 7. Fluxo da interface Reflex

- [ ] 7.1 Integrar a sessão fornecida pela mudança separada de autenticação e proteger o planejador de viagens.
- [ ] 7.2 Carregar e selecionar estações de origem e destino.
- [ ] 7.3 Solicitar o trajeto com indicação de carregamento e prevenção de solicitações duplicadas.
- [ ] 7.4 Renderizar estações, linhas, operadores, baldeações derivadas e tempo estimado, convertendo segundos para minutos apenas na exibição.
- [ ] 7.5 Exibir operador discretamente associado à linha, por exemplo, “Linha 8–Diamante — ViaMobilidade”.
- [ ] 7.6 Diferenciar seleção inválida, autenticação inválida, ausência de trajeto e falha do serviço.
- [ ] 7.7 Garantir que nova consulta substitua corretamente o resultado anterior.
- [ ] 7.8 Não calcular ou exibir lotação, rotas alternativas, custo adicional de transferência ou área administrativa.

## 8. Testes e validação

- [ ] 8.1 Testar tipos, nulabilidade, obrigatoriedade, `trim`, defaults e unicidade de estações e linhas.
- [ ] 8.2 Testar Table References, `ordem` positiva required not nullable e unique composto de `estacao_id + linha_id`.
- [ ] 8.3 Testar referências, tempo positivo em segundos, default de `ativo`, validação de extremos iguais, unique de duplicata direta e validação de duplicata inversa.
- [ ] 8.4 Testar percurso bidirecional a partir de um único registro de trecho.
- [ ] 8.5 Testar autenticação obrigatória, sessão válida, ausente, inválida e expirada.
- [ ] 8.6 Testar trajetos de uma linha, com baldeações e envolvendo operadores distintos.
- [ ] 8.7 Testar soma dos tempos e ausência de custo adicional de transferência.
- [ ] 8.8 Testar menor tempo e desempate pela menor quantidade de baldeações.
- [ ] 8.9 Testar ausência de trajeto, erro do serviço e resposta incompleta.
- [ ] 8.10 Executar validação integrada Reflex–Xano somente após as implementações autorizadas.
- [ ] 8.11 Executar a aplicação seguindo `reflex-process-management` e validar manualmente os principais cenários.

## Roadmap futuro — fora dos critérios de conclusão

- Criar futuramente uma mudança OpenSpec separada, conceitualmente denominada `historico-trajetos`.
- Depender da definição anterior da autenticação e da tabela de usuários.
- Preservar na mudança futura as decisões já documentadas sobre os 10 itens mais recentes, repetição consecutiva, exclusão individual, limpeza integral, propriedade exclusiva do usuário e recálculo com a malha atual.
- Criar futuramente uma mudança OpenSpec separada para avaliar tolerância de tempo ou penalidade por baldeação, evitando trajetos com economia mínima de tempo e quantidade excessiva de trocas de linha.

Estes itens não pertencem aos critérios de aceite desta mudança, não bloqueiam a conclusão de `busca-trajetos` e não autorizam alterações no Xano.

## Evidencias e limites da revisao de 13/09/2026

- A mudanca separada `autenticacao-planejamento` existe e contem a implementacao
  local de autenticacao; por isso o item 3.1 foi atualizado.
- Login, GET `/estacoes` e POST `/trajetos/buscar` (1 para 5) passaram pelo cliente
  Python. O resultado foi Vergueiro, Paraiso, Brigadeiro e Trianon-Masp, com
  360 segundos e uma baldeacao em Paraiso.
- A interface de planejamento ainda usa dados demonstrativos. Os itens 6.5,
  7.2 a 7.8 e a validacao integrada pelo navegador permanecem pendentes.
- O item 2.7 precisa de evidencia de validacao no armazenamento de trechos;
  rejeitar extremos iguais no endpoint de busca nao comprova essa constraint.
- A suite automatizada e a validacao estrita OpenSpec nao foram reexecutadas
  nesta revisao. Nao usar este registro como evidencia de aprovacao desses checks.
- O estado remoto atual dos indices e dos arquivos XanoScript nao foi reexportado.

Detalhes: `docs/validacao-integracao-xano.md`.

## Atualizacao da suite automatizada — 13/09/2026

O usuario executou novamente a suite no terminal do projeto apos corrigir a
asserção de login bem-sucedido que estava no teste de sessao ausente. Resultado:
`35 passed, 1 warning in 1.84s`. A correcao apenas reposicionou a asserção; nao
alterou o comportamento da aplicacao. O registro anterior de bloqueio descreve
a tentativa no ambiente do assistente. A validacao estrita OpenSpec passou posteriormente para as duas mudancas
(2 passed, 0 failed), conforme captura do usuario. Os cenarios completos no
navegador continuam pendentes.
