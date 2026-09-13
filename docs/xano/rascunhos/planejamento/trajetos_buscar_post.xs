// Calcula o trajeto principal por menor tempo e, no desempate, menos baldeações.
query "trajetos/buscar" verb=POST {
  api_group = "planejamento"
  auth = "usuarios"

  input {
    int estacao_origem_id
    int estacao_destino_id
  }

  stack {
    precondition ($input.estacao_origem_id != $input.estacao_destino_id) {
      error_type = "inputerror"
      error = "Origem e destino devem ser diferentes."
    }

    db.get "estacoes" {
      field_name = "id"
      field_value = $input.estacao_origem_id
    } as $origem

    db.get "estacoes" {
      field_name = "id"
      field_value = $input.estacao_destino_id
    } as $destino

    precondition ($origem != null && $destino != null) {
      error_type = "notfound"
      error = "Estação de origem ou destino não encontrada."
    }

    precondition ($origem.ativa == true && $destino.ativa == true) {
      error_type = "inputerror"
      error = "A origem e o destino precisam estar ativos."
    }

    db.query "estacoes" {
      where = $db.estacoes.ativa == true
      output = ["id", "nome", "codigo"]
    } as $estacoes

    db.query "linhas" {
      join = {
        operador: {
          table: "operadores"
          type : "inner"
          where: $db.linhas.operador_id == $db.operador.id
        }
      }
      eval = {
        operador_nome  : $db.operador.nome
        operador_codigo: $db.operador.codigo
      }
      where = $db.linhas.ativa == true && $db.operador.ativo == true
      output = ["id", "nome", "codigo", "cor", "operador_id", "operador_nome", "operador_codigo"]
    } as $linhas

    db.query "trechos" {
      join = {
        linha: {
          table: "linhas"
          type : "inner"
          where: $db.trechos.linha_id == $db.linha.id
        }
        operador: {
          table: "operadores"
          type : "inner"
          where: $db.linha.operador_id == $db.operador.id
        }
      }
      where = $db.trechos.ativo == true && $db.linha.ativa == true && $db.operador.ativo == true
      output = ["id", "estacao_origem_id", "estacao_destino_id", "linha_id", "tempo_estimado"]
    } as $trechos

    var $dados {
      value = {
        origem_id : $input.estacao_origem_id
        destino_id: $input.estacao_destino_id
        estacoes  : $estacoes
        linhas    : $linhas
        trechos   : $trechos
      }
    }

    var $resultado {
      value = $dados|lambda:"const stations = new Map($this.estacoes.map((e) => [e.id, e])); const lines = new Map($this.linhas.map((l) => [l.id, {...l, operador: {id: l.operador_id, nome: l.operador_nome, codigo: l.operador_codigo}}])); const edges = []; for (const t of $this.trechos) { edges.push({...t, from: t.estacao_origem_id, to: t.estacao_destino_id}); edges.push({...t, from: t.estacao_destino_id, to: t.estacao_origem_id}); } const queue = [{station: $this.origem_id, line: null, time: 0, transfers: 0, steps: []}]; const best = new Map(); let found = null; while (queue.length) { queue.sort((a,b) => a.time-b.time || a.transfers-b.transfers); const current = queue.shift(); const key = current.station + '|' + (current.line ?? 0); const known = best.get(key); if (known && (known.time < current.time || (known.time === current.time && known.transfers <= current.transfers))) continue; best.set(key, {time: current.time, transfers: current.transfers}); if (current.station === $this.destino_id) { found = current; break; } for (const edge of edges) { if (edge.from !== current.station || !stations.has(edge.to) || !lines.has(edge.linha_id)) continue; const transfers = current.transfers + (current.line !== null && current.line !== edge.linha_id ? 1 : 0); const next = {station: edge.to, line: edge.linha_id, time: current.time + edge.tempo_estimado, transfers, steps: [...current.steps, {...edge, route_from: edge.from, route_to: edge.to}]}; const nextKey = next.station + '|' + next.line; const old = best.get(nextKey); if (!old || next.time < old.time || (next.time === old.time && next.transfers < old.transfers)) queue.push(next); } } if (!found) return null; const lineDto = (id) => { const l = lines.get(id); return {id: l.id, nome: l.nome, codigo: l.codigo, cor: l.cor, operador: l.operador}; }; const stationIds = [$this.origem_id, ...found.steps.map((s) => s.route_to)]; const baldeacoes = []; for (let i=1; i<found.steps.length; i++) { if (found.steps[i-1].linha_id !== found.steps[i].linha_id) baldeacoes.push({estacao_id: found.steps[i].route_from, linha_anterior: lineDto(found.steps[i-1].linha_id), linha_seguinte: lineDto(found.steps[i].linha_id)}); } return {estacao_origem_id: $this.origem_id, estacao_destino_id: $this.destino_id, estacoes: stationIds.map((id) => stations.get(id)), trechos: found.steps.map((s) => ({id: s.id, estacao_origem_id: s.route_from, estacao_destino_id: s.route_to, linha: lineDto(s.linha_id), tempo_estimado: s.tempo_estimado})), baldeacoes, tempo_total_segundos: found.time, quantidade_baldeacoes: found.transfers};"
    }

    precondition ($resultado != null) {
      error_type = "notfound"
      error = "Nenhum trajeto disponível entre as estações informadas."
    }
  }

  response = $resultado
}
