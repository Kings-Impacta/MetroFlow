## Context

O Xano calcula o trajeto em `POST /trajetos/buscar`. O cliente
`MetroFlow/planning/infrastructure/xano_client.py` normaliza a resposta para
`RouteResult`; `RouteView` gera o contrato público, que expõe nomes de estações,
linhas e o `sentido` de cada trecho; e `PlanningState._build_instructions` agrupa
trechos em cartões `EMBARQUE`, `SIGA`, `BALDEAÇÃO`, `INTEGRAÇÃO` e `DESEMBARQUE`,
cada um como `dict[str, str]` com `step`, `kind`, `title`, `detail` e `meta`. Ver
`proposal.md` para a motivação.

Restrição desta entrega: o Xano não é alterado. A funcionalidade fica ligada por
padrão e pode ser desligada por variável de ambiente, sem mudar código.

## Goals / Non-Goals

**Goals:**

- Isolar as orientações do cálculo de trajeto, de modo que falhas nelas nunca
  bloqueiem o planejamento.
- Permitir ligar e desligar a funcionalidade sem mudar código.
- Manter a coleta rastreável, com fonte e data por registro.
- Exibir as orientações nos cartões existentes, sem novo fluxo de tela.

**Non-Goals:**

- Criar ou alterar tabelas, endpoints ou dados no Xano.
- Validar a veracidade das orientações além do formato; a qualidade depende da
  coleta registrada na fonte.

## Decisions

### Arquivo CSV local em vez de tabela no Xano

As orientações ficam em `docs/dados/orientacoes-estacoes.csv`, lidas pelo backend
Python. Nenhum recurso do Xano é criado ou alterado.

O `AGENTS.md` determina manter no Xano o cálculo de trajetos e os dados da malha.
As orientações não são dados da malha: não definem estações, linhas, trechos ou
tempos e não participam do cálculo. São conteúdo editorial de apresentação, ligado
a um trajeto já calculado pelo Xano. A escolha é temporária e reversível; quando os
dados estiverem validados, uma mudança futura poderá migrá-los para uma tabela no
Xano sem alterar a especificação, trocando apenas a origem atrás da mesma porta.

Alternativa considerada: tabela `orientacoes_estacao` e endpoint
`GET /orientacoes` no Xano. Foi adiada porque altera o ambiente remoto usado na
apresentação e depende de autorização do administrador do workspace.

### Interruptor por variável de ambiente

A funcionalidade fica ligada por padrão e só é desligada com
`METROFLOW_ORIENTACOES=0`. Desligada, o arquivo não é lido, o campo novo não
aparece na resposta e os cartões não mudam. O padrão segue o uso de variáveis já
adotado em `XANO_*_API_BASE_URL` e `METROFLOW_ENV`.

A primeira versão desta mudança nascia desligada e exigia
`METROFLOW_ORIENTACOES=1`. Em 26/10/2026 a decisão foi invertida a pedido do
grupo, para que as dicas apareçam sempre que o projeto rodar. O interruptor
permanece como forma de reversão imediata.

### Lado de desembarque como principal e observação livre

Colunas do CSV: `estacao`, `linha`, `sentido`, `lado_desembarque` (`esquerdo`,
`direito` ou `ambos`), `observacao` (texto livre de até 200 caracteres), `fonte` e
`data_coleta` (`AAAA-MM-DD`). Os nomes seguem o que o planejador exibe, por
exemplo `Palmeiras-Barra Funda`, `Linha 8 - Diamante` e `Júlio Prestes`.

O lado de desembarque é a informação mais fácil de verificar em campo, porque o
trem o anuncia, e por isso é o dado principal. Qualquer outra dica (carro mais
perto da escada, saída, caminho da baldeação, cuidado com a plataforma) vai para a
observação. O limite de 200 caracteres mantém o cartão legível.

Alternativa considerada: campos separados para carro recomendado, saída e
baldeação, com uma coluna `linha_destino` para dicas específicas de cada
baldeação. Foi descartada porque tornava a coleta lenta e rígida. O lado da porta
não depende da linha seguinte, então a chave fica restrita a estação, linha e
sentido; uma dica de baldeação é escrita na observação.

### Associação por nomes normalizados

A associação compara nomes normalizados (sem acentos, sem diferença de caixa e
com espaços e hífens uniformizados). O contrato público do trajeto só traz nomes,
e os códigos internos do Xano não estão documentados no repositório; usar nomes
evita depender de um dado que não podemos consultar sem alterar o contrato. Se um
nome mudar no Xano, a orientação simplesmente deixa de aparecer, o que é seguro.

### Leitura, validação e associação no backend Python

- **Infraestrutura:** um leitor de CSV devolve orientações normalizadas, descarta
  linhas inválidas individualmente e devolve lista vazia se o arquivo estiver
  ausente ou ilegível. Duplicatas são descartadas por inteiro. O arquivo é lido uma
  vez e mantido em memória enquanto o processo roda; para aplicar alterações,
  reinicia-se o `reflex run`, como já acontece com o código.
- **Aplicação:** uma função pura recebe `RouteResult` e as orientações e devolve a
  orientação de cada trecho final de etapa, pela estação de descida, linha e
  sentido. Integrações a pé ficam sem orientação.
- **Contrato público:** `SegmentView` ganha `guidance` opcional com
  `alighting_side` e `note`, ambos opcionais. Sem orientação ou com a
  funcionalidade desligada, o campo é omitido na serialização, mantendo a resposta
  idêntica à anterior.

Os logs registram apenas a quantidade de registros válidos e descartados, sem
conteúdo do arquivo nem dados de sessão.

### Apresentação no Reflex

Cada cartão de instrução recebe as chaves `side`, com o lado de desembarque em
destaque, e `note`, com a observação. Ambas são strings vazias quando não houver
orientação, e o componente só renderiza cada linha quando ela não estiver vazia.
Manter `dict[str, str]` evita mudar o tipo da variável de estado e o `rx.foreach`
existente.

As chaves são preenchidas nos cartões em que o passageiro desce do trem:
`BALDEAÇÃO`, `INTEGRAÇÃO` logo após uma etapa de trem e `DESEMBARQUE` final. O
texto de `side` é "Desembarque pelo lado esquerdo", "Desembarque pelo lado
direito" ou "As portas abrem dos dois lados".

### Planilha de referência gerada com apoio de IA

O inventário `base_estacoes_metro_trem_sp_inicial.xlsx` serve só como lista de
trabalho para a coleta. Ele não contém orientações verificadas e não é lido pela
aplicação.

## Risks / Trade-offs

- [Dado fictício ou não confirmado aparece para o usuário] → a coluna `fonte`
  registra a origem de cada dado, o guia de coleta orienta a substituição e
  `METROFLOW_ORIENTACOES=0` desliga a funcionalidade sem mudar código.
- [Nome de estação, linha ou sentido diverge do Xano] → normalização, teste com os
  nomes reais do piloto e ausência segura da orientação quando não houver
  correspondência.
- [Dado coletado errado ou desatualizado] → fonte e data obrigatórias por registro
  e exibição apenas dos campos preenchidos.
- [Observação livre com conteúdo impreciso ou longo] → fonte e data
  obrigatórias, limite de 200 caracteres e orientação de escrita no guia de coleta.
- [Desvio da diretriz de dados no Xano] → justificativa registrada nesta seção e
  migração prevista em mudança futura.

## Migration Plan

1. Implementar o leitor, a associação e a apresentação, ligados por padrão.
2. Preencher o CSV com a coleta em campo e validar com o teste da planilha.
3. Testar localmente com e sem `METROFLOW_ORIENTACOES=0`.
4. Reversão: definir `METROFLOW_ORIENTACOES=0`; nenhuma outra ação é necessária.
5. Futuro: migrar o CSV para uma tabela no Xano em nova mudança OpenSpec.
