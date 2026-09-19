# Alterações da malha no Xano — 18/09/2026

Registro das alterações aplicadas no workspace Xano 149130, branch `v1`, fonte
de dados `live`. Este documento registra as decisões relevantes; não substitui
uma exportação oficial do banco.

## Busca de trajetos

- O endpoint `POST /trajetos/buscar` considera 600 segundos por troca de linha.
- A penalidade participa da escolha da melhor rota e do tempo total retornado.
- Trechos direcionados são respeitados.
- O resultado informa sentido, tipo e serviço de cada trecho.
- Os sentidos são calculados pela ordem das estações em `estacoes_linhas`.

## Expresso Aeroporto

Tempos direcionais cadastrados para totalizar 2.100 segundos (35 minutos):

| ID | Trecho | Tempo |
|---:|---|---:|
| 201 | Palmeiras-Barra Funda → Luz | 480 s |
| 202 | Luz → Guarulhos-Cecap | 1.320 s |
| 203 | Guarulhos-Cecap → Aeroporto-Guarulhos | 300 s |
| 207 | Aeroporto-Guarulhos → Guarulhos-Cecap | 300 s |
| 208 | Guarulhos-Cecap → Brás | 1.080 s |
| 209 | Brás → Luz | 240 s |
| 210 | Luz → Palmeiras-Barra Funda | 480 s |

## Outros tempos corrigidos

- Linha 10, Palmeiras-Barra Funda ↔ Luz: 480 segundos por sentido nos registros
  199 e 200.
- Linha 11, Palmeiras-Barra Funda ↔ Luz: 480 segundos no registro 152.

## Validação funcional

- Vila Madalena ↔ Vila Prudente: Linha 2, 1.560 segundos, sem baldeação.
- Paraíso ↔ Palmeiras-Barra Funda: Linhas 1 e 3, 1.680 segundos, uma baldeação
  em Sé.
- Palmeiras-Barra Funda ↔ Aeroporto-Guarulhos: Expresso Aeroporto, 2.100
  segundos, sem baldeação.
- Palmeiras-Barra Funda → Brigadeiro: Linhas 3, 4 e 2, com a integração a pé
  Paulista–Consolação.
