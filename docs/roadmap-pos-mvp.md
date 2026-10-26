# Roadmap pós-MVP

Ordem definida em 21/09/2026: **P0 → P4 → P1 → P5 → P3 → P2**. A área administrativa (P6) fica em espera.

| Etapa | Entrega | Critério de conclusão |
| --- | --- | --- |
| P0 | CI, sessão expirada e auditoria de segredos | Checks verdes; sessão inválida bloqueada; credenciais ausentes de respostas, URLs, históricos e logs examinados |
| P4 | Recuperação de senha e verificação de e-mail | Fluxos seguros, tokens de uso único e testes de ponta a ponta |
| P1 | Estimativas de caminhada, espera e baldeação | Dados confiáveis e comparação com a regra fixa atual |
| P5 | Lotação e condições em tempo real | Fonte autorizada, atualização conhecida e estado indisponível claro |
| P3 | Dez trajetos planejados recentes por usuário | Acesso exclusivo, exclusão e recálculo com a malha atual |
| P2 | Rotas alternativas | Critérios explícitos de diversidade, tempo e baldeações |

Cada etapa requer uma mudança OpenSpec própria antes de alterar contratos ou dados do Xano.

## Estado atual em 19/10/2026

- **P0 concluído:** CI, proteção de sessão expirada e auditoria de segredos foram validados e arquivados em `2026-09-23-auditoria-segredos-sessao`.
- **P4 concluído:** confirmação de e-mail, recuperação de senha, uso único dos tokens e invalidação de sessões anteriores foram validados e arquivados em `2026-10-08-recuperacao-senha-verificacao-email`.
- **Próxima etapa planejada: P1**, ainda sem mudança OpenSpec ativa.
- **P5 avaliada em 21/10/2026:** a ARTESP oferece contrato documentado para a
  malha delegada, enquanto a fonte agregada observada para Metrô e CPTM ainda exige
  confirmação de autorização e condições de republicação. A mudança ativa
  `integrar-status-operacional-multifonte` registra o desenho e as pendências; a
  implementação permanece condicionada a essas confirmações e não altera a ordem P1 → P5.

## Concorrência de rotas em 26/10/2026

A mudança `concorrencia-rotas` foi incluída fora da sequência P0–P6. Ela registra as viagens confirmadas no próprio MetroFlow, estima a lotação de cada trecho ferroviário por sentido e, quando o trajeto principal passa por um trecho lotado, apresenta o caminho de menor tempo que o evita. A estimativa é interna e não substitui o P5, que depende de fonte autorizada e de informação ao usuário, nem o P2, que prevê várias opções de trajeto.

- **Concluído:** endpoint local `/api/planning/trip`, registro automático após uma busca bem-sucedida, testes do backend, da interface e das funções de cálculo, e publicação no Xano das tabelas e dos endpoints descritos em [docs/xano/rascunhos/concorrencia-rotas](xano/rascunhos/concorrencia-rotas/README.md).
- **Pendente:** reimportar a malha perdida no [incidente da tabela `trechos`](xano/incidente-trechos-2026-10-26.md), validar o fluxo com uma sessão real e substituir os parâmetros de lotação de teste (`1` e `1%`) pelos valores definidos pela equipe.

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
