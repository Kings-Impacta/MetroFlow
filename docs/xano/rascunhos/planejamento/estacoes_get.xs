// Lista somente estações, linhas e operadores ativos.
query "estacoes" verb=GET {
  api_group = "planejamento"
  auth = "usuarios"

  input {
  }

  stack {
    db.query "estacoes" {
      where = $db.estacoes.ativa == true
      sort = {nome: "asc"}
      output = ["id", "nome", "codigo"]
    } as $estacoes

    db.query "estacoes_linhas" {
      join = {
        linha: {
          table: "linhas"
          type : "inner"
          where: $db.estacoes_linhas.linha_id == $db.linha.id
        }
        operador: {
          table: "operadores"
          type : "inner"
          where: $db.linha.operador_id == $db.operador.id
        }
        estacao: {
          table: "estacoes"
          type : "inner"
          where: $db.estacoes_linhas.estacao_id == $db.estacao.id
        }
      }
      eval = {
        linha_nome    : $db.linha.nome
        linha_codigo  : $db.linha.codigo
        linha_cor     : $db.linha.cor
        operador_id   : $db.operador.id
        operador_nome : $db.operador.nome
        operador_codigo: $db.operador.codigo
      }
      where = $db.estacao.ativa == true && $db.linha.ativa == true && $db.operador.ativo == true
      output = ["estacao_id", "linha_id", "linha_nome", "linha_codigo", "linha_cor", "operador_id", "operador_nome", "operador_codigo"]
    } as $vinculos

    var $dados {
      value = {estacoes: $estacoes, vinculos: $vinculos}
    }

    var $resultado {
      value = $dados|lambda:"return {estacoes: $this.estacoes.map((e) => ({id: e.id, nome: e.nome, codigo: e.codigo, linhas: $this.vinculos.filter((v) => v.estacao_id === e.id).map((v) => ({id: v.linha_id, nome: v.linha_nome, codigo: v.linha_codigo, cor: v.linha_cor, operador: {id: v.operador_id, nome: v.operador_nome, codigo: v.operador_codigo}}))}))};"
    }
  }

  response = $resultado
}
