# MetroFlow — manual de uso

O **MetroFlow** ajuda passageiros a planejar viagens na rede ferroviária metropolitana de São Paulo. Ao informar origem e destino, a pessoa recebe um trajeto com linhas, sentidos, baldeações e tempo estimado. O aplicativo também apresenta condições operacionais das linhas e permite que administradores consultem indicadores e gerenciem a situação das estações.

O problema atendido é reunir, em uma sequência compreensível, informações que o passageiro precisaria consultar em diferentes mapas e quadros de operação. O público principal são usuários do Metrô, CPTM e concessionárias.

**Versão descrita:** entrega integrada à main pelo PR #52, com validação administrativa em 18/11/2026. Os limites dessa versão estão na seção [Limitações conhecidas](#7-limitações-conhecidas).

## 1. Acesso ao aplicativo

Não há link de deploy público homologado informado nesta entrega. A demonstração validada usa o aplicativo executado localmente, com internet para acessar os serviços do projeto.

Se o grupo já iniciou o servidor, abra [http://localhost:3000](http://localhost:3000), ou a porta indicada no terminal. Esse endereço funciona no computador que está executando o MetroFlow; não é um link público de acesso remoto. Mantenha o terminal do servidor aberto.

### Preparar a execução no Windows

É necessário ter **Git**, **uv**, acesso ao repositório e conexão com a internet. O uv prepara o Python 3.12 e as dependências registradas no projeto.

```powershell
git clone https://github.com/Kings-Impacta/MetroFlow.git
cd MetroFlow
.\iniciar-status-local.ps1
```

Para atualizar uma cópia existente, pare o servidor com **Ctrl+C** e, na pasta do projeto, execute:

```powershell
git status
git switch main
git pull --ff-only origin main
.\iniciar-status-local.ps1
```

Se houver alterações locais ou conflito, preserve os arquivos e peça orientação ao grupo antes de continuar. Não descarte alterações para forçar a atualização.

O iniciador habilita as três fontes de status da configuração local validada. Também é possível iniciar sem essa ativação com `iniciar-metroflow.ps1`; nesse caso, a busca continua disponível, mas o status pode aparecer como indisponível. Nenhuma senha ou chave pessoal deve ser colocada no README.

Para outros ambientes e detalhes de configuração, consulte o [guia técnico](docs/guia-tecnico.md).

## 2. Perfis de usuários

| Perfil | O que pode fazer |
|---|---|
| Visitante, sem login | Acessar as telas de entrada, cadastro e recuperação de acesso. O planejamento exige autenticação. |
| Passageiro autenticado | Selecionar estações, usar a sugestão por localização, buscar trajetos, consultar instruções e status e encerrar sua sessão. |
| Administrador autenticado | Usar as funcionalidades de passageiro e acessar **Administração**: indicadores agregados, pesquisa/filtro de estações e controles de ativação/inativação. |

O cadastro comum **não concede acesso administrativo**. Uma pessoa responsável pelo projeto precisa conceder esse papel no backend. Não existe autoatribuição de administrador na interface. A ausência do link não é a única proteção: cada operação administrativa verifica a autorização no servidor.

## 3. Funcionalidades disponíveis

- Cadastro com confirmação de e-mail, login, logout, reenvio de confirmação e recuperação de senha.
- Sugestão da estação mais próxima como origem, mediante permissão de localização.
- Busca por origem e destino, com linhas, operadores, sentidos, estações, esperas e baldeações estimadas.
- Registro automático da viagem após uma busca bem-sucedida, sem botão adicional de confirmação.
- Seleção automática de alternativa quando a ocupação estimada por outras buscas justificar um caminho dentro dos limites configurados.
- Indicadores de status das linhas no resumo e nos embarques, com consulta detalhada em `/status`.
- Painel administrativo com indicadores de uso, malha, volume, estações mais usadas e ocupação estimada, além de consulta e gestão da situação das estações.

## 4. Manual de utilização — passageiro

### 4.1 Criar uma conta e entrar

1. Na tela **Entrar**, clique em **Cadastre-se**.
2. Preencha os dados solicitados e envie o cadastro.
3. Abra a mensagem recebida no seu e-mail e conclua a confirmação. Confira a pasta de spam, se necessário.
4. Retorne ao aplicativo e entre com o e-mail e a senha cadastrados.
5. Se a mensagem não chegar ou o link não funcionar, use o fluxo de reenvio da confirmação disponibilizado pelo aplicativo.

**Resultado esperado:** após autenticar, você pode acessar **Buscar trajeto**. Uma sessão ausente, inválida ou expirada exige novo login.

### 4.2 Escolher a origem pela localização — opcional

1. Abra **Buscar trajeto**.
2. No aviso **Encontrar a estação mais próxima de você?**, clique em **Usar minha localização**.
3. Autorize a localização no navegador, se desejar. O pedido só ocorre após esse clique.
4. Confira a estação sugerida e a distância aproximada exibida abaixo da origem.
5. Se preferir outra estação, substitua a origem manualmente. **Agora não** permite continuar sem localização.

**Resultado esperado:** a origem é preenchida com a estação cadastrada mais próxima a até 5 km. A distância é **em linha reta**, não o percurso a pé até uma entrada da estação. O cálculo ocorre no navegador; a posição do usuário não é enviada ao backend nem ao Xano.

Se não houver permissão, o tempo de resposta terminar ou nenhuma estação estiver dentro do limite, escolha a origem manualmente. A localização exige um contexto seguro: funciona em `localhost` e HTTPS; um endereço de rede local servido apenas por HTTP pode não permitir o recurso.

### 4.3 Buscar e interpretar um trajeto

1. Digite parte do nome da estação de origem e **selecione a sugestão** correspondente.
2. Faça o mesmo no destino. Digitar sem selecionar a estação não conclui a escolha.
3. Para trocar os sentidos, use o botão de inversão entre os campos.
4. Clique em **Buscar trajeto** e aguarde o resultado.
5. Confira o **tempo estimado**, o número de baldeações e as linhas utilizadas.
6. Leia **Como chegar**: espera, embarque, sentido, percurso, integração ou baldeação e desembarque.
7. Observe os indicadores de status no resumo e nos cartões de embarque.

**Resultado esperado:** um trajeto válido entre as estações selecionadas. O tempo inclui os deslocamentos, esperas disponíveis e baldeações estimadas, com **um minuto de margem apenas sobre o total**. A indicação não garante a duração real da viagem.

Uma busca bem-sucedida registra automaticamente a viagem para a demonstração de concorrência. Cada conta mantém no máximo uma viagem ativa; uma nova busca bem-sucedida substitui a anterior. Não há confirmação ou cancelamento manual.

### 4.4 Entender a alternativa automática

Outras contas com viagens sobrepostas podem influenciar a rota retornada. O sistema compara a ocupação estimada por trecho e sentido e só aceita alternativas dentro dos limites de tempo, baldeações e redução de exposição.

Isso **não significa que toda segunda busca terá uma rota diferente**. Se não houver sobreposição relevante ou alternativa proporcional, o caminho principal pode continuar sendo escolhido. A interface apresenta um único trajeto, sem exibir dados de ocupação dos demais passageiros.

### 4.5 Consultar o status detalhado

1. Abra [Condições operacionais das linhas](http://localhost:3000/status), no mesmo servidor do aplicativo. Se estiver usando outra porta, acrescente `/status` ao endereço em uso.
2. Clique em **Atualizar condições**, caso a consulta ainda não tenha sido iniciada.
3. Confira situação, fonte e horário de coleta de cada linha.
4. Para voltar, use **Voltar ao planejador**.

**Resultado esperado:** informação operacional das linhas efetivamente retornadas pelas fontes. As cores são acompanhadas de texto: verde para normalidade, amarelo para restrição, vermelho para interrupção e cinza para estados como encerramento, desconhecido ou indisponível.

A tela consulta novamente a cada minuto, respeitando o cache e o intervalo de cada fonte; isso não significa uma nova coleta externa a cada minuto. Em falhas, o último retorno permitido é mantido com sua data. Os indicadores compactos do trajeto não mostram o sufixo de idade; confira a validade e as datas no detalhe.

O status é **informativo**: não bloqueia a busca nem altera automaticamente o cálculo ou o registro de viagens.

### 4.6 Recuperar acesso e sair

1. Na tela de entrada, clique em **Esqueci minha senha** e informe o e-mail.
2. Siga as instruções da mensagem recebida para definir a nova senha.
3. Após concluir, entre novamente. O aplicativo não informa a terceiros se determinado e-mail tem conta cadastrada.
4. Para encerrar sua sessão, clique em **Sair**.

Evite repetir envios enquanto aguarda o e-mail. Não compartilhe links de recuperação, senhas ou tokens.

## 5. Manual de utilização — administrador

### 5.1 Consultar o painel

1. Entre com uma conta que já recebeu a concessão administrativa.
2. Clique em **Administração** no cabeçalho, ou abra `/admin` no endereço do aplicativo.
3. Aguarde o carregamento separado dos indicadores e da lista de estações.
4. Confira **Apurados em**, para saber quando os números foram calculados.
5. Clique em **Atualizar indicadores** para solicitar uma nova apuração.

**Resultado esperado:** contagens agregadas de uso, estações/linhas/trechos cadastrados ativos, volume de registros, ranking de estações e critério da ocupação demonstrativa. Os indicadores não apresentam e-mails nem registros individuais de passageiros. Uma busca registrada não comprova uma viagem realizada.

Sem concessão, a página informa acesso restrito. Se o serviço estiver lento ou indisponível, aguarde e use **Tentar novamente**. Isso não concede permissão. A recuperação automática é limitada às consultas de leitura; alterações de estação não são reenviadas automaticamente.

### 5.2 Pesquisar e filtrar estações

1. Na seção **Estações**, digite o nome ou o código em **Pesquisar por nome ou código**.
2. Use **Filtrar por situação** para escolher todas, ativas ou inativas.
3. Confira nome, código, linhas e situação na tabela.
4. Limpe a pesquisa e volte ao filtro **Todas** para recuperar a listagem completa.

**Resultado esperado:** somente a tabela exibida é filtrada. Pesquisar ou filtrar não altera a malha.

### 5.3 Gestão da situação — somente em manutenção autorizada

A interface implementa os seguintes controles, que afetam as próximas buscas:

1. **Inativar** abre uma confirmação com a estação e as linhas envolvidas.
2. **Cancelar** encerra a confirmação sem alterar a situação.
3. **Inativar estação** confirma a retirada da estação da seleção e dos caminhos futuros.
4. **Ativar** solicita a reativação, sem a etapa adicional de confirmação.
5. Confira a situação devolvida pelo servidor. As alterações efetivas registram responsável e momento no backend; solicitar a mesma situação não deve criar um novo histórico.

Viagens já registradas não são encerradas por essa alteração. Use esses controles somente em manutenção autorizada: eles afetam o banco compartilhado. **A alteração real da situação e seu efeito ponta a ponta não foram validados nesta rodada**, que preservou todas as estações e os parâmetros. A validação realizada cobriu consultas e indicadores.

## 6. Exemplos de utilização

| Cenário | Como realizar | O que observar |
|---|---|---|
| Planejamento principal | Buscar **Palmeiras-Barra Funda → Paraíso** com uma conta passageiro. | Instruções, sentidos, baldeação e tempo estimado. |
| Concorrência entre contas | Em duas sessões isoladas, usar contas diferentes e fazer a mesma busca com poucos segundos de diferença. | Pode surgir uma alternativa proporcional para a segunda conta. Duas abas da mesma sessão não representam dois passageiros. |
| Origem sugerida | Usar a localização e depois, se necessário, escolher outra origem. | Distância em linha reta e liberdade para substituir a sugestão. |
| Consulta administrativa | Pesquisar `republica` e conferir a estação República; depois limpar o filtro. | Pesquisa sem distinção de acentos, sem gravar alterações. |
| Entrada incompleta ou inválida | Tentar buscar sem as duas estações selecionadas ou com origem igual ao destino. | Mensagem de validação, sem criar um trajeto válido. |

No teste de **17/11/2026**, a primeira conta recebeu Linha 3 → Sé → Linha 1, com **1215 segundos estimados (21 min arredondados)**; a segunda recebeu Linha 3 → República → Linha 4 → Paulista/Consolação → Linha 2, com **1725 segundos (29 min arredondados)**. São referências de uma rodada validada, **não tempos fixos nem promessa de repetir o mesmo caminho**. Horários, ocupação prevista e disponibilidade mudam o resultado. Consulte a [auditoria da rodada](docs/xano/acesso-administrativo-concorrencia-2026-11-17.md).

Não há credenciais de demonstração publicadas no repositório. O grupo deve preparar previamente contas próprias e uma concessão administrativa autorizada.

## 7. Limitações conhecidas

- **Tempos:** são estimativas; podem variar por operação, circulação interna, espera e outras condições externas. A margem é única sobre o total.
- **Ocupação:** é uma demonstração baseada nas buscas registradas, não uma medição oficial de lotação dos trens. O critério atual de 1 usuário/1% é demonstrativo.
- **Status:** a cobertura observada é de 12 linhas (1/2/3/4/5/8/9/10/11/12/15/17). Linhas 6/7/13 e serviços especiais sem resposta própria permanecem indisponíveis. A API Direto dos Trens aguarda token e validação autorizada. As condições para ativação pública das fontes continuam pendentes.
- **Atualidade:** preservar o último retorno não comprova que a condição na origem ainda seja atual. O fuso de `dataGeracao` da CPTM não foi confirmado; a coleta local é a referência de validade disponível.
- **Localização:** depende de permissão e disponibilidade do navegador. A precisão em diferentes dispositivos/celulares não foi certificada; as coordenadas representam estações, não suas entradas nem uma rota acessível a pé.
- **Orientações de desembarque:** alguns lados de porta do piloto foram sorteados para demonstração e estão marcados como fictícios na fonte dos dados. Não devem ser usados como orientação confiável; confira a sinalização e os avisos da estação. A cobertura é parcial e depende de confirmação em campo.
- **Malha e serviços especiais:** refletem o modelo cadastrado. A Linha 6 representa a operação parcial modelada; não é garantia de operação atual ou de todas as conexões futuras. Os retornos diretos pendentes do Expresso L10 podem deixar de aparecer como opção mais rápida.
- **Administração:** abertura, consultas e atualização manual foram validadas com sessão real. Ativação/inativação, revogação e disputas administrativas não foram integralmente validadas em produção nesta rodada; não são demonstradas por alteração real da malha.
- **Disponibilidade:** autenticação, planejamento, e-mail e status dependem da internet e de serviços externos. A recuperação limitada do painel não elimina lentidão prolongada do fornecedor.
- **Melhorias futuras:** histórico pessoal dos dez trajetos recentes e múltiplas opções para escolha ainda não estão entregues. A alternativa automática da concorrência não substitui essas funcionalidades. A área administrativa já está implementada, com os limites acima.

Os seis itens adiados de malha/status estão registrados em [melhorias futuras e limitações](docs/melhorias-futuras-malha-status.md). O teste anterior de configuração ausente foi **HTTP local isolado**, não HTTP no runtime nativo do Xano; isso não comprova gravações administrativas simultâneas.

## Documentação técnica

- [Guia técnico: ambiente, configuração e testes](docs/guia-tecnico.md).
- [Visão geral](docs/project-overview.md), [modelo de domínio](docs/domain-model.md) e [arquitetura](ARCHITECTURE.md).
- [Configuração e limites de status](docs/status-operacional.md).
- [Evidências da correção administrativa e da concorrência](docs/xano/acesso-administrativo-concorrencia-2026-11-17.md).

Este manual documenta o uso; não certifica a disponibilidade das operadoras.
