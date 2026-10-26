// Parametros do criterio de lotacao. A busca le somente o registro id 1.
// Sem esse registro, ou com valores fora dos limites, nenhum trecho e
// considerado lotado.
table configuracao_lotacao {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    // Quantidade minima de viagens ativas no trecho e sentido (>= 1).
    int minimo_usuarios filters=min:1
  
    // Percentual minimo do total de viagens ativas, de 0 a 100 (> 0).
    decimal percentual_lotacao filters=min:0|max:100
  }

  index = [{type: "primary", field: [{name: "id"}]}]
  guid = "_L9a3gw9dSj2sJzAWz1lwtlELw4"
}