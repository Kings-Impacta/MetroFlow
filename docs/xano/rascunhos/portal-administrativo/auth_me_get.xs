// Obter dados do usuario autenticado e validar versao da sessao
query "auth/me" verb=GET {
  api_group = "auth"
  auth = "usuarios"

  input {
  }

  stack {
    // Busca informacoes do usuario incluindo status e versao da sessao
    db.get usuarios {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "email", "ativo", "email_verificado", "versao_sessao"]
    } as $usuarios
  
    // Rejeita com HTTP 401 generico se o usuario for inexistente, inativo ou nao verificado
    precondition ($usuarios != null && $usuarios.ativo && $usuarios.email_verificado) {
      error_type = "unauthorized"
      error = "Sessão inválida."
    }
  
    // Rejeita com HTTP 401 generico se a versao da sessao no token for diferente da versao no banco
    precondition ($auth.extras.versao_sessao == $usuarios.versao_sessao) {
      error_type = "unauthorized"
      error = "Sessão inválida."
    }
  
    // Indica se o usuario e administrador, somente para adaptar a interface;
    // a autorizacao real e verificada em cada endpoint administrativo.
    db.query administradores {
      where = $db.administradores.usuario_id == $usuarios.id
      return = {type: "single"}
    } as $administrador
  
    var $eh_administrador {
      value = false
    }
  
    conditional {
      if ($administrador != null) {
        var.update $eh_administrador {
          value = true
        }
      }
    }
  }

  response = {
    id           : $usuarios.id
    email        : $usuarios.email
    administrador: $eh_administrador
  }

  history = false
  guid = "-4gYPUjMfwKp353mK5iH4yk7fIs"
}