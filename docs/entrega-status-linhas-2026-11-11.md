# Integração de status e correções validadas

A entrega acrescenta cobertura informativa de Metrô, CPTM e Motiva. A busca, a malha, a calibração e o registro por concorrência permanecem independentes das fontes externas.

## Executar na pasta do projeto

Após atualizar a main e parar o servidor anterior com Ctrl+C:

```powershell
.\iniciar-status-local.ps1
```

O iniciador usa o ambiente `.venv` e as dependências registradas pelo projeto; não depende dos caminhos usados durante a validação. Habilita apenas as três fontes públicas no processo local, sem chave, e restaura as variáveis ao sair. O log continua em `reflex.log`. Fontes permanecem desligadas na configuração padrão; esse iniciador é a opção explícita para usá-las localmente.

## Cobertura e interface

| Fonte | Linhas observadas |
| --- | --- |
| Metrô | 1, 2, 3, 4, 5, 15 e 17 |
| CPTM | 10, 11 e 12 |
| Motiva | 8 e 9 |

Linhas 6, 7 e 13 e os serviços especiais sem resposta própria permanecem indisponíveis. A API Direto dos Trens está preparada, mas aguarda token e validação autorizada. O coletor experimental do site, bloqueado por verificação interativa, não integra o código entregue.

O resumo do trajeto lista as linhas usadas, alinhadas à direita das métricas. Cada embarque apresenta seu indicador com bolinha e texto. A lista não duplica linhas, não atribui status a caminhadas e não modifica o caminho. Os detalhes de fonte e datas ficam em `/status` e nos detalhes dos indicadores.

## Atualização e falhas

A tela consulta a cada minuto; o cache limita chamadas às origens a um intervalo mínimo de cinco minutos, respeitando prazos maiores, política de armazenamento e recuo. O último retorno armazenável e suas datas permanecem até uma nova resposta válida, inclusive em falhas prolongadas ou retorno parcial. Sem retorno anterior, informa indisponibilidade. O texto compacto mostra somente o último status, conforme decisão do usuário; a validade interna continua registrada.

Somente o Metrô utiliza a correção de transporte IPv4, conexão de cinco segundos e leitura de quinze segundos. HTTPS e certificado continuam validados. Timeout ou resposta inválida não provoca repetição imediata, não apaga dados nem bloqueia busca e concorrência.

## Validação

- Versão final limpa sobre main: 276 testes e 86 subtestes passaram; compilação Reflex e os 12 itens OpenSpec passaram.
- Foram excluídos seis testes exclusivos do coletor experimental; os testes de repetição automática permanecem na suíte.
- Na versão local validada, as sete linhas do Metrô renovaram automaticamente às 11:35, 11:40 e 11:46 em 11/11, sem falha observada nesses ciclos.
- A retenção de dados e datas após um dia de falha simulada passou em cache isolado.
- A busca interna Barra Funda → Paraíso foi observada pela Sé e Linha 1; o usuário confirmou outra conta pelas linhas 4 e 2. Não houve nova auditoria de IDs e sobreposição no Xano nessa rodada.

Nenhuma credencial, cache, arquivo de treinamento ou dado da malha é distribuído. A validação não promete disponibilidade contínua das origens nem representa lotação oficial. Ver [guia de status](status-operacional.md) e [correção do Metrô](correcao-consulta-metro-2026-11-11.md).

## Confirmação após entrega na main

O PR #41 foi integrado e os checks da main passaram. Em 11/11, o cliente reiniciado na main renovou automaticamente as fontes e o Xano confirmou as viagens 67/68, com reprodução da calibração e dos limites de concorrência. A alternativa desta rodada foi pela Luz, não por República. Veja o [reteste e as pendências revisadas](xano/reteste-main-status-concorrencia-2026-11-11.md). As evidências locais anteriores acima permanecem históricas.
