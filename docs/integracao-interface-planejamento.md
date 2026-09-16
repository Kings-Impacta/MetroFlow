# Interface de planejamento — 14/09/2026

Implementacao na branch `feature/conectar-interface-planejamento`.

## Comportamento

- O planejador carrega estacoes ativas e apresenta nome, linha e operador.
- Origem e destino devem ser escolhidos na lista e ser diferentes.
- A consulta mostra carregamento e bloqueia envios duplicados e alteracoes na
  selecao durante a requisicao.
- O resultado mostra estacoes em ordem, trechos, linhas, operadores, tempo em
  segundos/minutos e baldeacoes. Nao mostra lotacao ou alternativas ficticias.
- Uma nova selecao ou consulta limpa o resultado anterior; callbacks antigos
  sao ignorados. O logout limpa o estado do planejador.
- Sessao ausente/expirada redireciona ao login. Erros de lista oferecem recarga;
  erros de trajeto permitem repetir a busca.
- `/rotas`, `/trajeto` e `/comparar` preservam os enderecos existentes e apresentam
  o mesmo planejador, sem resultados estaticos.

## Fronteira de autenticacao

As rotas locais `/api/planning/stations` e `/api/planning/route` recebem o cookie
HttpOnly. O backend verifica a sessao em `/auth/me` antes da consulta e passa o
token ao cliente Xano somente em memoria. As chamadas do navegador usam a mesma
origem, `credentials: include` e `cache: no-store`; nao leem o token.

O POST local exige IDs inteiros positivos. Respostas de erro do servico nao sao
repassadas literalmente ao navegador. A conversao do resultado verifica origem,
destino, continuidade dos trechos e correspondencia das baldeacoes.

O contrato remoto ainda usa 404 para estacao inexistente e para ausencia de
caminho. A interface informa que nao encontrou trajeto para a selecao e oferece
atualizacao das estacoes, sem alegar que distinguiu esses dois motivos.

## Verificacoes automatizadas

Resultado em 14/09/2026: **59 testes aprovados, 6 subtestes aprovados e 2 avisos**
em 2,30 s. Os avisos sao de deprecacao; nenhum pacote foi alterado para oculta-los.

Testes HTTP usam TestClient e clientes Xano substituidos por mocks, sem acessar
o backend real. Cobrem autenticacao, parametros invalidos, ordenacao da lista,
operadores, tempos, baldeacoes, erros 401/404/502/503 e rejeicao de resposta de
outra selecao ou sequencia inconsistente.

Testes de estado cobrem selecao invalida, carregamento, duplicatas, callbacks
antigos, logout, nova selecao, lista vazia, falha de rede, payload incompleto e
sucesso. A aplicacao foi importada, suas paginas foram construidas e o compilador
Reflex foi chamado com `dry_run=True`.

O lancador Python da `.venv` apresentou bloqueio de permissao no ambiente do
assistente. As verificacoes foram executadas com Python 3.12.14 do runtime local
do Codex e as dependencias da `.venv` do projeto. O comando CLI Reflex tambem foi
limitado pelo acesso a metadados; a compilacao foi exercitada diretamente pelo
metodo `app._compile(dry_run=True)`. Nao houve instalacao ou atualizacao de pacotes.

## Validacao manual ainda necessaria

No PowerShell da raiz do projeto, configure as variaveis novamente se o terminal
for novo:

```powershell
$env:XANO_AUTH_API_BASE_URL="https://x8ki-letl-twmt.n7.xano.io/api:75UptKSb"
$env:XANO_PLANNING_API_BASE_URL="https://x8ki-letl-twmt.n7.xano.io/api:metroflow-planejamento"
.\.venv\Scripts\python.exe -m reflex compile --dry
.\.venv\Scripts\python.exe -m reflex run --env prod --single-port 2>&1 | Tee-Object -FilePath reflex.log
```

Usar o endereco indicado pelo servidor, sem presumir uma porta. Antes de iniciar
outro processo, verificar se o projeto ja esta em execucao e seguir o skill
`reflex-process-management` para reinicio seguro.

1. Abrir `/buscar-trajeto` sem sessao e conferir o redirecionamento ao login.
2. Entrar com uma conta existente e carregar as estacoes.
3. Selecionar Vergueiro e Trianon-Masp e conferir o trajeto, tempo e baldeacao
   contra a malha atual. No teste anterior, foram 360 s e uma troca em Paraiso.
4. Alterar a selecao e conferir que o resultado anterior desaparece.
5. Testar extremos iguais, consulta inversa e rota na mesma linha.
6. Sair da conta e conferir que nenhum resultado anterior permanece no planejador.
7. Conferir a tela em largura pequena, navegacao por teclado e nova tentativa
   apos falha de rede.

Nenhum teste com credenciais reais foi executado pelo assistente nesta etapa.
As validacoes reais anteriores foram dos clientes Python, nao desta nova tela.

## Referencias utilizadas

- [API Transformer do Reflex](https://reflex.dev/docs/api-routes/overview)
- [Select do Reflex](https://reflex.dev/docs/library/forms/select/)
- Skills Reflex locais e componentes da versao instalada 0.9.10.post1.
