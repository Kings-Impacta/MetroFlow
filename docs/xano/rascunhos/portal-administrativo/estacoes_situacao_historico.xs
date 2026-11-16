// Registro das alteracoes de situacao das estacoes feitas pelo painel
// administrativo. Acessivel somente no Xano; nenhuma resposta publica o devolve.
table estacoes_situacao_historico {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int estacao_id {
      table = "estacoes"
    }
  
    // Situacao aplicada pela alteracao.
    bool ativa
  
    // Administrador da sessao que fez a alteracao.
    int usuario_id {
      table = "usuarios"
    }
  
    timestamp alterada_em
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "estacao_id", op: "asc"}]}
    {type: "btree", field: [{name: "alterada_em", op: "desc"}]}
  ]

  guid = "mS9-1ysz2cSiL2yd4eeY9_59V4w"
}