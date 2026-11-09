# Continuação: linhas 1, 2 e 5 e integrações

Estado local em 04/11/2026. Complementa `guaianases-tempos-e-baldeacoes-2026-11-04.md`. Nenhum valor publicado no Xano, nenhuma margem aplicada e Linha 6 adiada. Os cenários abaixo não foram selecionados como tempos operacionais definitivos.

## Novos cenários e procedência

Foram guardados mais 102 sentidos candidatos: 44 da Linha 1, 26 da Linha 2 e 32 da Linha 5. O inventário agora tem **229 sentidos com modelo e 178 com referências ainda a avaliar**, entre 407. `estimativas-linhas-adicionais.json` contém 206 candidatos; `estimativas-lacunas.json`, 23.

| Linha | Âncora de deslocamento no ensaio | Procedência e limite |
|---|---:|---|
| 1 | 42min25s | Estudo técnico com dados históricos de 2006: 42min23s no pico da manhã, arredondado a cinco segundos. Não é medição atual. |
| 2 | 32min30s | Total programado do GTFS preservado em 01/11/2026. Os intervalos entre estações do pacote são uniformes; a redistribuição não comprova observação real. |
| 5 | 34 min | Referência histórica de benefício entre os bairros Capão Redondo e Chácara Klabin. O documento não fornece cronometragem embarcada entre plataformas; cenário conservador, sem Jardim Ângela. |

Fontes: [estudo técnico da Linha 1](https://www.aeamesp.org.br/biblioteca/stm/12SMTF060830T05.pdf), [GTFS oficial da SPTrans](https://www.sptrans.com.br/desenvolvedores/) e [relatório de empreendimentos de janeiro de 2019](https://transparencia.metrosp.com.br/sites/default/files/Relat%C3%B3rio%20de%20Empreendimentos%20-%20Janeiro%20-2019.pdf). Os limites permanecem junto a cada registro e em `fontes-adicionais.csv`.

O método mantém a âncora completa e distribui os intervalos por distância geodésica GTFS, com parcela fixa de 20 segundos como parâmetro de distribuição. Não acrescenta esse parâmetro ao total, nem o apresenta como parada medida. Há arredondamento a cinco segundos preservando a soma e simetria assumida. As estações são associadas por sequência ferroviária e nomes normalizados, com equivalências explícitas para nomes antigos e comerciais; divergências interrompem o gerador. Não usar coordenadas de um ponto de ônibus com nome parecido.

A Linha 2 tem evidência mais fraca: trata-se de remodelar um programa já conhecido como uniforme. Isso permite testar sensibilidade e comparar caminhos, mas não fecha a seleção do tempo-base. A referência da Linha 5 também permanece limitada pelo significado de viagem entre bairros no documento. O usuário aceita estimativas sem comprovação documental integral; isso não transforma essas âncoras em medições atuais.

## Santa Cruz e Chácara Klabin

As integrações foram desdobradas pela estação anterior e seguinte em cada linha, com apoio das descrições oficiais de [Santa Cruz](https://www.metro.sp.gov.br/sua-viagem/linhas-estacoes/linha-1-azul/estacao-santa-cruz/) e [Chácara Klabin](https://www.metro.sp.gov.br/sua-viagem/linhas-estacoes/linha-2-verde/estacao-chacara-klabin/).

Foram acrescentadas oito combinações em Santa Cruz e quatro em Chácara Klabin. O acervo passou a **76 combinações por sentido de troca**, incluindo as etapas anteriores. Permanecem os candidatos de oito minutos de caminhada em Santa Cruz e cinco em Chácara Klabin, sem alegar nova medição por plataforma. O desdobramento ajuda a identificar o que falta medir; não comprova 76 caminhos internos ou tempos acessíveis.

A duração da caminhada continua separada da espera pelo trem. Os testes identificam o ponto efetivo da baldeação pela resposta, não por qualquer estação atravessada. Por exemplo, Hospital São Paulo → Santos-Imigrantes passa por Santa Cruz, mas troca em Chácara Klabin; não deve receber o custo de troca de Santa Cruz.

## Comparação local antes/depois

Antes: `../outputs/guaianases-final-20261104/candidato`. Depois: `../outputs/metro125-final-20261104/candidato`. Exemplos às 12h10 de 04/11/2026, linhas isoladas nos testes, sem margem e incluindo as esperas candidatas:

| Consulta | Antes | Depois |
|---|---:|---:|
| Tucuruvi → Jabaquara | 45 min | 43min25s |
| Vila Madalena → Vila Prudente | 27 min | 33min30s |
| Capão Redondo → Chácara Klabin | 36 min | 38 min |
| Hospital São Paulo → Vila Mariana, troca em Santa Cruz | 17 min | 16min55s |
| Hospital São Paulo → Santos-Imigrantes, troca em Chácara Klabin | 16 min | 15min45s |

Os inversos foram exercitados. O aumento da Linha 2 corresponde à escolha do total GTFS para este cenário; não é prova de maior demora real. Na Linha 5, os 38 minutos incluem quatro minutos de espera herdados do perfil candidato, ainda sem calibração completa própria. A redução em consultas curtas decorre da redistribuição dos deslocamentos; os custos de troca foram mantidos.

O candidato preservou o alcance separado dos trens até Guaianases e dos integrais, as faixas de espera, a correção de Brás na Linha 10 e o corredor Paulista–Consolação sem cobrança duplicada.

## Verificação

- 880 execuções amplas antes/depois: 214 buscas e 120 cenários de concorrência alterados em relação à exportação original; sem ciclos ou alternativas acima do dobro nos casos exercitados. Essa é uma comparação com a exportação original, distinta da comparação entre candidatos da tabela acima.
- 32 testes dirigidos de alcance da Linha 11, transições de faixa, âncoras e trocas passaram, comparando com o candidato anterior.
- 18 verificações das linhas parciais/corredor e 16 de exceções foram repetidas com sucesso. Total: 66 verificações específicas, além do conjunto amplo.
- Conferidas chaves únicas de combinações, valores positivos e ausência da Linha 6 entre os novos modelos. Os hashes das tabelas de referência foram preservados pela simulação.
- Validação estrita das 12 especificações/mudanças passou; checagem de espaços sem erro. Não foi necessário executar ou reiniciar o Reflex para estes arquivos de pesquisa e laboratório.

Resultados reproduzíveis em `../outputs/metro125-final-20261104/`, relativo à raiz do worktree. A geração usa `estimar_linhas_adicionais.py`, `estimar_esperas_baldeacoes.py` e `mapear_cobertura_tempos.py`; a comparação usa `simular_estimativas_lacunas.py --incluir-esperas-baldeacoes --incluir-linhas-adicionais`, `validar_guaianases_tempos.py`, `validar_linhas_parciais.py` e `validar_excecoes_calibracao.py --l3-calibrada`.

## O que falta

Faltam estimativas selecionadas para as linhas 7, 8-tronco, 9, 10, 12, conflitos da Linha 17 e pequenos intervalos fora das âncoras. Os cenários das demais linhas precisam de análise de sensibilidade e escolha coerente de base; a cobertura não está concluída apenas porque há um modelo.

Continuam abertas as integrações não desdobradas, as seis combinações genéricas de Paraíso, acessibilidade, parte dos horários por dia/feriado e a atualização conjunta do registro/cronologia da concorrência com a busca. Os padrões de trens parciais permanecem metadados de laboratório, não um contrato publicado.

Somente depois de completar a cobertura e simular: aplicar 60 segundos uma única vez ao total final, mantendo “Tempo estimado” e informação de variação externa, e preparar publicação coerente. Nada foi alterado no Xano; Linha 6 por último.
