# Ramal de Washington Luís e alternativas — 28/10/2026

## Resultado aplicado e limites de implantação

No Xano, o trecho 200 agora liga Brooklin Paulista (180) a Washington Luís (182),
com chave `B:180:182:14:3`. Preservados ID, duração de 120 s, serviço 3,
bidirecionalidade e os demais 206 trechos. O tronco informa sentido Congonhas ou
Morumbi; o ramal informa Washington Luís ou Brooklin Paulista.

A busca distingue os trens do tronco e do ramal. A troca obrigatória em Brooklin
conta uma baldeação e os 600 s estimados já usados pelo projeto. Não foram criados
uma linha fictícia, uma estação duplicada ou um trecho de caminhada inexistente.

O normalizador, as orientações e a mensagem do Reflex foram corrigidos localmente
para aceitar e apresentar a troca dentro da Linha 17. O cliente atualizado envia
`suporta_troca_mesma_linha=true`; clientes anteriores continuam recebendo as rotas
regulares e o trecho direto Brooklin–Washington, mas não recebem um trajeto com
baldeação na mesma linha que seu normalizador rejeitaria. **Para usar a troca no
aplicativo, é necessário executar a versão Python atualizada deste trabalho.**
Os arquivos ainda estão locais, fora da `main`.

## Comparação sem outras viagens ativas

| Percurso | Cadastro anterior | Cadastro corrigido |
|---|---|---|
| Morumbi → Washington Luís | via Congonhas, 14 min, sem troca | via Brooklin, 22 min, uma troca |
| Washington Luís → Morumbi | via Congonhas, 14 min, sem troca | via Brooklin, 22 min, uma troca |
| Congonhas ↔ Washington Luís | ligação direta inexistente, 2 min | via Brooklin, 14 min, uma troca |
| Brooklin Paulista ↔ Washington Luís | via Congonhas, 4 min | ramal direto, 2 min, sem troca |
| Morumbi ↔ Congonhas | tronco, 12 min | mantido, 12 min |
| Campo Belo ↔ Washington Luís | via Congonhas, 8 min | via Brooklin, 16 min, uma troca |

São tempos estimados do cadastro, incluindo a penalidade fixa de troca, não
tempos medidos ou garantia de duração. O aumento corrige a falta de transferência.
Os horários permanecem segunda a sábado, 06h–22h, conforme o comunicado oficial.

## Alternativas para Paraíso

Todas as alternativas usam a mesma regra de menor tempo e desempate por menos
baldeações. Não foi introduzida preferência por uma linha ou por menos estações.

| Origem e alternativa | Tempo do modelo atual |
|---|---:|
| Barra Funda → Sé → Azul → Paraíso | 28 min |
| Barra Funda → República → Amarela → Paulista/Consolação → Verde → Paraíso | 39 min |
| Jandira → Barra Funda → Vermelha → Azul → Paraíso | 68 min |
| Jandira → Linha 9 → Pinheiros → Amarela → Paulista/Consolação → Verde → Paraíso | 77 min |
| Luz → Turquesa → Barra Funda → Linha 8 → Jandira | 48 min |
| Luz → Coral → Barra Funda → Linha 8 → Jandira | 48 min |
| Luz → Amarela → Pinheiros → Linha 9 → Linha 8 → Jandira | 64 min |

A rota pela Amarela está conectada e participa da busca. Porém, os 10 min fixos
por troca e os tempos genéricos do cadastro influenciam a comparação. Uma viagem
real pode ser mais rápida por essa alternativa conforme espera, fluxo e caminhada;
essas variações ainda não são medidas pelo sistema.

Nos testes controlados com a malha real:

- Um trecho da Azul após a Sé ocupado fez a busca preferir Turquesa–Verde.
- Com um trecho dessa segunda opção também ocupado, venceu Vermelha–Amarela–Verde.
- Em uma cópia de teste com tempos maiores na Azul e Turquesa, a Amarela venceu
  pelo tempo mesmo sem lotação. Esses tempos controlados **não foram gravados**.
- As onze rotas de referência tiveram respostas idênticas antes/depois, incluindo
  Jandira–Paraíso e Barra Funda–Paraíso. As alterações intencionais ficaram no ramal.

## Outras pendências tratadas

A tabela oficial do Expresso Linha 10, vinculada na página atual da CPTM, foi
baixada e conferida visualmente. O horário com parada em São Caetano foi aplicado
por sentido, tanto na busca quanto na confirmação:

| Sentido com São Caetano | Manhã | Tarde |
|---|---|---|
| Santo André → Tamanduateí | 05h40–09h00 | 16h10–19h50 |
| Tamanduateí → Santo André | 05h50–08h50 | 16h00–20h00 |

As últimas partidas são incluídas pela precisão de minuto; não se calcula espera
pelo próximo trem ou horário futuro de chegada ao embarque. Partidas são dados
distintos da duração do percurso.

O calendário deixou de copiar datas fixas de 2026. Datas móveis são calculadas
pela Páscoa gregoriana, mantendo os feriados recorrentes vigentes de São Paulo
para 2026–2099 e bloqueando anos fora dessa faixa. Não se trata de calendário
oficial futuro: decretos excepcionais, mudanças legais e feriados de outros
municípios ainda precisam ser acompanhados. Testados Sexta-feira Santa e Corpus
Christi em 2027 e um dia útil normal desse ano.

## Validação e evidências

### Reteste posterior com logins renovados

Depois de sair e entrar novamente, foram confirmadas duas contas distintas nas
viagens Luz–Jandira: uma iniciou pelo trecho 204 (Expresso Aeroporto) e a outra
pelo trecho 2 (Turquesa), com 14,2 s entre os registros. Ambas ficaram ativas. Isso
resolve a dúvida de identidade nesse reteste; as observações anteriores abaixo
permanecem como histórico, não como diagnóstico atual de falha de autenticação.

O teste confirma a alternância, mas não certifica a melhor opção prática. Os
trechos Luz–Barra Funda da Turquesa, Coral e Expresso têm 480 s no cadastro, sem
espera pela partida. O desempate existente usa tempo e número de baldeações, sem
preferência por serviço regular, podendo escolher o Expresso entre custos iguais.
O PDF atual do serviço, vinculado pela CPTM e conferido visualmente, informa
partidas horárias dos terminais nos dias úteis/sábados/feriados e meia hora aos
domingos. A chegada a uma estação intermediária não é o horário de partida do
terminal. Não foi inferida uma partida da Luz a partir do horário do Aeroporto.

É necessário modelar a espera e definir desempate entre serviço regular e
especial, além de registrar exceções operacionais. Não se deve declarar o
Expresso mais rápido apenas por ignorar a espera ou excluir o serviço sem motivo.

- 137 testes e 14 subtestes aprovados, incluindo cálculo, contrato, instruções,
  orientações de desembarque, janelas por sentido e concorrência.
- Reflex compilado com sucesso; XanoScript e OpenSpec validados.
- Publicados apenas `trajetos/buscar` e `viagens/confirmar`, após prévia.
- Código publicado relido: lambdas idênticas às testadas.
- Oito tabelas relidas e comparadas campo a campo com o plano. Permanecem 207
  trechos, 207 chaves distintas e ausência do registro inválido 215.
- A primeira tentativa de teste em duas abas do navegador interno criou dois
  registros, mas ambos pertenciam ao mesmo usuário. Não comprova duas sessões
  independentes; esse resultado é compatível com sessão compartilhada, sem provar
  por si só a causa. A concorrência entre usuários
  distintos continua dependendo de teste integrado com sessão isolada.
- Na repetição manual Luz–Jandira, os dois registros também pertenciam ao mesmo
  usuário, separados por 21,6 s, ambos começando no trecho 2 (Luz–Barra Funda pela
  Turquesa). A própria viagem é excluída da lotação de quem busca. O usuário
  confirmou posteriormente que usou e-mails diferentes; portanto existe uma
  divergência a investigar entre as contas informadas e os registros observados.
  As chamadas recentes de busca e registro retornaram HTTP 200. A comparação de
  `/api/auth/me` em cada janela foi solicitada para distinguir identidade da sessão,
  outra instância em execução ou ausência da segunda chamada no histórico. Não se
  declara comprovado um compartilhamento de cookie ou uma falha de autenticação.
  O controle de navegador
  foi interrompido pela revisão automática com limite de uso atingido; nenhum
  clique bloqueado foi executado por outro meio.
- A instância local adicional de produção para inspeção no navegador não iniciou:
  Bun apresentou ENOENT e o fallback npm encontrou EPERM ao criar dependências.
  A instância já existente em `localhost:3000` não foi interrompida.
- O teste administrativo de duas gravações simultâneas de trecho com login real
  também permanece pendente; não foram criadas contas ou tokens para simulá-lo.

Backup e relatório reproduzível fora do Git, na pasta desta conversa:
`outputs/ramal-brooklin-20261028-160833/`.
Contém os dados antes/depois, código, PDF oficial, imagem conferida e
`comparacao-ramal-alternativas.json`.

## Pendências que ainda exigem dados ou validação

1. **Duração e retornos diretos do Expresso L10:** a tabela oficial não informa
   tempo de percurso. Mantidos os 90 s por trecho anteriores, sem certificá-los;
   retornos sem São Caetano precisam de custos documentados antes de novas arestas.
2. **Tempos reais de baldeação/espera:** medir ou obter dados confiáveis por estação
   antes de substituir a regra fixa. É o que permitirá comparar melhor a Sé com
   República/Paulista e as opções por Pinheiros em diferentes condições.
3. **Tarifas de integração:** as faixas de gratuidade de Tatuapé/Itaquera não são
   calculadas; a conectividade física permite viagem paga. Não bloquear uma
   ligação física apenas porque a transferência pode exigir nova tarifa.
4. **Exceções e terminais:** manter feriados locais e esquemas especiais; a conexão
   aos terminais de Guarulhos ainda não tem nós de terminal no grafo.
5. **Implantação da interface e sessões reais:** incorporar a versão local ao fluxo
   de entrega e repetir os testes integrados, sem declarar conclusão por teste
   controlado ou por duas abas que compartilham a conta.

## Fontes oficiais

- [Metrô, 29/09/2026: transferência obrigatória em Brooklin Paulista](https://www.metro.sp.gov.br/2026/09/29/metro-amplia-horario-da-linha-17-ouro-a-partir-desta-quarta-feira-30/).
- [CPTM: página de transferências e intervalos](https://www.cptm.sp.gov.br/cptm/sua-viagem/transferencias-e-intervalos/), com o arquivo Serviço Expresso Linha 10 acessado em 28/10/2026.
- [CPTM: grade oficial do Expresso Aeroporto](https://www.cptm.sp.gov.br/dx/api/dam/v1/collections/05321fd9-3791-4689-a8ac-9e2adde39c4b/items/bdfdcc63-cee4-43a2-bb91-70dd75adae0d/renditions/b3fca1ea-5b3c-4133-8c87-e1f7ac3efac0?binary=true).
- [PDF oficial do Expresso L10](https://www.cptm.sp.gov.br/dx/api/dam/v1/collections/05321fd9-3791-4689-a8ac-9e2adde39c4b/items/996297d1-45bf-4a2c-adb2-23cf38c61c9a/renditions/9bb7e05d-a547-40da-9b30-181dc8154c8d?binary=true).
- [Metrô: guia de integrações](https://www.metro.sp.gov.br/wp-content/uploads/2026/10/guia_do_passageiro_online.html).
- [Metrô: transferências da Linha 10 em Luz e Barra Funda, e da Linha 8 na Barra Funda](https://www.metro.sp.gov.br/pt_BR/sua-viagem/horarios/).
- [Prefeitura de São Paulo: feriados de 2026](https://prefeitura.sp.gov.br/web/prefeitura-de-sao-paulo/w/prefeitura-de-s%C3%A3o-paulo-divulga-calend%C3%A1rio-de-feriados-e-pontos-facultativos-para-2026).
- [Lei federal 14.759/2023: 20 de novembro](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14759.htm).
