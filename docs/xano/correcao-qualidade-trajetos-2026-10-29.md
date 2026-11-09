# Correções de qualidade dos trajetos — 29/10/2026

## Escopo e decisão do usuário

A Linha 6-Laranja fica por último, adiada e sem inclusão de estações ou conexões nesta entrega. O trabalho atende a malha já utilizada e não condiciona a conclusão do projeto à entrega integral daquela linha.

## Comportamento implementado

- A busca e a confirmação rejeitam percursos que retornam à mesma estação. Linhas regulares e corredores fechados não recebem uma partida fictícia na abertura; serviços especiais com grade mantêm suas esperas documentadas. A consulta atual não é um agendador de viagem para a manhã seguinte.
- As linhas regulares distinguem sentidos; o tronco da Linha 8 informa Itapevi/Júlio Prestes e a extensão informa Amador Bueno/Itapevi. A troca em Itapevi conta um novo embarque e os mesmos 600 segundos provisórios das demais trocas. Não se inventou frequência da extensão. Um sinalizador de capacidade impede entregar a troca a clientes antigos cujo contrato não a suporta.
- A ocupação é comparada ao intervalo previsto do novo passageiro, com interseção estrita de intervalos: horários que apenas se encostam não são ocupação simultânea. Preservados sentido, própria viagem excluída, viagem mais recente por usuário e leitura de registros antigos.
- A alternativa livre deve ficar dentro de **min(600, max(120, 25% do tempo principal)) segundos adicionais** e de uma troca adicional. A restrição participa da busca, permitindo procurar outra alternativa válida se a mais rápida não satisfizer o limite de trocas. Os números são uma política de produto versionada, não uma medição oficial.
- Se todas as rotas compartilham um trecho ocupado, uma alternativa que reduza o tempo em trechos ocupados só é aceita sem aumentar tempo total ou trocas. Isso mantém opções equivalentes por Turquesa/Coral antes da Diamante. Sem ganho razoável, permanece o principal; não é obrigatório dar caminhos diferentes a duas pessoas.
- Integrações entre a Vermelha e os trens em Tatuapé/Itaquera exibem aviso de possível novo pagamento fora das faixas de gratuidade documentadas em dias úteis. Aos sábados antes das 10h, há orientação para confirmar a gratuidade porque as fontes divergem. O aviso usa o horário previsto da troca, respeita o calendário e não cria bloqueio por suposição.

## Evidência e fontes

O [guia da ViaMobilidade](https://trilhos.motiva.com.br/viamobilidade8e9/guia-de-uso/) identifica a integração em Itapevi com a extensão para Amador Bueno. A [página de bilhetes do Metrô](https://www.metro.sp.gov.br/sua-viagem/bilhetes-cartoes/) e o [guia de outubro/2026](https://www.metro.sp.gov.br/wp-content/uploads/2026/10/guia_do_passageiro_online.html) fundamentam os avisos e registram o conflito sobre sábado. Os [horários do Metrô](https://www.metro.sp.gov.br/sua-viagem/horarios/) diferenciam novo embarque, permanência na mesma linha e transferências. As fontes da auditoria anterior permanecem vinculadas em [auditoria-trajetos-uso-diario-2026-10-29.md](auditoria-trajetos-uso-diario-2026-10-29.md).

## Comparações controladas

Os dados exportados do Xano são executados localmente sem criar viagens reais. Nas 290 buscas sem lotação, as sete voltas artificiais de madrugada desapareceram. Nas 108 simulações de ocupação, os 23 desvios superiores ao dobro do tempo principal desapareceram. O total é de 398 cenários, não de medições em campo.

| Caso | Antes | Depois |
| --- | --- | --- |
| Engenheiro Goulart → Aeroporto, primeiro trecho ocupado | Desvio por Tatuapé, Brás e Luz, 65 min no modelo | Mantém a Jade direta; desvio rejeitado |
| Presidente Altino → Pinheiros, primeiro trecho ocupado | 46 min via Barra Funda/República, em vez dos 8 min do modelo | Mantém a Esmeralda direta |
| Paraíso → Jandira na madrugada de domingo | Ida a Itaquera e retorno ao centro para alcançar abertura | Não oferece essa volta; sem trajeto viável naquele instante |
| Júlio Prestes → Amador Bueno | 44 min e um embarque | 54 min no modelo, com troca em Itapevi |
| Luz → Jandira com gargalo comum na Diamante | Exclusão de todos os trechos pode eliminar ambas as opções regulares | Pode usar a Coral com o mesmo tempo e menos exposição, preservando a Diamante necessária |

Os 11 pares de referência ao meio-dia são comparados novamente, junto de mais 149 cenários de espera/serviços especiais. Os testes incluem os limites da política, uma segunda alternativa válida, ocupação futura/expirada, sentidos, confirmação, avisos de acesso, domínio e apresentação.

## Limites que permanecem

Não foi concluída a calibração real dos 188 trechos regulares de 120 segundos, nem substituídos os 600 segundos fixos de cada troca. Permanecem estimativas provisórias. Para alterá-las são necessários tempos atuais por trecho, sentido e faixa horária, além de caminhada e frequência de embarque. Não distribuir uma duração terminal uniformemente por estações nem converter relatos isolados em tempos oficiais.

O GTFS público da [ARTESP](https://dadosabertos.artesp.sp.gov.br/dataset/gtfs) descreve dados metropolitanos de ônibus e explicita interpolação linear dos tempos; ele não resolve esta calibração ferroviária. O conjunto de [infraestrutura do Metrô](https://transparencia.metrosp.com.br/dataset/infraestrutura-dados-de-linhas-e-esta%C3%A7%C3%B5es) fornece extensão e quantidade de estações, não a tabela necessária de passagens. Fontes históricas de intervalos não foram aplicadas como frequência atual.

O denominador global de viagens ativas e os parâmetros de demonstração foram preservados. A ocupação continua uma simulação interna, não capacidade medida dos trens. Não foi simulada espera pelo próximo trem regular sem grade documentada. Status operacional e exceções por obras dependem da integração própria e sua vigência. A Linha 6 não integra as próximas correções enquanto essa prioridade não for revista pelo usuário.

## Implantação

Busca e confirmação foram publicados no workspace 149130, branch `v1`, após prévia limitada a dois endpoints e confirmação de que os originais não tinham alterações concorrentes. A exportação posterior dos 26 documentos confirmou mudanças somente nesses dois arquivos; seus corpos de cálculo correspondem aos candidatos validados, desconsiderando a quebra de linha final normalizada pelo Xano.

As oito tabelas foram relidas e permaneceram idênticas às anteriores, incluindo a configuração de demonstração, os 207 trechos e as 207 chaves únicas; o registro inválido 215 continua ausente. Não houve modificação de registros ou esquema da malha.

Passaram 132 testes distintos e 19 subtestes, a compilação seca do Reflex, os dois XanoScripts e a validação estrita dos 11 itens OpenSpec. Os 398 cenários da auditoria foram comparados com a versão candidata final e as 160 comparações de espera foram repetidas com o código relido da publicação; as 11 referências permaneceram preservadas. A interface foi validada por testes de estado e compilação, sem alegar novo ensaio autenticado com duas contas no navegador.

O cliente Reflex atualizado e a documentação permanecem locais na branch `fix/pendencias-malha-restaurada`, sem commit, push ou envio à main nesta etapa. É necessário executar esse cliente atualizado para usar a troca em Itapevi e ver os avisos de acesso. A mudança continua aberta para a calibração com dados suficientes, registrada separadamente das correções já publicadas.
