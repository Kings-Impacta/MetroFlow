// Registra a viagem confirmada pelo usuario da sessao e encerra a anterior.
// A resposta nao devolve registros de viagens.
query "viagens/confirmar" verb=POST {
  api_group = "planejamento"
  auth = "usuarios"

  input {
    // Lista ordenada de {id, estacao_origem_id, estacao_destino_id}.
    json trechos
  }

  stack {
    // Mesmas verificacoes de sessao publicadas em trajetos/buscar (26/10/2026).
    // Busca dados do usuario autenticado para validacao de sessao
    db.get usuarios {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "ativo", "email_verificado", "versao_sessao"]
    } as $usuario_autenticado
  
    // Rejeita com HTTP 401 caso o usuario nao exista, esteja inativo ou nao verificado
    precondition ($usuario_autenticado != null && $usuario_autenticado.ativo && $usuario_autenticado.email_verificado) {
      error_type = "unauthorized"
      error = "Sessão inválida."
    }
  
    // Rejeita com HTTP 401 caso a versao da sessao no token seja diferente da versao no banco
    precondition (`$auth.extras.versao_sessao` != null && `$auth.extras.versao_sessao` == ($usuario_autenticado.versao_sessao ?? 1)) {
      error_type = "unauthorized"
      error = "Sessão inválida."
    }
  
    var $agora {
      value = now
    }
  
    db.query trechos {
      join = {
        linha   : {
          table: "linhas"
          where: $db.trechos.linha_id == $db.linha.id
        }
        operador: {
          table: "operadores"
          where: $db.linha.operador_id == $db.operador.id
        }
      }
    
      where = $db.trechos.ativo == true && $db.linha.ativa == true && $db.operador.ativo == true
      return = {type: "list"}
      output = [
        "id"
        "estacao_origem_id"
        "estacao_destino_id"
        "tempo_estimado"
        "tipo"
        "direcionado"
        "servico_id"
      ]
    } as $trechos
  
    var $dados {
      value = {
        agora              : $agora
        trechos_confirmados: $input.trechos
        trechos            : $trechos
      }
    }
  
    // Valida a sequencia e copia sentido, tempo_estimado, tipo e servico
    // de cada trecho. O tempo nunca e lido do corpo da requisicao.
    var $viagem {
      value = $dados
        |lambda:"const num = (v) => { const n = Number(v); return isNaN(n) ? 0 : n; }; const positive = (v) => Number.isInteger(v) && v > 0; const requested = Array.isArray($this.trechos_confirmados) ? $this.trechos_confirmados : []; const now = num($this.agora); if (requested.length === 0 || requested.length > 200 || now <= 0) return null; const available = new Map($this.trechos.map((t) => [num(t.id), t])); const steps = []; let total = 0; for (const item of requested) { if (!item || typeof item !== 'object') return null; const id = item.id; const fromId = item.estacao_origem_id; const toId = item.estacao_destino_id; if (!positive(id) || !positive(fromId) || !positive(toId) || fromId === toId) return null; const stored = available.get(id); if (!stored) return null; const storedFrom = num(stored.estacao_origem_id); const storedTo = num(stored.estacao_destino_id); const forward = storedFrom === fromId && storedTo === toId; const backward = !Boolean(stored.direcionado) && storedFrom === toId && storedTo === fromId; if (!forward && !backward) return null; if (steps.length && steps[steps.length - 1].estacao_destino_id !== fromId) return null; const seconds = num(stored.tempo_estimado); if (seconds <= 0) return null; total += seconds; steps.push({ ordem: steps.length + 1, trecho_id: id, estacao_origem_id: fromId, estacao_destino_id: toId, tempo_estimado: seconds, tipo: stored.tipo || 'ferroviario', servico_id: stored.servico_id == null ? null : num(stored.servico_id) }); } return { fim_janela: now + total * 1000, trechos: steps };"
    }
  
    precondition ($viagem != null) {
      error_type = "inputerror"
      error = "Trajeto confirmado invalido."
    }
  
    db.transaction {
      stack {
        db.query viagens_confirmadas {
          where = $db.viagens_confirmadas.usuario_id == $auth.id && $db.viagens_confirmadas.substituida == false && $db.viagens_confirmadas.fim_janela > $agora
          return = {type: "list"}
          output = ["id"]
        } as $anteriores
      
        foreach ($anteriores) {
          each as $anterior {
            db.edit viagens_confirmadas {
              field_name = "id"
              field_value = $anterior.id
              data = {substituida: true, substituida_em: $agora}
            } as $encerrada
          }
        }
      
        db.add viagens_confirmadas {
          data = {
            usuario_id   : $auth.id
            confirmada_em: $agora
            fim_janela   : $viagem.fim_janela
            trechos      : $viagem.trechos
            substituida  : false
          }
        } as $registrada
      }
    }
  }

  response = {confirmada: true}
  guid = "mqU-UuFADFAEbvWdQrcR76arpjI"
}