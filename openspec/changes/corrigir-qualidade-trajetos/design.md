# Decisões

- O cálculo permanece no Xano. Busca, confirmação e cliente devem concordar sobre a cronologia.
- Não visitar duas vezes a mesma estação no percurso apresentado. Um trem regular ou corredor fechado não é uma partida programada: não circular por outras linhas para aguardar sua abertura. Serviços especiais com grade continuam podendo exigir espera legítima.
- Serviços regulares distinguem o sentido pela ordem das estações e a extensão Itapevi–Amador Bueno, que exige novo embarque. Não criar frequência fictícia para a extensão.
- A ocupação é confrontada com o intervalo previsto do candidato, mantendo sentido e exclusão da própria viagem. O denominador e os parâmetros de demonstração do Xano permanecem preservados.
- Uma alternativa por lotação pode acrescentar no máximo uma troca e um acréscimo de tempo limitado ao menor entre 10 minutos e 25% do principal, com tolerância mínima de 2 minutos para percursos curtos. Estes são critérios de produto versionados, não tempos oficiais. Se não houver alternativa dentro desses limites, manter o principal. Não simular o próximo trem sem frequência documentada.
- Se os caminhos compartilham um gargalo e não existe opção inteiramente livre dentro do limite, pode-se reduzir o tempo em trechos com ocupação prevista somente sem aumentar o tempo total nem a quantidade de trocas. Isso preserva alternativas equivalentes, como Turquesa/Coral antes de compartilhar a Diamante, sem inventar um desvio para fugir do trecho inevitável.
- Compatibilidade é explícita para novas trocas na mesma linha: clientes sem capacidade não recebem uma sequência que seu normalizador rejeitaria.
- Antes de publicar, exportar o estado atual, comparar com a base da edição, usar prévia de somente dois endpoints e reler código e tabelas. Não alterar tabelas nem enviar à main nesta entrega.
- Linha 6 não integra a implementação; permanece no fim das pendências, sem adicionar estações ou conexões agora.

# Validação

Reproduzir os 398 cenários da auditoria, acrescentar testes para ocupação futura e expirada, desvios excessivos, empate, sentido, repetição, extensão da Linha 8, fechamento e compatibilidade. Tempos sem fonte continuam pendentes e serão distinguidos dos ajustes efetivamente aplicados.
