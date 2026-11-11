> Registro da validação local. Para executar a entrega do repositório, use `iniciar-status-local.ps1`; os caminhos em outputs citados como evidência pertencem ao histórico da validação.

# Status automático local: CPTM

Configuração de demonstração validada em 09/11/2026, sem publicação na main nem alteração no Xano. Usa o adaptador CPTM existente e a repetição automática da tela, na cópia isolada deste cliente.

## Cobertura real

A consulta HTTPS real ao endereço público `https://api.cptm.sp.gov.br/AppCPTM/v1/Linhas/ObterStatus` respondeu HTTP 200 e retornou somente L10, L11 e L12, com situação Operação Normal na consulta. Isso é uma observação datada, não uma garantia de operação futura. L13 não veio na resposta. Todas as linhas e serviços ausentes permanecem indisponíveis; não são preenchidos como normais.

O iniciador habilita somente CPTM, desliga os demais adaptadores e limpa a seleção do arquivo de coleta pública durante o processo. Não precisa do coletor do Direto dos Trens nem de chave. O acesso ao painel continua exigindo login.

## Atualização e isolamento

A tela relê o status a cada minuto enquanto montada. O cache compartilhado consulta a fonte no máximo a cada cinco minutos, respeitando também Cache-Control, limitações e recuo em caso de erro. Não é uma garantia de atualização instantânea. A segunda leitura real preservou o horário de coleta, confirmando reutilização do cache. O arquivo separado `cptm-status.sqlite3` fica na pasta dos iniciadores.

Falhas da CPTM não participam do cálculo do trajeto nem do registro da viagem. Após a revisão de retenção, os últimos dados armazenáveis permanecem como desatualizados até uma nova resposta válida, sem renovar sua data. Sem retorno anterior, aparece indisponível; não são inventados dados de operação normal.

## Iniciar

Na pasta raiz deste chat, o arquivo `iniciar-status-local.ps1` inicia a cópia isolada. Pare o coletor anterior e o Reflex anterior com Ctrl+C antes de executar o iniciador. Abra `http://localhost:3000/status` e atualize com Ctrl+F5. Mantenha somente o terminal desse cliente aberto. Ao encerrar, Ctrl+C restaura as variáveis do terminal; o projeto habitual não é modificado.

## Validação

- Consulta real pelo adaptador e pelo serviço: L10, L11, L12 atuais; todos os demais indisponíveis.
- Segunda leitura real preservou a coleta via cache; relatório local em `outputs/demo-status-aula-20261109/validacao-cptm.json`, na raiz do chat.
- 262 testes e 75 subtestes passaram, incluindo falha do status com busca e registro funcionando e regras de concorrência.
- Compilação Reflex em modo de verificação passou. Houve avisos existentes de depreciação e falha não fatal ao consultar informações de CPU neste ambiente.
- Iniciador PowerShell validado sintaticamente.

Não foi iniciado um segundo servidor sobre a porta ocupada nem executado novo teste com duas contas reais. A verificação desta entrega é local, com consulta real da CPTM e testes de regressão; a confirmação visual depende de iniciar este cliente.
