# Guia técnico do MetroFlow

Complemento ao [manual de uso](../README.md). O conteúdo técnico foi separado para manter o README centrado nas jornadas dos usuários. Estado documentado após o PR #52; esta reorganização não altera dependências, variáveis ou comportamento.

## Ambiente e execução

O projeto declara Python >= 3.12; `.python-version` seleciona 3.12. O Reflex está fixado em **0.9.10.post1**, e `uv.lock` registra as dependências. Use uv e não misture instalações manuais com pip nem gere requirements.txt sem uma mudança dessa decisão.

```powershell
uv sync --frozen --group dev --python 3.12
.\iniciar-status-local.ps1
```

Execute os comandos na raiz do repositório. O iniciador prepara o ambiente e usa Reflex em modo de produção com porta única, registrando a saída em `reflex.log`. O iniciador básico `iniciar-metroflow.ps1` não habilita por si só as fontes de status.

Execução direta no ambiente já preparado:

```powershell
.\.venv\Scripts\python.exe -m reflex run --env prod --single-port 2>&1 | Tee-Object -FilePath reflex.log
```

Abra `http://localhost:3000` ou a porta indicada. `0.0.0.0` é o endereço de escuta, não o endereço de navegação. A API local deve compartilhar a origem da página; use porta única ou proxy que encaminhe `/api/` ao backend. Pare o processo anterior com Ctrl+C antes de iniciar outra instância. Alterações exigem reinício, pois esse modo não faz hot reload.

## Configuração de backend

As URLs públicas do projeto são usadas como padrão quando as variáveis estiverem ausentes:

```powershell
$env:XANO_AUTH_API_BASE_URL="https://x8ki-letl-twmt.n7.xano.io/api:75UptKSb"
$env:XANO_PLANNING_API_BASE_URL="https://x8ki-letl-twmt.n7.xano.io/api:metroflow-planejamento"
$env:XANO_ADMIN_API_BASE_URL="https://x8ki-letl-twmt.n7.xano.io/api:metroflow-administracao"
```

Esses endereços não substituem autenticação nem concedem acesso administrativo. As variáveis valem para o processo atual e seus filhos. Os clientes não carregam `.env` automaticamente. Use valores explícitos se apontar para outro ambiente.

As fontes ficam desativadas por padrão; o iniciador local habilita Metrô/CPTM/Motiva somente no processo iniciado e mantém Direto dos Trens desativado. Veja [status operacional](status-operacional.md) para cache, limites, credenciais e condições de futura ativação. Chaves externas ficam no backend; a chave de envio de e-mail permanece no Xano. Não compartilhar credenciais pelo Git ou em arquivos públicos.

A localização pode ser desativada com `METROFLOW_LOCALIZACAO=0` e as orientações com `METROFLOW_ORIENTACOES=0`, antes de iniciar o servidor. Essas opções são documentadas aqui, mas não foram alteradas nesta atualização documental. Fora de localhost, a geolocalização exige HTTPS.

Para hospedagem pública, HTTPS e `METROFLOW_ENV=production` são necessários para o cookie Secure. A opção `reflex --env prod` não substitui essa variável. Esta instrução é condição técnica, não confirmação de prontidão ou autorização das fontes para serviço público.

## Administração e cálculo

A concessão administrativa é consultada pelo Xano a cada operação. O campo de perfil retornado por auth/me adapta a interface; não substitui essa verificação. Consulte o [registro do painel](xano/rascunhos/portal-administrativo/README.md) para os recursos e a concessão autorizada.

O Xano calcula os trajetos e registra as viagens. O contrato calibrado compartilha versão e cronologia entre busca e registro; a penalidade fixa de 600 segundos pertence ao legado. A margem pública é de 60 segundos uma única vez e não amplia a ocupação. O [modelo de domínio](domain-model.md) descreve os limites de concorrência e a preferência pelo Metrô.

A correção do painel permite uma única repetição de GET em falha transitória; não repete POST, 401/403/429, Retry-After ou contrato inválido. Não existe cache de autorização para contornar revogação. A indisponibilidade externa persistente continua possível.

## Testes e evidências

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
openspec.cmd validate --all --strict --no-interactive
```

A suíte da correção administrativa passou com **440 testes e 119 subtestes**, com um aviso de depreciação existente do TestClient; a compilação `reflex compile --dry` foi concluída. OpenSpec estrito: **16 itens aprovados** naquele estado. Esses resultados pertencem à correção e não equivalem a testes novos executados para cada edição documental.

O workflow [.github/workflows/quality.yml](../.github/workflows/quality.yml) executa testes e OpenSpec em PRs e na main, configurando Python 3.12 e Node.js 22. Os testes de scripts de interface e funções JavaScript precisam de Node; sem ele, parte da suíte pode ser ignorada. A suíte não substitui testes reais de navegador/Xano.

[A auditoria de 17/11 e validação de 18/11](xano/acesso-administrativo-concorrencia-2026-11-17.md) documenta os registros 89/90, a atualização do painel e seus limites. A configuração ausente foi validada por **HTTP local isolado**, não HTTP no runtime nativo do Xano. A manutenção administrativa simultânea de trechos e a gravação real da situação das estações não foram comprovadas por esse laboratório.

Antes de editar ou executar o projeto, siga [AGENTS.md](../AGENTS.md). Antes de alterações Reflex, consulte os skills locais indicados nele. Os arquivos em `docs/xano/rascunhos/` registram o código observado, mas não substituem exportação oficial do workspace. Alterações remotas exigem autorização e fluxo de backup/validação; este manual não autoriza novas publicações.

## Problemas comuns

| Sintoma | Verificação |
|---|---|
| uv não encontrado | Instalar o gerenciador pela fonte oficial indicada no guia de apresentação e abrir novo terminal. |
| Porta ocupada | Encerrar a instância anterior; conferir a porta no log. Não iniciar vários servidores sem necessidade. |
| Mudanças não aparecem | Confirmar a versão, reiniciar o servidor e atualizar o navegador com Ctrl+F5. |
| Autenticação ou painel indisponível | Conferir internet e disponibilidade do Xano; aguardar antes de tentar novamente. Não conceder acesso ou alterar parâmetros para contornar a falha. |
| Status indisponível | Conferir o iniciador usado, a cobertura efetiva e a data do último retorno; não inferir normalidade. |
| Localização não obtida | Conferir permissão e contexto seguro; manter seleção manual. |

Histórico e referências: [visão geral](project-overview.md), [arquitetura](../ARCHITECTURE.md), [roadmap](roadmap-pos-mvp.md), [especificações](../openspec/specs/) e [registros Xano](xano/README.md).
