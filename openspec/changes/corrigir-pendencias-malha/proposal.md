## Why

A restauração preservou a conectividade, mas deixou serviços especiais sem vínculo,
ordenação incompleta do Expresso Aeroporto e ausência do índice único canônico.
A busca ignora as janelas de funcionamento cadastradas e a configuração da Linha
17 ainda contém o horário anterior ao ampliado em setembro de 2026.

## What Changes

- Vincular Expresso Linha 10 e Linha 17 aos serviços correspondentes.
- Completar Brás na ordenação do Expresso Aeroporto.
- Atualizar a Linha 17 para segunda a sábado, 06h–22h, inclusive feriados nesses dias.
- Aplicar janelas cadastradas na busca e confirmação, no fuso America/Sao_Paulo.
- Restaurar índice único da chave canônica e controlar falhas de gravação.
- Corrigir o operador da Linha 7 para TIC Trens, sem renomear a CPTM das demais linhas.
- Corrigir a Linha 17 para o Metrô, responsável pela operação transitória atual.
- Preservar tempos recuperados, topologia e penalidade geral de transferência.
- Corrigir o trecho 200 para Brooklin Paulista–Washington Luís e os sentidos da
  Linha 17, reconhecendo a troca obrigatória de trem mesmo sem mudar de linha.
- Comparar as alternativas pela Sé, República/Paulista e Pinheiros sem impor
  preferência por quantidade de estações; preservar a regra de menor tempo.

## Capabilities

### Added Capabilities

- `disponibilidade-malha`: exclui serviços fora da janela cadastrada e preserva trajetos regulares.

## Impact

Dados e endpoints de planejamento no Xano; cópias locais, testes e documentação.
Não publica fontes de status operacional. Não inventa tempos de caminhada nem
tarifas: gratuidade de Tatuapé/Itaquera exige contexto de tarifa que o contrato
atual não possui. As ligações físicas permanecem disponíveis para viagens pagas.
