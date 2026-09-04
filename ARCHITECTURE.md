# Arquitetura do MetroFlow

O projeto usa uma organizacao modular inspirada em arquitetura hexagonal. As
camadas sao criadas apenas quando existe uma responsabilidade concreta, sem
diretorios vazios ou abstracoes prematuras.

```text
MetroFlow/
|-- MetroFlow.py                    # composicao e registro de rotas
|-- auth/
|   |-- infrastructure/             # cliente Xano e cookie HttpOnly
|   `-- presentation/               # API, estado e paginas Reflex
`-- planning/
    `-- presentation/               # paginas e componentes de trajetos

tests/
`-- unit/
    `-- auth/                        # testes isolados de autenticacao
```

## Direcao das dependencias

- `presentation` coordena entradas e saidas da interface.
- `infrastructure` encapsula integracoes externas, como o Xano.
- `MetroFlow.py` apenas monta a aplicacao e registra suas rotas.
- Os testes reproduzem a divisao por modulo e por tipo.

Quando a busca ganhar regras reais, `planning` recebera as camadas `domain`,
`application` e `infrastructure`. Elas serao adicionadas junto com seus modelos,
casos de uso e adaptadores concretos.
