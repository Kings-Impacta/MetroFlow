# Orientações de estação

O arquivo `orientacoes-estacoes.csv` reúne as dicas exibidas nos cartões de
"Como chegar" quando o passageiro desce do trem, no destino ou numa baldeação. A
informação principal é o **lado de desembarque**. Uma **observação adicional**, em
texto livre, registra qualquer outra dica relevante. Não existe API pública com
esses dados, por isso eles são coletados pelo grupo e registrados com fonte e data.

## Estado atual

- A funcionalidade fica **ligada por padrão**: basta rodar o projeto. Para
  desligá-la, defina no terminal que executa o projeto e reinicie o `reflex run`:

  ```powershell
  $env:METROFLOW_ORIENTACOES="0"
  ```

- Desligada, a aplicação se comporta exatamente como antes desta funcionalidade.
- O arquivo tem 10 registros para Palmeiras-Barra Funda, Sé e Paraíso, nos dois
  sentidos de cada linha, cobrindo a rota de demonstração Jandira → Paraíso e a
  rota inversa Paraíso → Palmeiras-Barra Funda.
- **O lado de desembarque dos 10 registros é fictício.** Nenhuma fonte pública
  consultada em 25/10/2026 informa esse dado, e em 26/10/2026 os valores foram
  sorteados apenas para demonstrar a funcionalidade. A coluna `fonte` de cada
  linha registra isso. Substitua pelos valores observados em campo antes de usar
  o app com passageiros reais.
- As observações vieram de pesquisa na internet: ficha oficial da estação no site
  do Metrô, Wikipédia e um guia de baldeações (blog comercial). Todas estão
  marcadas como `fonte secundária, confirmar em campo`. Ao confirmar, troque a
  fonte pela observação em campo e preencha o lado da porta.
- O Xano não é alterado. Migrar estes dados para uma tabela no Xano será uma
  mudança futura.
- O arquivo é lido uma vez quando o servidor sobe. Depois de editá-lo, reinicie o
  `reflex run`.

## Colunas

| Coluna | Obrigatória | Conteúdo |
|---|---|---|
| `estacao` | sim | Estação onde o passageiro **desce**, com o nome exibido no planejador. |
| `linha` | sim | Linha em que o passageiro chega, como `Linha 8 - Diamante`. |
| `sentido` | sim | Sentido do trem, igual ao texto "Sentido …" exibido no planejador. |
| `lado_desembarque` | não* | `esquerdo`, `direito` ou `ambos`, olhando para a frente do trem. |
| `observacao` | não* | Texto livre de até 200 caracteres com qualquer dica relevante. |
| `fonte` | sim, se houver lado ou observação | Como o dado foi obtido: observação em campo, foto ou documento oficial. |
| `data_coleta` | sim, se houver lado ou observação | Data no formato `AAAA-MM-DD`. |

\* Preencha o lado, a observação ou os dois. Linhas sem nenhum deles são tratadas
como pendentes e não aparecem na tela.

Cada combinação de estação, linha e sentido deve aparecer uma única vez. Registros
duplicados são descartados. Se a observação tiver vírgula, o editor de planilha
coloca o texto entre aspas ao salvar em CSV; ao editar o arquivo à mão, use aspas
você mesmo.

Exemplo de linha preenchida:

```csv
Paraíso,Linha 1 - Azul,Jabaquara,esquerdo,"Desça no carro 4, em frente à escada rolante.",observação em campo (foto da placa) - nome do integrante,2026-10-25
```

## O que escrever na observação

Escreva o que ajudaria alguém que nunca esteve na estação. Exemplos:

- carro mais perto da escada, da escada rolante ou do elevador;
- caminho para a outra linha numa baldeação ("siga as placas da Linha 3 pela
  passarela central");
- saída mais útil ou cuidado na plataforma ("vão largo entre o trem e a
  plataforma").

Use frases curtas, com as palavras da sinalização da estação, e não repita o lado
da porta, que já aparece em destaque.

## Como coletar em campo

1. **Confira os nomes no planejador.** Faça a busca da rota e copie exatamente o
   nome da estação, da linha e o texto do sentido. Um nome diferente faz a dica
   não aparecer. O piloto foi preenchido com os nomes esperados; confirme
   principalmente os sentidos de Sé (`Corinthians-Itaquera`) e Paraíso
   (`Jabaquara`) e se a rota realmente faz baldeação em Sé.
2. **Lado da porta.** Antes da parada, o trem costuma anunciar o lado do
   desembarque. Confirme olhando para qual lado a porta abre, em relação à frente
   do trem.
3. **Observação.** Anote o que for útil seguindo as dicas acima e tire uma foto da
   placa ou do mapa da plataforma como evidência.
4. **Fonte e data.** Escreva quem coletou e como, por exemplo
   `observação em campo (foto da placa) - nome do integrante`, e a data da visita.

## Validação

O teste `tests/unit/planning/test_guidance_csv_file.py` confere o cabeçalho, os
valores permitidos, o tamanho da observação, a fonte e a data dos registros
preenchidos e a ausência de duplicatas. Rode a suíte antes de enviar alterações:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
```

## Referência

A planilha `base_estacoes_metro_trem_sp_inicial.xlsx` foi gerada com apoio de IA
como inventário inicial de estações. Ela não contém orientações verificadas, não
é lida pela aplicação e serve apenas como lista de trabalho para a coleta.
