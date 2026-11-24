## ADDED Requirements

### Requirement: Preparação isolada da hospedagem

O pacote SHALL servir interface compilada e API na mesma origem, manter o contrato de planejamento e não alterar a malha ou os parâmetros do Xano.

#### Scenario: Inicialização válida

- **WHEN** há build e origem HTTPS válidos
- **THEN** o servidor usa a porta configurada e cookie de produção com um worker

#### Scenario: Configuração inválida

- **WHEN** falta a origem ou a porta é inválida
- **THEN** a execução é recusada antes de iniciar o servidor

### Requirement: Fontes públicas pendentes

O pacote SHALL manter todas as fontes desligadas até revisão explícita da implantação.

#### Scenario: Tentativa de ativação

- **WHEN** uma variável de fonte indica ativação
- **THEN** o pacote recusa a inicialização, sem coletar informações externas

### Requirement: Evidência limitada ao ambiente executado

A documentação SHALL distinguir validação local de publicação e homologação no Render.

#### Scenario: Validação local concluída

- **WHEN** testes locais passam
- **THEN** não se declara deploy, custo zero garantido ou concorrência real remotamente validada
