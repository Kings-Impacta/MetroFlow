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
      "id": 15,
      "origin_id": 1,
      "destination_id": 2,
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
`transfers` informa a estação e as linhas envolvidas. Em cada trecho, `id`,
`origin_id` e `destination_id` identificam o trecho e o sentido percorrido,
usados na confirmação da viagem.

O trajeto apresentado pode ser o principal ou, conforme a mudança
`concorrencia-rotas`, o caminho que o substitui por lotação. A resposta tem a
mesma forma nos dois casos e não informa lotação nem substituição.

## Confirmação de viagem

`POST /api/planning/trip`

```json
{
  "segments": [
    {"id": 15, "origin_id": 1, "destination_id": 2}
  ]
}
```

Resposta `204`, sem corpo. O usuário é obtido da sessão pelo Xano, e o tempo de
cada trecho vem do cadastro. O corpo não aceita outros campos, como usuário ou
tempo. Os trechos devem ser consecutivos, com no máximo 200 itens.

### Orientações de estação

O trecho que encerra uma etapa pode trazer o campo opcional `guidance`, com as
dicas da estação onde o passageiro desce. O campo é omitido quando não há
orientação cadastrada ou quando a funcionalidade é desligada com
`METROFLOW_ORIENTACOES=0`. Fonte e data de coleta não fazem parte da resposta.

```json
{
  "id": 15,
  "origin_id": 1,
  "destination_id": 2,
  "origin": "Vergueiro",
  "destination": "Paraíso",
  "line": "Linha 1 - Azul",
  "operator": "Metrô",
  "direction": "Jabaquara",
  "segment_type": "ferroviario",
  "directed": false,
  "service_id": null,
  "seconds": 120,
  "guidance": {
    "alighting_side": "esquerdo",
    "note": "Desça no carro 4, em frente à escada rolante da saída Rua Tutóia."
  }
}
```

Os valores acima são ilustrativos. `alighting_side` aceita `esquerdo`, `direito`
ou `ambos`; `note` é a observação adicional, com até 200 caracteres. Qualquer um
dos dois pode ser `null`. Uma falha na leitura das orientações não altera o status da resposta:
o trajeto é devolvido sem o campo.

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
| Viagem com trechos desconexos ou recusada pelo Xano | 400 | Não foi possível confirmar esta viagem. Busque o trajeto novamente. |
| Corpo da confirmação vazio, com campo extra ou ID inválido | 422 | Erro de validação do corpo da requisição. |

Mensagens internas do Xano, credenciais e tokens não devem ser incluídos nessas
respostas.
