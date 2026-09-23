## Context

O cliente local oculta erros de validação e o Xano foi configurado para desabilitar o histórico dos endpoints que emitem token. A configuração foi publicada, mas não existe comprovação posterior por chamada HTTP externa.

## Goals / Non-Goals

- Confirmar ausência de senha, hash e token em superfícies indevidas.
- Confirmar o tratamento da expiração natural da sessão com a busca aberta.
- Não guardar credenciais reais, tokens ou conteúdo sensível em capturas e relatórios.

## Decisions

Usar contas e marcadores de teste, registrar apenas status e presença ou ausência de dados sensíveis e separar leitura da auditoria de qualquer alteração remota. Corrigir somente falhas reproduzidas.

## Risks / Trade-offs

O histórico anterior à alteração pode permanecer pelo período de retenção do Xano. Uma chamada executada dentro do painel não substitui a verificação HTTP externa.
