# Exemplos da API local de planejamento

As rotas abaixo usam o cookie de sessão `HttpOnly` criado pelo login. O token
não faz parte do corpo, da URL ou das respostas públicas.

## Listagem de estações

`GET /api/planning/stations`

```json
[
  {
    "id": 1,
    "name": "Vergueiro",
    "label": "Vergueiro · Linha 1 - Azul — Metrô"
  }
]
```

## Consulta bem-sucedida

`POST /api/planning/route`

```json
{
  "origin_id": 1,
  "destination_id": 2
}
```

Resposta `200`:

```json
{
  "origin": "Vergueiro",
  "destination": "Paraíso",
  "stations": ["Vergueiro", "Paraíso"],
  "seconds": 120,
  "minutes": 2,
  "transfer_count": 0,
  "segments": [
    {
      "origin": "Vergueiro",
      "destination": "Paraíso",
      "line": "Linha 1 - Azul",
      "operator": "Metrô",
      "direction": "Jabaquara",
      "segment_type": "ferroviario",
      "directed": false,
      "service_id": null,
      "seconds": 120
    }
  ],
  "transfers": []
}
```

Quando há mudança de linha, `seconds` inclui 600 segundos por baldeação e
`transfers` informa a estação e as linhas envolvidas.

## Respostas de erro

As respostas seguem o formato padrão de erro do FastAPI:

```json
{
  "detail": "mensagem pública"
}
```

| Situação | HTTP | Mensagem pública |
|---|---:|---|
| Sessão ausente | 401 | Entre na sua conta para planejar um trajeto. |
| Sessão inválida ou expirada | 401 | Sua sessão expirou. Entre novamente. |
| Origem igual ao destino | 400 | Selecione estações diferentes para origem e destino. |
| ID ausente, não inteiro ou não positivo | 422 | Erro de validação do corpo da requisição. |
| Estação inválida ou entrada recusada pelo Xano | 400 | Verifique as estações selecionadas e tente novamente. |
| Trajeto não encontrado | 404 | Não foi encontrado trajeto para essas estações. Atualize a lista e tente novamente. |
| Xano indisponível | 503 | O serviço de trajetos está indisponível. Tente novamente. |
| Falha ao verificar a sessão | 503 | Não foi possível verificar sua sessão. Tente novamente. |
| Resposta inconsistente ou incompleta | 502 | Não foi possível obter um resultado válido. Tente novamente. |

Mensagens internas do Xano, credenciais e tokens não devem ser incluídos nessas
respostas.
