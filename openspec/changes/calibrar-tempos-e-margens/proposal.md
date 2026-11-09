# Calibrar tempos, esperas e transferências com margem explícita

## Why

A malha preserva valores provisórios. O usuário aceita estimativas concretas sem exigir comprovação documental integral, autorizou guardar referências parciais e esclareceu que a margem é um único minuto sobre o trajeto total. Aplicação e publicação ficam condicionadas à cobertura completa e às simulações. Linha 6 fica adiada.

## What Changes

- Inventariar deslocamentos por sentido, embarques por serviço/dia/faixa e transferências por linhas, plataformas e sentidos.
- Guardar fonte, vigência, grau de confiança e conflitos sem confundir referência com medição.
- Separar total-base e margem única de 60 segundos no total, sem acréscimo por estação, espera ou baldeação.
- Recalcular chegada, partidas especiais e ocupação com a mesma cronologia em busca e registro de viagem; validar cenários antes/depois.
- Publicar somente após cobertura e consistência completas. A coleta atual não satisfaz esse critério.

## Impact

Afeta futuramente cadastro e funções Xano de planejamento e registro e normalização do contrato. Nesta etapa, acervo e inventário são preservados e a interface local passa a explicitar a variação do tempo estimado; nenhuma margem numérica ou publicação foi aplicada.

## Atualização documental de 09/11/2026

A calibração foi publicada após autorização, incluindo a Linha 6 parcial; as restrições de loopback abaixo descrevem o laboratório, não impedem o contrato calibrado na API oficial. Os resultados e a versão atual estão em `docs/xano/publicacao-preferencia-metro-2026-11-09.md`.
