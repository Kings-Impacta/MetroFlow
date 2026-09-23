## Context

A auditoria de 21/09/2026 confirmou referências, tempo positivo e índice de duplicata direta, mas encontrou as duas lacunas. O painel do plano Free não permite Database Triggers.

## Goals / Non-Goals

- Garantir que todo novo trecho passe por validação de extremos e de duplicata inversa.
- Preservar os registros existentes e a leitura bidirecional.
- Não apresentar a validação do endpoint de busca como garantia da tabela.

## Decisions

Antes de alterar o Xano, revisar backups e todos os caminhos capazes de gravar trechos. Se um único endpoint validado não puder ser imposto, documentar a limitação em vez de afirmar integridade inexistente.

## Risks / Trade-offs

Um endpoint seguro não protege a tabela se outras rotas de escrita permanecerem disponíveis. A mudança exige testes de concorrência e de reentrada no caminho de gravação escolhido.
