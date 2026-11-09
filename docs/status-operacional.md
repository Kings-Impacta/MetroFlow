# Status operacional das linhas

## Entrega de 09/11/2026

O cliente disponibiliza condições operacionais na página `/status` e, após uma busca, somente para as linhas do percurso. Um endpoint separado, autenticado por sessão (`GET /api/planning/line-status`), concentra a integração. Status não modifica o caminho, seus tempos nem os parâmetros de concorrência; busca e registro não fazem chamadas às fontes externas.

A ausência de dado aparece como **indisponível**, nunca como operação normal. São preservados o rótulo e a descrição da fonte, a origem, a coleta e, quando existirem, a última mudança e a última verificação. Uma situação antiga que continua verificada pode ser atual. O booleano `operacao_normal` da ARTESP inclui operação com restrições e não é usado isoladamente para normalizar a situação.

## Fontes e ativação

- ARTESP: adaptador do contrato documentado em `empresas[].linhas[].status`, autenticação pelo cabeçalho `Authorization: Api-Key`, atribuição CC BY-NC 4.0 e correspondência por código de linha. A chave foi informada como disponível pelo usuário, mas não foi recebida nem configurada nesta sessão.
- Complemento agregado Metrô/CPTM: adaptador preparado e testado com amostras sintéticas do contrato observado. Continua desativado; ativar somente depois de confirmar condições de consumo/republicação e validar amostras reais. Não é apresentado como API com contrato estável já certificado.
- A ARTESP prevalece nas linhas delegadas 4/5/6/7/8/9/17. Nas demais, somente o complemento autorizado fornece status. Divergências entre fontes ficam em log genérico. A relação de responsabilidade exige revisão quando houver transferência de operador.
- Expresso Aeroporto e Expresso L10 aparecem como indisponíveis: o status da linha regular não comprova a condição do serviço especial.

As fontes ficam desligadas por padrão. Configure no ambiente **do backend**, antes de iniciar o Reflex:

```powershell
$env:METROFLOW_ARTESP_ENABLED = "1"
$statusKey = Read-Host "Chave ARTESP (não será exibida)" -AsSecureString
$env:METROFLOW_ARTESP_API_KEY = [System.Net.NetworkCredential]::new("", $statusKey).Password
$env:METROFLOW_STATUS_COMPLEMENTAR_AUTORIZADO = "0"
```

Inicie o projeto normalmente nesse mesmo terminal. Não envie a chave ao chat nem a coloque no Git. O arquivo `.env.example` é apenas referência; estas instruções usam variáveis do processo e não dependem de carregamento automático de `.env`. Sem chave e ativação, a consulta retorna indisponível e o planejamento continua.

## Cache e falhas

O cache SQLite `.cache/line-status.sqlite3`, ignorado pelo Git, é compartilhado entre usuários e processos que apontam para o mesmo arquivo no servidor. Reserve uma tentativa a cada cinco minutos e no máximo 12 em uma janela móvel de uma hora por chave; erros também contam. HTTP 429 suspende novas tentativas por uma hora. Timeout, JSON inválido, tamanho excessivo, cache sem permissão e erro HTTP não são repassados ao planejador. Redirecionamentos não são seguidos com a credencial.

A reserva é transacional e antecede a chamada HTTP; consultas concorrentes reutilizam o cache ou recebem indisponível enquanto a primeira atualização termina. Uma falha conhecida torna o último dado desatualizado. A validade vence após dez minutos desde a coleta/verificação; após uma hora o valor não é exibido. Sem `verificado_em`, somente a idade da coleta é conhecida. O botão permite nova consulta, mas não ignora a reserva nem o limite da origem. O quadro indica a condição na última consulta, não uma assinatura contínua de alertas.

Múltiplas máquinas precisam compartilhar um coletor/cache central antes de ativar a mesma chave; arquivos SQLite separados não coordenam a cota entre servidores. O cache não contém chaves ou dados de viagens. O hash da chave serve somente para separar a cota e o cache por credencial. Descrições são apresentadas como texto, não HTML.

## Validação e limites

Testes sem rede real cobrem normalização, nulabilidade, situações desconhecidas, datas, prioridade, falhas, cota, concorrência da reserva, cache entre instâncias, sessão, proteção de credenciais e manutenção da busca/registro após falha de status. A interface foi compilada em cópia isolada, sem reiniciar o aplicativo em uso ou alterar o Xano.

Ainda falta configurar a chave no ambiente usado pelo usuário e conferir uma resposta autenticada real, incluindo a cobertura efetiva e os horários informados. A publicação do código não significa que as fontes foram ativadas. Autorizações e ativação do complemento continuam pendentes no OpenSpec; esta entrega não conclui o P5 de lotação real.

Fontes: [documentação ARTESP](https://ccm.artesp.sp.gov.br/metroferroviario/api/docs/) (releitura de 09/11/2026) e [avaliação anterior do complemento](fontes-status-operacional-2026-10-21.md).


### Resultado dos checks antes da entrega

- 231 testes e 55 subtestes aprovados, incluindo 23 testes novos de status; um aviso preexistente de depreciação do TestClient.
- Compilação seca do Reflex aprovada; avisos do ambiente Windows e de Radix não impediram a compilação.
- 12 itens do OpenSpec aprovados em validação estrita; `git diff --check` sem erros.
- A execução local apontou inicialmente falhas de acesso ao diretório temporário do ambiente de testes; a repetição usou uma pasta temporária gravável dentro do checkout, sem modificar testes anteriores.
- Nenhum token foi enviado às fontes nos testes. Ainda não há validação de uma resposta ARTESP autenticada real ou de uma ativação em produção.
