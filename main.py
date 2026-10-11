# We need a CLI argument parsing here as the main application server.
# The arguments we need to check are as follows
# --port The port of the cache_proxy server to run.
# --origin The URL of the upstream server which the requests will be forwarded.

import argparse
import logging

from src.cache_proxy.server import start_proxy_server
from src.cache_proxy.validation import valid_port

parser = argparse.ArgumentParser(prog="cache_proxy")

parser.add_argument("--port", type=int, help="The port of the cache_proxy server")
parser.add_argument(
    "--origin",
    type=str,
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
    print("Clear cache and exit.")
else:
    if not valid_port(port=args.port):
        parser.error("Invalid port, please provide a valid port between 0 - 65535")

    start_proxy_server(port=args.port)
