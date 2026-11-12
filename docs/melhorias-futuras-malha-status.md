# Melhorias futuras e limites de malha e status

Decisão de 12/11/2026: encerrar `corrigir-pendencias-malha` e `integrar-status-operacional-multifonte` com escopo reduzido. Antes do encerramento havia, respectivamente, 17/19 e 15/19 tarefas concluídas. Os seis itens abaixo foram **adiados, não executados e não aprovados**. A redução de escopo não acrescenta validações à entrega nem modifica o funcionamento do projeto.

## Itens transferidos

### corrigir-pendencias-malha

- **Não executado:** Certificar tempos e incluir os retornos diretos do Expresso L10 com custos documentados.
- **Não executado:** Repetir o teste administrativo de gravações simultâneas de trechos por HTTP autenticado.

### integrar-status-operacional-multifonte

- **Não executado:** Receber token Direto dos Trens e validar resposta autorizada, limites, datas e condições de uso.
- **Não executado:** Confirmar condições para ativação em serviço público; a configuração local não equivale a hospedagem pública.
- **Não executado:** Confirmar fuso de dataGeracao CPTM; enquanto ausente, usar apenas coleta local como referência de validade.
- **Não executado:** Revisar cobertura 6/7/13 e serviços especiais após obter a API, sem inferir normalidade.

## Limitações atuais e condições para retomada

- **Expresso L10:** os retornos diretos pendentes podem deixar de ser oferecidos como opção mais rápida. Retomar com estimativas documentadas e simulações antes/depois, sem publicar custos inventados.
- **Administração da malha:** a disputa de gravações de trechos por HTTP autenticado não foi retestada. O índice e os testes existentes não equivalem a esse ensaio. Fazer manutenção por uma pessoa de cada vez reduz a exposição; a comprovação requer ensaio isolado. Isso é independente da exclusividade das viagens de passageiros já validada.
- **Direto dos Trens:** adaptador preparado, mas resposta autenticada ainda não validada. Aguardar credencial autorizada e validar limites, datas, formato e condições antes de ativar.
- **Uso público:** configuração e validação locais não comprovam condições de uso nem prontidão para publicação pública. Essa revisão continua necessária antes de disponibilizar as fontes publicamente.
- **CPTM:** fuso de `dataGeracao` não confirmado. A validade usa a coleta local como referência; coleta recente não comprova que a informação na origem seja recente.
- **Cobertura de status:** a evidência local cobre 12 linhas (1/2/3/4/5/8/9/10/11/12/15/17). Linhas 6/7/13 e serviços especiais sem resposta própria permanecem indisponíveis, sem inferir normalidade. Não houve nova coleta nesta revisão.

A busca e a concorrência permanecem independentes das fontes de status. O último retorno é preservado em falhas conforme a política existente, com validade e datas disponíveis no estado/painel detalhado; isso não garante atualização contínua de terceiros. Estimativas de tempo não são garantia de duração real.

## Evidências e alcance

A configuração ausente da concorrência foi validada por **HTTP local isolado**, não HTTP no runtime nativo do Xano: [método e limites](xano/http-local-configuracao-ausente-2026-11-12.md). Esse teste não substitui o ensaio administrativo de trechos.

Os testes e observações anteriores permanecem com suas datas e limites. Não foram feitas novas chamadas de teste, alterações de código, malha, parâmetros, credenciais ou configuração para este encerramento. A data do arquivo OpenSpec corresponde à decisão de encerramento com escopo reduzido em 12/11, não a uma alegação de que todos os itens originais foram executados nessa data.
