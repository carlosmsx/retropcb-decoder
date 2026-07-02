#!/usr/bin/env python3
"""
Servidor de desarrollo para PCB Reverser.
Sirve estáticos (GET) y permite guardar archivos en data/ (PUT).

Uso:
    python scripts/dev_server.py          # puerto 4174
    python scripts/dev_server.py 8080     # puerto custom
"""

import http.server
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_PUT(self):
        raw = self.path.split('?')[0].lstrip('/')

        # Solo se permite escribir dentro de data/
        if not raw.startswith('data/'):
            self.send_error(403, 'PUT solo permitido en data/')
            return

        target = (ROOT / raw).resolve()

        # Prevenir path traversal
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            self.send_error(403, 'Ruta no permitida')
            return

        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)

        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, fmt, *args):
        method = fmt.split()[0] if fmt else ''
        if method == 'PUT':
            print(f'  [PUT] {args[0]}  →  guardado')
        else:
            super().log_message(fmt, *args)


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4174
    with http.server.HTTPServer(('', port), Handler) as httpd:
        print(f'PCB Reverser dev server  http://localhost:{port}/')
        print(f'Raiz : {ROOT}')
        print('PUT  : solo data/')
        print('Ctrl+C para detener\n')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nDetenido.')
