# Validação complementar do planejamento

Registro reproduzível da escolha do trajeto principal, sem alterar dados ou recursos remotos do Xano.

## Método

O teste `tests/unit/planning/test_xano_route_algorithm.py` lê diretamente a função `lambda` registrada em `docs/xano/rascunhos/planejamento/trajetos_buscar_post.xs` e a executa com Node.js. Dessa forma, a evidência usa a mesma lógica documentada para o endpoint, em vez de reimplementar o algoritmo em Python.

Duas malhas pequenas são construídas apenas em memória:

- caminhos com 200 e 300 segundos, nos quais deve ser escolhido o caminho de 200 segundos;
- caminhos empatados em 800 segundos, um sem baldeação e outro com uma baldeação de 600 segundos, nos quais deve ser escolhido o caminho sem baldeação.

Nenhum usuário, credencial, token ou dado do Xano participa desses testes.

## Ambiente verificado

- ambiente virtual existente em `.venv`;
- Python 3.12.14;
- Reflex 0.9.10.post1, conforme a versão fixada pelo projeto;
- Node.js disponível para executar a função documentada do XanoScript;
- instalação e execução descritas no `README.md`, em `iniciar-metroflow.ps1` e nos skills locais `setup-python-env` e `reflex-process-management`.

O comando `uv` não estava visível no `PATH` do ambiente controlado da revisão. Isso não altera a `.venv` existente nem o procedimento oficial `uv sync --frozen --group dev --python 3.12`; o script `iniciar-metroflow.ps1` continua verificando essa dependência para novas instalações.

## Limite da evidência

O teste confirma o comportamento da função registrada no XanoScript local e impede regressões nesse artefato. Ele não comprova sozinho que o arquivo local corresponde à revisão publicada no workspace remoto; essa comparação continua sujeita a uma exportação identificada do Xano.

## Execução local da revisão

Os dois testes controlados passaram em 1,11 segundo. A suíte completa voltou a bloquear no `TestClient` dentro do ambiente controlado, sem produzir uma falha de asserção. A compilação seca iniciou o Reflex, mas não concluiu porque o ambiente não conseguiu acessar os registros do Node. O arquivo gerado `reflex.lock/package.json` foi restaurado, sem mudança de dependências.

No terminal normal do projeto, 102 testes e 18 subtestes passaram em 16,59 segundos; a compilação seca do Reflex terminou com sucesso; e a validação estrita aprovou os 5 itens OpenSpec. Permaneceram apenas os avisos conhecidos de depreciação do `TestClient` e da ativação implícita do Radix Themes.
