# Guia de execução e apresentação do MetroFlow

Este guia permite que qualquer integrante do grupo prepare e apresente o projeto a partir da branch `main`, sem receber senhas ou chaves pessoais de outro integrante.

## Pré-requisitos

- Windows 10 ou 11 com PowerShell;
- Git;
- `uv`, disponível em <https://docs.astral.sh/uv/getting-started/installation/>;
- acesso ao repositório do grupo e à internet durante a apresentação.

O `uv` prepara o Python 3.12 e instala as versões registradas em `uv.lock`. O projeto usa as APIs públicas do MetroFlow no Xano. O Brevo é chamado pelo Xano; sua chave não deve ser colocada no computador do apresentador nem enviada pelo grupo.

## Preparação inicial

No PowerShell, execute:

```powershell
git clone https://github.com/Kings-Impacta/MetroFlow.git
cd MetroFlow
.\iniciar-metroflow.ps1
```

Se o repositório já estiver no computador:

```powershell
git switch main
git pull origin main
.\iniciar-metroflow.ps1
```

Caso a política do PowerShell bloqueie o script, use somente para essa execução:

```powershell
powershell -ExecutionPolicy Bypass -File .\iniciar-metroflow.ps1
```

O terminal informa o endereço da aplicação. Abra `http://localhost:3000`; se essa porta estiver ocupada, use a porta indicada no log, como `http://localhost:3001`. Mantenha o terminal aberto durante toda a demonstração. Para encerrar, pressione `Ctrl+C` nele.

## Roteiro mínimo da apresentação

1. Cadastre uma conta de demonstração ou entre com uma conta já confirmada.
2. Se criar uma conta, abra a mensagem recebida e confirme o e-mail antes de entrar.
3. Pesquise um trajeto nos dois sentidos, por exemplo Palmeiras-Barra Funda e Brigadeiro.
4. Mostre as estações, linhas, sentidos, baldeações e o tempo estimado.
5. Encerre a sessão e confirme que a busca protegida solicita login.
6. Se houver tempo, demonstre a recuperação de senha e o retorno à tela de login.

## Verificação antes da aula

Com o servidor desligado, execute:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
openspec.cmd validate --all --strict --no-interactive
```

O OpenSpec é uma verificação de documentação e pode exigir a ferramenta instalada separadamente. Ele não é necessário para iniciar a aplicação. Os testes da interface em JavaScript usam Node.js quando disponível; o site também pode ser executado sem instalar Node.js separadamente, pois o Reflex gerencia sua execução.

## Solução rápida de problemas

- **`uv` não encontrado:** instale o `uv`, feche e abra o PowerShell e tente novamente.
- **Porta 3000 ocupada:** abra a porta exibida em `reflex.log`.
- **Serviço de autenticação indisponível:** confirme a conexão com a internet e verifique se o Xano está disponível.
- **E-mail não chegou:** confira spam e promoções e aguarde o registro do envio; não exponha chaves do Brevo para tentar corrigir localmente.
- **Mudanças recentes não aparecem:** encerre o Reflex com `Ctrl+C`, atualize a `main` e execute novamente o script.

## Limite operacional

A apresentação depende da disponibilidade da internet, do Xano e do provedor de e-mail. O código, as dependências e as instruções ficam disponíveis no GitHub, mas os dados da malha e a autenticação são serviços remotos do projeto.
