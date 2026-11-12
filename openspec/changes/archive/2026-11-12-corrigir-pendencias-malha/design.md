## Context

Comparar a função publicada usando exportação anterior e posterior, sem viagens
ativas e com viagens controladas. Guardar o workspace antes de qualquer publicação.
Publicar somente os endpoints selecionados via Xano CLI após dry-run.

## Decisions

- Preservar os 207 IDs de trechos e as chaves canônicas; mudar apenas sufixos dos
  serviços onde o vínculo estava ausente. Criar índice por endpoint específico.
- Brás fica na ordem 3 do Expresso, entre Luz e Cecap; as direções continuam
  determinadas pelos segmentos direcionados, inclusive no retorno via Brás.
- A disponibilidade vem das tabelas existentes. Segmentos sem serviço conservam
  seu comportamento. Serviço sem cadastro ativo ou janela válida fica indisponível.
- Usar início inclusivo e fim exclusivo; 00:00 como fim significa 24h. Janelas
  atravessando a meia-noite respeitam o dia em que começaram.
- Considerar o instante da consulta, não prever a chegada ao embarque. Horários
  de partidas, intervalos e interrupções operacionais permanecem fora do cálculo.
- O calendário explícito de feriados de São Paulo cobre 2026; pontos facultativos
  não são feriados. Serviços que não operam em feriado exigem calendário conhecido;
  fora da vigência ficam indisponíveis até revisão. Feriados locais do ABC e
  alterações excepcionais precisam de confirmação específica da operadora.

Na continuação, a lista fixa de 2026 é substituída pelo cálculo dos feriados
recorrentes de São Paulo para 2026–2099: datas fixas e Sexta-feira Santa/Corpus
Christi a partir da Páscoa gregoriana. Isso evita desabilitar o serviço em todos
os dias de 2027. Não é uma previsão de decretos futuros; mudanças legais, feriados
excepcionais, feriados do ABC e esquemas da operadora continuam exigindo revisão.

O PDF do Expresso L10 ligado pela página atual da CPTM foi baixado e conferido
visualmente. A grade com parada em São Caetano tem janelas diferentes por sentido:
Santo André → Tamanduateí, 05:40–09:00 e 16:10–19:50; Tamanduateí → Santo André,
05:50–08:50 e 16:00–20:00. A seleção por minuto inclui a última partida (fim da
janela um minuto depois); as partidas intermediárias não são tratadas como serviço
contínuo real nem geram previsão de espera. A confirmação valida o mesmo sentido.
O PDF não fornece duração e também documenta voltas sem São Caetano: os tempos
de 90 s e a falta de arestas diretas permanecem pendências, sem inventar custos.
- As janelas antigas do Expresso Linha 10 permanecem configuração conservadora
  do projeto (06h–09h e 16h–19h em dias úteis); as fontes confirmam operação de pico,
  mas não certificam essa grade exata atual. Não alterar os tempos de 90 s sem fonte.
- A Linha 17 recebe o horário oficial ampliado de segunda a sábado, 06h–22h.
- Nenhum novo trecho de caminhada é necessário em Brás: o ID compartilhado já
  permite a troca. Não acrescentar custo de caminhada aos 600 s sem separar componentes.

## Risks / Trade-offs

A continuação corrige o ramal da Linha 17 segundo o comunicado do Metrô de
29/09/2026. O trecho 200 mantém ID, duração, serviço e bidirecionalidade, mas muda
origem de Congonhas (181) para Brooklin Paulista (180); a chave passa a
`B:180:182:14:3`. O sentido crescente do tronco passa a Congonhas, e o ramal indica
Washington Luís na ida e Brooklin Paulista na volta.

O estado de busca inclui o serviço de trem: tronco e ramal são estados distintos
da mesma linha. Trocar entre eles conta uma baldeação e os mesmos 600 s estimados
usados nas demais trocas. `baldeacoes` pode ter linhas anterior/seguinte iguais;
o contrato existente comporta isso e a interface usa sentidos diferentes para
separar as etapas. Ajustar a mensagem para troca de trem, sem inventar outra linha.

O cliente atualizado envia `suporta_troca_mesma_linha=true`. O padrão do endpoint
é false para não devolver a clientes antigos uma resposta rejeitada pelo seu
normalizador. Esses clientes continuam recebendo as rotas regulares e a viagem
direta Brooklin–Washington; rotas com troca dentro da linha exigem atualização do
cliente. Nenhuma rota que exigia a ligação inexistente via Congonhas é preservada.

As alternativas Vermelha–Amarela–Verde e via Pinheiros já pertencem ao grafo.
Comparar sem lotação, com bloqueio controlado da rota principal e com tempos
controlados em testes. A regra fixa de 600 s e a caminhada de 180 s não medem a
espera real; não recalibrar tempos só para obter uma preferência desejada.

O filtro horário altera rotas quando o serviço está fechado, como pretendido.
Preservar os parâmetros de lotação e seus testes. Conferir que dados sensíveis
não aparecem nas evidências. Não substituir esquemas com PUT de xanoscript.

## Migration Plan

1. Backup de sete tabelas, esquema e endpoints; comparação de estado.
2. Testes de dados e comportamento com relógio controlado.
3. Atualizar conteúdo com campos explícitos, índice dedicado e publicação transacional.
4. Reler dados e código, repetir auditoria e trajetos de referência, registrar limites.

## Decisão final de escopo — 12/11/2026

Entrega encerrada com escopo reduzido, por autorização do usuário. As pendências não executadas foram retiradas do compromisso atual e preservadas como melhorias futuras em `docs/melhorias-futuras-malha-status.md`; consulte também as limitações no checklist. O texto anterior preserva a proposta e as decisões históricas, não representa certificação de todas as hipóteses nem garantia de disponibilidade pública. Esta revisão é somente documental.
