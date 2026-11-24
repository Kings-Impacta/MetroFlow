## ADDED Requirements

### Requirement: Retenção independente de status

O armazenamento SHALL conservar a última condição armazenável por fonte e linha sem alterar a malha ou os parâmetros da concorrência.

#### Scenario: Falha ou resposta parcial

- **WHEN** a origem falha ou omite uma linha
- **THEN** o último retorno dessa linha permanece com os horários originais e validade antiga

### Requirement: Escrita coordenada

A persistência SHALL exigir reserva válida, fonte autorizada, geração corrente e resposta normalizada. O limite SHALL ser de uma tentativa por cinco minutos e 12 por hora por fonte.

#### Scenario: Coletores simultâneos

- **WHEN** duas reservas disputam a mesma fonte
- **THEN** somente uma geração é concedida sob bloqueio transacional

#### Scenario: Resposta atrasada

- **WHEN** uma publicação usa geração antiga ou lease expirado
- **THEN** nenhuma condição válida é substituída

### Requirement: Independência e limites de evidência

A ativação SHALL ser explícita por fonte e distinguir teste local de homologação Xano. Leituras SHALL ser compartilhadas no servidor para reduzir consumo da cota comum. No modo remoto o site SHALL ler somente o snapshot, sem consultar as fontes diretamente.

#### Scenario: Banco de status indisponível

- **WHEN** a consulta de status falha
- **THEN** busca e registro não dependem dessa consulta, e o último retorno local é preservado quando disponível

### Requirement: Escrita administrativa separada

O endpoint de controle SHALL validar sessão ativa, verificada, versão atual e concessão administrativa existente. O coletor local SHALL manter credenciais apenas em memória e enviar somente retornos já persistíveis, sem renovar suas datas.

#### Scenario: Passageiro tenta gravar status

- **WHEN** uma sessão sem concessão administrativa tenta reservar ou publicar
- **THEN** o Xano recusa a operação sem gravar condições

#### Scenario: Reenvio de um retorno antigo

- **WHEN** o coletor reenvia um retorno anterior
- **THEN** as datas originais são mantidas e a informação antiga não se torna atual apenas pelo reenvio
