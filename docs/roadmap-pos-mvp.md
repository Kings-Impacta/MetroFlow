# Roadmap pós-MVP

Ordem definida em 21/09/2026: **P0 → P4 → P1 → P5 → P3 → P2**. A área administrativa (P6) fica em espera.

## Prioridade de trajetos em 29/10/2026

Por decisão do usuário, corrigir primeiro a qualidade dos trajetos existentes: desvios excessivos por concorrência, voltas na madrugada, ocupação prevista, troca na extensão de Itapevi e informação sobre acesso nas integrações. A mudança `corrigir-qualidade-trajetos` registra critérios e validação.

A calibração de deslocamentos, frequências regulares e transferências específicas depende de dados atuais por trecho e sentido; não usar médias genéricas como se fossem medições. A integração de status segue em sua mudança própria, sem presumir normalidade quando a fonte estiver ausente.

**Atualização em 09/11:** a Linha 6 foi tratada por último e sua operação parcial modelada foi incluída na publicação de 05/11. Conexões futuras não são oferecidas. As prioridades de 29/10 abaixo são históricas.

| Etapa | Entrega | Critério de conclusão |
| --- | --- | --- |
| P0 | CI, sessão expirada e auditoria de segredos | Checks verdes; sessão inválida bloqueada; credenciais ausentes de respostas, URLs, históricos e logs examinados |
| P4 | Recuperação de senha e verificação de e-mail | Fluxos seguros, tokens de uso único e testes de ponta a ponta |
| P1 | Estimativas de caminhada, espera e baldeação | Dados confiáveis e comparação com a regra fixa atual |
| P5 | Lotação e condições em tempo real | Fonte autorizada, atualização conhecida e estado indisponível claro |
| P3 | Dez trajetos planejados recentes por usuário | Acesso exclusivo, exclusão e recálculo com a malha atual |
| P2 | Rotas alternativas | Critérios explícitos de diversidade, tempo e baldeações |

Cada etapa requer uma mudança OpenSpec própria antes de alterar contratos ou dados do Xano.

## Estado histórico de 19/10 e atualizações até 09/11/2026

- **P0 concluído:** CI, proteção de sessão expirada e auditoria de segredos foram validados e arquivados em `2026-09-23-auditoria-segredos-sessao`.
- **P4 concluído:** confirmação de e-mail, recuperação de senha, uso único dos tokens e invalidação de sessões anteriores foram validados e arquivados em `2026-10-08-recuperacao-senha-verificacao-email`.
- **P1 entregue posteriormente:** cobertura estimada da malha ativa e publicação calibrada em 05/11; fechamento do teste de concorrência em 09/11. A próxima frente é P5, nos limites da mudança ativa de status.
- **P5 avaliada em 21/10/2026:** a ARTESP oferece contrato documentado para a
  malha delegada, enquanto a fonte agregada observada para Metrô e CPTM ainda exige
  confirmação de autorização e condições de republicação. A mudança ativa
  `integrar-status-operacional-multifonte` registra o desenho e as pendências; a
  implementação permanece condicionada a essas confirmações e não altera a ordem P1 → P5.

## Concorrência de rotas em 26/10/2026

A mudança `concorrencia-rotas` foi incluída fora da sequência P0–P6. Ela registra as viagens confirmadas no próprio MetroFlow, estima a lotação de cada trecho ferroviário por sentido e, quando o trajeto principal passa por um trecho lotado, apresenta o caminho de menor tempo que o evita. A estimativa é interna e não substitui o P5, que depende de fonte autorizada e de informação ao usuário, nem o P2, que prevê várias opções de trajeto.

- **Concluído:** endpoint local `/api/planning/trip`, registro automático após uma busca bem-sucedida, testes do backend, da interface e das funções de cálculo, e publicação no Xano das tabelas e dos endpoints descritos em [docs/xano/rascunhos/concorrencia-rotas](xano/rascunhos/concorrencia-rotas/README.md).
- **Atualização em 09/11:** malha restaurada e calibrada; fluxo com duas contas e alternativa por República confirmado. Os parâmetros `1` e `1%` continuam autorizados para demonstração. Valores de produção e verificações remotas complementares permanecem no [fechamento de trajetos e concorrência](xano/fechamento-trajetos-concorrencia-2026-11-09.md).

Os registros abaixo preservam a sequência de evidências obtidas durante o P0. Menções a trabalho ainda pendente descrevem o estado naquela data e foram superadas pelas conclusões posteriores registradas neste mesmo documento.

## Histórico do P0: evidências e pendências da época

- O workflow `Qualidade` da `main`, execução [35648638273](https://github.com/Kings-Impacta/MetroFlow/actions/runs/35648638273) no commit `40f20ca`, passou.
- Uma busca sem cookie respondeu 401. O teste de estado cobre limpeza e redirecionamento para `/login` ao receber 401.
- A resposta padrão 422 do FastAPI repetia o valor enviado em `senha`. A API agora devolve um detalhe genérico; o teste de regressão cobre login e cadastro. A resposta do serviço local após a alteração também foi conferida com dados fictícios e não repetiu os marcadores enviados.
- Depois da correção, 63 testes e 8 subtestes passaram, com 2 avisos de depreciação.
- Naquele momento, a expiração natural ainda precisava ser observada no navegador com a busca aberta. O teste controlado posterior reduziu temporariamente a validade, comprovou o bloqueio e o redirecionamento e restaurou a validade de 24 horas.
- No histórico remoto do Xano, a entrada de `auth/login` mascara a senha, mas a saída guardava o token de autenticação completo. Não reproduzir o valor em evidências. O histórico padrão é retido por 24 horas. A opção `Request History` foi alterada de `Inherit Settings` para `Disabled` nos endpoints `auth/login` e `auth/signup`, ambos emissores de token. Os dois rascunhos foram publicados juntos, com confirmação de publicação na interface. Os registros anteriores à alteração ainda podem permanecer até o fim da retenção.
- Nos logs de erro do Xano, os 6 erros das últimas 24 horas foram de limite de requisições (`429`) em `auth/me`; não havia erro recente de login ou cadastro na visão examinada.
- No registro de `auth/me` examinado, a seção de cabeçalhos da requisição estava vazia. Um novo usuário de teste foi criado e apareceu na tabela `usuarios`, mas essa chamada ocorreu antes da publicação e, por isso, ainda constava no histórico. Um teste com credenciais fictícias no executor do Xano após a publicação retornou `ERROR_CODE_UNAUTHORIZED`, como esperado. Naquele momento ainda faltavam um fluxo real posterior à publicação e a observação da expiração; ambos foram concluídos no fechamento do P0.

## Verificação complementar de 22/09/2026

- A configuração publicada de `auth/login` e `auth/signup` continua com `Request History: Disabled`; a própria visualização do histórico de cadastro informa que ele está desativado.
- Uma chamada HTTP externa de login com e-mail e senha inteiramente fictícios retornou 401. A resposta não repetiu a senha enviada. Como a chamada não emitiu token, ela não substitui a verificação de um login ou cadastro bem-sucedido após a publicação.
- Naquela verificação ainda restavam a auditoria do fluxo bem-sucedido e a expiração da sessão. As duas tarefas foram concluídas em 23/09/2026; a mudança correspondente está arquivada em `openspec/changes/archive/2026-09-23-auditoria-segredos-sessao/`.
## Conclusão do P0 em 23/09/2026

- Um cadastro real posterior à desativação do histórico criou o usuário de teste ativo sem expor senha ou token; `auth/login` e `auth/signup` permaneceram com `Request History: Disabled`.
- A validade dos tokens foi reduzida temporariamente de 86.400 para 60 segundos nos dois endpoints emissores e publicada apenas durante o teste controlado.
- O teste revelou que a consulta de rota verificava somente a presença do cookie. O endpoint `/api/planning/route` passou a revalidar o token pelo `auth/me` antes do cálculo.
- Com o processo reiniciado e o token expirado, uma nova consulta foi bloqueada e o navegador foi redirecionado para `/login`.
- A validade de `auth/login` e `auth/signup` foi restaurada e publicada em 86.400 segundos (24 horas), sem rascunhos pendentes no Xano.
- A suíte local passou com 63 testes e 8 subtestes; restou apenas um aviso de depreciação do `TestClient`.

## Atualização em 11/11/2026

A parcela informativa de P5 está entregue na main pelo PR #41: três fontes públicas habilitáveis localmente, 12 linhas, renovação automática e retenção do último retorno. Direto dos Trens aguarda token; 6/7/13, serviços especiais e condições de ativação pública continuam pendentes. Isso não entrega lotação oficial nem várias alternativas simultâneas de P2. O reteste no Xano confirmou registros 67/68, calibração e concorrência pela Luz dentro dos limites. Consulte o [resultado e a lista atual de pendências](xano/reteste-main-status-concorrencia-2026-11-11.md); as avaliações de P5 acima descrevem seu estágio histórico.

## Encerramento com escopo reduzido — 12/11/2026

Por decisão do usuário, `corrigir-pendencias-malha` e `integrar-status-operacional-multifonte` foram encerradas e arquivadas com o escopo já entregue, em `openspec/changes/archive/2026-11-12-corrigir-pendencias-malha/` e `openspec/changes/archive/2026-11-12-integrar-status-operacional-multifonte/`. As referências anteriores a mudanças ativas descrevem o estado antes desta decisão.

Os dois itens restantes da malha e os quatro de status foram **adiados, não executados nem aprovados**, e estão preservados em [melhorias futuras e limitações](melhorias-futuras-malha-status.md). As contagens originais eram 17/19 e 15/19; não foram convertidas em alegações de execução integral. As listas arquivadas distinguem tarefas executadas e itens retirados do compromisso atual. Não há mudanças ativas no OpenSpec após este encerramento; isso não significa ausência de melhorias ou restrições.

Foram consolidadas as capacidades `disponibilidade-malha` e `status-operacional-linhas`, alinhando referências históricas à calibração e à configuração local já entregues. Nenhuma alteração de código, funcionamento, malha, parâmetros, fontes ou configuração foi feita. O encerramento permanece local até entrega posterior na main.

A configuração ausente foi validada por **HTTP local isolado**, não por HTTP no runtime nativo do Xano, e não comprova o teste administrativo de gravações simultâneas de trechos. A ativação pública das fontes e a validação autorizada Direto dos Trens continuam fora do escopo encerrado.
