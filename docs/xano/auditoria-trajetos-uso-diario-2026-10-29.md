# Auditoria de trajetos para uso diário — 29/10/2026

## Conclusão e alcance

Há pendências reais que impedem afirmar que o caminho de menor tempo do cadastro é o melhor caminho prático. A correção de espera e disponibilidade resolveu a comparação dos serviços especiais, mas os tempos genéricos e a exclusão absoluta de trechos lotados ainda distorcem resultados. Uma ampliação dos cenários também revelou voltas artificiais na madrugada.

Esta auditoria somente leu o Xano e executou cópias de seu cálculo com relógio controlado. Não alterou endpoints, parâmetros de demonstração, tabelas ou viagens. A releitura encontrou 182 estações, 16 linhas, 220 vínculos e 207 trechos; as oito tabelas examinadas permaneceram iguais à releitura da entrega anterior. O código publicado foi exportado novamente para os testes.

Foram examinados 58 pares, nos dois sentidos, com 290 buscas sem lotação e 108 simulações de lotação: **398 cenários**, não 398 viagens de campo. As consultas simulam dois horários de pico, entrepico, domingo de madrugada e madrugada de feriado. Não representam atrasos reais, todas as estações em todos os horários ou ensaio completo de carga. O relatório bruto fica fora do repositório, em `outputs/auditoria-uso-diario-20261029/auditoria-rotas.json`. O comando reproduzível é `python scripts/auditar_trajetos_uso_diario.py DIRETORIO_DA_EXPORTACAO`.

## 1. Prioridade imediata: desvios excessivos por concorrência

A busca retira todos os trechos considerados lotados e aceita qualquer alternativa restante, sem comparar o acréscimo de tempo ou de baldeações com o caminho principal. Não modela a opção de aguardar o próximo trem regular. Em 23 das 108 simulações, a alternativa ultrapassou o dobro do tempo do principal.

Exemplo reproduzido às 7h30: Engenheiro Goulart → Aeroporto-Guarulhos usa a Jade direta, estimada no cadastro em 4 minutos. Com apenas o primeiro trecho ocupado, o resultado vai por Tatuapé, Brás e Luz, de onde embarca no Expresso Aeroporto: **65 minutos e duas trocas**. Esses valores são do modelo, não tempos reais certificados. O problema de qualidade permanece mesmo corrigindo os 4 minutos subestimados.

Outro exemplo: Presidente Altino → Pinheiros muda de 8 para 46 minutos estimados, via Linha 8, Barra Funda, Vermelha e Amarela, para evitar o primeiro trecho da Esmeralda.

É preciso comparar o benefício estimado de evitar a ocupação com o custo do desvio, preservando o principal quando não existir alternativa razoável. Um teto em minutos, percentual e trocas deve ser especificado e testado, sem inventar agora um número como regra definitiva. Os parâmetros baixos atuais são intencionais para a demonstração; não foram tratados como erro nem modificados.

## 2. Prioridade imediata: voltas na madrugada

Sete das 290 buscas sem lotação repetiram estações. À 1h10 do domingo 01/11/2026, Paraíso → Jandira passa por Sé, segue até Corinthians-Itaquera e depois retorna por Tatuapé, Brás, Luz e Barra Funda. Consolação → Paulista chega a atravessar outras quatro linhas, repetindo República, em vez de informar a indisponibilidade da conexão direta naquele horário.

O limite de duas horas de espera é aplicado individualmente ao embarque. A busca consegue consumir tempo circulando nas linhas abertas até caber nesse limite e alcançar a reabertura de outra linha. A identificação da continuidade também não distingue os sentidos de um trem regular. A inspeção indica a necessidade de representar espera e troca de sentido explicitamente, eliminar voltas artificiais e aplicar uma política de horário à viagem inteira. A regra de madrugada não deve permitir transferências fechadas só porque uma das linhas circula 24 horas.

Os [horários oficiais do Metrô](https://www.metro.sp.gov.br/sua-viagem/horarios/) distinguem o funcionamento geral, o último embarque por estação, viagens na mesma linha após meia-noite e os limites das transferências. O modelo atual ainda simplifica essas diferenças.

## 3. Prioridade alta: tempos de deslocamento e espera regular

**188 dos 190 trechos ferroviários regulares têm exatamente 120 segundos**. Dos 207 trechos totais, 195 têm esse tempo. Assim, o cálculo ainda se aproxima de contar estações em grande parte da malha. A Jade inteira é estimada em quatro minutos, Brás → Engenheiro Goulart em quatro e Barra Funda → Jundiaí em 32, todos sem espera regular conhecida.

É necessário calibrar durações por trecho, sentido e faixa de operação e guardar fonte, data e confiança. A [apresentação técnica da CPTM sobre a Linha 13](https://www.cptm.sp.gov.br/a-companhia/obras-modern/Documents/Apresenta%C3%A7%C3%A3o%20Linha%2013%20-%20Completa.pdf) descreve 12,2 km e estimativa de implantação de 17 minutos: é evidência histórica da inadequação do cadastro de quatro minutos, **não uma duração atual a ser copiada automaticamente**. Não se distribuiu um tempo terminal igualmente por estação.

Também falta frequência regular por linha, trecho, sentido e faixa horária. Não se deve trocar ausência de informação por promessa de espera zero. O [boletim oficial da ViaMobilidade de 04/02/2025](https://trilhos.motiva.com.br/content/dam/conteudo-multicanal/mobilidade/conteudo/pt/midia/documentos/realizacoes/viamobilidade-8-e-9/2025/Informacoes_a_imprensa_04_02_2025_06_30.pdf) exemplifica intervalos diferentes entre segmentos da mesma linha; por ser histórico, não foi aplicado como tabela atual.

## 4. Prioridade alta: transferências reais, direção e extensão da Linha 8

Todas as trocas recebem 600 segundos. Isso trata igualmente uma travessia simples de plataforma, corredores longos, escadas e trocas entre operadores. Paulista–Consolação ainda soma seus 180 segundos de caminhada à penalidade genérica ao acessar a outra linha. A composição precisa separar caminhada e espera, evitando sobreposição entre estimativas.

O [debate de usuários sobre Paraíso e Ana Rosa](https://www.reddit.com/r/saopaulo/comments/1q60hfn/transfer%C3%AAncia_linha_azul_linha_verde_para%C3%ADso_ou/) destaca diferenças por sentido, plataforma, escadas e familiaridade. Há preferências contraditórias: não é fundamento para declarar uma estação sempre melhor nem para inventar minutos exatos. As observações devem orientar a conferência dos mapas e a coleta local.

O modelo também não distingue o trem da extensão Itapevi–Amador Bueno do tronco da Linha 8. Júlio Prestes → Amador Bueno aparece como um único embarque, sem troca nem espera em Itapevi. O [guia da operadora](https://trilhos.motiva.com.br/viamobilidade8e9/guia-de-uso/) identifica ali integração com a extensão operacional; a grade e as exceções atuais precisam ser conferidas antes de modelar a troca. A solução implementada para Brooklin Paulista não generaliza automaticamente essa situação.

## 5. Prioridade alta: integração tarifada e restrita por horário

Tatuapé e Corinthians-Itaquera são nós compartilhados sem política de gratuidade, bloqueio, saída à rua ou novo pagamento. A busca não diferencia essas condições.

As [informações de bilhetes do Metrô](https://www.metro.sp.gov.br/sua-viagem/bilhetes-cartoes/) informam integração livre em dias úteis entre 10h–17h e 20h–24h e durante toda a operação aos fins de semana e feriados. O [guia oficial de outubro/2026](https://www.metro.sp.gov.br/wp-content/uploads/2026/10/guia_do_passageiro_online.html) diverge para sábado, começando às 10h. Uma [página anterior da CPTM](https://cptm.sp.gov.br/sua-viagem/Pages/Transfer%C3%AAncias-e-Intervalos.aspx) ainda cita liberação excepcional em Tatuapé por obras. Portanto, há conflito entre fontes oficiais e não é seguro impor um bloqueio definitivo por suposição. É preciso representar custo/acesso e registrar exceções com vigência, sem prometer integração gratuita no pico.

As estações Lapa da Linha 7 e da Linha 8 permanecem separadas: não foi criada uma integração gratuita fictícia. Proximidade geográfica ou nome igual também não autoriza unir Luz e Júlio Prestes como conexão interna.

## 6. Cobertura ausente: Linha 6-Laranja

As seis estações do trecho João Paulo I–Perdizes não estão no cadastro. O [Governo de SP](https://www.casacivil.sp.gov.br/sec_casa_civil/noticias/metrolinha6) registra operação assistida de segunda a sexta, 10h–15h, gratuita, na abertura de julho; o [fabricante Alstom](https://www.alstom.com/pt/press-releases-news/2026/7/alstom-celebra-inicio-da-operacao-da-linha-6-laranja-com-trens-produzidos-em-taubate) confirma o início desse trecho. São João Paulo I, Freguesia do Ó, Santa Marina, Água Branca, SESC-Pompeia e Perdizes. Não há fundamento para cadastrar toda a linha até São Joaquim como operacional.

O [relato de campo da comunidade](https://www.reddit.com/r/saopaulo/comments/1umvzj5/testei_a_linha_6laranja_hoje/) descreve circulação pela rua na conexão entre as duas estações Água Branca. Isso exige confirmar acesso atual, caminhada e pagamento; não se deve reutilizar o mesmo nó da Linha 7 como se houvesse plataforma integrada. A FAQ da concessionária ainda mistura previsões de construção, reforçando a necessidade de conferir a vigência operacional antes de cadastrar.

As expansões Ipiranga, Boa Esperança e Jacu-Pêssego da Linha 15 não foram tratadas como prontas: a [página oficial do Metrô](https://www.metro.sp.gov.br/pt_BR/obras/linha-15-prata/) distingue o trecho operacional Vila Prudente–Jardim Colonial das obras de expansão.

## 7. Ocupação prevista e status operacional

O registro já salva a cronologia, mas a escolha por concorrência ainda consulta a ocupação **no instante atual**, inclusive para trechos que a nova pessoa só atingirá depois. Isso cumpre a regra anterior; falta avaliar sobreposição no horário previsto de chegada para produzir uma orientação mais útil. Viagens de outros corredores também entram no denominador percentual, algo a revisar antes de interpretar o resultado como ocupação de um trem.

Falhas, via única, manutenção, serviços parciais e trocas temporárias não estão ligados ao cálculo. A [operadora publicou intervenções específicas em outubro/2026](https://trilhos.motiva.com.br/viamobilidade8e9/noticias/2026/outubro/viamobilidade-intensifica-manutencoes-preventivas-nas-linhas-8-d/) por trecho e período. O aviso é histórico, não diagnóstico de que a ocorrência permanece ativa hoje. A futura integração ARTESP e fontes complementares deve ter data de atualização, vigência e tratamento de informação ausente; um rótulo geral da linha não basta para decidir todos os trechos.

## Critérios para a próxima correção

1. Rejeitar voltas artificiais e não recomendar desvio desproporcional só para alternar usuários.
2. Comparar permanecer no principal, esperar o próximo trem e seguir uma alternativa disponível; falta de dados deve permanecer explícita.
3. Calibrar tempos e transferências por conexão e sentido, priorizando Jandira/Barra Funda–Paraíso, os eixos por Pinheiros e o acesso ao aeroporto.
4. Representar extensão de Itapevi, acesso tarifado e horários de transferência; incluir a Linha 6 somente com operação e conexões comprovadas.
5. Usar ocupação no horário previsto e avisos operacionais com vigência.
6. Repetir os casos nas duas direções, com/sem concorrência, pico/entrepico, fins de semana, feriados e madrugada; comparar também a qualidade do caminho, não apenas invariantes e soma de tempos.

Os testes anteriores continuam sendo evidência de compatibilidade e preservação das correções. Eles não certificam, sozinhos, o melhor trajeto no mundo real. Esta revisão amplia a cobertura e registra precisamente essa distinção.
