# Esperas parciais, conflitos e registro — continuação local de 04/11/2026

Nenhuma alteração no Xano ou na aplicação executada. Nenhum commit ou publicação. A margem de um minuto continua sem aplicação, e a Linha 6 permanece adiada. Este relatório complementa `cobertura-modelada-407-2026-11-04.md`; não transforma 407 modelos numéricos em tempos medidos.

## Frequências e alcance

O [boletim oficial de 06/02/2025](https://trilhos.motiva.com.br/content/dam/conteudo-multicanal/mobilidade/conteudo/pt/midia/documentos/realizacoes/viamobilidade-8-e-9/2025/Informacoes_a_imprensa_06_02_2025_06_30.pdf) distingue os intervalos dos trechos das linhas 8 e 9 e confirma o looping. Esses dados são históricos: não comprovam a grade de novembro de 2026. O aviso de manutenção das 22h à meia-noite no mesmo boletim é restrito àquela data, sem aplicação permanente.

`docs/dados/tempos/padroes-l789-candidatos.json` separa agora:

| Linha | Agregado central candidato | Integral candidato |
|---|---|---|
| 7 | Barra Funda–Francisco Morato, frequências GTFS preservadas | Barra Funda–Jundiaí, piso de intervalo de 12 min |
| 8 | Júlio Prestes–Barueri, intervalo de 5 min | Júlio Prestes–Itapevi, piso de 10 min; extensão continua separada |
| 9 | Pinheiros–Mendes, intervalo de 5 min | Osasco–Varginha, piso de 9 min |

Os pisos são hipóteses de frequência integral para evitar prometer continuidade com a frequência do agregado. Não demonstram partidas individuais. O piso da Linha 9 além de Mendes é uma extrapolação explícita: o boletim não informa Varginha. Para a Linha 7, o quadro histórico do Serviço 710 não é grade atual da TIC; o índice o preserva, mas a abertura do PDF falhou nesta pesquisa. O piso de 12 min e o recorte até Morato permanecem candidatos de baixa confiança.

A janela experimental de novos embarques no agregado é **dias úteis, 06h–20h**; é hipótese de laboratório, não horário publicado pelo operador. Sábados, domingos, feriados e o restante do dia mantêm apenas o integral candidato. Quem já embarcou pode continuar depois das 20h sem outra espera. Uma espera que ultrapassa o fim da janela impede novo embarque agregado. Permanecem em uso os calendários do helper existente, sem afirmar cobertura de feriados locais extraordinários.

Um [aviso oficial da TIC para 05/07/2026](https://www.tictrens.com.br/noticias/linha-7-rubi-tera-obras-de-modernizacao-do-sistema-de-sinalizacao-neste-domingo-5-2704) foi preservado: intervalos diferenciados e acréscimo de viagem por obras não foram convertidos em operação de todos os domingos.

## Antes e depois

Comparação com o candidato anterior de 407 sentidos, às 07h30 de um dia útil. Inclui esperas e caminhadas modeladas, sem margem final. Casos por linha isolam o corredor para verificar seu alcance; não significam que ele seja sempre a melhor escolha na rede.

| Consulta | Antes | Depois |
|---|---:|---:|
| Barra Funda → Jundiaí, Linha 7 | 88min30s | 91min30s |
| Júlio Prestes → Itapevi, Linha 8 | 55min30s | 58min |
| Pinheiros → Varginha, Linha 9 | 41min55s | 44min25s |
| Jandira → Paraíso, rede completa | 70min20s | 72min50s |
| Luz → Jandira, rede completa | 60min50s | 63min20s |
| Paulista → Brigadeiro | 9min15s | 9min15s |
| Morumbi → Washington Luís | 23min20s | 23min20s |

O aumento nos corredores longos vem da espera por serviço com alcance suficiente, não de margem por trecho. No tronco, o agregado mantém a vantagem sem estendê-la artificialmente além do limite.

## Conflitos de estimativas

As decisões estão em `docs/dados/tempos/decisoes-conflitos.json`. Foram separados conflitos de contexto: meta de projeto versus operação na Linha 7; programação histórica e terminais nas linhas 8/9; frequência versus tempo de percurso na Linha 17. Isso resolve a mistura de grandezas/fontes, não determina o tempo real atual.

Quatro cenários de sensibilidade produziram 40 comparações:

- Linha 7: cenário exploratório de 70 min, sem tratar relato histórico de outra configuração como medição atual; Jundiaí → Paraíso passou de 118min45s para 102min44s, preservando o caminho.
- Linha 8: estresse de 65 min no núcleo em lugar de 53 min; Jandira → Paraíso passou de 72min50s para 82min14s, mantendo o caminho.
- Linha 9: estresse de 60 min somente no núcleo Osasco–Grajaú em lugar de 45 min; Osasco → Varginha passou de 57min25s para 72min25s, mantendo o caminho. Não se atribuiu a fonte de 60 min ao terminal Varginha.
- Linha 17: hipótese 20% mais lenta elevou Morumbi → Congonhas de 14min30s para 16min30s pela manhã; às 21h45, a viagem isolada deixou de ser disponível. **O atendimento próximo ao encerramento permanece sensível e não está aprovado para publicação.**

Os custos foram variados em tabelas independentes por consulta e na preparação do grafo, sem acumular fatores entre consultas. Não houve mudança de caminho nos demais 39 casos; essa amostra não prova estabilidade de todos os pares da rede. As âncoras históricas continuam preservadas, sem escolha automática do menor tempo.

## Registro e concorrência alinhados no laboratório

`scripts/gerar_registro_calibrado.py` gera a reprodução do registro a partir da mesma preparação executável da busca: custos, perfis de trem, esperas, alcance e regras de transferência. Assim, a caminhada explícita não recebe novamente 600 segundos, e um padrão parcial não perde sua identidade na confirmação.

O contrato experimental exige versão da calibração, instante do cálculo e padrão por trecho. A versão cobre a busca e oito tabelas; regeneração sem mudanças mantém o identificador. O registro aceita cálculo com até 30 segundos, recalcula tudo com o modelo local e rejeita versões/padrões incompatíveis, trechos inválidos, desconexos ou cíclicos. Tempos e horários enviados pelo cliente são ignorados. Autenticação e obtenção do usuário pelo servidor continuam responsabilidade dos endpoints existentes; esta reprodução não cria autenticação nem grava dados.

Em **34 casos**, a cronologia reproduzida coincide com a busca, inclusive fim da janela, espera por trecho e soma das caminhadas. O avaliador anterior divergiu nos 34 casos exercitados. Exemplos:

| Consulta | Busca candidata | Registro anterior | Registro alinhado |
|---|---:|---:|---:|
| Jandira → Paraíso | 72min50s | 76min20s | 72min50s |
| Luz → Jandira | 63min20s | 59min35s | 63min20s |
| Paulista → Brigadeiro | 9min15s | 18min45s | 9min15s |

Há nove rejeições verificadas e um caso de adulteração de tempos ignorada. Quatro cenários com dois usuários **simulados em memória**, sem sessões reais, verificaram exclusão da própria viagem, ausência de ocupação antecipada e limites de desvio/trocas. Três mantiveram a rota principal; Barra Funda → Aeroporto-Guarulhos aceitou alternativa de 63min15s para 65min, dentro do limite. Não se força uma alternativa quando ela não atende à política de qualidade.

Essa geração é de laboratório e não produz um endpoint pronto para publicar. O cliente/backend em execução ainda não transportam esse novo contrato experimental; sua integração e revisão permanecem pendentes.

## Verificação e próximos pontos

- 880 execuções gerais do candidato, sem ciclos ou desvios acima dos limites verificados.
- 34 comparações antes/depois e 34 reproduções de registro, incluindo permanência após o fim da janela do agregado.
- 40 comparações de hipóteses conflitantes.
- Regressões: 32 casos de Guaianases, 18 de linhas parciais e 16 de exceções, aprovados.
- Nove referências inválidas rejeitadas, adulteração de tempos ignorada e quatro cenários de concorrência em memória.

Resultados em `outputs/parciais-registro-20261104/`, na pasta superior ao repositório. Os scripts recebem cópias locais e não fazem chamadas ao Xano.

Continuam pendentes a escolha operacional das estimativas frágeis, frequência atual por dia/faixa e especialmente até Varginha, calendário completo de exceções, conexões inferidas/acessibilidade e integração do contrato ao cliente/backend antes de qualquer publicação conjunta. Não se exige comprovação documental integral para estimativas; é necessário explicitar hipóteses e evitar promessas contraditórias. A margem continua reservada para **60 segundos uma única vez sobre o total final**, após concluir a cobertura e as simulações, sem aumentar ocupação física ou deslocar partidas.
