"""Executa as chamadas JavaScript com DOM e rede simulados, sem acessar o Xano."""

import json
import shutil
import subprocess

import pytest

from MetroFlow.auth.presentation.state import (
    build_auth_script,
    build_email_action_script,
    build_session_script,
    build_token_action_script,
    build_token_capture_script,
)
from MetroFlow.planning.presentation.state import request_script


NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js necessário para executar JavaScript")

HARNESS = r"""
const assert = require('node:assert/strict');
let source = '';
process.stdin.on('data', chunk => source += chunk);
process.stdin.on('end', async () => {
  try {
    const input = JSON.parse(source);
    const calls = [];
    const button = {disabled: false, textContent: 'Enviar', setAttribute() {}, removeAttribute() {}};
    const fields = {email: 'teste@example.com', senha: 'senha-ficticia'};
    const form = {querySelector: () => button, reset: () => fields.senha = ''};
    global.document = {getElementById: () => form};
    global.window = {
      location: {origin: input.origin, hostname: new URL(input.origin).hostname,
                 port: new URL(input.origin).port, pathname: '/redefinir-senha',
                 hash: '#token=token-ficticio-de-acao-com-32-caracteres'},
      history: {replaceState: () => window.location.hash = ''},
    };
    global.FormData = class {get(key) {return fields[key];}};
    let failure = false;
    let responseStatus = 200;
    let hold = null;
    global.fetch = async (url, options) => {
      calls.push({url, options});
      if (hold) await hold;
      if (failure) throw new Error('Rede simulada indisponível');
      return {ok: responseStatus === 200, status: responseStatus, json: async () => ({})};
    };
    if (input.capture) {
      eval(input.capture);
      assert.equal(window.location.hash, '');
      assert.ok(form._metroflowActionToken);
    }
    if (input.scenario === 'retry') {
      fields.senha = 'curta';
      assert.equal((await eval(input.script)).status, 422);
      assert.equal(calls.length, 0);
      fields.senha = 'senha-ficticia';
      failure = true;
      assert.equal((await eval(input.script)).status, 0);
      assert.ok(form._metroflowActionToken);
      assert.equal(button.disabled, false);
      failure = false;
      responseStatus = 422;
      assert.equal((await eval(input.script)).status, 422);
      assert.ok(form._metroflowActionToken);
      responseStatus = 200;
    }
    if (input.scenario === 'duplicate') {
      let release;
      hold = new Promise(resolve => release = resolve);
      const pending = eval(input.script);
      assert.equal(button.disabled, true);
      assert.equal((await eval(input.script)).ignored, true);
      assert.equal(calls.length, 1);
      release();
      await pending;
    } else {
      if (input.scenario === 'expired') responseStatus = 401;
      await eval(input.script);
    }
    for (const call of calls) {
      assert.equal(new URL(call.url).origin, input.origin);
      assert.equal(new URL(call.url).pathname, input.endpoint);
      assert.equal(new URL(call.url).search, '');
      assert.equal(call.options.credentials, 'include');
    }
    assert.ok(calls.length > 0);
    if (input.capture) {
      assert.equal(form._metroflowActionToken, undefined);
      assert.equal(button.disabled, false);
      const lastBody = JSON.parse(calls.at(-1).options.body);
      assert.equal(lastBody.token, 'token-ficticio-de-acao-com-32-caracteres');
    }
    console.log('ok');
  } catch (error) { console.error(error); process.exitCode = 1; }
});
"""


def run_script(script, endpoint, *, origin="http://localhost:3000", **kwargs):
    result = subprocess.run(
        [NODE, "-e", HARNESS],
        input=json.dumps(dict(script=script, endpoint=endpoint, origin=origin, **kwargs)),
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("origin", ["http://localhost:3000", "http://127.0.0.1:3010", "https://metroflow.example"])
@pytest.mark.parametrize("kind", ["login", "session", "logout", "email", "stations", "route"])
def test_chamadas_usam_origem_da_pagina(kind, origin):
    scripts = {
        "login": (build_auth_script("login", "/api/auth/login", "Entrando"), "/api/auth/login"),
        "session": (build_session_script("/api/auth/me"), "/api/auth/me"),
        "logout": (build_session_script("/api/auth/logout", "POST"), "/api/auth/logout"),
        "email": (build_email_action_script("email", "/api/auth/senha/recuperar", "Enviando"), "/api/auth/senha/recuperar"),
        "stations": (request_script("/api/planning/stations", 1), "/api/planning/stations"),
        "route": (request_script("/api/planning/route", 1, {"origin_id": 1, "destination_id": 5}), "/api/planning/route"),
    }
    script, endpoint = scripts[kind]
    run_script(script, endpoint, origin=origin)


@pytest.mark.parametrize("scenario", ["retry", "duplicate", "expired"])
def test_recuperacao_preserva_token_apenas_enquanto_necessario(scenario):
    run_script(
        build_token_action_script("reset", "/api/auth/senha/redefinir", include_password=True),
        "/api/auth/senha/redefinir",
        capture=build_token_capture_script("reset"), scenario=scenario,
    )


def test_confirmacao_envia_token_e_limpa_formulario():
    run_script(
        build_token_action_script("verify", "/api/auth/email/confirmar", include_password=False),
        "/api/auth/email/confirmar",
        capture=build_token_capture_script("verify"),
    )
