# Correção local da consulta ao Metrô

## Diagnóstico

A investigação de 10/11 reproduziu timeout de leitura HTTP com o limite de cinco segundos. Não foi ausência de linhas nem incompatibilidade do parser: consultas bem-sucedidas ao mesmo quadro oficial retornaram HTTP 200 e as sete linhas previstas.

O transporte padrão escolheu IPv6. Na comparação rastreada, uma resposta IPv6 levou 3,469 segundos e outra por IPv4 levou 0,281 segundo. Porém, um timeout também ocorreu por IPv4: a família de conexão não explica sozinha toda a variação da origem. Por isso o ajuste combina IPv4 com uma tolerância de leitura específica para o Metrô, sem prometer disponibilidade contínua do site.

## Alteração

Somente o adaptador Metrô utiliza conexão de saída IPv4, com DNS normal para o hostname oficial, conexão de até cinco segundos e leitura de até quinze segundos por operação. O limite de tamanho permanece 500 kB e o orçamento verificado durante a leitura passa a vinte segundos. HTTPS, validação do certificado, ausência de redirecionamentos e isolamento de variáveis de proxy são preservados. Não foi desabilitado IPv6 no computador nem fixado IP remoto.

CPTM e Motiva mantêm suas configurações anteriores. Nenhuma repetição imediata de GET foi adicionada. Falhas respeitam o próximo ciclo e preservam o último retorno e seu horário. Os logs indicam a fonte e a categoria segura (por exemplo, read_timeout), sem registrar credenciais, payloads ou URLs autenticadas.

Busca, malha, registro e concorrência não foram alterados. O resultado compacto permanece sem sufixo de idade, conforme a decisão do usuário; a validade interna e os horários continuam preservados.

## Validação local concluída em 11/11

- Consulta real pela fábrica de fontes e cache corrigidos: L1, L2, L3, L4, L5, L15 e L17 atuais, em aproximadamente 0,5 segundo.
- Uma única chamada real; segunda leitura reutilizou o cache e manteve os horários de coleta.
- Após um dia de falha simulada em cache isolado, os sete últimos retornos e suas datas foram preservados.
- Suíte completa: 282 testes e 86 subtestes passaram, incluindo busca, registro e concorrência.
- Testes específicos de transporte conferiram IPv4 somente no Metrô, certificado obrigatório, limites de conexão/leitura e ausência de repetição do GET em timeout.
- Compilação Reflex e os 12 itens OpenSpec passaram; permanecem apenas os avisos existentes de depreciação e consulta não fatal de CPU.

O relatório real e a simulação estão em `outputs/demo-status-aula-20261109/validacao-correcao-metro.json`, na raiz do chat. Esse cache é separado do cliente em uso. Não houve acesso ao Xano, mudança de dados ou publicação nesta validação.

O cliente em execução precisa ser reiniciado pelo iniciador local existente para carregar o novo transporte. A confirmação no cliente reiniciado e um novo teste com duas contas reais não são substituídos pela suíte automatizada. A origem ainda pode falhar; nessa situação, os últimos dados devem continuar visíveis.

## Confirmação posterior no cliente reiniciado — 11/11

Na aba autenticada, as sete linhas apareceram atuais com coleta às 11:35. O cache registrou outra coleta válida às 11:40. Um monitor temporário do painel foi então deixado aberto, sem clicar em Atualizar ou refazer buscas, e as sete linhas avançaram automaticamente para coleta às 11:46. As três observações não registraram falha do adaptador Metrô. A captura `outputs/demo-status-aula-20261109/metro-atualizacao-automatica-20261111.jpg`, na raiz do chat, registra o painel após a renovação.

A conta interna mostrou Palmeiras-Barra Funda → Sé → Paraíso pelas linhas 3 e 1, com 22 minutos estimados e os indicadores compactos. O usuário realizou o teste nas duas contas e informou que a outra recebeu o caminho pelas linhas 4 e 2. O primeiro resultado foi observado diretamente; o segundo foi confirmado pelo relato do usuário. Não foram auditados nesta rodada IDs, sobreposição ou versão de registros diretamente no Xano.

Não foi provocada uma queda real na sessão em uso. A retenção em falha prolongada permanece comprovada pela simulação isolada descrita acima e pelos testes. O monitor temporário foi fechado, preservando a aba do usuário com seu trajeto. Não houve nova alteração de código, malha, configuração remota ou publicação nesta conferência.
