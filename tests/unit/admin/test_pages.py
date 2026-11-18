"""Componentes da página administrativa e do cabeçalho."""

import json
import unittest

import reflex as rx

from MetroFlow.admin.presentation.pages import _confirmation, _station_row, admin_page
from MetroFlow.admin.presentation.state import AdminState
from MetroFlow.planning.presentation.pages import header


def rendered(component: rx.Component) -> str:
    return str(component.render())


def text(value: str) -> str:
    """Texto como aparece na renderização: acentos escapados e repr do dicionário."""

    return json.dumps(value)[1:-1].replace("\\", "\\\\")


class AdminPageTests(unittest.TestCase):
    def test_pagina_condiciona_o_conteudo_ao_acesso(self) -> None:
        page = rendered(admin_page())

        self.assertIn(text("Painel administrativo"), page)
        self.assertIn("admin_state.access", page)
        for value in (
            "O acesso a este painel é restrito a administradores.",
            "Verificando acesso…",
            "O serviço administrativo está temporariamente indisponível. Tente novamente em instantes.",
            "Atualizar indicadores",
            "Pesquisar por nome ou código",
            "Trechos lotados agora",
            "Ainda não há dados para o ranking.",
            "Nenhuma estação encontrada.",
        ):
            with self.subTest(value=value):
                self.assertIn(text(value), page)

    def test_confirmacao_avisa_a_interrupcao_das_linhas(self) -> None:
        dialog = rendered(_confirmation())

        self.assertIn(text("Inativar estação?"), dialog)
        self.assertIn(text("interrompidas neste ponto"), dialog)
        self.assertIn(text("Viagens já em andamento não são encerradas."), dialog)
        self.assertIn("Cancelar", dialog)
        self.assertIn("admin_state.pending_name", dialog)
        self.assertIn("admin_state.pending_lines", dialog)
        self.assertIn("cancel_change", dialog)
        self.assertIn("confirm_change", dialog)

    def test_linha_da_estacao_oferece_ativar_ou_inativar(self) -> None:
        row = rendered(_station_row(AdminState.visible_stations[0]))

        self.assertIn("Inativar", row)
        self.assertIn("Ativar", row)
        self.assertIn("request_change", row)
        self.assertIn("admin_state.updating_id", row)

    def test_pagina_nao_expoe_dados_de_usuarios(self) -> None:
        page = rendered(admin_page()).lower()

        for forbidden in ("e-mail", "usuario_id", "token"):
            self.assertNotIn(forbidden, page)


class HeaderTests(unittest.TestCase):
    def test_link_do_painel_depende_da_indicacao_de_administrador(self) -> None:
        component = rendered(header())

        self.assertIn(text("Administração"), component)
        self.assertIn("auth_state.is_admin", component)
        self.assertIn('"/admin"', component)

    def test_logout_limpa_o_painel(self) -> None:
        self.assertIn("admin_state.clear_panel", rendered(header()))
