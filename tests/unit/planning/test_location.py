"""Sugestão da estação mais próxima: script do navegador e estado do planejador."""

import json
import shutil
import subprocess
import unittest

from MetroFlow.planning.presentation.state import (
    LOCATION_FAILURE_MESSAGE, LOCATION_NOT_NEAR_MESSAGE, PlanningState, distance_text,
    location_script,
)


NODE = shutil.which("node")

STATIONS = [
    {"id": 1, "lat": -23.568816, "lon": -46.639921},  # Vergueiro
    {"id": 2, "lat": -23.575386, "lon": -46.640960},  # Paraíso
]

# Executa o script com geolocalização simulada e imprime somente o retorno.
HARNESS = r"""
let source = '';
process.stdin.on('data', chunk => source += chunk);
process.stdin.on('end', async () => {
  const input = JSON.parse(source);
  const calls = [];
  const geolocation = {
    getCurrentPosition(success, failure, options) {
      calls.push(options);
      if (input.error) failure({code: input.error});
      else success({coords: {latitude: input.position[0], longitude: input.position[1]}});
    },
  };
  Object.defineProperty(globalThis, 'navigator', {
    value: input.no_geolocation ? {} : {geolocation}, configurable: true,
  });
  globalThis.window = {isSecureContext: input.secure !== false};
  const result = await eval(input.script);
  console.log(JSON.stringify({result, calls}));
});
"""


@unittest.skipIf(NODE is None, "Node.js necessário para executar JavaScript")
class LocationScriptTests(unittest.TestCase):
    def run_script(self, stations=STATIONS, **scenario):
        completed = subprocess.run(
            [NODE, "-e", HARNESS],
            input=json.dumps({"script": location_script(stations, 7), **scenario}),
            capture_output=True, text=True, timeout=15, encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_devolve_apenas_a_estacao_mais_proxima_e_a_distancia(self):
        output = self.run_script(position=[-23.5760, -46.6410])
        self.assertEqual(set(output["result"]), {"request_id", "ok", "station_id", "distance_m"})
        self.assertEqual(output["result"]["station_id"], "2")
        self.assertTrue(output["result"]["ok"])
        self.assertLess(output["result"]["distance_m"], 100)
        self.assertEqual(output["calls"][0]["timeout"], 10000)

    def test_distancia_acima_do_limite_volta_para_o_estado_decidir(self):
        output = self.run_script(position=[-23.30, -46.60])
        self.assertGreater(output["result"]["distance_m"], 5000)

    def test_permissao_negada_e_tempo_esgotado(self):
        self.assertEqual(self.run_script(error=1)["result"],
                         {"request_id": 7, "ok": False, "reason": "denied"})
        self.assertEqual(self.run_script(error=3)["result"]["reason"], "timeout")
        self.assertEqual(self.run_script(error=2)["result"]["reason"], "unavailable")

    def test_sem_https_ou_sem_geolocalizacao_nao_pede_posicao(self):
        insecure = self.run_script(secure=False, position=[-23.57, -46.64])
        self.assertEqual((insecure["result"]["reason"], insecure["calls"]), ("unavailable", []))
        missing = self.run_script(no_geolocation=True)
        self.assertEqual(missing["result"]["reason"], "unavailable")

    def test_sem_estacoes_com_coordenadas(self):
        output = self.run_script(stations=[], position=[-23.57, -46.64])
        self.assertEqual(output["result"]["ok"], False)


class LocationStateTests(unittest.TestCase):
    def setUp(self):
        self.state = PlanningState(_reflex_internal_init=True)
        self.state.stations_status = "ready"
        self.state.stations = [
            {"id": "1", "name": "Vergueiro", "label": "Vergueiro · Linha 1"},
            {"id": "2", "name": "Paraíso", "label": "Paraíso · Linha 1"},
        ]
        self.state._station_coordinates = STATIONS
        self.state.location_available = True

    def located(self, **result):
        return {"request_id": self.state._location_request_id, **result}

    def test_lista_de_estacoes_define_disponibilidade(self):
        data = [
            {"id": 1, "name": "Vergueiro", "label": "Vergueiro", "latitude": -23.5, "longitude": -46.6},
            {"id": 2, "name": "Paraíso", "label": "Paraíso"},
        ]
        self.state.receive_stations({"request_id": self.state._request_id, "ok": True, "data": data})
        self.assertTrue(self.state.location_available)
        self.assertEqual(self.state._station_coordinates, [{"id": 1, "lat": -23.5, "lon": -46.6}])
        self.state.receive_stations({"request_id": self.state._request_id, "ok": True, "data": data[1:]})
        self.assertFalse(self.state.location_available)

    def test_pedido_envia_somente_coordenadas_das_estacoes(self):
        event = self.state.request_location()
        self.assertIsNotNone(event)
        self.assertEqual(self.state.location_status, "loading")
        self.assertIn("getCurrentPosition", event.args[0][1]._var_value)
        self.assertIsNone(self.state.request_location())

    def test_sem_coordenadas_nao_pede_localizacao(self):
        self.state.location_available = False
        self.assertIsNone(self.state.request_location())

    def test_agora_nao_oculta_o_aviso_sem_pedir_permissao(self):
        self.state.dismiss_location_prompt()
        self.assertTrue(self.state.location_prompt_dismissed)
        self.assertEqual(self.state.location_status, "idle")
        self.assertEqual(self.state.origin_id, "")

    def test_sucesso_preenche_origem_e_distancia(self):
        self.state.request_location()
        self.state.receive_location(self.located(ok=True, station_id="2", distance_m=447))
        self.assertEqual((self.state.origin_id, self.state.origin_query), ("2", "Paraíso"))
        self.assertEqual(self.state.origin_distance_text,
                         "Estação mais próxima: ~450 m (distância em linha reta)")
        self.assertTrue(self.state.location_prompt_dismissed)
        self.assertEqual(self.state.location_status, "idle")

    def test_escolha_manual_substitui_a_sugestao(self):
        self.state.request_location()
        self.state.receive_location(self.located(ok=True, station_id="2", distance_m=447))
        self.state.choose_origin("1", "Vergueiro")
        self.assertEqual((self.state.origin_id, self.state.origin_distance_text), ("1", ""))
        self.state.receive_location(self.located(ok=True, station_id="2", distance_m=447))
        self.state.update_origin_query("Ver")
        self.assertEqual(self.state.origin_distance_text, "")

    def test_nenhuma_estacao_ate_5_km_nao_altera_origem(self):
        self.state.request_location()
        self.state.receive_location(self.located(ok=True, station_id="2", distance_m=5001))
        self.assertEqual(self.state.origin_id, "")
        self.assertEqual(self.state.location_message, LOCATION_NOT_NEAR_MESSAGE)

    def test_falhas_e_respostas_invalidas_mantem_origem(self):
        for result in [
            {"ok": False, "reason": "denied"},
            {"ok": True, "station_id": "99", "distance_m": 10},
            {"ok": True, "station_id": "2", "distance_m": "perto"},
            {"ok": True, "station_id": "2", "distance_m": -1},
            {"ok": True, "station_id": "2", "distance_m": True},
        ]:
            self.state.request_location()
            self.state.receive_location(self.located(**result))
            self.assertEqual(self.state.origin_id, "")
            self.assertEqual(self.state.location_message, LOCATION_FAILURE_MESSAGE)
            self.assertEqual(self.state.location_status, "idle")

    def test_resposta_antiga_e_ignorada(self):
        self.state.request_location()
        self.state.receive_location({"request_id": self.state._location_request_id - 1,
                                     "ok": True, "station_id": "2", "distance_m": 100})
        self.assertEqual((self.state.origin_id, self.state.location_status), ("", "loading"))

    def test_texto_da_distancia(self):
        self.assertEqual(distance_text(3), "Estação mais próxima: ~10 m (distância em linha reta)")
        self.assertEqual(distance_text(1234), "Estação mais próxima: ~1.230 m (distância em linha reta)")


if __name__ == "__main__":
    unittest.main()
