"""Smoke HTTP real para os builds modernos e Win7 Legacy (Python 3.8+)."""
from __future__ import annotations

import json
import socket
from urllib.request import ProxyHandler, build_opener

from pt2vhf_aprs import __version__
from pt2vhf_aprs.local_server import start_local_server
from pt2vhf_aprs.web import create_app


def main() -> None:
    app = create_app()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        preferred_port = int(probe.getsockname()[1])

    server = start_local_server(app, host="127.0.0.1", start_port=preferred_port, attempts=30)
    opener = build_opener(ProxyHandler({}))
    try:
        if not server.wait_ready(10):
            raise RuntimeError("Servidor HTTP indisponivel.")
        origin = "http://127.0.0.1:{}".format(server.port)

        def get(path):
            with opener.open(origin + path, timeout=10) as response:
                if response.status != 200:
                    raise AssertionError("{} retornou HTTP {}".format(path, response.status))
                return response.read()

        page = get("/")
        if b"PT2VHF" not in page:
            raise AssertionError("HTML esperado nao foi entregue.")
        js = get("/static/js/app.js")
        if len(js) < 1000:
            raise AssertionError("JavaScript principal nao foi entregue.")
        ping = json.loads(get("/api/diagnostics/ping").decode("utf-8"))
        if not ping.get("ok") or ping.get("version") != __version__:
            raise AssertionError("Ping/versionamento invalido: {!r}".format(ping))
        remote = json.loads(get("/api/local-interface/remote-probe").decode("utf-8"))
        if not remote.get("server_received_request"):
            raise AssertionError("API de prova HTTP invalida: {!r}".format(remote))
        if remote.get("external_access_confirmed"):
            raise AssertionError("Loopback foi confundido com acesso externo.")
        print("HTTP smoke OK: {} port {} (HTML, JS, ping e remote-probe)".format(__version__, server.port))
    finally:
        server.close()


if __name__ == "__main__":
    main()
