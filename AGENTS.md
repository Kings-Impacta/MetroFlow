# Orientações para agentes no MetroFlow

Antes de alterar o projeto, leia [a visão geral](docs/project-overview.md), [o modelo de domínio](docs/domain-model.md), [a arquitetura](ARCHITECTURE.md) e a mudança pertinente em `openspec/changes/`.

## Documentação e idioma

- Escreva documentação, mensagens exibidas ao usuário e comentários explicativos em português do Brasil.
- Preserve identificadores exigidos por Python, Reflex, Xano, APIs e pelo esquema do OpenSpec. Não traduza caminhos, nomes de campos ou cabeçalhos estruturais cuja alteração quebre a integração ou a validação.
- Atualize a documentação quando uma regra de negócio ou decisão arquitetural mudar. Diferencie estado atual, histórico e trabalho pendente.

## Arquitetura e segurança

- Implemente a interface exclusivamente com Reflex e seus mecanismos de componentes, estado, eventos e páginas.
- Mantenha o cálculo de trajetos e os dados da malha no Xano; o backend Python valida e normaliza o contrato recebido.
- Não exponha tokens, senhas ou respostas internas do Xano à interface, às URLs ou aos logs. Preserve a sessão em cookie HttpOnly e o comportamento de redirecionamento quando ela expirar.
- Evite alterar funcionalidades não relacionadas e mantenha a separação entre domínio, aplicação, infraestrutura e apresentação.

## Processo de desenvolvimento

- Use uma mudança OpenSpec para novas funcionalidades ou alterações de contrato. Registre proposta, desenho, especificação e tarefas antes da implementação; valide e arquive a mudança quando os critérios estiverem concluídos.
- Execute os testes pertinentes e a validação estrita do OpenSpec antes de concluir a alteração. Registre limitações que os testes não cobrem.
- Antes de editar código Reflex, consulte os skills locais `reflex-docs`, `setup-python-env` e `reflex-process-management` em `.agents/skills/`. Para instalar os skills em outro ambiente, consulte [os recursos oficiais do Reflex](https://github.com/reflex-dev/agent-skills).
- `reflex init` serve para inicializar um projeto novo; para executar este projeto, use o ambiente existente e `reflex run`.
