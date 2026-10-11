from functools import partial
from http.server import HTTPServer

from cache_proxy.handler import RequestHandler


def start_proxy_server(port: int, origin: str):
    server_address = ("", port)
    handler = partial(RequestHandler, origin)

    httpd = HTTPServer(server_address, handler)
    print(f"Proxy server started listening on port {httpd.server_port}")
    httpd.serve_forever()
