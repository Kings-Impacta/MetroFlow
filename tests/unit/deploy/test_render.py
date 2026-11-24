"""Invariantes da implantação sem acesso ao Xano ou a fontes externas."""
import os
import pytest
from deploy.render.environment import STATUS_FLAGS, configure

@pytest.fixture(autouse=True)
def clean_environment():
    before = dict(os.environ)
    for key in (*STATUS_FLAGS, "METROFLOW_PUBLIC_URL", "RENDER_EXTERNAL_URL", "PORT"):
        os.environ.pop(key, None)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(before)


def test_https_production(monkeypatch):
    monkeypatch.setenv("RENDER_EXTERNAL_URL", "https://metroflow-demo.onrender.com")
    monkeypatch.setenv("PORT", "10000")
    assert configure() == (10000, "https://metroflow-demo.onrender.com")
    assert os.environ["GRANIAN_WORKERS"] == "1"
    from MetroFlow.auth.infrastructure.session_cookie import is_production_environment
    assert is_production_environment()
    from MetroFlow.status.service import StatusService
    assert StatusService.from_environment().providers == []

@pytest.mark.parametrize("url", ["", "http://example.com", "https://user:pass@example.com",
    "https://example.com/path", "https://example.com?token=private", "https://example.com#x", "https://example.com:invalid", "https://bad host"])
def test_reject_bad_origin(monkeypatch, url):
    monkeypatch.setenv("METROFLOW_PUBLIC_URL", url)
    with pytest.raises(ValueError):
        configure()

@pytest.mark.parametrize("port", ["0", "80", "65536", "oops", "10000;echo", "-1"])
def test_reject_bad_port(monkeypatch, port):
    monkeypatch.setenv("PORT", port)
    with pytest.raises(ValueError):
        configure()

@pytest.mark.parametrize("flag", STATUS_FLAGS)
def test_reject_public_status_activation(monkeypatch, flag):
    monkeypatch.setenv(flag, "1")
    with pytest.raises(ValueError, match="Ativação pública"):
        configure()


def test_http_local_requires_explicit_option(monkeypatch):
    monkeypatch.setenv("METROFLOW_PUBLIC_URL", "http://127.0.0.1:10000")
    with pytest.raises(ValueError):
        configure()
    # Não deixa variáveis de configuração vazarem para outros testes.
    before = dict(os.environ)
    try:
        assert configure(local=True)[1] == "http://127.0.0.1:10000"
    finally:
        os.environ.clear()
        os.environ.update(before)
