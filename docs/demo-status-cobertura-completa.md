> Registro da validação local. Para executar a entrega do repositório, use `iniciar-status-local.ps1`; os caminhos em outputs citados como evidência pertencem ao histórico da validação.

# Cobertura provisória local enquanto aguardamos a API

Em 09/11/2026, o usuário autorizou habilitar localmente todas as linhas disponíveis pelas fontes públicas já avaliadas. Esta configuração substitui, para a demonstração, a anterior somente CPTM. Não é uma publicação na main, alteração no Xano ou ativação pública.

## Cobertura observada

| Fonte pública | Linhas reconhecidas |
| --- | --- |
| Quadro Direto do Metrô | 1, 2, 3, 4, 5, 15 e 17 |
| JSON oficial CPTM | 10, 11 e 12 |
| Quadro oficial Motiva/ViaMobilidade | 8 e 9 |
| Sem cobertura nessas fontes | 6, 7 e 13 |

São 12 das 15 linhas cadastradas. EXP-AER e EXP-L10 também permanecem indisponíveis: não herdam automaticamente o estado da linha regular. A resposta CPTM não trouxe L13; nenhum dado foi inferido para preencher essa ausência.

Fontes consultadas:

- https://www.metro.sp.gov.br/sua-viagem/direto-metro/ (quadro incorporado no próprio site).
- https://api.cptm.sp.gov.br/AppCPTM/v1/Linhas/ObterStatus
- https://trilhos.motiva.com.br/viamobilidade8e9/situacao-das-linhas/

## Leitura da Motiva

As abas são vinculadas aos painéis por seus identificadores acessíveis e títulos 8-Diamante/9-Esmeralda, sem inferir pela cor ou ordem. O adaptador lê somente a marcação HTML pública e escolhe a ocorrência com maior data por linha, em Brasília. Histórico anterior não permanece como alerta atual quando existe uma publicação posterior. Empates conflitantes, datas futuras ou estrutura incompatível deixam a fonte indisponível. Não executa scripts nem acessa credenciais internas.

A data da ocorrência é diferente do horário da coleta: uma operação normal publicada horas antes continua sendo a última situação publicada se a consulta atual a confirmou no quadro. A validade envelhece pelo horário da coleta; não se inventa uma data de verificação informada pela fonte.

## Atualização e falhas

O painel consulta o backend a cada minuto enquanto aberto. Cada fonte usa cache compartilhado e intervalo mínimo de cinco minutos; Motiva e CPTM respeitam também Cache-Control e recuo em falhas. Timeout, mudança no HTML ou queda de uma fonte não fazem as outras desaparecerem. Nenhum estado ausente é preenchido como operação normal.

Uma primeira consulta do serviço ao Metrô falhou; a consulta direta seguinte pelo mesmo adaptador funcionou. A reserva do cache foi mantida para respeitar o intervalo antes de repetir a validação integrada. Falhas transitórias devem continuar visíveis como indisponibilidade, sem prometer cobertura contínua.

No ciclo seguinte, a validação integrada real confirmou as 12 linhas atuais: L1, L2, L3, L4, L5, L8, L9, L10, L11, L12, L15 e L17. Somente L6, L7 e L13 ficaram sem cobertura entre as linhas cadastradas. A segunda leitura preservou os horários de coleta das três fontes, confirmando o uso do cache.

Busca, escolha de alternativa e registro da viagem não consomem esse status. A nova fonte é desativada por padrão; somente o iniciador local habilita os três adaptadores e limpa o arquivo de demonstração anterior. Direto dos Trens/ARTESP permanecem desligados.

## Execução

Pare o coletor anterior e o Reflex anterior com Ctrl+C. Execute `iniciar-status-local.ps1` na raiz do projeto e abra `http://localhost:3000/status` com Ctrl+F5. Não precisa de outro coletor nem de token. As variáveis são restauradas ao encerrar; o cliente habitual e suas configurações não são modificados.

O relatório de consulta real fica em `outputs/demo-status-aula-20261109/validacao-status-completo.json`, na raiz do chat. O cache separado fica em `status-completo.sqlite3`, na mesma pasta.

## Verificações locais

- 266 testes e 81 subtestes passaram, incluindo seleção da última ocorrência, vínculo correto entre linhas, campos ausentes, datas futuras, conflito de histórico e falha isolada de fonte.
- Após reforçar a rejeição de número/nome de linha incompatíveis, os quatro testes específicos passaram novamente, com sete subtestes.
- Testes existentes de busca, registro e concorrência passaram, inclusive indisponibilidade do status.
- Compilação Reflex passou, com os avisos existentes de depreciação e de consulta não fatal de CPU.
- OpenSpec: 12 itens passaram na validação estrita.
- Iniciador PowerShell validado sintaticamente.

A validação não cria viagens reais nem substitui um novo teste com duas contas no navegador. A ativação pública e a migração para API continuam para etapa posterior, após acesso e condições de uso confirmados.
