# MetroFlow

Projeto integrador para consulta de trajetos do transporte ferroviário metropolitano de São Paulo, com interface Python/Reflex e APIs Xano.

## Estado atual

O cliente Python de autenticação e os adaptadores de estações e trajetos estão implementados. Foram executados testes reais de login, listagem de cinco estações e consulta de Vergueiro até Trianon-Masp (360 segundos, uma baldeação).

O planejador agora carrega estações e solicita trajetos pelo backend local, usando a sessão HttpOnly existente. A tela apresenta carregamento, resultado real, ausência de trajeto e falhas; os resultados demonstrativos foram removidos. A validação completa no navegador com o Xano real ainda precisa ser executada. Consulte [a integração da interface](docs/integracao-interface-planejamento.md).

Consulte [a arquitetura](ARCHITECTURE.md), [o registro de validação](docs/validacao-integracao-xano.md) e as mudanças em `openspec/changes/` para distinguir implementação de pendências.

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

Essa chamada usa o Python existente e não depende de `uv` no PATH. Em 13/09/2026, o usuário executou a suíte completa após corrigir uma asserção posicionada no teste errado: 35 testes passaram, com 1 aviso de depreciação, em 1,84 s. Consulte o registro de validação para os limites dessa cobertura.

Antes de iniciar, compilar ou depurar o servidor Reflex, siga `.agents/skills/reflex-process-management/SKILL.md`. Antes de editar componentes ou estado, use também `.agents/skills/reflex-docs/SKILL.md`.

## Xano e escopo

O Xano calcula o caminho por menor tempo e, em empate, menos baldeações. O primeiro MVP não inclui lotação, alternativas, tempo de espera ou custo adicional de transferência.

Os arquivos locais em `xano/`, quando presentes, ainda precisam ter a procedência conferida contra uma exportação remota. Não devem ser usados para sincronização ou descritos como backup fiel sem essa verificação. Alterações em recursos ou dados remotos exigem autorização específica.
