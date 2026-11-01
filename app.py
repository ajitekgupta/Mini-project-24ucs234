"""Local final-demo interface. Run: python3 app.py"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from src.pipeline import answer_scenario


ROOT = Path(__file__).resolve().parent
PAGE = (ROOT / "web" / "index.html").read_bytes()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path != "/":
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(PAGE)))
        self.end_headers()
        self.wfile.write(PAGE)

    def do_POST(self) -> None:
        if self.path not in {"/api/analyze", "/api/compare"}:
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 12000:
                raise ValueError("Request is empty or too large")
            body = json.loads(self.rfile.read(length))
            mode = body.get("mode", "baseline")
            include_proposed = body.get("include_proposed", False) is True
            first = answer_scenario(body.get("scenario", ""), mode=mode,
                                    include_proposed=include_proposed).public_dict()
            if self.path == "/api/compare":
                second = answer_scenario(body.get("changed_scenario", ""), mode=mode,
                                         include_proposed=include_proposed).public_dict()
                result = {"before": first, "after": second,
                          "type_changed": first["dialogue_type"] != second["dialogue_type"]}
            else:
                result = first
            status = 200
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            result, status = {"error": str(exc)}, 400
        except Exception:
            result, status = {"error": "The analysis could not be completed."}, 500
        data = json.dumps(result, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    address = ("127.0.0.1", 8765)
    server = ThreadingHTTPServer(address, Handler)
    print(f"Open http://{address[0]}:{address[1]} in your browser")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
