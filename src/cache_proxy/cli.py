import argparse
from pathlib import Path


from cache_proxy.server import start_proxy_server
from cache_proxy.validation import origin, port_number
from cache_proxy.cache import clear_cache, ensure_cache_dir


def main() -> None:

    ensure_cache_dir()

    parser = argparse.ArgumentParser(prog="cache_proxy")

    parser.add_argument(
        "--port",
        type=port_number,
        help="The port of the cache_proxy server",
    )
    parser.add_argument(
        "--origin",
        type=origin,
        help="The URL of the upstream server which the requests will be forwarded",
    )

    # Clear cache argument
    parser.add_argument(
        "--clear-cache",
        help="If given, the stored cache will be cleared",
        action="store_true",
    )

    args = parser.parse_args()

    if args.clear_cache:
        try:
            clear_cache()
        except Exception as e:
            parser.error(f"clear cache failed: {e}")
    else:
        if not args.port:
            parser.error("--port is required")
        if not args.origin:
            parser.error("--origin is required")

        start_proxy_server(port=args.port, origin=args.origin)
