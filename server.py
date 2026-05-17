#!/usr/bin/env python3
"""
Life Journey – local persistence server.
Run:  python3 server.py
Then open http://localhost:8765 in any browser.
Data is saved to events.json in the same directory.
"""
import http.server
import json
import os
from pathlib import Path

PORT      = 8765
DATA_FILE = Path(__file__).parent / 'events.json'
HTML_FILE = Path(__file__).parent / 'index.html'


class Handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self._serve_file(HTML_FILE, 'text/html; charset=utf-8')
        elif self.path == '/api/events':
            data = {}
            if DATA_FILE.exists():
                try:
                    data = json.loads(DATA_FILE.read_text('utf-8'))
                except Exception:
                    data = {}
            self._json(data)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/api/events':
            length = int(self.headers.get('Content-Length', 0))
            body   = self.rfile.read(length)
            try:
                data = json.loads(body)
                DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), 'utf-8')
                self._json({'ok': True})
            except Exception as e:
                self.send_error(400, str(e))
        else:
            self.send_error(404)

    # ── helpers ────────────────────────────────────────────────

    def _serve_file(self, path: Path, mime: str):
        if not path.exists():
            self.send_error(404)
            return
        content = path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

    def _json(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f'  {self.address_string()} – {fmt % args}')


if __name__ == '__main__':
    os.chdir(Path(__file__).parent)
    with http.server.HTTPServer(('127.0.0.1', PORT), Handler) as srv:
        print(f'\n  Life Journey  →  http://localhost:{PORT}\n')
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print('\n  Server stopped.')
