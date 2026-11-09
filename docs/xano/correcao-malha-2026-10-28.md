# Conferência e correções da malha — 28/10/2026

**Continuação:** o ramal de Washington Luís, os sentidos e a troca de trem foram
corrigidos posteriormente no mesmo dia. A grade do Expresso L10 e o calendário
também receberam ajustes. Consulte o [estado posterior e seus limites](ramal-brooklin-e-alternativas-2026-10-28.md).
As pendências abaixo refletem a primeira etapa, antes dessa continuação.

## Escopo e evidências

Comparação das exportações do Xano, documentos anteriores e funções efetivamente
publicadas. Os testes executam as lambdas exportadas com Node.js, dados reais da
malha e relógio controlado, sem usar sessões de passageiros ou criar viagens.
Isso não equivale a um teste completo de navegador e autenticação no servidor.

Backups locais, fora do Git: `outputs/corrigir-pendencias-malha-20261028-114056`,
`outputs/tempos-malha-20261028-111705` e
`outputs/correcao-sentidos-20261028-112431`, relativos à pasta desta conversa.
Guardam conteúdo anterior/posterior, código e comparações reproduzíveis, sem
credenciais nas evidências. Não são arquivos públicos de implantação.

## Aplicado no Xano

- Preservados os 207 IDs, tempos recuperados e sentidos corrigidos anteriormente;
  o trecho inválido 215 continua ausente.
- Nove vínculos preenchidos: trechos 8 e 10 no serviço 2 (Expresso Linha 10) e
  194–200 no serviço 3 (Linha 17). As chaves canônicas acompanham os serviços.
- Brás acrescentado à ordem do Expresso Aeroporto, entre Luz e Cecap, completando
  o sentido informado no retorno. Segmentos direcionados continuam definindo as
  paradas diferentes na ida e volta; a ordenação não cria ligações adicionais.
- Linha 17: segunda a sábado, 06h–22h, inclusive feriado nesses dias. O operador
  passa de Motiva para Metrô; Linha 7 recebe operador próprio TIC Trens.
- Janela da integração Paulista–Consolação encerra à meia-noite. O trecho continua
  com 180 s e tipo `transferencia`, sem acrescentar outro trecho duplicado.
- Busca e confirmação agora respeitam as disponibilidades cadastradas, em
  America/Sao_Paulo, com início inclusivo e fim exclusivo.
- Restaurado o índice único canônico e incluído tratamento de duplicata na corrida
  entre verificar a chave e gravar. Não foram alterados os parâmetros de lotação.

## Antes e depois dos ajustes de tempo desta revisão

Comparação com o estado restaurado anterior à reaplicação dos tempos documentados,
sem viagens ativas. Tempos são estimativas do projeto, não duração garantida.

| Percurso | Antes | Depois |
|---|---|---|
| Jandira → Paraíso | L8 → L10 → L1, 64 min | L8 → L3 → L1, 68 min |
| Barra Funda → Paraíso | L10 → L1, 24 min | L3 → L1, 28 min |
| Barra Funda ↔ Aeroporto-Guarulhos | Expresso, 6 min | Expresso, 35 min |
| Vila Madalena → Vila Prudente | L2, 26 min | L2, 26 min |
| Barra Funda → Brigadeiro | L10 → L2, 34 min | L3 → L4 → integração a pé → L2, 37 min |

O aumento corrige custos artificialmente baixos; não significa que o percurso
físico tenha ficado mais lento. Jandira troca na Barra Funda para a Vermelha e na
Sé para a Azul. Essas rotas e seus retornos foram preservados na etapa adicional
de disponibilidade.

## Comparação adicional de disponibilidade

Foram comparadas 12 rotas em quatro horários: quarta-feira às 07h e às 12h,
sábado às 12h e domingo às 12h (48 comparações). Quarenta consultas de referência
preservaram os mesmos IDs de trechos e tempos. Os dados após a aplicação foram
relidos e comparados campo a campo com o plano.

| Caso | Antes do filtro | Depois |
|---|---|---|
| Tamanduateí → Santo André, quarta 07h | Expresso, 3 min | Expresso, 3 min |
| Tamanduateí → Santo André, quarta 12h | Expresso, 3 min | L10 regular, 8 min |
| Morumbi → Congonhas, sábado 12h | L17, 12 min | L17, 12 min |
| Morumbi → Congonhas, domingo 12h | L17, 12 min | Sem rota ferroviária cadastrada disponível |
| Pinheiros → Paraíso | L4 → L2, 27 min | L4 → L2, 27 min |
| Consolação ↔ Paulista, em operação | Integração, 3 min | Integração, 3 min |

Brás já é uma estação compartilhada da malha, assim como os demais complexos
conferidos na auditoria de integrações. Não faltava uma aresta de caminhada para
permitir a troca da Linha 3 aos trens. Criar uma aresta adicional sem separar os
componentes de tempo poderia cobrar a transferência duas vezes.

## Pendências confirmadas e limites

1. **Linha 17: ramal de Washington Luís e troca em Brooklin Paulista.** O cadastro
   ainda encadeia Congonhas–Washington Luís. A operadora informa um trem separado
   Brooklin Paulista–Washington Luís e transferência obrigatória em Brooklin. A
   topologia e as instruções precisam de correção conjunta: o contrato e a
   apresentação atuais reconhecem baldeação apenas ao mudar de linha. Alterar só
   os extremos manteria instrução incorreta de permanecer no mesmo trem. Este
   trecho e os sentidos da Linha 17 não estão certificados nesta entrega.
2. **Expresso Linha 10:** confirmar a grade atual, tempos e paradas por sentido.
   Mantidas provisoriamente as janelas anteriores 06h–09h e 16h–19h em dias úteis e
   90 s por trecho; não são valores certificados pela consulta oficial atual.
3. **Tarifa e tempo real de transferência:** Tatuapé/Itaquera têm faixas de
   gratuidade. O planejador representa conectividade física, não elegibilidade
   tarifária, e ainda usa 600 s por mudança de linha, sem tempos medidos por
   plataforma, acessibilidade ou espera por partidas.
4. **Calendário/serviços:** ampliar o calendário antes de 2027, considerar feriados
   municipais fora de São Paulo e atualizar exceções operacionais. A conexão de
   aeroporto aos terminais não tem estações de terminal no grafo.
5. **Validação integrada:** repetir sessões reais de busca/registro e duas
   gravações simultâneas de trechos para confirmar o erro controlado HTTP.

Portanto, as diferenças de disponibilidade/integridade previstas foram tratadas,
mas não se declara a malha inteira concluída ou sem pendências.

## Fontes oficiais consultadas

- [Metrô, 29/09/2026: horários e transferência da Linha 17](https://www.metro.sp.gov.br/2026/09/29/metro-amplia-horario-da-linha-17-ouro-a-partir-desta-quarta-feira-30/).
- [Metrô, 01/10/2026: operação ampliada e conexões](https://www.metro.sp.gov.br/2026/10/01/linha-17-ouro-transporta-mais-de-25-mil-passageiros-no-primeiro-dia-com-horario-ampliado/).
- [Guia do Passageiro, outubro de 2026: integrações e meia-noite](https://www.metro.sp.gov.br/wp-content/uploads/2026/10/guia_do_passageiro_online.html).
- [TIC Trens: operação da Linha 7](https://www.tictrens.com.br/noticias/estacao-vila-aurora-da-linha-7-rubi-recebe-nova-identidade-visual-2614).
- [CPTM: Expresso Linha 10, informação de 2025 que não certifica grade de 2026](https://www.cptm.sp.gov.br/wcm/connect/cptm_content/cptm/noticias/httpswwwcptmspgovbrnoticiaspagescptm-inicia-testes-para-diminuir-intervalo-no-expresso-linha-10-a-partir-desta-segunda-28aspx).
- [Prefeitura de São Paulo: calendário de 2026](https://prefeitura.sp.gov.br/web/prefeitura-de-sao-paulo/w/prefeitura-de-s%C3%A3o-paulo-divulga-calend%C3%A1rio-de-feriados-e-pontos-facultativos-para-2026).
