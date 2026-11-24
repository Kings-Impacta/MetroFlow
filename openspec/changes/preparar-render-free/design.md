## Decisão

Usar runtime Python nativo do Render com uv.lock e Node 22, evitando exigir Docker no computador do grupo. Exportar frontend durante build; iniciar Granian e o app Reflex com a montagem dos arquivos compilados na mesma origem. Esta integração usa mecanismos da versão fixada 0.9.10.post1 e precisa ser revalidada antes de atualizar Reflex.

## Segurança e limites

Uma instância/worker; cookie de produção; nenhum segredo incluído. Nenhuma criação de recursos remotos. Status recusam ativação por variáveis neste pacote. Xano continua responsável pelo cálculo, exclusividade e registro. Cache local é efêmero e não garante preservação entre reinícios. O servidor suspenso não coleta status. O limite de memória do Free e o acesso real às fontes exigem homologação posterior.

## Laboratório Linux preparado em 23/11/2026

Docker é opcional somente para homologação local, não altera o runtime nativo proposto no Render. Imagens oficiais fixam Python 3.12.14, Node 22.22.0 e uv 0.12.23. O alvo de testes executa instalação limpa congelada, exportação e suíte; o runtime executa o `serve.py` original, com usuário sem privilégios, 512 MB e 0,1 CPU. Nenhuma porta é publicada e nenhum volume do host é montado.

O domínio reservado `.invalid` representa a origem de produção na compilação. URLs Xano apontam para loopback sem serviço e fontes ficam desligadas. O runtime usa `--network none`; a verificação por `docker exec` faz somente HTTP em loopback e não registra viagens. Conferir páginas/asset 200, APIs sem sessão 401, upgrade WebSocket 101 e reinício. Isso não homologará TLS público, sessão real, carga, e-mails ou disponibilidade no Render.

A execução continua pendente até obter logs reais. Neste terminal, primeiro o motor estava ausente e depois o canal local do Docker retornou permissão negada. Scripts e documentação em `deploy/render/linux/` permitem executar no terminal normal do usuário, sem tratar essa limitação de acesso como falha comprovada do projeto em Linux.
