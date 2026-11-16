"""Casos de uso do painel administrativo."""

from unittest.mock import MagicMock

import pytest

from MetroFlow.admin.application.services import (
    AdminService,
    InvalidStationChange,
    alphabetical_key,
)
from MetroFlow.admin.domain.models import AdminStation, StationStatus


def test_estacoes_em_ordem_alfabetica_sem_distinguir_acentos() -> None:
    gateway = MagicMock()
    gateway.stations.return_value = (
        AdminStation(3, "Sé", "SE", True),
        AdminStation(1, "Ána Rosa", "ANR", True),
        AdminStation(2, "Barra Funda", "BFU", False),
        AdminStation(4, "santa Cecília", "SCE", True),
    )

    names = [item.name for item in AdminService(gateway).stations("token")]

    assert names == ["Ána Rosa", "Barra Funda", "santa Cecília", "Sé"]
    gateway.stations.assert_called_once_with("token")


def test_chave_alfabetica_ignora_acentos_e_caixa() -> None:
    assert alphabetical_key("Sé") == alphabetical_key("se")


def test_alteracao_repassa_estacao_e_situacao() -> None:
    gateway = MagicMock()
    gateway.set_station_status.return_value = StationStatus(7, False)

    status = AdminService(gateway).change_station_status(7, False, "token")

    assert status == StationStatus(7, False)
    gateway.set_station_status.assert_called_once_with(7, False, "token")


@pytest.mark.parametrize(
    ("station_id", "active"),
    [(0, True), (-3, False), (True, True), ("7", True), (7, "false"), (7, None)],
)
def test_alteracao_invalida_nao_chama_o_xano(station_id, active) -> None:
    gateway = MagicMock()

    with pytest.raises(InvalidStationChange):
        AdminService(gateway).change_station_status(station_id, active, "token")

    gateway.set_station_status.assert_not_called()


def test_resposta_de_outra_estacao_e_rejeitada() -> None:
    gateway = MagicMock()
    gateway.set_station_status.return_value = StationStatus(8, False)

    with pytest.raises(ValueError):
        AdminService(gateway).change_station_status(7, False, "token")
