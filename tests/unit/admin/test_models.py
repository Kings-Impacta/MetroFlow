"""Invariantes dos modelos do painel administrativo."""

from dataclasses import replace

import pytest

from MetroFlow.admin.domain.models import (
    AdminIndicators,
    AdminStation,
    CrowdingIndicator,
    StationStatus,
    StationUsage,
)


def indicators(**overrides) -> AdminIndicators:
    base = dict(
        computed_at_ms=1_763_316_000_000,
        active_routes=3,
        users_travelling=3,
        recent_users=10,
        enabled_accounts=25,
        active_stations=180,
        inactive_stations=2,
        active_lines=16,
        active_segments=207,
        trips_today=4,
        trips_last_7_days=30,
        ranking=(StationUsage(1, "Sé", "SE", 9), StationUsage(2, "Luz", "LUZ", 4)),
        crowding=CrowdingIndicator(1, 2, 50.0),
    )
    base.update(overrides)
    return AdminIndicators(**base)


def test_indicadores_validos() -> None:
    item = indicators()

    assert item.crowding.available is True
    assert len(item.ranking) == 2


@pytest.mark.parametrize(
    "field",
    ["active_routes", "recent_users", "enabled_accounts", "inactive_stations", "trips_today"],
)
def test_contagem_negativa_e_rejeitada(field: str) -> None:
    with pytest.raises(ValueError):
        indicators(**{field: -1})


def test_volume_do_dia_nao_pode_superar_os_7_dias() -> None:
    with pytest.raises(ValueError):
        indicators(trips_today=31, trips_last_7_days=30)


def test_ranking_acima_de_cinco_e_rejeitado() -> None:
    ranking = tuple(StationUsage(i, f"Estação {i}", f"E{i}", 10 - i) for i in range(1, 7))

    with pytest.raises(ValueError):
        indicators(ranking=ranking)


def test_ranking_fora_de_ordem_e_rejeitado() -> None:
    with pytest.raises(ValueError):
        indicators(ranking=(StationUsage(2, "Luz", "LUZ", 4), StationUsage(1, "Sé", "SE", 9)))


def test_estacao_do_ranking_sem_uso_e_rejeitada() -> None:
    with pytest.raises(ValueError):
        StationUsage(1, "Sé", "SE", 0)


def test_lotacao_indisponivel_tem_todos_os_campos_vazios() -> None:
    crowding = CrowdingIndicator(None, None, None)

    assert crowding.available is False
    assert indicators(crowding=crowding).crowding.crowded_segments is None


@pytest.mark.parametrize(
    "values",
    [
        pytest.param((1, None, None), id="incompleto"),
        pytest.param((-1, 2, 50.0), id="lotados-negativo"),
        pytest.param((1, 0, 50.0), id="minimo-zero"),
        pytest.param((1, 2, 0.0), id="percentual-zero"),
        pytest.param((1, 2, 150.0), id="percentual-acima-de-100"),
    ],
)
def test_lotacao_inconsistente_com_o_criterio_e_rejeitada(values) -> None:
    with pytest.raises(ValueError):
        CrowdingIndicator(*values)


def test_estacao_exige_identificador_nome_e_codigo() -> None:
    station = AdminStation(1, "Sé", "SE", True)

    with pytest.raises(ValueError):
        replace(station, id=0)
    with pytest.raises(ValueError):
        replace(station, name="  ")
    with pytest.raises(ValueError):
        StationStatus(0, True)
