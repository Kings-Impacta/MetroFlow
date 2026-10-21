## ADDED Requirements

### Requirement: Condição operacional rastreável

O sistema SHALL representar a condição operacional com código da linha, situação
normalizada, rótulo e descrição da origem, fonte, instante da coleta, instante da
origem quando disponível e estado de validade.

#### Scenario: Condição atual disponível

- **WHEN** uma fonte autorizada retorna uma condição válida dentro de sua validade
- **THEN** o sistema associa a condição à linha pelo código e informa fonte e atualização

#### Scenario: Resposta sem horário da origem

- **WHEN** a fonte retorna condição válida sem informar seu próprio horário
- **THEN** o sistema preserva o instante da coleta e não inventa um horário da origem

### Requirement: Precedência por responsabilidade

O sistema SHALL usar a ARTESP como fonte primária para a malha delegada e uma fonte
oficial autorizada do operador público para as linhas sob gestão direta.

#### Scenario: Duas fontes cobrem a mesma linha delegada

- **WHEN** ARTESP e outra fonte retornam condições para a mesma linha delegada
- **THEN** o sistema apresenta a condição da ARTESP e registra a divergência de forma não sensível

### Requirement: Cache compatível com a origem

O sistema SHALL compartilhar o cache entre usuários e respeitar a frequência máxima
e os limites documentados por cada fonte.

#### Scenario: Consulta dentro da validade do cache

- **WHEN** outro usuário solicita uma condição ainda válida no cache
- **THEN** o sistema reutiliza o valor sem consumir nova chamada externa

### Requirement: Indisponibilidade explícita

O sistema SHALL distinguir condição atual, desatualizada e indisponível e SHALL
continuar permitindo o planejamento quando a condição operacional não puder ser
obtida.

#### Scenario: Todas as fontes falham

- **WHEN** as fontes excedem o tempo limite, retornam erro ou resposta inválida
- **THEN** o sistema informa que a condição está indisponível e mantém a busca de trajeto

#### Scenario: Cache ultrapassa a validade

- **WHEN** existe um último valor conhecido, mas sua validade terminou
- **THEN** o sistema o identifica como desatualizado e não o apresenta como condição atual

### Requirement: Credenciais protegidas

O sistema SHALL manter chaves externas exclusivamente no backend e SHALL impedir que
elas apareçam na interface, URLs, respostas públicas ou logs.

#### Scenario: Consulta autenticada à ARTESP

- **WHEN** o backend consulta a API Trilhos com a chave configurada
- **THEN** o navegador recebe somente a condição normalizada e nenhum valor da credencial

### Requirement: Uso informativo

O sistema SHALL apresentar a condição operacional como informação e SHALL preservar
a regra atual de escolha do trajeto nesta entrega.

#### Scenario: Linha do trajeto apresenta ocorrência

- **WHEN** a linha escolhida possui condição diferente de operação normal
- **THEN** o sistema apresenta o aviso sem recalcular ou substituir automaticamente o trajeto
