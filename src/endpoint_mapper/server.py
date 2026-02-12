from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from .mapper import EndpointMapper


def handler_factory(mapper: EndpointMapper):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self._send(200, {"status": "ok", "concepts": len(mapper.concepts)})
            else:
                self._send(404, {"error": "not_found"})

        def do_POST(self):
            if self.path != "/map":
                self._send(404, {"error": "not_found"})
                return
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            if not payload.get("endpoint"):
                self._send(400, {"error": "endpoint is required"})
                return
            result = mapper.map(payload["endpoint"], payload.get("domain"))
            self._send(200, result.to_dict())

        def _send(self, status: int, body: dict):
            data = json.dumps(body, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, fmt, *args):
            return

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ontology", default="config/endpoints.json")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    mapper = EndpointMapper.from_json(args.ontology)
    server = HTTPServer(("127.0.0.1", args.port), handler_factory(mapper))
    print(f"endpoint mapper API: http://127.0.0.1:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
