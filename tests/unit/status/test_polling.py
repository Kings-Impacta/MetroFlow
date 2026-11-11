"""Repetição automática do painel sem dependência de coletor experimental."""
from unittest import TestCase


class AutomaticScreenTests(TestCase):
    def test_agenda_releitura_e_cancela_ao_sair(self):
        from MetroFlow.status.presentation import LineStatusState
        state=LineStatusState(_reflex_internal_init=True)
        self.assertIsNotNone(state.start())
        current=state._request_id
        timer=state.receive(dict(request_id=current,status=200,data=[]))
        self.assertIsNotNone(timer)
        self.assertIsNone(state.repeat(current-1))
        self.assertIsNotNone(state.repeat(current))
        state.stop()
        self.assertIsNone(state.repeat(state._request_id))

    def test_falha_continua_releitura_sem_afetar_busca(self):
        from MetroFlow.status.presentation import LineStatusState
        state=LineStatusState(_reflex_internal_init=True)
        state.start()
        self.assertIsNotNone(state.receive(dict(request_id=state._request_id,status=503,data=None)))
        self.assertIn("continuar buscando",state.message)
