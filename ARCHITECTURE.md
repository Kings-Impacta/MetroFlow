# Arquitetura do MetroFlow

O MetroFlow usa uma organização modular para manter a interface, as regras locais e as integrações externas separadas. O frontend é implementado com Reflex; o backend Python protege a sessão e adapta as respostas; o Xano armazena a malha e calcula o caminho.

```text
MetroFlow/
├── MetroFlow.py              composição da aplicação e registro de rotas
├── admin/
│   ├── domain/               indicadores, estações e suas invariantes
│   ├── application/          casos de uso e contrato com o Xano
│   ├── infrastructure/       cliente do grupo `administracao` do Xano
│   └── presentation/         API, estado e página do painel administrativo
├── auth/
│   ├── infrastructure/       cliente Xano e cookie de sessão
│   └── presentation/         API, estado e páginas de autenticação
├── planning/
│   ├── domain/               modelos e validações do resultado
│   ├── application/          casos de uso e contratos
│   ├── infrastructure/       cliente da API de planejamento do Xano
│   └── presentation/         API, estado, páginas e instruções de trajeto
└── status/                   status operacional informativo das linhas

tests/unit/                  testes por módulo e responsabilidade
docs/                        visão geral, domínio, integração e evidências
docs/dados/                  orientações de estação coletadas pelo grupo (CSV)
openspec/                    configuração, mudanças e especificações
```

## Fluxo de autenticação e planejamento

O usuário se autentica pelo Xano. O token permanece no backend e em cookie HttpOnly; a interface recebe apenas os dados públicos necessários. As páginas e os endpoints de planejamento exigem uma sessão válida. Uma resposta de sessão expirada remove o estado autenticado e conduz ao login.

O navegador consulta os endpoints locais `/api/planning/stations` e `/api/planning/route` e, após uma busca bem-sucedida, registra automaticamente a viagem em `/api/planning/trip`. O backend valida a sessão e os parâmetros, chama o Xano e normaliza a resposta. No registro, o navegador envia somente os trechos e o sentido percorrido; o Xano obtém o usuário pela sessão e o tempo pelo cadastro. O domínio local verifica invariantes do trajeto antes de apresentá-lo. A interface descarta resultados e confirmações de consultas antigas quando o usuário muda a seleção ou encerra a sessão.

## Painel administrativo

A página `/admin` usa o mesmo cookie HttpOnly. O navegador chama `/api/admin/indicators`, `/api/admin/stations` e `POST /api/admin/stations/{id}/status`; o backend repassa o token ao grupo `administracao` do Xano sem consultar `auth/me` antes, para gastar uma única requisição por operação. Cada endpoint do Xano repete as verificações de sessão da busca e confere a concessão em `administradores`.

O backend distingue 401 de 403. Com 401, a interface descarta os dados e conduz ao login. Com 403, mostra acesso restrito sem encerrar a sessão. Nenhuma resposta administrativa é guardada em cache, e erros do Xano chegam à interface só como mensagens genéricas.

O Xano apura os indicadores e grava a situação da estação junto com o histórico, na mesma transação. O backend valida e normaliza o contrato. Indicadores e estações são carregados separadamente, então uma falha nos indicadores não bloqueia a lista. Não há consulta periódica, para respeitar o limite de requisições do plano gratuito.

`auth/me` passa a informar `administrador`, usado apenas para mostrar o link no cabeçalho. A situação `ativa` da estação já era respeitada pela listagem, pela busca e pela confirmação, então o cálculo de trajetos não mudou.

## Cálculo e apresentação

O Xano escolhe pelo menor horário estimado de chegada: deslocamento, esperas de embarque e custos calibrados por combinação de transferência. O contrato legado conserva seus custos anteriores. Em empate, prefere menos serviços especiais e menos baldeações. A cronologia é compartilhada com o registro da viagem e distingue os trens da Linha 17 e da extensão da Linha 8. A concorrência compara intervalos previstos e respeita os limites descritos na [correção de qualidade dos trajetos](docs/xano/correcao-qualidade-trajetos-2026-10-29.md). O resultado também pode conter avisos públicos de acesso em integrações. Tempos genéricos e penalidade fixa continuam sendo estimativas, não medições.

Com a mudança `concorrencia-rotas`, publicada no Xano em 26/10/2026, a busca também estima a lotação de cada trecho ferroviário a partir das viagens confirmadas. Se o trajeto principal passar por um trecho lotado, o Xano devolve o caminho de menor tempo que o evita. A estimativa permanece no Xano e não faz parte da resposta pública.

## Orientações de estação (origem local temporária)

As orientações de estação, com o lado de desembarque como informação principal e uma observação adicional em texto livre, vêm do arquivo `docs/dados/orientacoes-estacoes.csv`, lido pelo backend Python, e não do Xano. A funcionalidade fica ligada por padrão; com `METROFLOW_ORIENTACOES=0`, a resposta e a interface permanecem como antes.

Essa origem local é uma decisão temporária. As orientações não são dados da malha: não definem estações, linhas, trechos ou tempos e não participam do cálculo, que continua no Xano. O backend associa as dicas a um trajeto já calculado, por nome normalizado de estação, linha e sentido, e qualquer falha na leitura devolve o trajeto sem elas. Uma mudança futura poderá migrar o cadastro para o Xano. O [guia de coleta](docs/dados/README.md) descreve o formato e o estado atual dos dados.

## Estação mais próxima (coordenadas locais temporárias)

As coordenadas das estações vêm do arquivo `docs/dados/coordenadas-estacoes.csv`, lido e validado pelo backend Python, e não do Xano. `GET /api/planning/stations` acrescenta `latitude` e `longitude` opcionais às estações com coordenada. A funcionalidade fica ligada por padrão; com `METROFLOW_LOCALIZACAO=0`, os campos ficam nulos e o planejador permanece como antes.

Quando há coordenadas, o planejador exibe o aviso "Encontrar a estação mais próxima de você?". A permissão de localização só é pedida no toque em "Usar minha localização". O cálculo ocorre no navegador: o script recebe apenas as coordenadas públicas das estações e devolve ao estado Reflex somente o identificador da estação mais próxima e a distância em linha reta. A posição do usuário não chega ao backend, ao Xano nem aos logs. A origem é preenchida pelo mesmo caminho da escolha manual, sem alterar a busca. Os navegadores só oferecem localização em HTTPS ou em `localhost`.

As coordenadas não participam do cálculo de trajetos. A origem local é temporária, e uma mudança futura poderá migrá-las para a tabela de estações do Xano.

O [modelo de domínio](docs/domain-model.md) detalha esses conceitos. As [evidências de validação](docs/validacao-integracao-xano.md) e a [auditoria complementar do Xano](docs/xano/auditoria-integridade-2026-10-08.md) registram o que foi verificado e os limites operacionais restantes. Registros históricos de implementação permanecem nesses documentos e no histórico do Git.

## Contrato calibrado publicado

O cliente da main declara suporte à calibração na API oficial. Busca e registro compartilham versão, padrões de trem e cronologia física; o registro aceita a referência por até 30 segundos e rejeita versão incompatível. Sem referência preenchida, o contrato legado permanece disponível. A margem de 60 segundos é aplicada somente ao total público, sem prolongar a ocupação.

A política de concorrência publicada em 09/11 admite redução parcial mínima de 40% da exposição, min(9 minutos, 45%) de acréscimo e uma baldeação extra; prefere percurso inteiramente pelo Metrô até um minuto mais lento que a alternativa elegível original. Os limites da alternativa totalmente livre permanecem separados, conforme o modelo de domínio. O [reteste real](docs/xano/publicacao-preferencia-metro-2026-11-09.md) confirmou os dois registros com a mesma versão e a alternativa por República.

O laboratório em loopback continua separado da API oficial. O status das linhas ainda não participa do cálculo; a integração informativa é uma entrega própria.


## Integração informativa inicial de status

O módulo `MetroFlow/status` adiciona endpoint e cache independentes; a consulta de condições operacionais não participa da busca ou da confirmação. Veja [status operacional](docs/status-operacional.md) para configuração, limites e ativação pendente.


Preparação posterior de 09/11: a fábrica de status seleciona somente Direto dos Trens (principal), CPTM (complemento) e o quadro Metrô como reserva explícita desativada. Credenciais e cache permanecem no backend; flags legadas ARTESP/Azure não disparam coleta. A requisição autenticada da principal usa transporte HTTPS dedicado sem exposição em logs ou URLs públicas. Aguardam-se token e validação real, sem alteração no Xano.


## Entrega de status em 11/11/2026

A configuração local validada usa Metrô, CPTM e Motiva, com 12 linhas observadas e preservação do último retorno. O iniciador portátil fica na raiz do projeto. A API Direto dos Trens aguarda token. Fontes continuam desativadas por padrão e não participam do cálculo nem do registro de viagens. Consulte o guia de status para a configuração e os limites atuais.
