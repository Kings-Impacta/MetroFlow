import httpx
from MetroFlow.status.service import StatusService, SnapshotStatusService, snapshot_service
from MetroFlow.status.xano_snapshot import XanoStatusSnapshotReader


def item(source="CPTM", validity="current", **changes):
    return dict(line_code="L11", situation="restricted", label="Velocidade reduzida",
                source=source, validity=validity, collected_at=1000, verified_at=1000,
                updated_at=900, **changes)


def test_remote_mode_shares_reader_and_never_constructs_direct_sources(monkeypatch):
    monkeypatch.setenv("METROFLOW_STATUS_XANO_URL", "https://snapshot.example/api:status")
    monkeypatch.setenv("METROFLOW_CPTM_ENABLED", "1")
    monkeypatch.setattr("MetroFlow.status.service.HttpProvider", lambda *a, **k: (_ for _ in ()).throw(AssertionError("coleta direta")))
    snapshot_service.cache_clear()
    first = StatusService.from_environment()
    assert isinstance(first, SnapshotStatusService)
    assert StatusService.from_environment() is first
    first.reader.close()
    snapshot_service.cache_clear()


def test_aggregate_retains_value_and_dates_on_invalid_http_response():
    now = [1000]
    body = {"version": 1, "sources": [{"source": "cptm", "conditions": [item()]}]}
    response = [httpx.Response(200, json=body)]
    calls = []
    def handler(request):
        calls.append(request)
        return response[0]
    reader = XanoStatusSnapshotReader("https://snapshot.example", clock=lambda: now[0],
                                     transport=httpx.MockTransport(handler))
    service = SnapshotStatusService(reader)
    try:
        assert len(service.conditions()) == 17
        for _ in range(20): service.conditions()
        assert len(calls) == 1
        response[0] = httpx.Response(503)
        now[0] += 61
        saved = next(x for x in service.conditions() if x.line_code == "L11")
        assert saved.situation == "restricted" and saved.validity == "stale"
        assert (saved.collected_at, saved.verified_at, saved.updated_at) == (1000, 1000, 900)
    finally:
        reader.close()


def test_main_source_precedes_complement_regardless_of_snapshot_order():
    body = {"version": 1, "sources": [
        {"source": "cptm", "conditions": [item()]},
        {"source": "ddt", "conditions": [item("Direto dos Trens")]},
    ]}
    reader = XanoStatusSnapshotReader("https://snapshot.example", clock=lambda: 1000,
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json=body)))
    try:
        assert next(x for x in SnapshotStatusService(reader).conditions() if x.line_code == "L11").source == "Direto dos Trens"
    finally:
        reader.close()
