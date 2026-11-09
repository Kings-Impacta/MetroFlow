# Frequências por dia e integração local — 04/11/2026

Continuação de `parciais-registro-e-conflitos-2026-11-04.md`. Nenhum acesso de escrita ao Xano, alteração de cadastro, commit ou publicação. A aplicação em execução não foi reiniciada. A Linha 6 permanece adiada e a margem de 60 segundos continua sem aplicação.

## Frequências preservadas e estimadas

O pacote GTFS preservado em 01/11 contém serviço `USD` para as linhas 7/8/9, com oferta de segunda a domingo e vigência declarada de 01/10/2023 a 01/05/2027. Não há `calendar_dates.txt` nesse pacote. Isso confirma o calendário declarado pelo arquivo, não a precisão atual das frequências ou que todos os trens percorram o integral. A interpretação de feriados continua no helper temporal; ponto facultativo não vira feriado automaticamente.

`docs/dados/tempos/frequencias-l789-por-dia.json` guarda perfis explícitos de dia útil, sábado e domingo/feriado. As linhas 7 e 8 preservam as estimativas de intervalo integral da etapa anterior, agora separadas por dia, sem inventar diferenças inexistentes na fonte. Os agregados candidatos continuam limitados a seus trechos centrais e à janela experimental de dias úteis 06h–20h. Essas restrições continuam hipóteses locais, não grade atual confirmada.

Para a Linha 9, substituiu-se o piso uniforme de nove minutos do atendimento integral por estes **cenários estimados**, válidos somente no laboratório:

| Tipo de dia | Faixa | Intervalo entre trens candidato | Espera média candidata |
|---|---|---:|---:|
| Dia útil | 04h–11h30 | 10 min | 5 min |
| Dia útil | 11h30–15h30 | 7 min | 3min30s |
| Dia útil | 15h30–24h | 10 min | 5 min |
| Sábado | 04h–24h | 10 min | 5 min |
| Domingo/feriado | 04h–24h | 10 min | 5 min |

O [comunicado oficial de 20/05/2026](https://trilhos.motiva.com.br/viamobilidade8e9/noticias/2026/maio/confira-as-manutencoes-programadas-nas-linhas-8-diamante-e-9-esm/) informa sete minutos regulares para toda a linha no período de 11h30–15h30 e diferencia o intervalo durante obras. O [comunicado de 08/05/2026](https://trilhos.motiva.com.br/viamobilidade8e9/noticias/2026/maio/viamobilidade-realiza-manutencoes-nas-linhas-8-e-9/) preserva seis minutos regulares em outros recortes. São referências datadas e diferentes; sete minutos foi escolhido como cenário, sem afirmar uma grade atual de novembro.

Dez minutos no trecho sul aparecem em [reportagem com declaração atribuída à operadora de 23/09](https://www.metrocptm.com.br/problema-na-linha-9-esmeralda-causa-maiores-intervalos-nesta-quarta-feira-23/). A frequência de fim de semana é uma extrapolação identificada de [referência secundária sobre oferta de feriado equivalente a domingo](https://metroreport.com.br/noticias/motiva-trilhos-divulga-operacao-e-manutencoes-para-o-feriado-3204). Não é tabela oficial atual completa. Não se generalizou o looping emergencial em Jurubatuba nem se estendeu o agregado histórico Pinheiros–Mendes até Varginha.

As exceções de obras foram preservadas em `excecoes-frequencia-referencias.json`, separadas da grade candidata: 08/05, 20/05 e noite de 03 para 04/10. O [aviso oficial de outubro](https://trilhos.motiva.com.br/viamobilidade8e9/noticias/2026/setembro/confira-as-manutencoes-programadas-das-linhas-8--diamante-e-9-es/) distingue Osasco–Jurubatuba e Jurubatuba–Varginha. Esse intervalo de obra não passou a valer em todos os domingos. Horários de manutenção durante a madrugada também não comprovam, isoladamente, autorização para embarque comercial em todas as estações.

## Comparações de Osasco → Varginha

Totais do modelo de deslocamento anterior, acrescidos da espera candidata, sem minuto de margem. Comparação contra a etapa anterior do laboratório, não contra uma cronometragem real.

| Consulta | Antes | Depois |
|---|---:|---:|
| Quarta, 07h30 | 57min25s | 57min55s |
| Quarta, 12h10 | 57min25s | 56min25s |
| Quarta, 18h30 | 57min25s | 57min55s |
| Sábado, 12h10 | 57min25s | 57min55s |
| Domingo, 12h10 | 57min25s | 57min55s |
| Feriado de Finados, 12h10 | 57min25s | 57min55s |

O teste de transição às 15h27 considera que a espera atravessará a mudança de faixa e conserva a espera maior. Essa espera é cobrada uma vez no embarque, sem repetição por estação. Foram verificados os dois sentidos e o feriado de 20/11.

## Integração no código local

O caminho completo foi implementado localmente: resposta da busca → domínio → contrato público da API → estado Reflex → confirmação automática → cliente de planejamento → reprodução do registro. A referência opcional contém versão e padrões de trem, sem usuário ou tempos escolhidos pelo navegador.

- Sem referência, o contrato legado permanece igual, inclusive a validação de 600 segundos por troca.
- Com referência, o domínio valida os custos separados por passo e reconhece troca de padrão dentro da mesma linha. Caminhada explicitamente coberta pode ter custo adicional de troca zero, preservando a contagem de baldeações.
- A interface transporta os identificadores sem exibi-los como instrução ao passageiro. O agrupamento de etapas considera mudança de padrão.
- O registro continua recalculando espera, caminhada e início de passagem com a mesma versão da busca. A referência não permite enviar duração ou identidade de usuário pelo cliente.
- `METROFLOW_CALIBRACAO_LOCAL=1` habilita o contrato experimental **somente quando a API de planejamento aponta para localhost, 127.0.0.1 ou ::1**. Uma configuração remota é recusada. Sem essa opção, registros calibrados são recusados antes de qualquer envio. Nenhuma variável do ambiente atual foi ativada ou modificada.

Essa opção é uma preparação de contrato para testes com API local; não inicia um servidor local nem substitui o cálculo do Xano em operação normal. O teste usa `httpx.MockTransport` e dois clientes HTTP independentes, com sessões e usuários fictícios. Não é um teste com contas reais conectadas ao Xano.

## Validações e limites

- 880 execuções gerais de busca/concorrência sobre cópias locais, com origem preservada.
- 22 comparações completas passando por API, normalização, estado e registro; 22 fins de janela iguais ao total da busca.
- 24 casos adicionais de faixa/dia nos dois sentidos de Osasco–Varginha, com 24 reproduções de registro iguais à busca.
- Dois usuários simulados distintos com registros ativos: Barra Funda → Aeroporto-Guarulhos passou de 63min15s para alternativa de 65min dentro da política. Versão incompatível e ausência de cookie foram recusadas sem novo registro.
- 80 testes unitários/fronteira aprovados, mais 28 subtestes. O modo legado e o bloqueio de envio calibrado a destino remoto foram exercitados.
- Compilação seca do Reflex aprovada. Houve avisos de dependências/depreciação e falha na leitura opcional de informação do processador; a compilação terminou com sucesso, sem iniciar servidor.

Resultados em `outputs/frequencias-integracao-20261104/`, na pasta superior ao repositório: `comparacao.json`, `integracao-local.json` e `validacao-frequencias-por-dia.json`. Reprodução principal: `scripts/validar_integracao_calibrada.py`; limites temporais: `scripts/validar_frequencias_por_dia.py`. A reprodução do registro é gerada por `scripts/gerar_registro_calibrado.py`.

Ainda não há cobertura operacional concluída: frequências atuais completas, calendário de exceções com alcance/datas, seleção das hipóteses de menor confiança, baldeações inferidas/acessibilidade e disponibilidade da Linha 17 perto do encerramento continuam pendentes. Os valores aceitam estimativas fundamentadas, sem exigir documentação integral; permanecem rotulados conforme a evidência disponível. Só depois de concluir a cobertura e as simulações será aplicada a margem única de um minuto e preparada uma publicação conjunta. Nada foi publicado nesta etapa.
