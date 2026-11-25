## Preparação local

- [x] Consultar plano e workspace somente em leitura e documentar os limites.
- [x] Especificar esquema separado, reserva, autenticação e política de retenção.
- [x] Preparar e validar redutor, rascunhos XanoScript e cliente desativado.
- [x] Executar testes locais e documentar seu alcance (incluindo HTTPS em loopback, não runtime Xano).

## Pendências sem autorização de publicação

- [ ] Confirmar disponibilidade de agendamento no painel/suporte do plano atual.
- [ ] Confirmar uso de espaço/registros antes de criar a tabela.
- [ ] Confirmar condições das fontes e configurar conta técnica/chaves somente no backend.
- [ ] Fazer backup e homologar transação, JWT, bloqueio, cota e falhas no runtime Xano.
- [ ] Validar carga junto com duas contas de viagens antes de ativar ou publicar.


## Integração autorizada em 24/11/2026

- [x] Integrar leitor compartilhado à fábrica, com fontes diretas excluídas no modo remoto.
- [x] Reutilizar permissão administrativa existente para escrita isolada, sem alterar concessões.
- [x] Validar suíte local e contratos antes da instalação; GET/POST sem sessão conferidos por HTTP.
- [x] Fazer backup e instalar somente tabela, grupo, endpoints e inicializador de status no Xano.
- [x] Validar HTTP nativo de leitura/proteção: 200/401/400/403 com fonte desligada, preservando malha e parâmetros.
- [ ] Entregar na main após checks e configurar leitura no Render.
- [ ] Alimentar apenas fontes liberadas, mantendo pendências explícitas.


- [x] Validar gravação/releitura e retenção no banco nativo com um registro sintético invisível; remover registro e função temporários.
- [x] Comparar hashes das oito tabelas protegidas antes/depois, sem diferenças.
- [ ] Validar publicação positiva e reserva concorrente do redutor/transação no runtime nativo; a CLI recusou lambda em contexto de função. Não marcar como executado.
