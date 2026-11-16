// Indicadores agregados do painel administrativo. A resposta contem somente
// contagens, nomes e codigos de estacoes e o criterio de lotacao; nunca
// identificadores de usuarios, e-mails ou registros de viagem.
query "admin/indicadores" verb=GET {
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
  
    // A concessao e consultada a cada chamada: a revogacao vale na hora.
    db.query administradores {
      where = $db.administradores.usuario_id == $auth.id
      return = {type: "single"}
    } as $administrador
  
    precondition ($administrador != null) {
      error_type = "accessdenied"
      error = "Acesso restrito a administradores."
    }
  
    var $agora {
      value = now
    }
  
    // Sete dias corridos antes da apuracao.
    var $inicio_periodo {
      value = $agora - 604800000
    }
  
    // fim_janela nunca e anterior a confirmada_em; o filtro usa o indice
    // existente e a funcao confere confirmada_em.
    db.query viagens_confirmadas {
      where = $db.viagens_confirmadas.fim_janela >= $inicio_periodo
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
  
    db.query usuarios {
      where = $db.usuarios.ativo == true && $db.usuarios.email_verificado == true
      return = {type: "list"}
      output = ["id"]
    } as $contas
  
    db.query estacoes {
      return = {type: "list"}
      output = ["id", "nome", "codigo", "ativa"]
    } as $estacoes
  
    db.query linhas {
      join = {
        operador: {
          table: "operadores"
          where: $db.linhas.operador_id == $db.operador.id
        }
      }
    
      where = $db.linhas.ativa == true && $db.operador.ativo == true
      return = {type: "list"}
      output = ["id"]
    } as $linhas_ativas
  
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
      output = ["id"]
    } as $trechos_ativos
  
    db.get configuracao_lotacao {
      field_name = "id"
      field_value = 1
    } as $configuracao
  
    var $dados {
      value = {
        agora         : $agora
        viagens       : $viagens
        contas        : $contas
        estacoes      : $estacoes
        linhas_ativas : $linhas_ativas
        trechos_ativos: $trechos_ativos
        configuracao  : $configuracao
      }
    }
  
    // Viagem em andamento: nao substituida e confirmada_em <= agora < fim_janela,
    // uma por usuario (a mais recente). O dia corrente usa o deslocamento fixo
    // de -3 h de Sao Paulo. A lotacao segue o criterio publicado em
    // trajetos/buscar (conferido em 16/11/2026), avaliado no instante da
    // apuracao e sem excluir nenhum usuario.
    var $indicadores {
      value = $dados
        |lambda:"const num = (v) => { const n = Number(v); return isNaN(n) ? 0 : n; }; const list = (v) => (Array.isArray(v) ? v : []); const DAY = 86400000; const OFFSET = 10800000; const now = num($this.agora); const since = now - 7 * DAY; const startToday = Math.floor((now - OFFSET) / DAY) * DAY + OFFSET; const trips = list($this.viagens); const active = new Map(); for (const trip of trips) { const user = num(trip.usuario_id); const confirmed = num(trip.confirmada_em); if (trip.substituida || now < confirmed || now >= num(trip.fim_janela)) continue; const previous = active.get(user); if (!previous || confirmed > num(previous.confirmada_em) || (confirmed === num(previous.confirmada_em) && num(trip.id) > num(previous.id))) active.set(user, trip); } const recent = trips.filter((t) => { const at = num(t.confirmada_em); return at >= since && at <= now; }); const recentUsers = new Set(recent.map((t) => num(t.usuario_id))); const today = recent.filter((t) => num(t.confirmada_em) >= startToday).length; const stations = new Map(list($this.estacoes).map((e) => [num(e.id), e])); const uses = new Map(); for (const t of recent) { const steps = list(t.trechos).slice().sort((a, b) => num(a.ordem) - num(b.ordem)); if (!steps.length) continue; for (const id of [num(steps[0].estacao_origem_id), num(steps[steps.length - 1].estacao_destino_id)]) { if (stations.has(id)) uses.set(id, (uses.get(id) || 0) + 1); } } const ranking = [...uses.entries()].map(([id, usos]) => ({ id: id, nome: String(stations.get(id).nome || ''), codigo: String(stations.get(id).codigo || ''), usos: usos })).sort((a, b) => b.usos - a.usos || a.nome.localeCompare(b.nome, 'pt-BR') || a.id - b.id).slice(0, 5); const allStations = [...stations.values()]; const activeStations = allStations.filter((e) => e.ativa === true).length; const config = $this.configuracao || null; const minimum = config ? num(config.minimo_usuarios) : 0; const percentage = config ? num(config.percentual_lotacao) : 0; const valid = minimum >= 1 && percentage > 0 && percentage <= 100; let crowded = null; if (valid) { const occupancy = new Map(); for (const trip of active.values()) { let cursor = num(trip.confirmada_em); for (const step of list(trip.trechos)) { const explicit = num(step.inicio_previsto_em); const begin = explicit > 0 ? explicit : cursor + (num(step.espera_estimada_segundos) + num(step.baldeacao_antes_segundos)) * 1000; cursor = begin + num(step.tempo_estimado) * 1000; if ((step.tipo || 'ferroviario') !== 'ferroviario' || step.servico_id != null || !Number.isFinite(begin) || cursor <= begin || now < begin || now >= cursor) continue; const key = num(step.trecho_id) + '|' + num(step.estacao_origem_id) + '|' + num(step.estacao_destino_id); if (!occupancy.has(key)) occupancy.set(key, new Set()); occupancy.get(key).add(num(trip.usuario_id)); } } crowded = 0; for (const users of occupancy.values()) { if (users.size >= minimum && users.size * 100 >= percentage * active.size) crowded += 1; } } return { apurado_em: now, uso: { rotas_ativas: active.size, usuarios_em_viagem: active.size, usuarios_uso_recente: recentUsers.size, contas_habilitadas: list($this.contas).length }, malha: { estacoes_ativas: activeStations, estacoes_inativas: allStations.length - activeStations, linhas_ativas: list($this.linhas_ativas).length, trechos_ativos: list($this.trechos_ativos).length }, volume: { viagens_hoje: today, viagens_7_dias: recent.length }, ranking_estacoes: ranking, lotacao: { trechos_lotados: crowded, minimo_usuarios: valid ? minimum : null, percentual_lotacao: valid ? percentage : null } };"
    }
  }

  response = $indicadores
  guid = "PGaZeAMo_Fl_3bMtcCby2XvS7G0"
}