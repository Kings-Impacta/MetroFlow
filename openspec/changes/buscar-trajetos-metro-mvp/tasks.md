## 1. Dados e estrutura no Xano

- [ ] 1.1 Definir e documentar o modelo de dados necessário para representar estações, linhas, conexões entre estações e pontos de baldeação; verificar os relacionamentos entre essas informações.

- [ ] 1.2 Definir como será armazenado o tempo estimado de percurso de cada trecho da rede, garantindo que os dados necessários para calcular o trajeto principal estejam disponíveis.

- [ ] 1.3 Inserir um conjunto inicial de estações, linhas, conexões e tempos estimados para permitir testes com trajetos de uma única linha e de múltiplas linhas.

## 2. Lógica de busca do trajeto no Xano

- [ ] 2.1 Implementar a lógica responsável por encontrar caminhos válidos entre a estação de origem e a estação de destino.

- [ ] 2.2 Implementar o critério de seleção do trajeto principal, priorizando o caminho com menor tempo estimado total.

- [ ] 2.3 Implementar o critério de desempate para que, quando dois ou mais trajetos tiverem o mesmo tempo estimado, seja escolhido aquele com menor quantidade de baldeações.

- [ ] 2.4 Validar a lógica com exemplos de trajetos de uma única linha, trajetos com baldeação, trajetos com tempos diferentes e trajetos com mesmo tempo estimado.

## 3. APIs do Xano

- [ ] 3.1 Criar e documentar o endpoint de listagem de estações disponíveis para seleção no frontend.

- [ ] 3.2 Criar e documentar o endpoint de consulta de trajeto utilizando estação de origem e estação de destino como parâmetros.

- [ ] 3.3 Definir o contrato de resposta da consulta contendo origem, destino, estações percorridas, trechos, linhas utilizadas, pontos de baldeação, tempo total estimado e quantidade de baldeações.

- [ ] 3.4 Definir respostas para consulta bem-sucedida, ausência de trajeto, parâmetros inválidos e falha no serviço; verificar o contrato utilizando exemplos JSON.

## 4. Integração e modelo de domínio no Reflex

- [ ] 4.1 Criar o adaptador de API no frontend Reflex para carregar estações e solicitar trajetos sem expor diretamente à interface o formato bruto retornado pelo Xano.

- [ ] 4.2 Criar os modelos normalizados de estação, trecho, linha, baldeação e resultado de trajeto; incluir tempo total estimado e quantidade de baldeações.

- [ ] 4.3 Implementar os estados da busca `idle`, `loading`, `success`, `not_found` e `error`, incluindo limpeza ou substituição do resultado anterior durante uma nova consulta.

- [ ] 4.4 Validar origem e destino antes da chamada ao Xano, rejeitando campos ausentes e origem igual ao destino.

## 5. Fluxo de interface Reflex

- [ ] 5.1 Implementar os controles para carregar e selecionar a estação de origem e a estação de destino.

- [ ] 5.2 Implementar a ação de solicitar o trajeto, mostrando o estado de carregamento e evitando solicitações duplicadas durante uma consulta.

- [ ] 5.3 Renderizar o trajeto principal com a sequência ordenada de estações, linhas utilizadas, pontos de baldeação e tempo estimado.

- [ ] 5.4 Renderizar mensagens diferentes para seleção inválida, ausência de trajeto e falha no serviço, permitindo nova tentativa quando necessário.

- [ ] 5.5 Garantir que uma nova consulta substitua corretamente o resultado anterior.

- [ ] 5.6 Garantir que esta versão não calcule nem exiba nível de lotação ou rotas alternativas.

## 6. Testes e validação

- [ ] 6.1 Criar testes para seleção incompleta e origem igual ao destino.

- [ ] 6.2 Criar testes para trajetos de uma única linha e trajetos com baldeação.

- [ ] 6.3 Criar testes confirmando que, entre trajetos com tempos diferentes, o sistema seleciona aquele com menor tempo estimado.

- [ ] 6.4 Criar testes confirmando que, em caso de empate no tempo estimado, o sistema seleciona o trajeto com menor quantidade de baldeações.

- [ ] 6.5 Criar testes para ausência de trajeto, erro do serviço e respostas incompletas da API.

- [ ] 6.6 Executar uma validação integrada entre Reflex e Xano utilizando dados de teste e verificar o fluxo completo de seleção, consulta e apresentação do trajeto.

- [ ] 6.7 Executar a aplicação Reflex e validar manualmente no navegador os principais cenários do MVP antes da entrega.