# py-cache-proxy

A caching HTTP proxy written with the Python standard library only. It forwards
requests to an origin server, stores successful responses on disk, and replays
them on later requests without contacting the origin again.

```
client ──► cache-proxy ──► origin
              │
              └─ .cache/  (hit: served from disk, miss: fetched and stored)
```

## Requirements

- Python 3.15+
- No third-party dependencies

## Installation

```sh
git clone <repo-url>
cd py-cache-proxy
python -m venv .venv
source .venv/bin/activate        # fish: source .venv/bin/activate.fish
pip install -e .
```

This installs the `cache-proxy` command.

## Usage

```sh
cache-proxy --port 3000 --origin https://dummyjson.com
```

Then send requests to the proxy instead of the origin:

```sh
curl -i localhost:3000/products   # X-Cache: MISS (fetched from origin)
curl -i localhost:3000/products   # X-Cache: HIT  (served from .cache/)
```

Stop the server with `Ctrl+C`.

### Options

| Option          | Description                                                          |
| --------------- | -------------------------------------------------------------------- |
| `--port`        | Port the proxy listens on (0-65535). Required unless clearing cache. |
| `--origin`      | Base URL of the upstream server, e.g. `https://dummyjson.com`.       |
| `--clear-cache` | Deletes the local `.cache` directory and exits.                      |

## How it works

- **Cache key:** SHA-256 of the request path including the query string
  (`/products?limit=5` and `/products` are separate entries).
- **Storage:** each entry is two files in `.cache/`, relative to the directory
  you start the server from:
  - `<hash>.body`: the raw response body, stored as bytes
  - `<hash>.json`: the status code and response headers
- **Atomic writes:** files are written to a temp file and renamed into place.
  The metadata file is written last, so a crash mid-write never produces a
  half-valid entry.
- **What is cached:** only `2xx` responses. Errors from the origin (403, 404,
  5xx) are relayed to the client but never stored.
- **Headers:** the origin's status and headers are replayed as-is, except
  hop-by-hop headers (`Connection`, `Transfer-Encoding`, ...) and
  `Content-Length`, which is recomputed from the body.
- **`X-Cache` header:** every response carries `X-Cache: HIT` or `X-Cache: MISS`.

## Limitations

- Only `GET` requests are handled.
- Cached entries never expire. Use `--clear-cache` to reset.
- Requests to the origin use a fixed `Accept: application/json` header and
  `User-Agent`; client request headers are not forwarded.
- Responses are cached by path only, so `Vary` is ignored.
- The server handles one request at a time.

## Project layout

```
src/cache_proxy/
├── cli.py          # argument parsing and entry point
├── server.py       # HTTP server startup and graceful shutdown
├── handler.py      # request handler: cache lookup, origin fetch, response
├── cache.py        # on-disk cache read/write/clear
└── validation.py   # argparse type validators for --port and --origin
```

## License

See [LICENSE](LICENSE).
