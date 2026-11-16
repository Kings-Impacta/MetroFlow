## 1. Dados de coordenadas

- [x] 1.1 Criar `docs/dados/coordenadas-estacoes.csv` com as 10 estações de `docs/dados/tempos/` e as demais estações da malha disponíveis em fonte pública, priorizando o centro e a região de Paraíso e Vila Mariana, com fonte e data de coleta em cada linha
- [x] 1.2 Conferir os nomes do CSV com os nomes exibidos pelo planejador e registrar as estações sem correspondência

## 2. Backend Python

- [x] 2.1 Criar a leitura e a validação do CSV de coordenadas, com cache e interruptor `METROFLOW_LOCALIZACAO`
- [x] 2.2 Acrescentar `latitude` e `longitude` opcionais a `StationChoice` e preenchê-las em `GET /api/planning/stations`
- [x] 2.3 Testar registros válidos e inválidos, estação repetida, arquivo ausente, interruptor e campos opcionais na lista de estações

## 3. Interface Reflex

- [x] 3.1 Criar o script de localização executado no navegador, que devolve apenas a estação mais próxima e a distância
- [x] 3.2 Acrescentar ao `PlanningState` o aviso, o pedido de localização, o callback validado e a limpeza da distância na escolha manual
- [x] 3.3 Exibir no planejador o aviso com "Usar minha localização" e "Agora não" e o texto da distância abaixo da origem
- [x] 3.4 Testar o script com navegador simulado (sucesso, permissão negada, sem localização, tempo esgotado, mais de 5 km) e o estado do planejador

## 4. Documentação e validação

- [x] 4.1 Atualizar o README, o `ARCHITECTURE.md` e o modelo de domínio com a funcionalidade, o interruptor e o limite de HTTPS
- [x] 4.2 Executar a suíte completa de testes e a validação estrita do OpenSpec e registrar o resultado
- [x] 4.3 Registrar os limites não cobertos pelos testes: precisão real do GPS e pedido de permissão em navegadores reais

## Registro de validação — 16/11/2026

- Dados: 188 estações com coordenadas, sem estação da malha faltando. As 10 que já estavam em `docs/dados/tempos/` mantêm os valores do GTFS da SPTrans e da Wikipédia; as demais vêm do OpenStreetMap (ODbL). Vergueiro, Jabaquara e as duas estações da Lapa foram escolhidas manualmente. A menor distância entre vizinhas é de cerca de 200 m (Consolação e Paulista); as maiores correspondem a serviços expressos.
- Suíte completa: 425 testes e 119 subtestes passaram, sem testes ignorados, com 1 aviso de depreciação já existente. Os testes do script de localização rodaram com Node.js e geolocalização simulada.
- `reflex compile --dry`: compilação concluída com sucesso.
- `openspec validate --all --strict`: 15 itens válidos.
- Limites: o pedido real de permissão e a precisão do GPS não foram testados em navegadores reais de celular e computador. A associação depende de nomes iguais aos do Xano, conferidos com `docs/dados/tempos/cobertura/cobertura-deslocamentos.json`, e não com uma resposta viva do Xano. Fora do `localhost`, a localização exige HTTPS. Coordenadas do OpenStreetMap marcam o prédio ou a área da estação, não um acesso específico.
