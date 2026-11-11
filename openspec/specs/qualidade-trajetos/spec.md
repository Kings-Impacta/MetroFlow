# qualidade-trajetos Specification

## Purpose
Preservar percursos coerentes para o passageiro, sem voltas artificiais, com ocupação prevista, transferências e limites proporcionais para as alternativas.

## Requirements

### Requirement: Informação de acesso na integração
O sistema SHALL informar quando a transferência entre metrô e trens puder exigir novo pagamento ou confirmação local de gratuidade, sem afirmar gratuidade não comprovada.

#### Scenario: Transferência no pico de dia útil
- **WHEN** uma rota troca entre metrô e trens em Tatuapé ou Corinthians-Itaquera fora dos períodos de integração livre
- **THEN** o resultado alerta sobre possível novo pagamento

#### Scenario: Sábado com conflito entre fontes
- **WHEN** a transferência ocorre antes das 10h de sábado
- **THEN** o resultado orienta conferir a gratuidade localmente sem impor um bloqueio por suposição

### Requirement: Alternativa proporcional
O sistema SHALL preservar o principal quando a alternativa por concorrência exceder o limite versionado de tempo ou acrescentar mais de uma transferência.

#### Scenario: Desvio pelo centro para evitar trecho curto
- **WHEN** evitar um trecho ocupado produz alternativa fora da tolerância
- **THEN** a busca mantém o trajeto principal

#### Scenario: Alternativa equivalente disponível
- **WHEN** uma alternativa disponível evita a ocupação dentro da tolerância
- **THEN** a busca apresenta essa alternativa

#### Scenario: Gargalo comum às alternativas
- **WHEN** nenhuma opção evita todos os trechos ocupados mas uma alternativa reduz a exposição sem aumentar tempo nem trocas
- **THEN** pode apresentar essa alternativa equivalente preservando o trecho comum necessário

### Requirement: Percurso sem voltas artificiais
O sistema SHALL apresentar percursos sem estações repetidas e SHALL não circular para consumir tempo até a abertura de conexão regular fechada.

#### Scenario: Rede parcial na madrugada
- **WHEN** a conexão regular necessária está fechada
- **THEN** não se constrói uma volta por outra linha até sua abertura

### Requirement: Ocupação prevista
O sistema SHALL confrontar o intervalo previsto de cada trecho com as viagens ativas no mesmo sentido, excluindo a própria viagem.

#### Scenario: Ocupação termina antes da chegada
- **WHEN** a ocupação de um trecho termina antes do embarque previsto do novo usuário
- **THEN** essa ocupação não força desvio

#### Scenario: Viagens atingem juntas uma conexão futura
- **WHEN** as janelas previstas no mesmo trecho e sentido se sobrepõem
- **THEN** essa ocupação participa da escolha da alternativa

### Requirement: Troca na extensão de Itapevi
O sistema SHALL distinguir o tronco da Linha 8 da extensão operacional e SHALL recalcular a mesma troca ao registrar a viagem.

#### Scenario: Viagem até Amador Bueno
- **WHEN** o trajeto passa do tronco à extensão em Itapevi
- **THEN** informa novo embarque sem criar frequência não documentada

#### Scenario: Cliente anterior
- **WHEN** o cliente não suporta a nova troca na mesma linha
- **THEN** não recebe um resultado incompatível com seu contrato
