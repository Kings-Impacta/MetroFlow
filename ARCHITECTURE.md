# Arquitetura do MetroFlow

O MetroFlow usa uma organização modular para manter a interface, as regras locais e as integrações externas separadas. O frontend é implementado com Reflex; o backend Python protege a sessão e adapta as respostas; o Xano armazena a malha e calcula o caminho.

```text
MetroFlow/
├── MetroFlow.py              composição da aplicação e registro de rotas
├── auth/
│   ├── infrastructure/       cliente Xano e cookie de sessão
│   └── presentation/         API, estado e páginas de autenticação
└── planning/
    ├── domain/               modelos e validações do resultado
    ├── application/          casos de uso e contratos
    ├── infrastructure/       cliente da API de planejamento do Xano
    └── presentation/         API, estado, páginas e instruções de trajeto

tests/unit/                  testes por módulo e responsabilidade
docs/                        visão geral, domínio, integração e evidências
docs/dados/                  orientações de estação coletadas pelo grupo (CSV)
openspec/                    configuração, mudanças e especificações
```

## Fluxo de autenticação e planejamento

O usuário se autentica pelo Xano. O token permanece no backend e em cookie HttpOnly; a interface recebe apenas os dados públicos necessários. As páginas e os endpoints de planejamento exigem uma sessão válida. Uma resposta de sessão expirada remove o estado autenticado e conduz ao login.

O navegador consulta os endpoints locais `/api/planning/stations` e `/api/planning/route` e, após uma busca bem-sucedida, registra automaticamente a viagem em `/api/planning/trip`. O backend valida a sessão e os parâmetros, chama o Xano e normaliza a resposta. No registro, o navegador envia somente os trechos e o sentido percorrido; o Xano obtém o usuário pela sessão e o tempo pelo cadastro. O domínio local verifica invariantes do trajeto antes de apresentá-lo. A interface descarta resultados e confirmações de consultas antigas quando o usuário muda a seleção ou encerra a sessão.

## Cálculo e apresentação

O Xano escolhe pelo menor horário estimado de chegada: deslocamento, esperas de embarque e custos calibrados por combinação de transferência. O contrato legado conserva seus custos anteriores. Em empate, prefere menos serviços especiais e menos baldeações. A cronologia é compartilhada com o registro da viagem e distingue os trens da Linha 17 e da extensão da Linha 8. A concorrência compara intervalos previstos e respeita os limites descritos na [correção de qualidade dos trajetos](docs/xano/correcao-qualidade-trajetos-2026-10-29.md). O resultado também pode conter avisos públicos de acesso em integrações. Tempos genéricos e penalidade fixa continuam sendo estimativas, não medições.

Com a mudança `concorrencia-rotas`, publicada no Xano em 26/10/2026, a busca também estima a lotação de cada trecho ferroviário a partir das viagens confirmadas. Se o trajeto principal passar por um trecho lotado, o Xano devolve o caminho de menor tempo que o evita. A estimativa permanece no Xano e não faz parte da resposta pública.

## Orientações de estação (origem local temporária)

As orientações de estação, com o lado de desembarque como informação principal e uma observação adicional em texto livre, vêm do arquivo `docs/dados/orientacoes-estacoes.csv`, lido pelo backend Python, e não do Xano. A funcionalidade fica ligada por padrão; com `METROFLOW_ORIENTACOES=0`, a resposta e a interface permanecem como antes.

Essa origem local é uma decisão temporária. As orientações não são dados da malha: não definem estações, linhas, trechos ou tempos e não participam do cálculo, que continua no Xano. O backend associa as dicas a um trajeto já calculado, por nome normalizado de estação, linha e sentido, e qualquer falha na leitura devolve o trajeto sem elas. Uma mudança futura poderá migrar o cadastro para o Xano. O [guia de coleta](docs/dados/README.md) descreve o formato e o estado atual dos dados.

O [modelo de domínio](docs/domain-model.md) detalha esses conceitos. As [evidências de validação](docs/validacao-integracao-xano.md) e a [auditoria complementar do Xano](docs/xano/auditoria-integridade-2026-10-08.md) registram o que foi verificado e os limites operacionais restantes. Registros históricos de implementação permanecem nesses documentos e no histórico do Git.

## Contrato calibrado publicado

O cliente da main declara suporte à calibração na API oficial. Busca e registro compartilham versão, padrões de trem e cronologia física; o registro aceita a referência por até 30 segundos e rejeita versão incompatível. Sem referência preenchida, o contrato legado permanece disponível. A margem de 60 segundos é aplicada somente ao total público, sem prolongar a ocupação.

A política de concorrência publicada em 09/11 admite redução parcial mínima de 40% da exposição, min(9 minutos, 45%) de acréscimo e uma baldeação extra; prefere percurso inteiramente pelo Metrô até um minuto mais lento que a alternativa elegível original. Os limites da alternativa totalmente livre permanecem separados, conforme o modelo de domínio. O [reteste real](docs/xano/publicacao-preferencia-metro-2026-11-09.md) confirmou os dois registros com a mesma versão e a alternativa por República.

O laboratório em loopback continua separado da API oficial. O status das linhas ainda não participa do cálculo; a integração informativa é uma entrega própria.
