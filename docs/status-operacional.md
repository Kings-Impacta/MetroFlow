# Status operacional: Direto dos Trens + CPTM

## Configuração preparada em 09/11/2026

O desenho definitivo mantém **Direto dos Trens como principal** e **JSON do site CPTM como complemento**, com Metrô como reserva. Enquanto o token não chega, o usuário autorizou uma configuração local provisória com Metrô, CPTM e Motiva: [cobertura de 12 linhas](demo-status-cobertura-completa.md). As fontes continuam desativadas por padrão; a ativação pública permanece separada. ARTESP e agregado Azure não participam da fábrica de fontes.

O endpoint autenticado `/api/planning/line-status`, a página `/status` e o quadro das linhas do trajeto continuam independentes da busca e do registro automático. Em falhas, mantêm o último retorno válido como desatualizado; sem retorno anterior, informam indisponibilidade. Isso não altera a rota, seus custos, partidas ou ocupação. Serviços especiais não herdam automaticamente o status de linhas regulares.

## Fontes e precedência

1. Usar condição atual do Direto dos Trens quando disponível para a linha.
2. Sem condição atual da principal, usar dado atual da CPTM para as linhas retornadas por ela.
3. Os quadros do Metrô e da Motiva só participam quando explicitamente habilitados; estão ligados no iniciador local provisório, não por padrão.
4. Se só há dados antigos, manter a mesma ordem entre as fontes, com rótulo desatualizado. Sem dado utilizável, apresentar indisponível.

A identificação da fonte acompanha o estado escolhido. Divergências são registradas sem payloads ou credenciais. Não combinar descrições ou horários de fontes diferentes como se fossem um único comunicado.

O catálogo público do Direto dos Trens contempla as linhas regulares da malha, inclusive 6/7/13; o retorno efetivo será validado quando o token chegar. O JSON CPTM observado trouxe 10/11/12. O parser aceita 13 somente se ela vier de fato numa resposta CPTM, sem inventar cobertura. O quadro de reserva do Metrô foi testado para 1/2/3/4/5/15/17.

## Preparação, sem ativação

As fontes continuam desativadas por padrão. O usuário já solicitou token Direto dos Trens e aguarda retorno. Não há token de exemplo utilizável e não foi feita chamada ao endpoint protegido nesta implementação.

```text
METROFLOW_DDT_ENABLED=0
METROFLOW_DDT_TOKEN=
METROFLOW_CPTM_ENABLED=0
METROFLOW_METRO_QUADRO_AUTORIZADO=0
METROFLOW_MOTIVA_QUADRO_ENABLED=0
METROFLOW_STATUS_CACHE_PATH=.cache/line-status.sqlite3
```

Configurar credenciais somente no ambiente do backend, nunca no navegador ou no Git. A futura ativação depende do recebimento do token, das condições aplicáveis e de uma primeira resposta autorizada. As flags antigas `METROFLOW_ARTESP_ENABLED` e `METROFLOW_STATUS_COMPLEMENTAR_AUTORIZADO` não iniciam coletores nesta configuração. O aplicativo em uso e o Xano não foram alterados nesta preparação local.

## Autenticação e transporte

O fornecedor Direto dos Trens documenta token na query da requisição. O transporte dedicado usa somente HTTPS para a origem fixa do fornecedor, não segue redirecionamentos, não usa o logger de URLs do httpx e descarta detalhes de exceções. A query existe apenas na requisição interna exigida pelo protocolo, nunca em URL do frontend, resposta ou log da aplicação. A representação pública e o cache contêm somente dados normalizados; a chave do cache é um hash da credencial. Antes de ativar, revisar também qualquer instrumentação externa de rede/APM para que ela não registre essa query.

A CPTM usa GET para o endpoint referenciado pelo próprio site, sem token na amostra observada. O quadro Metrô não recebe credencial Direto dos Trens nem ARTESP.

## Datas e interpretação

No Direto dos Trens, `criado` indica o início da ocorrência e `modificado` sua alteração; nenhum deles é inventado como última verificação da operadora. Datas sem fuso explícito não ganham deslocamento presumido. Na CPTM, `dataGeracao` com fuso pode servir como verificação da geração do lote; sem fuso, a validade usa somente a coleta local e a limitação permanece documentada. A data bruta observada fica preservada nas referências da pesquisa. No quadro do Metrô, a data local conhecida é interpretada como Brasília.

Situações desconhecidas permanecem desconhecidas; campo obrigatório ausente, contrato incompatível ou duplicatas invalidam a coleta. Descrições são texto limitado a 1200 caracteres, sem HTML executável. A ausência de ocorrência na descrição não equivale por si só a operação normal.

## Cache e falhas

O SQLite `.cache/line-status.sqlite3` é compartilhado entre usuários e processos do mesmo servidor. A política inicial conservadora limita cada fonte a uma tentativa por cinco minutos e 12 por hora; isso é um limite interno, não a cota contratual informada pelas novas fontes. As chamadas não são disparadas por usuário nem pelo cálculo de rota. Uma reserva transacional precede a rede, e falhas consomem tentativas.

`Cache-Control` é respeitado: `max-age`/`s-maxage` e `Age` limitam a validade; prazos maiores ampliam o intervalo. Validade esgotada não proíbe armazenar a última observação como desatualizada. `no-store`, `no-cache` e `private` impedem persistência da nova condição: a consulta que a recebeu pode apresentá-la, mas as demais aguardam a próxima tentativa permitida, mantendo eventual observação anterior cujo armazenamento era permitido. A reserva/cota permanece em disco. Valores vencidos nunca são apresentados como atuais.

HTTP 429 respeita Retry-After, com suspensão mínima conservadora de uma hora. Sem cabeçalho de validade, aplica-se o limite local de dez minutos para dado atual. Por decisão do usuário, o último estado armazenável é mantido como desatualizado até um novo retorno válido, sem descarte após uma hora. Falhas, respostas vazias ou linhas ausentes não apagam o último retorno, não renovam sua data nem inventam normalidade. A interface mantém os cartões enquanto aguarda a rede e descarta respostas atrasadas. A Motiva mantém timeout de cinco segundos e orçamento de leitura de dez segundos. O Metrô usa conexão IPv4 por requisição, com conexão de cinco segundos, leitura de quinze segundos e orçamento de processamento/leitura de vinte segundos. Não há repetição imediata de GET. HTTPS, validação de certificado e resolução DNS são preservados, sem mudar configurações do sistema ou fixar IP remoto. Timeout, resposta excessiva, erro HTTP, HTML/JSON incompatível e cache sem permissão não são propagados ao planejador.

Várias máquinas precisam compartilhar coletor/cache central antes de usar o mesmo token; arquivos separados não coordenam a cota. Instrumentação e logs não devem armazenar a requisição autenticada. Nenhuma credencial é necessária para executar os testes simulados.

## Referências e pendências

[Pesquisa de fontes e contratos](fontes-status-complementares-2026-11-09.md) · [Swagger Direto dos Trens](https://static.diretodostrens.com.br/swagger/) · [CPTM](https://www.cptm.sp.gov.br/cptm)

Ainda faltam token, condições aplicáveis e amostra autorizada da principal, além da confirmação do fuso CPTM. A configuração local de três fontes e o cliente em uso já foram validados; os detalhes estão no registro da correção do Metrô. Esta entrega não conclui a parcela de lotação oficial de P5.


## Validação desta preparação

Na revisão de retenção, passaram 275 testes e 82 subtestes, incluindo falha prolongada, resposta parcial/vazia, cache CDN vencido, pedidos simultâneos e independência de busca/registro/concorrência. A compilação Reflex passou. A verificação em cache isolado preservou os 12 últimos retornos e suas datas após um dia de falha simulada. Houve consulta HTTP 200 ao Metrô durante a investigação; ainda podem ocorrer falhas externas. Esse ensaio precedeu a entrega; o reinício e a verificação na main foram concluídos em 11/11. Isso não comprova uma resposta real da API Direto dos Trens nem repete a concorrência com duas contas reais.

## Indicadores compactos no trajeto

O resultado apresenta numero/nome de cada linha e bolinha colorida junto ao texto de status no resumo do tempo estimado, sem os antigos quadros detalhados no final. Cada instrucao de embarque repete apenas o indicador da linha correspondente. A lista do resumo e unica e segue a ordem de uso, com qualquer quantidade de linhas; caminhadas nao recebem status ferroviario. Verde indica normalidade, amarelo restricao, vermelho interrupcao e cinza encerramento, situacao desconhecida ou ausencia de dado. Nos indicadores compactos, retornos antigos preservam apenas o texto do status; fonte, coleta e descricao ficam nos detalhes ao foco ou ao passar o ponteiro. O codigo da linha vem do resultado, sem inferir uma linha pela cor; contratos legados sem codigo exibem o nome recebido com status indisponivel. A pagina /status preserva os detalhes. Apenas o resumo inicia a atualizacao automatica, compartilhada com todos os indicadores, sem consulta adicional por embarque.

### Ajuste visual de 10/11/2026

Por solicitacao do usuario, os indicadores compactos passam a mostrar somente o ultimo status, sem o sufixo desatualizado. Esta decisao substitui a descricao anterior desse sufixo no trajeto; a validade interna, a data de coleta, o painel detalhado /status e a retencao em falhas permanecem iguais. O resumo usa duas colunas a partir de telas pequenas: metricas a esquerda e lista alinhada no alto a direita, reduzindo a quebra para uma linha separada. Em telas estreitas, as colunas se empilham sem sobrepor o conteudo.

## Reteste após integração na main

Em 11/11, foram confirmadas renovação automática de Metrô/CPTM/Motiva e duas viagens calibradas no Xano, com alternativa dentro dos limites. Veja [evidências e pendências atuais](xano/reteste-main-status-concorrencia-2026-11-11.md). A validade antiga da Motiva foi sinalizada no painel, sem apagar o retorno nem afetar a busca.
