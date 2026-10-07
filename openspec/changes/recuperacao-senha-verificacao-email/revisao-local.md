# Revisão local em 02/10/2026

## Problemas e decisões

- As chamadas da interface forçavam a porta 8000 quando a página estava na porta 3000. Restaurar chamadas na mesma origem para o modo documentado `--env prod --single-port`, incluindo login, sessão, planejamento e ações por e-mail.
- O formulário removia o token do fragmento ao enviar e perdia a possibilidade de tentar novamente após erro de rede ou senha inválida. Capturar o token ao montar o formulário, remover o fragmento da URL e manter o valor apenas em uma propriedade JavaScript do elemento até sucesso ou rejeição definitiva. Nunca colocar o token no estado Reflex, em atributos HTML ou armazenamento persistente.
- Impedir envios duplicados e apagar o cookie local após redefinição bem-sucedida. A revogação de outras sessões continua sendo responsabilidade do Xano, pendente de validação remota nesta revisão.

## Verificação prevista

Executar os scripts com navegador simulado e rede substituída em Node.js para verificar destino das chamadas, tentativas após falhas e limpeza do token. Executar a suíte Python, compilação Reflex e validação estrita OpenSpec. Não modificar serviços remotos.

## Auditoria de 02/10/2026

- A suíte local passou com 97 testes e 10 subtestes; foram adicionados casos para o redirecionamento após redefinição e para mensagens de links rejeitados.
- A compilação seca do Reflex passou, e a validação estrita com `@fission-ai/openspec@1.7.0` aprovou as seis especificações e mudanças existentes.
- Em 04/10/2026, os endpoints `email/confirmar` e `senha/redefinir` foram publicados no Xano com consulta bloqueante, validação, consumo do token e alteração do usuário dentro da mesma transação.
- A consulta deixou de depender do filtro `consumido_em == null`; a precondição transacional exige que o registro exista e ainda não tenha sido consumido. Um teste com token sintaticamente válido, porém inexistente, foi rejeitado sem alterar dados.
- A redefinição atualiza a senha e incrementa `versao_sessao` na mesma transação. A eficácia contra uma sessão real anterior ainda depende do teste ponta a ponta pendente.
- Os links enviados pelo Brevo também precisam ser testados com o rastreamento desativado ou comprovadamente compatível com o fragmento. Um redirecionador que não preserve o fragmento remove o token antes de a página Reflex recebê-lo.
