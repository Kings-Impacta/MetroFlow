// Ativa ou inativa uma estacao. Altera somente o campo ativa e registra a
// alteracao na mesma transacao. Se a situacao pedida ja for a atual, responde
// com ela sem gravar. O administrador vem da sessao, nunca do corpo.
query "admin/estacoes/situacao" verb=POST {
  api_group = "administracao"
  auth = "usuarios"

  input {
    int estacao_id
    bool ativa
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
  
    db.get estacoes {
      field_name = "id"
      field_value = $input.estacao_id
      output = ["id", "ativa"]
    } as $estacao
  
    precondition ($estacao != null) {
      error_type = "notfound"
      error = "Estação não encontrada."
    }
  
    var $agora {
      value = now
    }
  
    conditional {
      if ($estacao.ativa != $input.ativa) {
        db.transaction {
          stack {
            db.patch estacoes {
              field_name = "id"
              field_value = $input.estacao_id
              data = {ativa: $input.ativa}
            } as $estacao_alterada
          
            db.add estacoes_situacao_historico {
              data = {
                estacao_id : $input.estacao_id
                ativa      : $input.ativa
                usuario_id : $auth.id
                alterada_em: $agora
              }
            } as $registro
          }
        }
      }
    }
  
    db.get estacoes {
      field_name = "id"
      field_value = $input.estacao_id
      output = ["id", "ativa"]
    } as $atual
  }

  response = {id: $atual.id, ativa: $atual.ativa}
  guid = "Q1weeAn6gQljqd7anezPlmERw6M"
}