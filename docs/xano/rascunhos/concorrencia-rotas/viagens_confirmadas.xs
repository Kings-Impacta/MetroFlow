// Viagens confirmadas pelos usuarios; base da lotacao estimada dos trechos.
// Os registros sao mantidos sem prazo de exclusao e nao sao devolvidos por
// nenhuma resposta publica.
table viagens_confirmadas {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int usuario_id {
      table = "usuarios"
    }
  
    // Momento da confirmacao e fim da janela (confirmacao + soma de
    // tempo_estimado dos trechos, sem a penalidade de baldeacao).
    timestamp confirmada_em
  
    timestamp fim_janela
  
    // Trechos em ordem: ordem, trecho_id, estacao_origem_id,
    // estacao_destino_id (sentido percorrido), tempo_estimado, tipo e
    // servico_id copiados da tabela trechos no momento da confirmacao.
    json trechos
  
    bool substituida?
    timestamp? substituida_em?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "usuario_id", op: "asc"}]}
    {type: "btree", field: [{name: "fim_janela", op: "desc"}]}
  ]

  guid = "6hFkS51Jy4ECPXqI75IBokK573s"
}