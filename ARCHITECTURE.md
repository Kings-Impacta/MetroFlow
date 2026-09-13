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
    |-- domain/                     # modelos normalizados e invariantes
    |-- application/                # casos de uso e portas
    |-- infrastructure/             # adaptador da API Xano
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

O calculo do caminho permanece no Xano. O dominio local valida e normaliza o
contrato, enquanto a aplicacao impede selecoes invalidas antes da chamada
externa.

## Estado da integracao em 13/09/2026

Os adaptadores Python foram exercitados contra o Xano com login, listagem de
estacoes e uma consulta de trajeto com baldeacao. Isso ainda nao valida o fluxo
completo no navegador: `planning/presentation/pages.py` usa dados demonstrativos
e ainda nao chama os casos de uso de planejamento.

A proxima etapa funcional deve conectar a interface ao backend preservando a
sessao HttpOnly e implementar carregamento, sucesso, ausencia de rota e erro.
Veja `docs/validacao-integracao-xano.md` para evidencias e limitacoes.
