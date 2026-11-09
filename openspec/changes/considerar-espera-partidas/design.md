## Decisions

- O relógio e o cálculo continuam no Xano, no fuso America/Sao_Paulo.
- O catálogo versionado de horários é publicado dentro das funções Xano. Fontes,
  data de conferência e limitações permanecem no repositório.
- Horários oficiais de terminal mais tempos cadastrados geram estimativas de
  passagem intermediária, não informação operacional em tempo real. Não completar
  partidas ausentes por suposição, como 13h30 de domingo na tabela do Expresso.
- Grades terminais e dias de serviço são validados contra cadastros ativos. Um
  trem já embarcado pode concluir seu percurso depois da última partida; uma nova
  conexão exige disponibilidade própria. Não esperar até o próximo dia de serviço
  quando isso ultrapassar duas horas.
- O estado da busca preserva o serviço e a viagem embarcada. Rótulos não dominados
  conservam opções que chegam depois a uma conexão, mas empatam após a espera com
  menos serviços especiais. Não resolver esse desempate por ordem de retorno do banco.
- Serviços sem grade regular de partidas não recebem um horário fictício. A espera
  desses trens continua desconhecida; mantém-se o valor-base de comparação e isso
  é documentado. A Linha 17 usa espera média de 270 s pelo intervalo publicado de 9 min.
- A penalidade atual de baldeação continua 600 s, sem recalibrar a malha para forçar
  uma alternativa. Espera é contabilizada depois da transferência.
- A resposta detalhada usa `suporta_espera_partidas=true`; clientes anteriores
  recebem espera incorporada em `tempo_estimado`, sem quebrar a soma antiga.
- O registro aceita `calculado_em` opcional, emitido na busca e válido por 30 s,
  limitado ao passado recente do servidor. Todos os tempos são recalculados da
  sequência e do cadastro, sem confiar em espera/duração fornecidas pelo usuário.
- Os novos trechos de viagem têm instantes previstos de início; registros antigos
  mantêm o cálculo legado. Sessão e substituição da viagem anterior são preservadas.

## Validation

Comparar malha antes/depois em dias úteis, sábado, domingo e feriados; perto das
aberturas, últimas partidas e meia-noite; atrasos em estações intermediárias;
desempates, confirmação e concorrência. Guardar exportação antes de publicar,
usar dry-run apenas dos dois endpoints e reler o código publicado e os dados.
