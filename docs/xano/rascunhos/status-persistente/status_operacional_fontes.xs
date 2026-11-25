// RASCUNHO LOCAL. Não publicar nesta etapa. Nenhum vínculo com a malha.
table status_operacional_fontes {
  auth = false
  schema {
    int id
    timestamp created_at?=now
    text codigo filters=trim|lower
    bool autorizada?=false
    bool habilitada?=false
    json condicoes
    json controle
    timestamp trava_em?
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "codigo", op: "asc"}]}
  ]
  guid = "nBzJVwA6uwDNjIqLwNEw9mNNYak"
}
