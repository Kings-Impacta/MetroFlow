# MetroFlow

Projeto integrador para consulta de trajetos do transporte ferroviário metropolitano de São Paulo, com interface Python/Reflex e APIs Xano.

## Estado atual

O fluxo autenticado de cadastro, login, restauração de sessão e logout está integrado ao Xano. O planejador carrega a malha ferroviária cadastrada, consulta trajetos reais e apresenta estações, linhas, operadores, sentidos, baldeações e tempo estimado.

O cadastro solicita confirmação por e-mail antes do primeiro login. O sistema também permite reenviar a confirmação e recuperar a senha; após a redefinição, a sessão local é encerrada e o usuário retorna ao login. Em 06/10/2026, a entrega real de e-mails, a redefinição de senha, o novo login e o planejamento autenticado foram validados com o Xano e o Brevo. Consulte [a revisão](docs/revisao-local-2026-10-02.md) para conhecer as evidências e pendências complementares.

O cálculo utiliza os tempos dos trechos e acrescenta 600 segundos por mudança de linha. Foram validadas rotas diretas, inversas, com baldeações, integrações a pé e o Expresso Aeroporto. A interface também foi verificada no Chrome após impedir que a tradução automática alterasse o DOM controlado pelo Reflex.

Para conhecer o projeto, leia a [visão geral](docs/project-overview.md), o [modelo de domínio](docs/domain-model.md) e a [arquitetura](ARCHITECTURE.md). O comportamento concluído está em `openspec/specs/`; o histórico das entregas está em `openspec/changes/archive/`; e novas mudanças ativas, quando existirem, ficam em `openspec/changes/`. O [registro de validação](docs/validacao-integracao-xano.md) e a [auditoria complementar de integridade do Xano](docs/xano/auditoria-integridade-2026-10-08.md) detalham evidências e limites atuais.

## Ambiente e configuração

O projeto declara Python >= 3.12 e Reflex 0.9.10.post1; `.python-version` seleciona Python 3.12. Antes de preparar o ambiente, siga `AGENTS.md` e o skill local `.agents/skills/setup-python-env/SKILL.md`.

O gerenciador de dependências adotado neste repositório é o `uv`, com ambiente em `.venv` e versões registradas em `uv.lock`. Não misture instalações manuais com `pip` nem gere `requirements.txt` sem uma mudança explícita dessa decisão. Para preparar ou atualizar o ambiente, use `uv sync --frozen --group dev --python 3.12`.

Quem for apenas executar ou apresentar o projeto pode seguir o [guia de apresentação](GUIA_APRESENTACAO.md). No Windows, o script `iniciar-metroflow.ps1` prepara o ambiente com as versões registradas e inicia o Reflex. As credenciais do Brevo permanecem no Xano e não precisam ser distribuídas aos integrantes.

Configure as URLs no PowerShell que executará o projeto:

```powershell
$env:XANO_AUTH_API_BASE_URL="https://x8ki-letl-twmt.n7.xano.io/api:75UptKSb"
$env:XANO_PLANNING_API_BASE_URL="https://x8ki-letl-twmt.n7.xano.io/api:metroflow-planejamento"
```

Essas variáveis valem apenas para o terminal atual e seus processos filhos. O código lê variáveis de ambiente; não há carregamento automático de `.env` implementado nos clientes.

Nesta branch, na ausência dessas variáveis, os clientes usam as URLs públicas do projeto como padrão. Configure-as explicitamente para apontar para outro ambiente.

### Executar localmente

Na raiz do projeto, mantenha o terminal aberto enquanto usa a aplicação:

```powershell
.\.venv\Scripts\python.exe -m reflex run --env prod --single-port 2>&1 | Tee-Object -FilePath reflex.log
```

Abra `http://localhost:3000` (ou a porta indicada no log). `0.0.0.0` é o endereço de escuta do servidor, não o endereço para navegar. As chamadas locais de autenticação e planejamento usam a mesma origem da página; esta configuração requer porta única ou um proxy que encaminhe `/api/` ao backend. Para aplicar alterações, encerre o processo anterior com Ctrl+C no terminal dele e execute novamente.

Para produção, a política local de cookie exige `METROFLOW_ENV=production` para ativar `Secure`; o serviço deve usar HTTPS. O token de usuário é recebido pelo login e permanece no backend/cookie HttpOnly. Não é uma chave administrativa do painel Xano.

## Testes

Com o ambiente virtual e as dependências de desenvolvimento preparados, execute na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
```

Essa chamada usa o Python existente e não depende de `uv` no PATH. Em 06/10/2026, a suíte completa passou com **98 testes, 10 subtestes e 1 aviso de depreciação**. A validação estrita do OpenSpec passou para os **6 itens** existentes. Consulte o registro de validação para os limites dessa cobertura.

Em 02/10/2026, a revisão local passou com **97 testes e 10 subtestes**, sem testes ignorados. Os testes de JavaScript usam Node.js com DOM e rede simulados; sem Node.js, esses testes são ignorados. O workflow configura Node.js explicitamente. Isso não substitui a validação visual e a integração real com o Xano.

Antes de iniciar, compilar ou depurar o servidor Reflex, siga `.agents/skills/reflex-process-management/SKILL.md`. Antes de editar componentes ou estado, use também `.agents/skills/reflex-docs/SKILL.md`.

## Xano e escopo

O Xano calcula o caminho pelo menor tempo estimado, somando os trechos e 600 segundos por mudança de linha; em empate, escolhe menos baldeações. O primeiro MVP não inclui lotação, alternativas ou tempos reais e específicos de caminhada, espera ou transferência.

Os arquivos em `docs/xano/rascunhos/` registram o XanoScript observado e publicado, mas não substituem uma exportação oficial do workspace. Alterações em recursos ou dados remotos exigem autorização específica.

## Qualidade contínua

O workflow `.github/workflows/quality.yml` executa a suíte Python e a validação estrita do OpenSpec em Pull Requests e em atualizações da `main`.
