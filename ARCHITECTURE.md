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
openspec/                    configuração, mudanças e especificações
```

## Fluxo de autenticação e planejamento

O usuário se autentica pelo Xano. O token permanece no backend e em cookie HttpOnly; a interface recebe apenas os dados públicos necessários. As páginas e os endpoints de planejamento exigem uma sessão válida. Uma resposta de sessão expirada remove o estado autenticado e conduz ao login.

O navegador consulta os endpoints locais `/api/planning/stations` e `/api/planning/route` e confirma viagens em `/api/planning/trip`. O backend valida a sessão e os parâmetros, chama o Xano e normaliza a resposta. Na confirmação, o navegador envia somente os trechos e o sentido percorrido; o Xano obtém o usuário pela sessão e o tempo pelo cadastro. O domínio local verifica invariantes do trajeto antes de apresentá-lo. A interface descarta resultados de consultas antigas quando o usuário muda a seleção ou encerra a sessão.

## Cálculo e apresentação

O Xano escolhe o caminho pelo menor tempo estimado: soma dos tempos dos trechos mais 600 segundos por mudança de linha. Em empate, prioriza menos baldeações. O resultado apresenta estações, linhas, operadores, sentidos e instruções de viagem. A penalidade fixa não representa tempos reais de caminhada, espera ou transferência.

Com a mudança `concorrencia-rotas`, publicada no Xano em 26/10/2026, a busca também estima a lotação de cada trecho ferroviário a partir das viagens confirmadas. Se o trajeto principal passar por um trecho lotado, o Xano devolve o caminho de menor tempo que o evita. A estimativa permanece no Xano e não faz parte da resposta pública.

O [modelo de domínio](docs/domain-model.md) detalha esses conceitos. As [evidências de validação](docs/validacao-integracao-xano.md) e a [auditoria complementar do Xano](docs/xano/auditoria-integridade-2026-10-08.md) registram o que foi verificado e os limites operacionais restantes. Registros históricos de implementação permanecem nesses documentos e no histórico do Git.
