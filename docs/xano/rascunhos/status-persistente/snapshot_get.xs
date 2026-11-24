// RASCUNHO LOCAL: leitura pública apenas de condições não pessoais, sem coleta.
// A API Python existente continua exigindo o cookie; este grupo permanece fechado.
query "snapshot" verb=GET {
  api_group = "status_operacional"
  input {}
  stack {
    db.query status_operacional_fontes {
      where = $db.status_operacional_fontes.autorizada == true && $db.status_operacional_fontes.habilitada == true
      return = {type: "list"}
      output = ["codigo", "condicoes", "controle"]
    } as $fontes
    var $dados { value = {fontes: $fontes, agora: now} }
    var $snapshot {
      value = $dados|lambda:"const now=$this.agora/1000; const result=[];\nfor(const row of $this.fontes || []) {\n const conditions=[];\n for(const entry of Object.values(row.condicoes || {})) {\n  const item={...entry.condition};\n  if(row.controle?.failed || now>=entry.fresh_until || now-item.collected_at>600 || now-item.verified_at>600 || item.validity==='stale') item.validity='stale';\n  conditions.push(item);\n }\n result.push({source:row.codigo, conditions});\n}\nreturn {version:1, sources:result};"
    }
  }
  response = $snapshot
  guid = "plnT6_yhRBF0WKVzxrvVZThSFAM"
}
