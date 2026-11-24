// Entrada: {fonte, pedido, agora}; relógio de controle em milissegundos.
const row = $this.fonte, input = $this.pedido, now = $this.agora;
const policies = {
  cptm: {codes:['L10','L11','L12','L13'], name:'CPTM', url:'https://www.cptm.sp.gov.br/cptm'},
  metro: {codes:['L1','L2','L3','L4','L5','L15','L17'], name:'Metrô', url:'https://www.metro.sp.gov.br/sua-viagem/direto-metro/'},
  motiva: {codes:['L8','L9'], name:'Motiva', url:'https://trilhos.motiva.com.br/viamobilidade8e9/situacao-das-linhas/'},
  ddt: {codes:['L1','L2','L3','L4','L5','L6','L7','L8','L9','L10','L11','L12','L13','L15','L17'], name:'Direto dos Trens', url:'https://www.diretodostrens.com.br/'}
};
const reject = reason => ({ok:false, reason});
if (!row || !input || !Number.isFinite(now) || now <= 0) return reject('invalid');
const policy = policies[row.codigo];
if (!policy || row.autorizada !== true || row.habilitada !== true) return reject('disabled');
const state = JSON.parse(JSON.stringify(row.controle || {}));
const conditions = JSON.parse(JSON.stringify(row.condicoes || {}));
const finish = response => ({ok:true, data:{controle:state, condicoes:conditions}, response});
if (input.acao === 'reserve') {
  const attempts = (state.attempts || []).filter(t => Number.isFinite(t) && t > now-3600000);
  if (now < (state.next_call || 0) || attempts.length >= 12)
    return finish({granted:false});
  state.generation = (state.generation || 0)+1;
  state.attempts = [...attempts, now];
  state.last_attempt = now;
  state.next_call = now+300000;
  state.lease_until = now+60000;
  return finish({granted:true, generation:state.generation, lease_until:state.lease_until});
}
if (!['publish','fail'].includes(input.acao)) return reject('invalid_action');
if (!Number.isInteger(input.generation) || input.generation !== state.generation || now > (state.lease_until || 0))
  return reject('lease');
const refresh = input.refresh_after === undefined ? 300 : input.refresh_after;
if (!Number.isFinite(refresh) || refresh < 300 || refresh > 31536000) return reject('interval');
if (input.acao === 'fail') {
  state.failed = true;
  state.lease_until = 0;
  state.next_call = Math.max(state.next_call || 0, now+refresh*1000);
  return finish({stored:0});
}
const rows = input.conditions;
if (!Array.isArray(rows) || rows.length > 17 || JSON.stringify(rows).length > 65536) return reject('payload');
const fresh = input.fresh_for === undefined ? 600 : input.fresh_for;
if (!Number.isFinite(fresh) || fresh < 0 || fresh > 31536000) return reject('freshness');
const normalized = [], seen = new Set();
const situations = ['normal','restricted','interrupted','closed','unknown'];
for (const raw of rows) {
  if (!raw || !policy.codes.includes(raw.line_code) || seen.has(raw.line_code) || !situations.includes(raw.situation) || raw.validity !== 'current') return reject('condition');
  if (!Number.isFinite(raw.collected_at) || raw.collected_at <= 0 || raw.collected_at*1000 > now+60000) return reject('timestamp');
  for (const field of ['updated_at','verified_at'])
    if (raw[field] !== undefined && raw[field] !== null && (!Number.isFinite(raw[field]) || raw[field] <= 0 || raw[field]*1000 > now+60000)) return reject('timestamp');
  if (typeof raw.label !== 'string' || raw.label.length < 1 || raw.label.length > 120 || typeof (raw.description || '') !== 'string' || (raw.description || '').length > 2000 || typeof (raw.attribution || '') !== 'string' || (raw.attribution || '').length > 300) return reject('text');
  seen.add(raw.line_code);
  normalized.push({line_code:raw.line_code, situation:raw.situation, label:raw.label,
    description:raw.description || '', source:policy.name, source_url:policy.url,
    collected_at:raw.collected_at, updated_at:raw.updated_at ?? null,
    verified_at:raw.verified_at ?? raw.collected_at, validity:'current', attribution:raw.attribution || ''});
}
// Nada de apagar uma observação ausente na resposta parcial.
for (const entry of Object.values(conditions)) entry.condition.validity = 'stale';
let stored = 0;
if (input.cacheable === true) {
  for (const item of normalized) {
    const old = conditions[item.line_code]?.condition;
    if (old && ((item.verified_at < old.verified_at) || (item.updated_at !== null && old.updated_at !== null && item.updated_at < old.updated_at))) continue;
    conditions[item.line_code] = {condition:item, fresh_until:Math.min(now/1000+Math.min(600,fresh), item.collected_at+600, item.verified_at+600)};
    stored++;
  }
}
state.failed = stored === 0;
state.lease_until = 0;
state.next_call = Math.max(state.next_call || 0, now+refresh*1000);
if (stored > 0) state.last_success = now;
return finish({stored});
