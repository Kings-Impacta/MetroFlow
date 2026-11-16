// Lista todas as estacoes cadastradas, ativas e inativas, com as linhas ativas
// que as atendem. Sem filtro por situacao da estacao.
query "admin/estacoes" verb=GET {
  api_group = "administracao"
  auth = "usuarios"

  input {
  }

  stack {
    // Mesmas verificacoes de sessao publicadas em trajetos/buscar.
    db.get usuarios {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "ativo", "email_verificado", "versao_sessao"]
    } as $usuario_autenticado
  
    precondition ($usuario_autenticado != null && $usuario_autenticado.ativo && $usuario_autenticado.email_verificado) {
      error_type = "unauthorized"
      error = "Sessão inválida."
    }
  
    precondition (`$auth.extras.versao_sessao` != null && `$auth.extras.versao_sessao` == ($usuario_autenticado.versao_sessao ?? 1)) {
      error_type = "unauthorized"
      error = "Sessão inválida."
    }
  
    db.query administradores {
      where = $db.administradores.usuario_id == $auth.id
      return = {type: "single"}
    } as $administrador
  
    precondition ($administrador != null) {
      error_type = "accessdenied"
      error = "Acesso restrito a administradores."
    }
  
    db.query estacoes {
      return = {type: "list"}
      output = ["id", "nome", "codigo", "ativa"]
    } as $estacoes
  
    db.query estacoes_linhas {
      join = {
        linha   : {
          table: "linhas"
          where: $db.estacoes_linhas.linha_id == $db.linha.id
        }
        operador: {
          table: "operadores"
          where: $db.linha.operador_id == $db.operador.id
        }
      }
    
      where = $db.linha.ativa == true && $db.operador.ativo == true
      eval = {
        linha_nome  : $db.linha.nome
        linha_codigo: $db.linha.codigo
        linha_cor   : $db.linha.cor
      }
    
      return = {type: "list"}
      output = [
        "estacao_id"
        "linha_id"
        "linha_nome"
        "linha_codigo"
        "linha_cor"
      ]
    } as $vinculos
  
    var $dados {
      value = {estacoes: $estacoes, vinculos: $vinculos}
    }
  
    var $resultado {
      value = $dados
        |lambda:"const list = (v) => (Array.isArray(v) ? v : []); const byStation = new Map(); for (const v of list($this.vinculos)) { const key = Number(v.estacao_id); if (!byStation.has(key)) byStation.set(key, []); if (!byStation.get(key).some((l) => l.id === v.linha_id)) byStation.get(key).push({ id: v.linha_id, nome: v.linha_nome, codigo: v.linha_codigo, cor: v.linha_cor == null ? null : v.linha_cor }); } return { estacoes: list($this.estacoes).map((e) => ({ id: e.id, nome: e.nome, codigo: e.codigo, ativa: e.ativa === true, linhas: byStation.get(Number(e.id)) || [] })) };"
    }
  }

  response = $resultado
  guid = "7MEkxHEC7IG_pzGyQqpPdQ5gPbQ"
}