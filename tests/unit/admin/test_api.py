"""Fronteira HTTP do painel administrativo."""

import unittest
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient

from MetroFlow.admin.domain.models import (
    AdminIndicators,
    AdminLine,
    AdminStation,
    CrowdingIndicator,
    StationStatus,
    StationUsage,
)
from MetroFlow.admin.infrastructure.xano_client import (
    AdminError,
    AdminForbidden,
    AdminNotFound,
    AdminUnauthorized,
    AdminUnavailable,
)
from MetroFlow.admin.presentation.api import admin_api
from MetroFlow.auth.infrastructure.session_cookie import SESSION_COOKIE_NAME
from MetroFlow.auth.presentation.api import validation_error


TOKEN = "private-admin-token"
INDICATORS = AdminIndicators(
    computed_at_ms=1_763_316_000_000,
    active_routes=2,
    users_travelling=2,
    recent_users=5,
    enabled_accounts=9,
    active_stations=180,
    inactive_stations=2,
    active_lines=16,
    active_segments=207,
    trips_today=3,
    trips_last_7_days=20,
    ranking=(StationUsage(1, "Sé", "SE", 6),),
    crowding=CrowdingIndicator(None, None, None),
)


class AdminApiTests(unittest.TestCase):
    def setUp(self) -> None:
        app = FastAPI()
        app.add_exception_handler(RequestValidationError, validation_error)
        app.include_router(admin_api)
        self.browser = TestClient(app)
        self.addCleanup(self.browser.close)
        self.browser.cookies.set(SESSION_COOKIE_NAME, TOKEN)
        self.gateway = MagicMock()
        self.gateway.__enter__.return_value = self.gateway
        patcher = patch(
            "MetroFlow.admin.presentation.api.XanoAdminClient.from_environment",
            return_value=self.gateway,
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.gateway.indicators.return_value = INDICATORS
        self.gateway.stations.return_value = (
            AdminStation(1, "Sé", "SE", True, (AdminLine(1, "Azul", "L1", "#0455A1"),)),
            AdminStation(4, "Brás", "BRS", False),
        )
        self.gateway.set_station_status.return_value = StationStatus(4, True)

    def assert_no_store(self, response) -> None:
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertNotIn(TOKEN, response.text)

    def test_indicadores(self) -> None:
        response = self.browser.get("/api/admin/indicators")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["usage"]["active_routes"], 2)
        self.assertEqual(body["network"]["inactive_stations"], 2)
        self.assertEqual(body["ranking"], [{"id": 1, "name": "Sé", "code": "SE", "uses": 6}])
        self.assertEqual(
            body["crowding"],
            {"crowded_segments": None, "minimum_users": None, "percentage": None},
        )
        self.assert_no_store(response)
        self.gateway.indicators.assert_called_once_with(TOKEN)

    def test_estacoes_em_ordem_com_inativas(self) -> None:
        response = self.browser.get("/api/admin/stations")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [(item["name"], item["active"]) for item in response.json()],
            [("Brás", False), ("Sé", True)],
        )
        self.assert_no_store(response)

    def test_alteracao_devolve_a_situacao_vigente(self) -> None:
        response = self.browser.post("/api/admin/stations/4/status", json={"active": True})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": 4, "active": True})
        self.gateway.set_station_status.assert_called_once_with(4, True, TOKEN)
        self.assert_no_store(response)

    def test_sem_cookie_nao_consulta_o_xano(self) -> None:
        self.browser.cookies.clear()

        for response in (
            self.browser.get("/api/admin/indicators"),
            self.browser.get("/api/admin/stations"),
            self.browser.post("/api/admin/stations/4/status", json={"active": True}),
        ):
            self.assertEqual(response.status_code, 401)
            self.assert_no_store(response)
        self.gateway.indicators.assert_not_called()
        self.gateway.set_station_status.assert_not_called()

    def test_codigos_de_erro_com_mensagens_genericas(self) -> None:
        cases = [
            (AdminUnauthorized("Sessão", 401), 401),
            (AdminForbidden("detalhe interno", 403), 403),
            (AdminNotFound("detalhe interno", 404), 404),
            (AdminError("detalhe interno", 400), 400),
            (AdminError("detalhe interno", 422), 400),
            (AdminUnavailable("detalhe interno"), 503),
            (AdminError("Resposta administrativa inválida."), 502),
            (ValueError("Resposta não corresponde."), 502),
        ]
        for error, status in cases:
            with self.subTest(error=error):
                self.gateway.set_station_status.side_effect = error
                response = self.browser.post("/api/admin/stations/4/status", json={"active": False})

                self.assertEqual(response.status_code, status)
                self.assertNotIn("detalhe interno", response.text)
                self.assert_no_store(response)

    def test_acesso_negado_nao_devolve_dados(self) -> None:
        self.gateway.indicators.side_effect = AdminForbidden("Acesso restrito.", 403)

        response = self.browser.get("/api/admin/indicators")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Acesso restrito a administradores."})

    def test_entradas_invalidas_sao_rejeitadas_sem_alterar(self) -> None:
        cases = [
            ("/api/admin/stations/4/status", {"active": "false"}),
            ("/api/admin/stations/4/status", {"active": 1}),
            ("/api/admin/stations/4/status", {}),
            ("/api/admin/stations/4/status", {"active": True, "usuario_id": 1}),
            ("/api/admin/stations/0/status", {"active": True}),
            ("/api/admin/stations/abc/status", {"active": True}),
        ]
        for path, body in cases:
            with self.subTest(path=path, body=body):
                response = self.browser.post(path, json=body)

                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json(), {"detail": "Dados da requisicao invalidos."})
        self.gateway.set_station_status.assert_not_called()
