## Contexto

Histórico consultado em 17/11: operações administrativas 200 normalmente abaixo de um segundo, com registros lentos de 43,432 a 202,092 segundos. Isso comprova latência observada, não a causa interna do fornecedor. Não há evidência de revogação nas chamadas examinadas.

## Decisões

O backend pode fazer no máximo duas tentativas de GET, separadas por um segundo, somente em timeout/falha de conexão ou HTTP 502/503/504 sem Retry-After. Toda tentativa volta ao endpoint autenticado do Xano. Sem cache de autorização, sem token no log, sem mudança de timeout ou repetição infinita. 401/403/429, falha de contrato e todas as mutações terminam imediatamente. Em indisponibilidade persistente, a página não mostra dados protegidos antes de uma resposta autorizada e mantém ação manual de recuperação. A origem lenta pode continuar processando um GET após timeout; o limite evita multiplicação ilimitada. Os dois carregamentos existentes permanecem independentes.

## Validação

Transporte simulado para recuperação, limite de tentativas, recusa/revogação, Retry-After, POST não repetido e contrato inválido. Testes de estado e página para preservação dos controles de acesso. Reproduzir offline a busca/registro publicados com dados reais, sem criar viagens ou modificar produção. Teste real do cliente corrigido depende da instalação e reinício da versão validada.
