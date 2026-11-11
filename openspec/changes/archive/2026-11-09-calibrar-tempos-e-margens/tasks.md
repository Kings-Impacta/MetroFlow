- [x] Registrar autorização e condição de cobertura antes da publicação.
- [x] Gerar inventário local por trecho/sentido, espera e par de linhas.
- [x] Preservar referências GTFS, observações parciais e fontes oficiais adicionais.
- [x] Guardar candidatos dos sete sentidos do Expresso e modelos de esperas e baldeações, com limitações explícitas.
- [x] Executar ensaio combinado local de 880 casos e cinco verificações de espera, sem margem nem publicação; cobertura operacional continua pendente.
- [x] Separar faixa noturna até 04h40, guardar cenário histórico da Linha 13 e oito combinações de Paraíso, com 16 testes direcionados antes/depois; demais plataformas e tempos uniformes continuam pendentes.
- [x] Guardar 50 sentidos candidatos das linhas 11/15, perfis da Linha 12, alcance parcial da Linha 10 e 20 combinações de plataforma; simular corredor sem cobrança duplicada e testar alcance/fim de pico localmente. Cobertura e contrato de registro continuam pendentes.
- [x] Separar agregado até Guaianases do integral, guardar cenários das linhas 3/4 e 64 combinações por sentido; executar 22 testes novos e repetir regressões. Cobertura operacional permanece incompleta.
- [x] Guardar cenários históricos/programados das linhas 1/2/5 e desdobrar Santa Cruz/Chácara Klabin; inventário com 229 sentidos modelados e 76 combinações, ainda sem aprovação operacional ou publicação.
- [x] Completar referências e resolver conflitos dos intervalos prioritários no escopo de estimativas aprovado.
- [x] Modelar os percursos internos das 320 combinações por chegada/saída e os corredores, incluindo ramais, com geometria disponível e hipóteses explícitas; não exigir estado de elevadores para essa cobertura numérica.
- [x] Completar a cobertura estimada de esperas por serviço, faixa, dia, feriado e estação de embarque da malha ativa modelada.
- [x] Selecionar tempos-base e estados de confiança para toda a cobertura da entrega.
- [x] Corrigir regra para 60 s uma vez no total e aceitar estimativas fundamentadas sem comprovação documental integral.
- [x] Explicitar variação por condições externas no tempo estimado da interface local.
- [x] Implementar margem única de 60 s no total público, sem duplicação no cliente ou registro e sem alteração de partidas.
- [x] Simular e testar itinerários, partidas finais, percursos internos e concorrência antes/depois; disponibilidade de elevadores e certificação de acessibilidade fora do escopo aprovado.
- [x] Validar contrato, preparar backup e publicar ajustes coerentes no Xano e no cliente (PR #37 e entrega de 05/11).
- [x] Reler e validar a publicação, incluindo alcance parcial e horários estimados da Linha 6; documentar o teste real de concorrência de 09/11.

- [x] Guardar os 178 sentidos restantes, totalizando 407 modelos numéricos, e expandir para 320 combinações candidatas de troca; simular 880 casos, 88 verificações direcionadas/regressões e 18 sensibilidades, sem publicação ou margem. Cobertura operacional, seleção de valores e contrato de registro permanecem pendentes.

- [x] Separar candidatos integrais/agregados L7/8/9, confrontar quatro hipóteses em 40 comparações e gerar reprodução do registro com a mesma preparação temporal da busca: 34 casos alinhados, nove rejeições, adulteração ignorada e quatro cenários com usuários simulados. Integração do contrato ao cliente/backend, frequência atual e aprovação operacional permanecem pendentes.

- [x] Separar perfis candidatos por dia e frequência integral até Varginha, preservando exceções datadas; integrar referência opcional de calibração no domínio/API/estado/cliente com bloqueio remoto. Validar 22 fluxos completos e 24 limites temporais, 80 testes e compilação seca. Cobertura operacional, ativação e publicação continuam pendentes.

- [x] Executar na cópia exceções datadas L9 de 08/05, 20/05 e 03–04/10 com alcance e transição de embarque; informar risco de último trem na Linha 17 sem alterar tempo ou ocupação. Validar 880 cenários, 42 casos direcionados/35 registros normalizados e 24 regressões temporais. Cobertura global, publicação e Linha 6 permanecem na ordem condicionada pelo usuário.

- [x] Guardar cenário de circulação assistida para 320 combinações e dois corredores, com 27 estações inventariadas e disponibilidade de equipamentos desconhecida; simular interdições L10/L11 de Finados e conexão datada por plataforma. Validar 640 custos, 58 comparações, 46 registros e oito cenários de concorrência; corrigir contagem duplicada no corredor. Acessibilidade autônoma, cobertura física completa e revisão final permanecem pendentes, sem publicação.

- [x] Rever 106 tempos de circulação interna, preservar todos os anteriores e comparar corredores via Sé, República/Paulista e Pinheiros. Validar 640 custos, 28 rotas/registros, oito cenários de concorrência, 880 execuções gerais e 42 regressões de exceções. Iniciar depois o inventário oficial da Linha 6, sem incluir estações/conexões projetadas no grafo atual.

- [x] Verificar o trecho em operação assistida da Linha 6 e guardar horários, referências de frequência e estimativas dos cinco trechos nos dois sentidos. Simular 25 cenários, 17 registros, 16 comparações de regressão e dois cenários de concorrência. A validação da última partida e o fechamento da cobertura integrada continuam pendentes.

- [x] Fechar a cobertura estimada da malha ativa em cópia local. Guardar as referências e estimar a última passagem da Linha 6 em dez pontos de embarque por estação e sentido. Verificar 419 sentidos com tempo positivo, embarque para os 415 sentidos ferroviários, 32 comparações de encerramento, 39 cronologias de registro e os 440 cenários de referência. Margem e publicação ficam para etapa própria.


## Fechamento em 09/11/2026

As ressalvas de cobertura pendente nos registros intermediários acima são históricas. A entrega atual aceita estimativas e não promete medições exatas. Publicação, versão e teste real estão em `docs/xano/publicacao-preferencia-metro-2026-11-09.md`; verificações complementares em `docs/xano/fechamento-trajetos-concorrencia-2026-11-09.md`.

## Revisão para arquivamento em 11/11/2026

Escopo concluído e publicado; os testes de entrega e a auditoria dos registros 67/68 são descritos em `docs/xano/reteste-main-status-concorrencia-2026-11-11.md`. Pendências de validação remota geral e de dados adicionais permanecem nas mudanças próprias, sem serem marcadas como concluídas aqui.

## Datas de conclusão e atualização

- Última atualização versionada anterior à revisão de arquivamento: **09/11/2026**, commit `6f0a998` (PR #39), que contém o fechamento e as evidências de publicação/validação. Esta é a data usada no diretório de arquivo por solicitação do usuário.
- Revisão documental e movimentação física para `archive`: **11/11/2026**. Essa revisão não é uma nova data de implementação ou publicação. Correções documentais de limites e contexto feitas na revisão não foram retrodatadas.
- Publicação da calibração/cliente: **05/11/2026**; atualização da preferência pelo Metrô e reteste com duas contas: **09/11/2026**. Fonte: `docs/xano/publicacao-preferencia-metro-2026-11-09.md`.
