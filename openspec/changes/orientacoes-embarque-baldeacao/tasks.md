## 1. Dados e coleta

- [x] 1.1 Criar `docs/dados/orientacoes-estacoes.csv` com cabeçalho `estacao,linha,sentido,lado_desembarque,observacao,fonte,data_coleta`
- [x] 1.2 Incluir as linhas do piloto Jandira → Paraíso (Palmeiras-Barra Funda, Sé e Paraíso) com os campos de orientação em branco para a coleta em campo
- [x] 1.3 Escrever `docs/dados/README.md` com o guia de coleta: como observar o lado da porta, o que escrever na observação, como registrar fonte e data, e como conferir os nomes exibidos pelo planejador
- [x] 1.4 Criar teste que valida a planilha versionada: cabeçalho, valores de `lado_desembarque`, tamanho da observação, fonte e data obrigatórias nos registros preenchidos e ausência de duplicatas

## 2. Domínio e aplicação

- [x] 2.1 Criar o modelo normalizado de orientação com validação dos valores permitidos
- [x] 2.2 Implementar a normalização de nomes para comparação (acentos, caixa, espaços e hífens)
- [x] 2.3 Implementar a associação das orientações às etapas pela estação de descida, linha e sentido normalizado, excluindo integrações a pé
- [x] 2.4 Testar a associação para destino, baldeação, sentido oposto, trecho intermediário e integração a pé

## 3. Infraestrutura

- [x] 3.1 Implementar o leitor do CSV, descartando linhas inválidas e duplicadas individualmente
- [x] 3.2 Devolver lista vazia quando o arquivo estiver ausente ou ilegível, registrando em log apenas as contagens
- [x] 3.3 Implementar o interruptor `METROFLOW_ORIENTACOES`, ligado por padrão e desligado com `0`
- [x] 3.4 Testar leitura válida, linhas inválidas, duplicatas, arquivo ausente e interruptor ligado e desligado

## 4. API e interface

- [x] 4.1 Adicionar o campo opcional `guidance` a `SegmentView`, omitido da resposta quando a funcionalidade estiver desligada
- [x] 4.2 Preencher `guidance` na consulta de trajeto somente com a funcionalidade ligada
- [x] 4.3 Adicionar as chaves `side` e `note` aos cartões em `_build_instructions` com os textos definidos no desenho
- [x] 4.4 Renderizar `side` em destaque e `note` como informação adicional, cada um somente quando não estiver vazio
- [x] 4.5 Testar a API e o estado: resposta idêntica com a funcionalidade desligada, trajeto com orientações, sem orientações e com arquivo inválido, e tempo e trechos inalterados

## 5. Documentação e validação

- [x] 5.1 Atualizar `docs/api-planejamento-exemplos.md` com o campo `guidance`, `docs/domain-model.md` com o conceito de orientação e `ARCHITECTURE.md` com a origem local temporária dos dados
- [x] 5.2 Executar a suíte completa com `pytest` e registrar o resultado
- [x] 5.3 Validar no navegador a rota Jandira → Paraíso com a funcionalidade ligada por padrão e desligada com `0`
- [x] 5.4 Executar `openspec validate --all --strict` e registrar os limites restantes: cobertura parcial, dados dependentes de coleta manual e associação por nomes

## 6. Revisão do formato: lado de desembarque e observação

- [x] 6.1 Trocar no modelo, no leitor do CSV e no contrato público os campos de carro, saída e baldeação e a linha de destino pelo lado de desembarque e pela observação de até 200 caracteres
- [x] 6.2 Simplificar a associação para a chave estação, linha e sentido
- [x] 6.3 Trocar a dica única dos cartões pelas chaves `side` e `note` e removê-las do cartão de embarque
- [x] 6.4 Atualizar o CSV do piloto, o guia de coleta e a documentação da API ao novo formato
- [x] 6.5 Atualizar os testes, executar a suíte, `reflex compile --dry` e `openspec validate --all --strict`

## Registro de validação (25/10/2026)

- Formato revisado: lado de desembarque como informação principal e observação livre de até 200 caracteres, sem campos de carro, saída e baldeação e sem linha de destino.
- Integração com a `main` de 26/10/2026, que trouxe `concorrencia-rotas`: conflitos resolvidos preservando o código remoto. Suíte completa: 191 testes e 50 subtestes passaram (162 e 40 da `main` atualizada, mais os desta mudança), com 1 aviso de depreciação já existente.
- Dependência de arquivamento: o delta de `busca-trajetos` parte do texto de "Escopo do MVP" definido por `concorrencia-rotas`. Arquive `concorrencia-rotas` antes desta mudança.
- `reflex compile --dry`: compilação concluída com sucesso.
- `openspec validate --all --strict`: 7 itens válidos.
- 26/10/2026: funcionalidade passou a ficar ligada por padrão, desligável com `METROFLOW_ORIENTACOES=0`. Suíte completa: 192 testes e 51 subtestes passaram.
- 5.3: validação no navegador com login real em 26/10/2026; as orientações apareceram nos cartões com a funcionalidade ligada por padrão.
- Dados: 10 registros com observação de fonte secundária (site do Metrô, Wikipédia e blog). Nenhuma fonte pública informa o lado da porta; em 26/10/2026 o lado foi sorteado para demonstração e marcado como fictício na coluna `fonte`.
- Limites: as observações precisam ser confirmadas em campo e o lado de desembarque depende da coleta; os nomes de sentido do piloto precisam ser conferidos no planejador; a associação depende de nomes iguais aos do Xano; a cobertura da malha é parcial.
