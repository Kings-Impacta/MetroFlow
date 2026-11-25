// Função privada, sem endpoint público. Somente cria fontes vazias/desativadas.
function "status_operacional/inicializar" {
  input {}
  stack {
    foreach (["cptm", "metro", "motiva", "ddt"]) {
      each as $codigo {
        db.has status_operacional_fontes {
          field_name = "codigo"
          field_value = $codigo
        } as $existe
        conditional {
          if ($existe == false) {
            db.add status_operacional_fontes {
              data = {codigo: $codigo, autorizada: false, habilitada: false, condicoes: {}, controle: {}}
            }
          }
        }
      }
    }
  }
  response = {ok: true}
  guid = "HJuVP8NKNcMP_nm8Msptll4aK40"
}
