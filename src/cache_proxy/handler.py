from http.server import BaseHTTPRequestHandler


import urllib.request
import urllib.error

from cache_proxy.cache import (
    CachedResponse,
    get_cached_response,
    hash_request_path,
    set_cached_response,
)

SKIP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "content-length",
}


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, origin, *args, **kwargs):
        self.origin = origin
        super().__init__(*args, **kwargs)

    def do_GET(self):

        path_hash = hash_request_path(self.path)

        cached = get_cached_response(path_hash)
        if cached is not None:
            self._send(cached, "HIT")
            return

        origin_req_url = f"{self.origin}{self.path}"

        req = urllib.request.Request(
            origin_req_url,
            headers={
                "Accept": "application/json",
                "User-Agent": "cache-proxy/0.1.0",
            },
        )

        try:
            origin_resp = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            origin_resp = e

        response = CachedResponse(
            status=origin_resp.status,
            headers=[
                (name, value)
                for name, value in origin_resp.headers.items()
                if name.lower() not in SKIP_HEADERS
            ],
            body=origin_resp.read(),
        )

        if 200 <= response.status <= 299:
            set_cached_response(path_hash, response)

        self._send(response, "MISS")

    def _send(self, response: CachedResponse, cache_state: str) -> None:
        self.send_response(response.status)
        for name, value in response.headers:
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(response.body)))
        self.send_header("X-Cache", cache_state)
        self.end_headers()
        self.wfile.write(response.body)
