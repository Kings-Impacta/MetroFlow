import json
import sqlite3
import httpx
import pytest
from MetroFlow.status.publish_cache import saved_conditions, send


def test_cache_export_keeps_dates_and_does_not_write_sqlite(tmp_path):
    path = tmp_path / "status.sqlite3"
    value = dict(line_code="L10", situation="normal", label="Operação Normal",
                 collected_at=1000, verified_at=1100, updated_at=900, validity="stale")
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE status_cache (key TEXT PRIMARY KEY, payload TEXT)")
        db.execute("INSERT INTO status_cache VALUES (?,?)", ("cptm-v1", json.dumps([value])))
    before = path.read_bytes()
    exported = saved_conditions(path, "cptm")
    assert path.read_bytes() == before
    assert [(r["collected_at"], r["verified_at"], r["updated_at"]) for r in exported] == [(1000, 1100, 900)]


def test_publisher_does_not_publish_without_a_reservation():
    calls = []
    def handle(request):
        calls.append(request)
        return httpx.Response(200, json={"granted": False})
    with httpx.Client(base_url="https://example.org/", transport=httpx.MockTransport(handle)) as client:
        assert not send(client, "cptm", [])
    assert len(calls) == 1


def test_publisher_uses_the_reserved_generation_without_changing_payload():
    calls = []
    items = [{"line_code": "L10", "collected_at": 1000}]
    def handle(request):
        data = json.loads(request.content)
        calls.append(data)
        return httpx.Response(200, json={"granted": True, "generation": 3} if len(calls) == 1 else {"stored": 1})
    with httpx.Client(base_url="https://example.org/", transport=httpx.MockTransport(handle)) as client:
        assert send(client, "cptm", items)
    assert calls[1]["pedido"]["generation"] == 3
    assert calls[1]["pedido"]["conditions"] == items


def test_cache_absence_does_not_create_a_database(tmp_path):
    path = tmp_path / "absent.sqlite3"
    with pytest.raises(sqlite3.OperationalError):
        saved_conditions(path, "cptm")
    assert not path.exists()


def test_publisher_checks_admin_in_profile_even_when_login_omits_role(monkeypatch, tmp_path):
    from types import SimpleNamespace
    from MetroFlow.status import publish_cache
    checked = []
    class Auth:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def login(self, email, password):
            return SimpleNamespace(user=SimpleNamespace(is_admin=False), auth_token="test-token")
        def me(self, token):
            checked.append(token)
            return SimpleNamespace(is_admin=True)
    monkeypatch.setattr(publish_cache.XanoAuthClient, "from_environment", lambda: Auth())
    monkeypatch.setattr("builtins.input", lambda _: "admin@example.org")
    monkeypatch.setattr(publish_cache.getpass, "getpass", lambda _: "test-password")
    monkeypatch.setattr(publish_cache, "saved_conditions", lambda *args: [])
    monkeypatch.setattr("sys.argv", ["publish_cache", "--url", "https://example.org/", "--cache", str(tmp_path/"unused"), "--sources", "cptm"])
    publish_cache.main()
    assert checked == ["test-token"]
