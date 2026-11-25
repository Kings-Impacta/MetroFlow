"""HTTPS em loopback e banco temporário; não é o runtime nativo do Xano."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import sqlite3
import ssl
import subprocess
from threading import Thread

import httpx
import pytest
from MetroFlow.status.xano_snapshot import XanoStatusSnapshotReader
from tests.unit.status.test_xano_persistence import T0, initial, publish, snapshot


def test_https_snapshot_survives_source_failure_and_server_restart(tmp_path):
    openssl = shutil.which("openssl")
    if openssl is None and os.name == "nt":
        candidate = Path(os.environ.get("ProgramFiles", "C:/Program Files"))/"Git/mingw64/bin/openssl.exe"
        openssl = str(candidate) if candidate.is_file() else None
    if openssl is None:
        pytest.skip("Laboratório HTTPS requer OpenSSL local.")
    cert, key = tmp_path/"cert.pem", tmp_path/"key.pem"
    subprocess.run([openssl, "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                    "-keyout", str(key), "-out", str(cert), "-days", "1",
                    "-subj", "/CN=localhost", "-addext", "subjectAltName=IP:127.0.0.1"],
                   check=True, capture_output=True, timeout=30)
    source = initial()
    publish(source)
    database = tmp_path/"snapshot.sqlite3"
    with sqlite3.connect(database) as db:
        db.execute("CREATE TABLE fonte (payload TEXT)")
        db.execute("INSERT INTO fonte VALUES (?)", (json.dumps(source),))
    clock, failed, calls = [T0/1000], [False], []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            calls.append(self.path)
            assert self.path == "/snapshot"
            with sqlite3.connect(database) as db:
                row = json.loads(db.execute("SELECT payload FROM fonte").fetchone()[0])
            data = json.dumps(snapshot(row, round(clock[0]*1000))).encode()
            self.send_response(503 if failed[0] else 200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    @contextmanager
    def server():
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert, key)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        thread = Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"https://127.0.0.1:{httpd.server_port}"
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=5)

    trust = ssl.create_default_context(cafile=str(cert))
    with server() as url:
        reader = XanoStatusSnapshotReader(url, transport=httpx.HTTPTransport(verify=trust, retries=0),
                                          clock=lambda: clock[0])
        try:
            assert reader.conditions()[0].validity == "current"
            for _ in range(20):
                assert reader.conditions()[0].line_code == "L10"
            assert calls == ["/snapshot"]
            clock[0] += 61
            failed[0] = True
            assert reader.conditions()[0].validity == "stale"
            assert reader.conditions()[0].collected_at == T0/1000
            reader.conditions()
            assert len(calls) == 2
        finally:
            reader.close()
    failed[0] = False
    clock[0] += 86400
    with server() as url:
        reader = XanoStatusSnapshotReader(url, transport=httpx.HTTPTransport(verify=trust, retries=0),
                                          clock=lambda: clock[0])
        try:
            restored = reader.conditions()[0]
            assert restored.label == "Operação Normal"
            assert restored.validity == "stale"
            assert restored.collected_at == T0/1000
        finally:
            reader.close()
