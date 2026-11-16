// Usuarios com papel de administrador do MetroFlow. A concessao e a revogacao
// sao feitas no painel do Xano, inserindo ou removendo a linha; nenhum endpoint
// publico grava nesta tabela.
table administradores {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int usuario_id {
      table = "usuarios"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree|unique"
      field: [{name: "usuario_id", op: "asc"}]
    }
  ]

  guid = "Or6Vex1LAiW465kNLOilnRTVph4"
}