# Margem pública do tempo estimado — 05/11/2026

A busca do Xano no workspace 149130, branch v1, acrescenta o campo `tempo_estimado_total_segundos` com o total-base mais 60 segundos. O total-base, os trechos, as esperas, as baldeações, a seleção de rotas e o registro de viagens permanecem com a cronologia anterior. O cliente atualizado nesta cópia local exibe o novo valor como “Tempo estimado” e aceita respostas antigas sem o campo.

Antes da publicação foram exportados 26 documentos de código e as oito tabelas de configuração e malha do planejamento, com manifesto SHA-256, em `outputs/backup-xano-calibracao-20261105-092117`. A prévia indicou um único endpoint, `POST trajetos/buscar`. A releitura após a publicação confirmou que só esse documento mudou e que sua função corresponde à validada.

Foram executadas 320 buscas e 120 cenários simulados de concorrência em cada versão da malha, a publicada e a calibrada em laboratório, mais 57 casos da Linha 6. Em cada busca disponível, o campo público subiu 60 segundos e os demais campos foram idênticos. O cliente passou em 239 testes e 39 subtestes de planejamento e compilou com Reflex. O relatório das simulações está em `outputs/margem-total-20261105/validacao.json`.

A publicação foi restrita à margem compatível com o contrato já em uso. A calibração dos 419 sentidos continua em laboratório. Para ativá-la, busca, confirmação e cliente precisam aceitar a mesma referência de calibração no ambiente remoto. Hoje o cliente deliberadamente limita esse contrato ao ambiente local. O cliente que lê a margem continua nesta cópia de trabalho e precisa ser entregue para que a interface em uso exiba o valor novo.
