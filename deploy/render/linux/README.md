# Laboratório Linux local — sem publicação

Este laboratório fecha as verificações que o Windows não comprovou: instalação limpa, exportação completa e inicializador Granian multiprocesso de produção. Usa Docker Desktop já instalado, em modo Linux. Não é um serviço Render, não envia imagens para um registry e não executa `workspace push` no Xano.

O Dockerfile usa Python 3.12.14, Node 22.22.0 e uv 0.12.23 de imagens oficiais, com `uv.lock` congelado. O build executa os mesmos comandos do Blueprint, sem ignorar a instalação nem reaproveitar `node_modules` do Windows. O alvo de testes acrescenta o grupo dev e executa a suíte; a imagem de runtime não inclui esse grupo. Executa como usuário sem privilégios.

O contexto exclui `.env`, caches, `.git`, ambientes virtuais e builds anteriores. Nenhuma credencial é necessária. Todas as fontes estão desligadas e as três URLs Xano apontam para loopback sem serviço. O contêiner de runtime usa `--network none`: o teste só pode alcançar o próprio loopback. Não há portas expostas ao host, volumes montados ou acesso ao banco real.

No terminal normal do Windows, com Docker Desktop em **Engine running**:

```powershell
& "C:\Users\rapha\Documents\Codex\metroflow-render-20261122\deploy\render\linux\validar-linux.ps1"
```

O script recusa qualquer contêiner preexistente com o nome do laboratório; não substitui nem remove contêineres. Cria um contêiner com limite de 512 MB, sem swap e com 0,1 CPU, verifica as páginas e assets reais, as APIs sem sessão (401), o upgrade WebSocket (101) e reinicia para repetir a verificação. Para o contêiner que criou ao terminar; mantém imagens e logs para revisão. Não interfere no MetroFlow habitual nem muda contexto global do Docker.

Evidências: `.cache/linux-validation-20261123/`. Uma falha interrompe a etapa seguinte. Mensagem de conclusão só ocorre se build, testes, supervisor e as duas verificações passarem.

## Alcance

Se passar, comprova esse ambiente Linux local e o smoke test sob o limite de memória/CPU; **não é homologação no Render**, carga real, disponibilidade contínua ou teste autenticado de duas contas. O domínio reservado `https://metroflow.invalid` é usado na compilação para conferir configuração de produção, mas o laboratório não implementa TLS público. Cookies, e-mails, localização HTTPS e duas contas no endereço público continuam para depois de uma publicação autorizada.

## Estado em 23/11/2026

**Executado e conferido.** O usuário executou o script no terminal normal do Windows após o terminal de controle receber permissão negada no canal do Docker. Os logs em `.cache/linux-validation-20261123/` confirmam instalação limpa congelada, exportação completa 4/4, **484 testes e 119 subtestes aprovados**, servidor multiprocesso de produção ativo e as duas verificações após início e reinício.

Páginas e asset responderam 200; APIs sem cookie, 401; upgrade WebSocket, 101. `runtime-state.json` confirmou `Running=true` e `OOMKilled=false`. A amostra de `docker stats` registrou **106,8 MiB de 512 MiB**, com 10 processos/threads contabilizados e NetIO de 0 B. Os contadores cgroup durante o verificador foram 137.105.408 e 112.979.968 bytes; não são picos de um teste de carga. O contêiner foi parado ao terminar, como registrado em `stop.log`.

Isso fecha os critérios locais de instalação e supervisor Linux. Não comprova capacidade com passageiros reais, carga simultânea, TLS público, limites de plataforma ou disponibilidade no Render; não houve publicação nem tráfego para o Xano de produção.
