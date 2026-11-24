// Escrita exclusiva de administradores autenticados; sem coleta externa no Xano.
query "controle" verb=POST {
  api_group = "status_operacional"
  auth = "usuarios"
  input {
    text fonte filters=trim|lower
    json pedido
  }
  stack {
    db.get usuarios {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "ativo", "email_verificado", "versao_sessao"]
    } as $usuario
    precondition ($usuario != null && $usuario.ativo && $usuario.email_verificado) {
      error_type = "unauthorized"
      error = "Sessão inválida."
    }
    precondition (`$auth.extras.versao_sessao` != null && `$auth.extras.versao_sessao` == ($usuario.versao_sessao ?? 1)) {
      error_type = "unauthorized"
      error = "Sessão inválida."
    }
    db.query administradores {
      where = $db.administradores.usuario_id == $auth.id
      return = {type: "exists"}
    } as $administrador
    precondition ($administrador == true) {
      error_type = "accessdenied"
      error = "Acesso exclusivo do coletor administrativo."
    }
    var $agora { value = now }
    db.transaction {
      stack {
        // O UPDATE da linha dedicada serializa somente a fonte em questão.
        db.edit status_operacional_fontes {
          field_name = "codigo"
          field_value = $input.fonte
          data = {trava_em: $agora}
        } as $bloqueio
        db.get status_operacional_fontes {
          field_name = "codigo"
          field_value = $input.fonte
        } as $fonte_atual
        var $dados { value = {fonte: $fonte_atual, pedido: $input.pedido, agora: $agora} }
        var $resultado {
          value = $dados|lambda:"// Entrada: {fonte, pedido, agora}; relógio de controle em milissegundos.\nconst row = $this.fonte, input = $this.pedido, now = $this.agora;\nconst policies = {\n  cptm: {codes:['L10','L11','L12','L13'], name:'CPTM', url:'https://www.cptm.sp.gov.br/cptm'},\n  metro: {codes:['L1','L2','L3','L4','L5','L15','L17'], name:'Metrô', url:'https://www.metro.sp.gov.br/sua-viagem/direto-metro/'},\n  motiva: {codes:['L8','L9'], name:'Motiva', url:'https://trilhos.motiva.com.br/viamobilidade8e9/situacao-das-linhas/'},\n  ddt: {codes:['L1','L2','L3','L4','L5','L6','L7','L8','L9','L10','L11','L12','L13','L15','L17'], name:'Direto dos Trens', url:'https://www.diretodostrens.com.br/'}\n};\nconst reject = reason => ({ok:false, reason});\nif (!row || !input || !Number.isFinite(now) || now <= 0) return reject('invalid');\nconst policy = policies[row.codigo];\nif (!policy || row.autorizada !== true || row.habilitada !== true) return reject('disabled');\nconst state = JSON.parse(JSON.stringify(row.controle || {}));\nconst conditions = JSON.parse(JSON.stringify(row.condicoes || {}));\nconst finish = response => ({ok:true, data:{controle:state, condicoes:conditions}, response});\nif (input.acao === 'reserve') {\n  const attempts = (state.attempts || []).filter(t => Number.isFinite(t) && t > now-3600000);\n  if (now < (state.next_call || 0) || attempts.length >= 12)\n    return finish({granted:false});\n  state.generation = (state.generation || 0)+1;\n  state.attempts = [...attempts, now];\n  state.last_attempt = now;\n  state.next_call = now+300000;\n  state.lease_until = now+60000;\n  return finish({granted:true, generation:state.generation, lease_until:state.lease_until});\n}\nif (!['publish','fail'].includes(input.acao)) return reject('invalid_action');\nif (!Number.isInteger(input.generation) || input.generation !== state.generation || now > (state.lease_until || 0))\n  return reject('lease');\nconst refresh = input.refresh_after === undefined ? 300 : input.refresh_after;\nif (!Number.isFinite(refresh) || refresh < 300 || refresh > 31536000) return reject('interval');\nif (input.acao === 'fail') {\n  state.failed = true;\n  state.lease_until = 0;\n  state.next_call = Math.max(state.next_call || 0, now+refresh*1000);\n  return finish({stored:0});\n}\nconst rows = input.conditions;\nif (!Array.isArray(rows) || rows.length > 17 || JSON.stringify(rows).length > 65536) return reject('payload');\nconst fresh = input.fresh_for === undefined ? 600 : input.fresh_for;\nif (!Number.isFinite(fresh) || fresh < 0 || fresh > 31536000) return reject('freshness');\nconst normalized = [], seen = new Set();\nconst situations = ['normal','restricted','interrupted','closed','unknown'];\nfor (const raw of rows) {\n  if (!raw || !policy.codes.includes(raw.line_code) || seen.has(raw.line_code) || !situations.includes(raw.situation) || raw.validity !== 'current') return reject('condition');\n  if (!Number.isFinite(raw.collected_at) || raw.collected_at <= 0 || raw.collected_at*1000 > now+60000) return reject('timestamp');\n  for (const field of ['updated_at','verified_at'])\n    if (raw[field] !== undefined && raw[field] !== null && (!Number.isFinite(raw[field]) || raw[field] <= 0 || raw[field]*1000 > now+60000)) return reject('timestamp');\n  if (typeof raw.label !== 'string' || raw.label.length < 1 || raw.label.length > 120 || typeof (raw.description || '') !== 'string' || (raw.description || '').length > 2000 || typeof (raw.attribution || '') !== 'string' || (raw.attribution || '').length > 300) return reject('text');\n  seen.add(raw.line_code);\n  normalized.push({line_code:raw.line_code, situation:raw.situation, label:raw.label,\n    description:raw.description || '', source:policy.name, source_url:policy.url,\n    collected_at:raw.collected_at, updated_at:raw.updated_at ?? null,\n    verified_at:raw.verified_at ?? raw.collected_at, validity:'current', attribution:raw.attribution || ''});\n}\n// Nada de apagar uma observação ausente na resposta parcial.\nfor (const entry of Object.values(conditions)) entry.condition.validity = 'stale';\nlet stored = 0;\nif (input.cacheable === true) {\n  for (const item of normalized) {\n    const old = conditions[item.line_code]?.condition;\n    if (old && ((item.verified_at < old.verified_at) || (item.updated_at !== null && old.updated_at !== null && item.updated_at < old.updated_at))) continue;\n    conditions[item.line_code] = {condition:item, fresh_until:Math.min(now/1000+Math.min(600,fresh), item.collected_at+600, item.verified_at+600)};\n    stored++;\n  }\n}\nstate.failed = stored === 0;\nstate.lease_until = 0;\nstate.next_call = Math.max(state.next_call || 0, now+refresh*1000);\nif (stored > 0) state.last_success = now;\nreturn finish({stored});\n"
        }
        precondition ($resultado.ok == true) {
          error_type = "inputerror"
          error = "Atualização de status recusada."
        }
        db.patch status_operacional_fontes {
          field_name = "codigo"
          field_value = $input.fonte
          data = $resultado.data
        } as $salvo
      }
    }
  }
  response = $resultado.response
  history = false
  guid = "ylR9GTIPVYSs-4IOehVYKPOybDo"
}
