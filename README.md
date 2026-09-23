# MetroFlow

Projeto integrador para consulta de trajetos do transporte ferroviário metropolitano de São Paulo, com interface Python/Reflex e APIs Xano.

## Estado atual

O fluxo autenticado de cadastro, login, restauração de sessão e logout está integrado ao Xano. O planejador carrega a malha ferroviária cadastrada, consulta trajetos reais e apresenta estações, linhas, operadores, sentidos, baldeações e tempo estimado.

O cálculo utiliza os tempos dos trechos e acrescenta 600 segundos por mudança de linha. Foram validadas rotas diretas, inversas, com baldeações, integrações a pé e o Expresso Aeroporto. A interface também foi verificada no Chrome após impedir que a tradução automática alterasse o DOM controlado pelo Reflex.

Para conhecer o projeto, leia a [visão geral](docs/project-overview.md), o [modelo de domínio](docs/domain-model.md) e a [arquitetura](ARCHITECTURE.md). O comportamento concluído está em `openspec/specs/`; o histórico das entregas está em `openspec/changes/archive/`; e as pendências continuam em `openspec/changes/`. O [registro de validação](docs/validacao-integracao-xano.md) e a [auditoria de integridade do Xano](docs/xano/auditoria-integridade-2026-09-21.md) detalham evidências e limites.

## Ambiente e configuração

O projeto declara Python >= 3.12 e Reflex 0.9.10.post1; `.python-version` seleciona Python 3.12. Antes de preparar o ambiente, siga `AGENTS.md` e o skill local `.agents/skills/setup-python-env/SKILL.md`.

Configure as URLs no PowerShell que executará o projeto:

```powershell
$env:XANO_AUTH_API_BASE_URL="https://x8ki-letl-twmt.n7.xano.io/api:75UptKSb"
$env:XANO_PLANNING_API_BASE_URL="https://x8ki-letl-twmt.n7.xano.io/api:metroflow-planejamento"
```

Essas variáveis valem apenas para o terminal atual e seus processos filhos. O código lê variáveis de ambiente; não há carregamento automático de `.env` implementado nos clientes.

Para produção, a política local de cookie exige `METROFLOW_ENV=production` para ativar `Secure`; o serviço deve usar HTTPS. O token de usuário é recebido pelo login e permanece no backend/cookie HttpOnly. Não é uma chave administrativa do painel Xano.

## Testes

Com o ambiente virtual e as dependências de desenvolvimento preparados, execute na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
```

Essa chamada usa o Python existente e não depende de `uv` no PATH. Em 21/09/2026, a suíte completa passou com **62 testes, 6 subtestes e 2 avisos de depreciação**. A validação estrita do OpenSpec também passou para as duas mudanças ativas. Consulte o registro de validação para os limites dessa cobertura.

Antes de iniciar, compilar ou depurar o servidor Reflex, siga `.agents/skills/reflex-process-management/SKILL.md`. Antes de editar componentes ou estado, use também `.agents/skills/reflex-docs/SKILL.md`.

## Xano e escopo

O Xano calcula o caminho pelo menor tempo estimado, somando os trechos e 600 segundos por mudança de linha; em empate, escolhe menos baldeações. O primeiro MVP não inclui lotação, alternativas ou tempos reais e específicos de caminhada, espera ou transferência.

Os arquivos em `docs/xano/rascunhos/` registram o XanoScript observado e publicado, mas não substituem uma exportação oficial do workspace. Alterações em recursos ou dados remotos exigem autorização específica.

## Qualidade contínua

O workflow `.github/workflows/quality.yml` executa a suíte Python e a validação estrita do OpenSpec em Pull Requests e em atualizações da `main`.
