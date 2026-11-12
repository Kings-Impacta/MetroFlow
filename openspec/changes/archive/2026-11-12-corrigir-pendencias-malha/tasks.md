## Preparação
- [x] Exportar tabelas e workspace atuais e conferir fontes oficiais.
- [x] Registrar escopo, limites e plano antes de implementar.

## Implementação
- [x] Corrigir vínculos de serviço, ordenação e operador.
- [x] Atualizar disponibilidade da Linha 17.
- [x] Restaurar índice único canônico e tratar falhas de gravação.
- [x] Aplicar disponibilidade na busca e confirmação sem alterar contrato público.

## Validação
- [x] Testar limites de horário, dias, feriados, entradas inválidas e conservação de rotas.
- [x] Repetir testes de concorrência com a função real e dados controlados.
- [x] Validar XanoScript, OpenSpec e dry-run com apenas os endpoints previstos.
- [x] Publicar, reler e comparar código/dados; registrar antes/depois e limites.

## Acompanhamento posterior (não certificado nesta entrega)
- [x] Corrigir conjuntamente o ramal Washington Luís e as instruções de troca na Linha 17; testar cliente anterior e capacidade opcional do atualizado.
- [x] Conferir a grade oficial do Expresso L10 com parada em São Caetano e validar as janelas por sentido na busca e confirmação.
- [x] Calcular feriados recorrentes depois de 2026 e testar datas móveis de 2027.
- [x] Comparar alternativas por Sé, República/Paulista e Pinheiros, com e sem lotação controlada.
- **Adiado, não executado nesta entrega:** Certificar tempos e incluir os retornos diretos do Expresso L10 com custos documentados.
- [x] Integrar o cliente calibrado na main (PR #37) e validar buscas/registro no teste real de 09/11.
- [x] Confirmar duas contas distintas em buscas e registros automáticos de Luz–Jandira após novo login, com Turquesa e Expresso Aeroporto.
- [x] Modelar espera por partidas e desempate entre serviços regulares/especiais; validar a alternativa por República em 09/11, sem prometer tempo real exato.
- **Adiado, não executado nesta entrega:** Repetir o teste administrativo de gravações simultâneas de trechos por HTTP autenticado.

## Encerramento com escopo reduzido — 12/11/2026

Por decisão explícita do usuário, esta entrega é encerrada com o escopo implementado e validado. Os itens identificados como adiados acima não foram executados nem aprovados; foram transferidos para `docs/melhorias-futuras-malha-status.md`, fora do compromisso desta entrega. Nenhuma caixa de tarefa não realizada foi marcada como concluída. O arquivamento registra o encerramento administrativo com limitações, não a execução integral do escopo original. Não houve alteração de código, malha, parâmetros, configuração ou runtime.

A configuração ausente da concorrência foi validada por **HTTP local isolado**, não por HTTP no runtime nativo do Xano; essa evidência não valida gravações administrativas simultâneas de trechos.
