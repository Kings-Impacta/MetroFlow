# Validacao manual Python → Xano

Registro de 13/09/2026 baseado nas capturas de terminal enviadas pelo usuario.

## Ambiente identificado na interface

- Workspace: Raphael's Workspace, ID 149130; branch Xano v1.
- Grupo planejamento: ID 431173.
- Base auth: `https://x8ki-letl-twmt.n7.xano.io/api:75UptKSb`.
- Base planejamento: `https://x8ki-letl-twmt.n7.xano.io/api:metroflow-planejamento`.
- GET `/estacoes`: ID 4035908.
- POST `/trajetos/buscar`: ID 4035909.

A base de planejamento foi observada no cartao do grupo e no campo Servers do
Swagger. Metodos e caminhos foram observados na lista de endpoints e no Swagger.

## Resultados observados

1. Login com o cliente de autenticacao: `Login OK!`.
2. Listagem: cinco estacoes, IDs 1 a 5 — Vergueiro, Paraiso, Ana Rosa, Brigadeiro
   e Trianon-Masp.
3. Consulta 1 → 5: Vergueiro → Paraiso → Brigadeiro → Trianon-Masp.
4. Tres trechos de 120 segundos: total 360 segundos, exibido como 6 minutos.
5. Uma baldeacao em Paraiso: Linha 1 - Azul → Linha 2 - Verde.
6. Sequencia de estacoes e extremos dos trechos conferidos pelo script manual.

Os scripts solicitaram credenciais no terminal e nao imprimiram tokens. Estes
resultados confirmam os cenarios descritos, sem comprovar todos os criterios do MVP.

## Situação posterior das verificações

As pendências funcionais registradas em 13/09/2026 foram cobertas posteriormente:

- consultas nos dois sentidos foram executadas com a malha ampliada, e trajetos sem baldeação foram registrados na validação da malha;
- seleção inválida, ausência de rota, sessão ausente ou expirada, falha de serviço e contrato incompleto possuem cobertura automatizada;
- menor tempo e desempate por menos baldeações foram validados com a função documentada do XanoScript e malhas controladas em memória;
- extremos iguais, duplicatas direta e inversa e concorrência foram exercitados contra o endpoint real de gravação;
- nova busca, inversão, respostas antigas, recarga, logout e restauração da sessão possuem cobertura de estado e API, complementada por execução real em porta única.

Permanece pendente somente a comparação com uma **exportação oficial e identificada do Xano**, incluindo metadados e versões. Os arquivos `.xs` locais continuam sendo documentação, não fonte de implantação.

## Limites da revisao automatizada

O usuario executou a suite completa no terminal do projeto em 13/09/2026.
A primeira execucao retornou 34 aprovados e 1 falha: a assercao de sucesso de
login estava dentro do teste de sessao ausente, enquanto o teste de sucesso
nao tinha assercao. A correcao moveu a verificacao para o teste correspondente,
preservando a verificacao de sessao ausente e o codigo da aplicacao.

A nova execucao retornou `35 passed, 1 warning in 1.84s`: nove testes de
planejamento e 26 de autenticacao. O aviso foi `StarletteDeprecationWarning`
relacionado ao uso de httpx pelo TestClient. Nenhuma dependencia foi alterada
para suprimir o aviso.

A evidencia e a captura enviada pelo usuario. Os testes unitarios nao substituem
os cenarios reais pendentes nem a validacao da interface no navegador.

Nenhum recurso ou dado do Xano foi alterado durante esta revisao.

## Validacao estrita OpenSpec e historico remoto

O usuario executou `openspec.cmd validate --all --strict`. Resultado comprovado
por captura: `2 passed, 0 failed (2 items)`, para `autenticacao-planejamento` e
`buscar-trajetos-metro-mvp`. O uso do lancador `.cmd` nao exigiu alterar a politica
de execucao do PowerShell. Essa validacao verifica as especificacoes, nao declara
a implementacao completa do MVP.

Apos `git fetch origin` executado pelo usuario, foram inspecionadas as referencias
locais atualizadas: `origin/main` em `02140cf` e HEAD em `d1d924e`, com tres commits
a frente e nenhum atrasado. A branch `feature/integrar-autenticacao-reflex` nao
aparecia entre as branches de origin. Esses hashes registram o estado anterior
aos novos commits de organizacao. Nao houve push, merge nem alteracao no Xano.
