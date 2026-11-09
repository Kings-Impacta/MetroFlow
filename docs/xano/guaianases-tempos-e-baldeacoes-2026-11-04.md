# Linha 11 até Guaianases, tempos adicionais e baldeações

Continuação local em 04/11/2026. Xano sem alterações, margem numérica ainda não aplicada e Linha 6 adiada. Referências históricas, cenários e medições continuam identificados separadamente; não foi declarada cobertura operacional completa.

## Alcance e espera na Linha 11

O [quadro oficial da CPTM](https://www.cptm.sp.gov.br/dx/api/dam/v1/collections/05321fd9-3791-4689-a8ac-9e2adde39c4b/items/a3f44abf-6e70-49f7-bb3b-97bdc864f5c6/renditions/46d4c0bf-cb38-490d-b7c5-cb23ba496cc6?binary=true) distingue intervalos menores entre Barra Funda e Guaianases. A referência está guardada em `referencias-intervalos.json`; alcance e faixas do agregado, em `padroes-l11-candidatos.json`.

| Faixa | Intervalo agregado até Guaianases | Intervalo integral |
|---|---:|---:|
| Úteis, 04h–08h e 15h30–20h | 3min30s | 7 min |
| Úteis, 08h–15h30 | 5min30s | 11 min |
| Sábado, 04h–10h | 5min30s | 11 min |

As demais faixas usam somente o integral, com perfis próprios de dia, noite, domingo e feriado. A espera média candidata é metade do intervalo, uma vez por embarque. Não é a previsão da próxima composição.

O agregado representa os trens disponíveis no trecho comum, não uma promessa de seguir no mesmo trem além de Guaianases. Para quem segue até Estudantes, a busca considera o integral desde o começo ou uma troca com caminhada e nova espera; não aplica a frequência menor ao trajeto inteiro. A indicação de sentido no agregado é “Guaianases ou Estudantes”.

A verificação inclui o instante previsto de embarque. Quando a espera atravessa uma mudança para faixa contígua com outra frequência, o modelo conserva a maior estimativa entre as duas. Se o agregado deixa de existir, não oferece embarque depois do limite. Segundos são considerados nessa fronteira; o cache temporal também foi ajustado. Permanecer num trem já embarcado não gera nova espera em cada estação nem faz o serviço desaparecer na mudança de faixa.

O [comunicado histórico sobre o loop](https://www.cptm.sp.gov.br/cptm/noticias/trens-da-linha-11-coral-atendem-a-demanda-de-passageiros-e-operacao-paese-e-suspensa) usa horários e alcance diferentes. Foi preservado como referência, sem misturar suas faixas ao PDF. O quadro não traz data explícita de vigência extraída; a atualidade operacional ainda precisa de avaliação antes da seleção final.

## Tempos das linhas 3 e 4

Foram guardados mais **54 sentidos candidatos**, somados aos 73 anteriores: agora são **127 sentidos com modelo e 280 com referências ainda a avaliar**, entre 407. Os 104 candidatos das linhas 3, 4, 11 e 15 estão em `estimativas-linhas-adicionais.json`; os demais 23 continuam no arquivo de lacunas.

- Linha 3: 34 sentidos, com cenário agregado de 38 minutos distribuído por distância geodésica e parcela fixa, preservando a soma. O [estudo técnico de sinalização](https://www.aeamesp.org.br/biblioteca/stm/13SMTF070829T20.pdf) distingue manhã e tarde e relata efeitos da chuva. É histórico e a data da observação não foi confirmada; 38 minutos não foram apresentados como média atual, nem os efeitos de chuva foram incorporados ao cenário normal.
- Linha 4: 20 sentidos ferroviários, excluindo o corredor a pé da sequência da linha. A [reportagem de primeira mão de 10/09/2025](https://www.metrocptm.com.br/veja-como-ficou-o-trajeto-onde-o-trem-da-linha-4-amarela-descarrilou/) percorreu Luz–Vila Sônia em 23 minutos. O contexto era de via única após acidente; embora o autor considere a duração normal, é uma amostra e não prova uma média. O sentido inverso é hipótese explícita.

Não foram usados tempos uniformes GTFS como medições. Os novos valores repartem âncoras agregadas por método explícito, com confiança baixa, arredondamento a cinco segundos e simetria assumida. A duração completa do vídeo de uma viagem não foi convertida automaticamente em duração do percurso.

## Trocas desdobradas

`plataformas-candidatas.json` passou de 20 para **64 combinações**: 8 em Paraíso, 8 em Ana Rosa, 4 em República, 8 em Sé e 36 em Brás. As novas combinações identificam a estação anterior e a seguinte em cada linha. Isso discrimina os sentidos; não atribui um número físico de plataforma não confirmado.

As descrições oficiais de [Sé](https://www.metro.sp.gov.br/sua-viagem/linhas-estacoes/linha-1-azul/estacao-se/) e [Brás](https://www.metro.sp.gov.br/sua-viagem/linhas-estacoes/linha-3-vermelha/estacao-bras/) confirmam a geometria e as integrações gerais. Foram mantidos os candidatos de classe de três e sete minutos, respectivamente, sem afirmar nova cronometragem de cada combinação. A acessibilidade, a posição do carro, as filas e os percursos por elevador continuam sem estimativa específica aprovada.

Foi preservado ainda o comunicado temporário de Finados sobre alternância de plataformas em Barra Funda. Essa condição de obras não foi transformada em redução permanente de todas as trocas no local.

## Comparações e verificações

Comparação direcionada entre o candidato anterior `../outputs/linhas-parciais-final-20261104/candidato` e o novo `../outputs/guaianases-final-20261104/candidato`. Consultas isoladas por linha para testar alcance; os totais não prometem ser o melhor itinerário da rede inteira. Sem margem:

| Caso | Espera anterior | Espera nova | Total novo do modelo |
|---|---:|---:|---:|
| Barra Funda → Guaianases, útil 07h30 | 2 min | 1min45s | 38min55s |
| Barra Funda → Estudantes, útil 07h30 | 2 min | 3min30s | 74min30s |
| Barra Funda → Guaianases, útil 12h10 | 3min30s | 2min45s | 39min55s |
| Barra Funda → Estudantes, útil 12h10 | 3min30s | 5min30s | 76min30s |
| Barra Funda → Guaianases, domingo | 2 min | 17min30s | 54min40s |

Os deslocamentos completos Luz–Estudantes ainda usam a âncora histórica de 63 minutos; Barra Funda–Luz mantém o valor anterior do cadastro. Portanto, os totais acima não são tempos reais comprovados.

Nos ensaios completos de linha, Barra Funda → Itaquera passou de 35min30s para 39min30s; Luz → Vila Sônia, de 21min30s para 24min30s, ambos incluindo a espera mantida para aquele horário. As variações resultam do cenário de distribuição, não de melhoria de serviço observada.

Bresser-Mooca → Engenheiro Goulart continuou pelo Tatuapé, com troca de cinco minutos no modelo; a busca não foi forçada a voltar ao Brás. A consulta foi ao meio-dia, dentro da faixa de integração gratuita preservada no helper. O mesmo teste confere a soma de deslocamento, espera e caminhada. Isso verifica consistência local, não substitui avaliação tarifária ou operacional atual.

Resultados: **880 execuções amplas**, com 214 buscas e 120 cenários de concorrência alterados, sem ciclos ou alternativas acima do dobro nos casos exercitados. **22 testes novos** cobriram alcance até/depois de Guaianases, ida/volta, útil/sábado/domingo/feriado, transições de faixa, totais das linhas 3/4 e trocas. **18 testes da etapa anterior e 16 de exceções também passaram**. O teste noturno usa 110 segundos de deslocamento no novo cenário da Linha 3, mantendo os 750 segundos de espera, sem confundir mudança de percurso com mudança de frequência.

Reprodução: gerar candidatos de linhas e esperas; atualizar o inventário; executar `simular_estimativas_lacunas.py` com `--incluir-esperas-baldeacoes --incluir-linhas-adicionais`; comparar com `validar_guaianases_tempos.py` e repetir as duas suítes anteriores (`validar_excecoes_calibracao.py --l3-calibrada` para este cenário). Resultados em `../outputs/guaianases-final-20261104/`, relativo à raiz do worktree. Os arquivos de referência exportados permaneceram sem alterações.

## Pendências para concluir a cobertura

Continuam abertas a seleção de tempos das linhas 1, 2, 5, 7, 8-tronco, 9, 10 e 12, os conflitos da Linha 17 e os pequenos intervalos fora das âncoras adotadas. As estimativas históricas das linhas 3/4 e as demais modeladas ainda precisam de seleção final e análise de sensibilidade; não são aprovadas só porque há um número preenchido.

As 64 combinações não cobrem todas as plataformas da malha. Permanecem as seis combinações genéricas de Paraíso, conexões ainda representadas por classes e acessibilidade. Horários especiais, feriados e calendário provisório de parte do GTFS também exigem fechamento coerente.

Antes de publicar, busca e registro precisam compartilhar a mesma versão de percursos, custos, alcance dos trens e cronologia de ocupação. A margem futura continua sendo **60 segundos uma única vez no total final**, sem alterar embarques alcançáveis, com “Tempo estimado” e indicação de variação por condições externas. Nada foi publicado nesta etapa; Linha 6 por último.
