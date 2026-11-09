## Context

O Xano armazena a malha e calcula trajetos; o backend Python protege a sessão e
normaliza contratos externos; o Reflex apresenta o resultado. A ARTESP oferece API
documentada para linhas delegadas, enquanto o endpoint agregado observado para as
demais linhas não possui contrato público de terceiros localizado.

## Goals / Non-Goals

- Apresentar condições operacionais com origem e atualidade verificáveis.
- Cobrir progressivamente a rede sem transformar ausência de dado em operação normal.
- Respeitar autenticação, limites, licença e atribuição de cada fonte.
- Não implementar lotação, tempos de espera, caminhada ou transferência.
- Não alterar nesta entrega o cálculo do menor caminho ou excluir linhas por status.
- Não depender de coleta do HTML de páginas das operadoras.

## Decisions

- O backend Python concentrará adaptadores, normalização e cache; credenciais não
  chegarão ao Reflex.
- Cada adaptador produzirá o mesmo modelo interno e será testável sem rede.
- A ARTESP será prioritária para linhas delegadas. Fontes oficiais autorizadas do
  Metrô e da CPTM serão prioritárias em suas próprias linhas.
- O código da linha será a chave de correspondência; nomes servirão somente para
  apresentação e validação de divergências.
- Falha, resposta inválida ou expiração produzirá estado explícito indisponível ou
  desatualizado. O planejamento continuará disponível.
- A primeira versão será informativa. Utilizar ocorrências como peso ou bloqueio de
  rota exigirá outra mudança e evidência sobre o impacto operacional.
- A integração complementar permanecerá desabilitada enquanto os termos de uso não
  forem confirmados.

## Risks / Trade-offs

- Endpoints sem contrato podem mudar ou ser retirados sem aviso.
- Fontes podem divergir para a mesma linha ou atualizar em momentos diferentes.
- O limite de 12 chamadas por hora da ARTESP exige cache compartilhado e impede uma
  consulta por usuário.
- Descrições livres podem citar trechos sem estrutura suficiente para modificar o
  cálculo de rota com segurança.

## Migration Plan

1. Confirmar por escrito termos, atribuição, limites e credenciais.
2. Implementar modelo interno e adaptadores desabilitados por padrão.
3. Implementar cache e observabilidade sem conteúdo sensível.
4. Publicar endpoint local protegido e apresentação informativa.
5. Validar respostas normais, ocorrências, divergência, expiração e indisponibilidade.
6. Ativar cada fonte somente depois de registrar sua autorização e configuração.

## Open Questions

- O endpoint agregado pode ser consumido e republicado por projeto acadêmico?
- Há SLA, limite, versão ou endereço permanente para esse serviço?
- Qual atribuição deve acompanhar os dados do Metrô e da CPTM?
- Quais são todos os valores possíveis de `StatusCode` e seus significados?


## Implementação de 09/11/2026

O status usa endpoint autenticado próprio e eventos Reflex separados. A busca e o registro não consultam fontes de status, nem aguardam sua resposta. A apresentação contextual usa códigos explícitos de linha, nunca dedução do nome. A página de status também permite consultar toda a rede.

Adaptadores ARTESP e agregado são desativados por padrão. ARTESP exige chave e ativação; complemento exige confirmação configurada de autorização e cobertura. Não há alteração de Xano nesta entrega. Normalizar `situacao`, não o booleano `operacao_normal`, que também abrange restrições. Preservar `atualizado_em` e `verificado_em` com significados diferentes.

Cache SQLite persistente entre usuários e processos do mesmo servidor, com reserva transacional antes da rede. Uma tentativa por 300 segundos, no máximo 12 na janela móvel de uma hora por credencial; falhas contam e HTTP 429 suspende novas tentativas por uma hora. Sem cache gravável, não consultar a origem. Em várias máquinas, exigir cache/coletor central antes de ativar. O estado fica desatualizado após 10 minutos desde coleta/verificação, imediatamente após falha conhecida, e indisponível após uma hora. Dados futuros ou sem situação válida não viram normalidade.

A fonte responsável prevalece; divergências são registradas sem payloads. A consulta fica disponível mesmo com todas as fontes desativadas, com estado indisponível. Sem amostras autenticadas e credenciais, testes usam contratos documentados e transporte HTTP simulado; isso não comprova ativação real.
