# Lacunas de cobertura e margem solicitada — 03/11/2026

## Resultado do inventário

Sim, ainda faltam intervalos e componentes para seleção de estimativas concretas. A coleta não está pronta para publicação. O usuário autorizou guardar dados parciais e, **depois de completar a cobertura e simular**, acrescentar um único minuto ao trajeto total e integrar ao Xano e ao projeto. Não exige comprovação documental integral. A autorização corrigida está em `openspec/changes/calibrar-tempos-e-margens/`, com publicação pendente e Linha 6 adiada.

O inventário local usa a exportação do Xano de 01/11/2026 e o GTFS preservado nessa data; não é leitura remota de 03/11. Nenhuma tabela ou função do Xano foi alterada. As observações e candidatos anteriores foram preservados.

| Componente | Unidades inventariadas | Estado |
| --- | --- | --- |
| Deslocamento por trecho e sentido | 407: 405 ferroviários e 2 direções do corredor a pé | 391 têm alguma referência externa; 16 não têm referência individual |
| Possibilidade de embarque | 405, por estação de origem, serviço e próxima estação | Todas têm alguma referência de linha ou GTFS; nenhuma grade completa foi aprovada por estação/faixa/dia |
| Trocas candidatas | 128, incluindo expressos, quatro trocas de ramal e dois sentidos do corredor | Só República L4→L3 tem observação por marcos; Paulista→Consolação tem segmento parcial; outras 126 ainda sem duração específica nessa classificação |

Os números não representam cobertura validada. Há 376 deslocamentos regulares com referência GTFS aproximada, 14 direções da Linha 17 com referência GTFS conflitante e uma direção do corredor com vídeo parcial. Os relatos históricos adicionais permanecem associados quando correspondem exatamente ao intervalo e sentido. Os horários uniformes do GTFS foram preservados como referência programada, sem reclassificação como medição real.

As 128 trocas são uma lista de pesquisa gerada das linhas incidentes e dos ramais. Nem todo par tem caminho físico e acesso direto confirmados; faltam desdobramentos de plataformas, sentidos e acessibilidade. Paraíso e outras estações podem exigir tempos distintos dentro do mesmo par de linhas. A matriz deve ser expandida, e não usada como tabela de 128 caminhadas prontas.

## Prioridades das lacunas

Os 16 sentidos sem referência externa individual são:

| Grupo | Intervalos |
| --- | --- |
| Extensão da Linha 8 — quatro sentidos | Santa Rita ↔ Ambuitá; Ambuitá ↔ Amador Bueno |
| Expresso Linha 10 — quatro sentidos | Tamanduateí ↔ São Caetano; São Caetano ↔ Santo André |
| Expresso Aeroporto — sete sentidos distintos | Barra Funda → Luz; Luz → Cecap; Cecap → Aeroporto; Aeroporto → Cecap; Cecap → Brás; Brás → Luz; Luz → Barra Funda |
| Corredor — um sentido | Consolação → Paulista |

Não repartir uma duração total do expresso entre paradas nem copiá-la no retorno, pois as paradas e os serviços podem ser diferentes. Os valores existentes no cadastro continuam preservados como provisórios, sem virar comprovação externa. Uma referência antiga de viagem total do Expresso Linha 10 tampouco resolve seus quatro intervalos.

Próxima prioridade: baldeações em Barra Funda, Luz, Brás, República no sentido inverso, Sé, Paraíso por sentido, Ana Rosa, Presidente Altino/Osasco, Pinheiros, Santa Cruz, Chácara Klabin, Santo Amaro, Tamanduateí, Tatuapé e Itaquera; trocas de trem em Itapevi e Brooklin Paulista. Os demais pares candidatos continuam no inventário para não serem esquecidos. Esperas precisam distinguir primeiro embarque, troca de trem, serviço parcial, pico, vale, sábado, domingo/feriado e último trem.

## Referências adicionais preservadas

- [ARTESP: início da operação assistida de Ambuitá](https://www.artesp.sp.gov.br/artesp/noticias/estacao%2Bambuita%2Bcomeca%2Ba%2Boperacao%2Bassistida%2Be%2Bdeve%2Btransportar%2Bmais%2Bde%2B65%2Bmil%2Bpessoas%2Bpor%2Bmes): índice oficial informa intervalo médio de 30 minutos e janela 4h–0h. A página integral não abriu nesta consulta. Preservado como referência histórica de operação assistida, com vigência a confirmar; não é duração dos intervalos de via.
- [Motiva: características da Linha 4](https://trilhos.motiva.com.br/linha-4-amarela/sobre/): indica possibilidade de intervalos de 90 segundos em operação normal e 75 em situação especial. É limite/capacidade, não frequência média universal. Não estimar 45 segundos de espera em todas as estações a partir disso.
- [CPTM: postagem sobre Expresso Linha 10](https://pt.linkedin.com/posts/cptm_cptm-linha10-expressolinha10-activity-7488224993676447745-0ihY): grade de 20 minutos em dias úteis, com janelas por sentido. Confirma partidas e não mede percurso entre paradas. A postagem foi lida sem autenticação; data exata de publicação não extraída.
- [Trivia: linhas e estações](https://www.triviatrens.com.br/linhas): informa resumo horário/semihorário do Expresso por tipo de dia, que precisa ser cotejado com o PDF de partidas. Não preenche automaticamente lacunas da grade, como 13h30 dominical, nem resolve conflito de feriados.
- Os PDFs de intervalos das linhas 10 e 13 já guardados foram transcritos como referências estruturadas. A Linha 10 tem padrão parcial de pico até Mauá: intervalo menor não vale automaticamente para quem segue além. As referências existentes da Linha 17 e grades especiais também continuam preservadas.

Os quatro embarques para os quais o GTFS não fornecia referência (envolvendo Ambuitá) agora estão ligados à referência histórica da ARTESP, ainda sem aprovação. Não confundir esse avanço de documentação com confirmação de espera atual. O navegador voltou a falhar na tentativa de pesquisar vídeos dessas lacunas; não foram declaradas novas medições visuais nesta etapa.

## Regra corrigida de um minuto sobre o total

O esclarecimento posterior do usuário substitui a interpretação anterior por componente. Registrar total-base e reserva separadamente:

- Somar os tempos-base dos deslocamentos, esperas e transferências.
- Acrescentar 60 s uma única vez ao total: 15 minutos passam a 16 minutos.
- Não acrescentar margem por estação, intervalo, espera ou baldeação, nem outra margem no cliente ou registro.

Como reserva final da estimativa, o minuto não desloca partidas, não altera a conexão alcançável e não gera ocupação adicional de segmentos. Uma espera desconhecida não vira um minuto por falta de dados. Busca e registro devem compartilhar os mesmos tempos-base e regras de apresentação.

Essa margem é conservadora, não garantia de erro máximo. Mesmo numa viagem de 24 intervalos o acréscimo final será somente um minuto. O usuário aceita estimativas fundamentadas sem exigir validação documental integral; cobertura e simulações permanecem como condição de publicação. A interface deve informar “Tempo estimado” e variação por condições externas.

## Arquivos e condição de conclusão

- `docs/dados/tempos/cobertura/cobertura-deslocamentos.json`: cada intervalo, sentido, referências e lacuna.
- `docs/dados/tempos/cobertura/cobertura-esperas.json`: cada possibilidade de embarque, referências e pendência de faixa/serviço.
- `docs/dados/tempos/cobertura/cobertura-baldeacoes.json`: trocas candidatas, sentidos e pendências.
- `docs/dados/tempos/cobertura/frequencias-gtfs-referencia.json`: faixas originais preservadas por viagem GTFS, sem aprovação operacional.
- `docs/dados/tempos/referencias-intervalos.json`: novas fontes e quadros programados, com limitações.
- `scripts/mapear_cobertura_tempos.py`: reprodução offline do inventário; verifica preservação dos dados de entrada por hash e unicidade dos intervalos.

O inventário marca explicitamente cobertura incompleta e zero novos valores publicados. Para concluir: resolver os 16 sentidos sem referência e os conflitos existentes, completar grades por faixa/dia/padrão, verificar caminhos internos, selecionar bases com procedência e grau de confiança, implementar margens sem duplicação e simular/testar busca e registro antes da publicação. Nenhuma nova calibração foi aplicada à simulação nesta etapa, pois o avanço foi de cobertura e referências, não de aprovação dos custos.
