"""Associa orientacoes cadastradas as etapas de um trajeto ja calculado."""

from collections.abc import Iterable

from MetroFlow.planning.domain.guidance import StationGuidance, normalize_name
from MetroFlow.planning.domain.models import RouteResult


WALKING_SEGMENT_TYPE = "transferencia"


def match_guidance(
    route: RouteResult,
    entries: Iterable[StationGuidance],
) -> dict[int, StationGuidance]:
    """
    Devolve a orientacao da estacao de descida por indice do trecho que
    encerra cada etapa ferroviaria. O trajeto em si nao e alterado.
    """

    by_key = {entry.key: entry for entry in entries}
    if not by_key:
        return {}

    segments = route.segments
    matches: dict[int, StationGuidance] = {}

    for index, segment in enumerate(segments):
        if segment.segment_type == WALKING_SEGMENT_TYPE:
            continue
        if segment.direction is None:
            continue

        following = segments[index + 1] if index + 1 < len(segments) else None
        if (
            following is not None
            and following.line.id == segment.line.id
            and following.segment_type == segment.segment_type
        ):
            # O passageiro continua no mesmo trem; nao ha desembarque aqui.
            continue

        found = by_key.get((
            normalize_name(segment.destination.name),
            normalize_name(segment.line.name),
            normalize_name(segment.direction),
        ))
        if found is not None:
            matches[index] = found

    return matches
