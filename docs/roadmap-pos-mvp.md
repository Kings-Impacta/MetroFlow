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

## P0: evidências e pendências

- O workflow `Qualidade` da `main`, execução [35648638273](https://github.com/Kings-Impacta/MetroFlow/actions/runs/35648638273) no commit `40f20ca`, passou.
- Uma busca sem cookie respondeu 401. O teste de estado cobre limpeza e redirecionamento para `/login` ao receber 401.
- A resposta padrão 422 do FastAPI repetia o valor enviado em `senha`. A API agora devolve um detalhe genérico; o teste de regressão cobre login e cadastro. A resposta do serviço local após a alteração também foi conferida com dados fictícios e não repetiu os marcadores enviados.
- Depois da correção, 63 testes e 8 subtestes passaram, com 2 avisos de depreciação.
- A expiração natural de 24 horas ainda precisa ser observada no navegador com a busca aberta.
- No histórico remoto do Xano, a entrada de `auth/login` mascara a senha, mas a saída guardava o token de autenticação completo. Não reproduzir o valor em evidências. O histórico padrão é retido por 24 horas. A opção `Request History` foi alterada de `Inherit Settings` para `Disabled` nos endpoints `auth/login` e `auth/signup`, ambos emissores de token. Os dois rascunhos foram publicados juntos, com confirmação de publicação na interface. Os registros anteriores à alteração ainda podem permanecer até o fim da retenção.
- Nos logs de erro do Xano, os 6 erros das últimas 24 horas foram de limite de requisições (`429`) em `auth/me`; não havia erro recente de login ou cadastro na visão examinada.
- No registro de `auth/me` examinado, a seção de cabeçalhos da requisição estava vazia. Um novo usuário de teste foi criado e apareceu na tabela `usuarios`, mas essa chamada ocorreu antes da publicação e, por isso, ainda constava no histórico. Um teste com credenciais fictícias no executor do Xano após a publicação retornou `ERROR_CODE_UNAUTHORIZED`, como esperado; o executor não comprova o comportamento do histórico de chamadas HTTP externas. A página de busca carregou após uma recarga com a sessão existente. Ainda faltam um login/cadastro real após a publicação, a confirmação de que essas novas chamadas não geram histórico e a observação da expiração natural da sessão.
