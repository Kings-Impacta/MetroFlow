# Avaliação de fontes para status operacional

Data da verificação: **21/10/2026**.

## Objetivo

Avaliar fontes capazes de informar as condições operacionais das linhas usadas pelo
MetroFlow sem confundir dados oficiais, páginas públicas e APIs com contrato de uso
documentado. Esta avaliação não autoriza a publicação da integração.

## Fontes verificadas

### API Trilhos da ARTESP

A API Trilhos é a fonte preferencial para a malha delegada. A documentação pública
define autenticação por `Api-Key`, atualização a cada cinco minutos, limite padrão de
12 requisições por hora, licença CC BY-NC 4.0 e os endpoints de status, ocorrências e
concessionárias.

Desde 03/09/2026, seu escopo exclui as linhas geridas diretamente por empresas
públicas estaduais. Por isso, ela não cobre sozinha toda a rede representada pelo
MetroFlow.

- Documentação: <https://ccm.artesp.sp.gov.br/metroferroviario/api/docs/>
- Cobertura adequada: linhas delegadas presentes na resposta autenticada.
- Contrato de uso: documentado, sujeito à chave, allowlist, limite e aceite de novas
  versões dos termos.

### Direto do Metrô e endpoint agregado observado

O Direto do Metrô declara informar em tempo real situações que podem alterar o tempo
de viagem. Durante a verificação, o endpoint abaixo respondeu `HTTP 200` sem
autenticação:

`https://apim-proximotrem-prd-brazilsouth-001.azure-api.net/api/v1/lines`

A resposta observada continha `Status`, `Message`, `MessageDebug` e `Data`. Cada item
de `Data` apresentou os seguintes campos:

| Campo | Tipo observado | Uso possível |
| --- | --- | --- |
| `Code` | inteiro | correspondência com `linhas.codigo` |
| `ColorName` | texto | nome público da cor |
| `ColorHex` | texto | cor para apresentação após validação |
| `Line` | texto | nome público da linha |
| `StatusCode` | texto | situação normalizada pela origem |
| `StatusLabel` | texto | rótulo público da situação |
| `StatusColor` | texto | indicação visual da origem |
| `Description` | texto ou nulo | explicação pública da condição |

Foram observados códigos para as linhas 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
13, 15 e 17. Isso permitiria complementar as linhas 1, 2, 3, 10, 11, 12, 13 e
15 que não pertencem ao escopo atual da API Trilhos.

- Canal oficial: <https://www.metro.sp.gov.br/sua-viagem/direto-metro/>
- Endpoint observado: <https://apim-proximotrem-prd-brazilsouth-001.azure-api.net/api/v1/lines>
- Contrato de uso: **não localizado**. Não foram encontradas documentação pública,
  versão, limite, SLA, licença dos dados ou autorização explícita para consumo por
  aplicações de terceiros.

O fato de o endpoint estar acessível sem chave não comprova autorização para
republicação. Os regulamentos de credenciamento encontrados no portal do Metrô
indicam que o fornecimento de dados para planejadores pode ser formalizado por
credenciamento. A autorização ou o enquadramento acadêmico deve ser confirmado pelo
Metrô antes do uso publicado.

### CPTM

O aplicativo oficial da CPTM divulga condições operacionais, mas seus termos tratam
do uso do aplicativo e não concedem, de forma localizada nesta avaliação, uma licença
para republicar o fluxo de status em outra aplicação. O endpoint agregado observado
retornou as linhas 10, 11, 12 e 13, porém não há contrato público encontrado que
permita atribuí-las a uma API pública estável da CPTM.

- Aplicativo: <https://cptm.sp.gov.br/Pages/aplicativo.aspx>
- Termos do aplicativo: <https://cptm.sp.gov.br/Pages/termos-aplicativo.aspx>
- Confirmação necessária: autorização, atribuição, limites e canal técnico para uso
  por terceiros.

### Sites da Motiva Trilhos

As páginas públicas da Motiva apresentam situação e histórico de ocorrências das
linhas concedidas. Esses dados se sobrepõem à cobertura oficial da ARTESP e dependem
da estrutura do HTML. Não devem ser usados como fonte principal enquanto a API
Trilhos estiver disponível.

## Decisão de integração

1. Usar a ARTESP como fonte primária das linhas delegadas somente após obter a chave
   e registrar os termos aceitos.
2. Não publicar consumo do endpoint agregado até obter confirmação escrita do Metrô
   e, para as linhas correspondentes, da CPTM sobre autorização e condições de uso.
3. Não coletar HTML dos sites das operadoras como dependência de produção.
4. Preparar a integração por adaptadores independentes, sem alterar o cálculo de
   trajetos enquanto a fonte complementar não estiver autorizada.

## Contrato interno proposto

Cada condição operacional normalizada deverá conter:

- código da linha;
- situação normalizada e rótulo da origem;
- descrição opcional;
- fonte e URL de origem;
- instante informado pela origem, quando existir;
- instante da coleta;
- validade calculada;
- indicação de dado disponível, desatualizado ou indisponível.

O estado nunca será inferido como operação normal quando a fonte falhar. Dados além
da validade serão apresentados como desatualizados e não poderão alterar a escolha do
trajeto nesta primeira entrega.

## Precedência e cache propostos

- ARTESP prevalece para a malha delegada.
- Uma fonte oficial autorizada do Metrô ou da CPTM prevalece para suas linhas.
- Divergências devem ser registradas sem expor credenciais ou respostas internas.
- O cache deve respeitar o maior intervalo exigido pela fonte. Para a ARTESP, cinco
  minutos e no máximo 12 consultas por hora por credencial.
- A indisponibilidade de status não pode impedir a busca de trajetos.

## Dados que permanecem ausentes

As fontes avaliadas não oferecem contrato comprovado para lotação, tempo real de
espera, caminhada ou transferência. Portanto, esta integração pode atender à parcela
de condições operacionais de P5, mas não conclui lotação nem P1.

## Pendências antes da implementação

- Solicitar a chave da API Trilhos e registrar produto, ambiente, allowlist, licença
  e versão dos termos aceitos.
- Solicitar ao Metrô confirmação de uso do endpoint agregado por uma aplicação
  acadêmica, incluindo cache, atribuição, limites e republicação.
- Solicitar à CPTM confirmação equivalente para as linhas 10, 11, 12 e 13.
- Repetir amostras em horários e situações diferentes para definir todos os valores
  possíveis de `StatusCode` e campos nulos.
- Só então implementar adaptadores, cache, normalização, observabilidade e interface.
