# auditoria-sessao Specification

## Purpose
TBD - created by archiving change auditoria-segredos-sessao. Update Purpose after archive.

## Requirements

### Requirement: Evidências de segurança sem dados sensíveis

O projeto SHALL registrar as verificações de autenticação e expiração de sessão sem conservar senha, hash ou token nas evidências produzidas.

#### Scenario: Registro de uma verificação de autenticação

- **WHEN** uma verificação de cadastro, login ou expiração de sessão é documentada
- **THEN** a evidência informa somente o resultado, o comportamento observado e dados de teste não sensíveis

### Requirement: Verificação reproduzível da expiração

O projeto SHALL permitir verificar que uma sessão expirada não autoriza novas consultas protegidas.

#### Scenario: Consulta após o vencimento do token

- **WHEN** um token de teste ultrapassa sua validade e o usuário solicita um trajeto com a página já aberta
- **THEN** a API rejeita a consulta, descarta o estado protegido e direciona o usuário para autenticação
