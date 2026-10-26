// Calcula o trajeto principal por menor tempo e, no desempate, menos baldeacoes.
// Quando o principal passa por trecho lotado no sentido percorrido, devolve o
// caminho de menor tempo que evita os trechos lotados; sem esse caminho,
// devolve o principal. A resposta nao contem lotacao nem indicacao de troca.
query "trajetos/buscar" verb=POST {
  api_group = "planejamento"
  auth = "usuarios"

  input {
    int estacao_origem_id
    int estacao_destino_id
  }

  stack {
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
  
    precondition ($input.estacao_origem_id != $input.estacao_destino_id) {
      error_type = "inputerror"
      error = "Origem e destino devem ser diferentes."
    }
  
    db.get estacoes {
      field_name = "id"
      field_value = $input.estacao_origem_id
    } as $origem
  
    db.get estacoes {
      field_name = "id"
      field_value = $input.estacao_destino_id
    } as $destino
  
    precondition ($origem != null && $destino != null) {
      error_type = "notfound"
      error = "Estacao de origem ou destino nao encontrada."
    }
  
    precondition ($origem.ativa && $destino.ativa) {
      error_type = "inputerror"
      error = "A origem e o destino precisam estar ativos."
    }
  
    db.query estacoes {
      where = $db.estacoes.ativa == true
      return = {type: "list"}
      output = ["id", "nome", "codigo"]
    } as $estacoes
  
    db.query linhas {
      join = {
        operador: {
          table: "operadores"
          where: $db.linhas.operador_id == $db.operador.id
        }
      }
    
      where = $db.linhas.ativa == true && $db.operador.ativo == true
      eval = {
        operador_nome  : $db.operador.nome
        operador_codigo: $db.operador.codigo
      }
    
      return = {type: "list"}
      output = [
        "id"
        "nome"
        "codigo"
        "cor"
        "operador_id"
        "operador_nome"
        "operador_codigo"
        "sentido_ordem_crescente"
        "sentido_ordem_decrescente"
      ]
    } as $linhas
  
    db.query estacoes_linhas {
      return = {type: "list"}
      output = ["estacao_id", "linha_id", "ordem"]
    } as $estacoes_linhas
  
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
        "linha_id"
        "tempo_estimado"
        "tipo"
        "direcionado"
        "servico_id"
      ]
    } as $trechos
  
    var $agora {
      value = now
    }
  
    // Viagens que ainda podem estar ativas; a funcao confere a janela,
    // desconsidera a viagem de quem busca e mantem uma viagem por usuario.
    db.query viagens_confirmadas {
      where = $db.viagens_confirmadas.substituida == false && $db.viagens_confirmadas.fim_janela > $agora
      return = {type: "list"}
      output = [
        "id"
        "usuario_id"
        "confirmada_em"
        "fim_janela"
        "substituida"
        "trechos"
      ]
    } as $viagens
  
    db.get configuracao_lotacao {
      field_name = "id"
      field_value = 1
    } as $configuracao
  
    var $dados {
      value = {
        origem_id      : $input.estacao_origem_id
        destino_id     : $input.estacao_destino_id
        estacoes       : $estacoes
        linhas         : $linhas
        estacoes_linhas: $estacoes_linhas
        trechos        : $trechos
        agora          : $agora
        usuario_id     : $auth.id
        viagens        : $viagens
        configuracao   : $configuracao
      }
    }
  
    var $resultado {
      value = $dados
        |lambda:"const num = (v) => { const n = Number(v); return isNaN(n) ? 0 : n; }; const originId = num($this.origem_id); const destinationId = num($this.destino_id); const stations = new Map($this.estacoes.map((e) => [num(e.id), e])); const lines = new Map($this.linhas.map((l) => [num(l.id), { ...l, operador: { id: num(l.operador_id), nome: l.operador_nome, codigo: l.operador_codigo } }])); const orderKey = (lineId, stationId) => `${num(lineId)}:${num(stationId)}`; const orders = new Map($this.estacoes_linhas.map((el) => [orderKey(el.linha_id, el.estacao_id), num(el.ordem)])); const edgeKey = (id, fromId, toId) => `${num(id)}|${num(fromId)}|${num(toId)}`; const edges = []; for (const t of $this.trechos) { const lineId = num(t.linha_id); const fromId = num(t.estacao_origem_id); const toId = num(t.estacao_destino_id); const seconds = num(t.tempo_estimado); const edge = { ...t, linha_id: lineId, tempo_estimado: seconds, tipo: t.tipo || 'ferroviario', direcionado: Boolean(t.direcionado), servico_id: t.servico_id == null ? null : num(t.servico_id), from: fromId, to: toId, route_from: fromId, route_to: toId }; edges.push(edge); if (!edge.direcionado) edges.push({ ...edge, from: toId, to: fromId, route_from: toId, route_to: fromId }); } const search = (blocked) => { const queue = [{ station: originId, line: null, time: 0, transfers: 0, steps: [] }]; const best = new Map(); while (queue.length) { queue.sort((a, b) => a.time - b.time || a.transfers - b.transfers); const current = queue.shift(); const key = `${current.station}|${current.line ?? 0}`; const known = best.get(key); if (known && (known.time < current.time || (known.time === current.time && known.transfers <= current.transfers))) continue; best.set(key, { time: current.time, transfers: current.transfers }); if (current.station === destinationId) return current; for (const edge of edges) { if (edge.from !== current.station) continue; if (!stations.has(edge.to) || !lines.has(edge.linha_id)) continue; if (blocked.has(edgeKey(edge.id, edge.route_from, edge.route_to))) continue; const transfers = current.transfers + (current.line !== null && current.line !== edge.linha_id ? 1 : 0); const next = { station: edge.to, line: edge.linha_id, time: current.time + edge.tempo_estimado + (current.line !== null && current.line !== edge.linha_id ? 600 : 0), transfers, steps: [...current.steps, edge] }; const nextKey = `${next.station}|${next.line}`; const old = best.get(nextKey); if (!old || next.time < old.time || (next.time === old.time && next.transfers < old.transfers)) queue.push(next); } } return null; }; const primary = search(new Set()); if (!primary) return null; const now = num($this.agora); const searcherId = num($this.usuario_id); const config = $this.configuracao || null; const minimum = config ? num(config.minimo_usuarios) : 0; const percentage = config ? num(config.percentual_lotacao) : 0; const activeTrips = new Map(); for (const trip of (Array.isArray($this.viagens) ? $this.viagens : [])) { const userId = num(trip.usuario_id); const start = num(trip.confirmada_em); if (userId === searcherId || trip.substituida || now < start || now >= num(trip.fim_janela)) continue; const previous = activeTrips.get(userId); if (!previous || start > num(previous.confirmada_em) || (start === num(previous.confirmada_em) && num(trip.id) > num(previous.id))) activeTrips.set(userId, trip); } const occupancy = new Map(); for (const trip of activeTrips.values()) { let cursor = num(trip.confirmada_em); for (const step of (Array.isArray(trip.trechos) ? trip.trechos : [])) { const begin = cursor; cursor += num(step.tempo_estimado) * 1000; if ((step.tipo || 'ferroviario') !== 'ferroviario' || step.servico_id != null) continue; if (now < begin || now >= cursor) continue; const key = edgeKey(step.trecho_id, step.estacao_origem_id, step.estacao_destino_id); occupancy.set(key, (occupancy.get(key) || 0) + 1); } } const crowded = new Set(); if (minimum >= 1 && percentage > 0 && percentage <= 100) { for (const [key, count] of occupancy) { if (count >= minimum && count * 100 >= percentage * activeTrips.size) crowded.add(key); } } const primaryCrowded = primary.steps.some((s) => crowded.has(edgeKey(s.id, s.route_from, s.route_to))); const found = primaryCrowded ? (search(crowded) || primary) : primary; const lineInfo = (id) => { const l = lines.get(num(id)); if (!l) return null; return { id: l.id, nome: l.nome, codigo: l.codigo, cor: l.cor, operador: l.operador, sentido_ordem_crescente: l.sentido_ordem_crescente ?? null, sentido_ordem_decrescente: l.sentido_ordem_decrescente ?? null }; }; const stationIds = [originId, ...found.steps.map((s) => s.route_to)]; const sentido = (lineId, fromId, toId) => { const line = lineInfo(lineId); if (!line) return null; const fromOrder = orders.get(orderKey(lineId, fromId)); const toOrder = orders.get(orderKey(lineId, toId)); if (fromOrder == null || toOrder == null || fromOrder === toOrder) return null; return toOrder > fromOrder ? line.sentido_ordem_crescente : line.sentido_ordem_decrescente; }; const baldeacoes = []; for (let i = 1; i < found.steps.length; i++) { if (found.steps[i - 1].linha_id !== found.steps[i].linha_id) { baldeacoes.push({ estacao_id: found.steps[i].route_from, linha_anterior: lineInfo(found.steps[i - 1].linha_id), linha_seguinte: lineInfo(found.steps[i].linha_id) }); } } return { estacao_origem_id: originId, estacao_destino_id: destinationId, estacoes: stationIds.map((id) => stations.get(id)), trechos: found.steps.map((s) => ({ id: s.id, estacao_origem_id: s.route_from, estacao_destino_id: s.route_to, linha: lineInfo(s.linha_id), sentido: sentido(s.linha_id, s.route_from, s.route_to), tipo: s.tipo, direcionado: s.direcionado, servico_id: s.servico_id, tempo_estimado: s.tempo_estimado })), baldeacoes, tempo_total_segundos: num(found.time), quantidade_baldeacoes: num(found.transfers) };"
    }
  
    precondition ($resultado != null) {
      error_type = "notfound"
      error = "Nenhum trajeto disponivel entre as estacoes informadas."
    }
  }

  response = $resultado
  guid = "PRIMQz2gERX5vW361l3iM8y2vvg"
}