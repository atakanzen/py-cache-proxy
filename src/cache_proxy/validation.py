import argparse
from urllib.parse import urlparse


def port_number(value: str) -> int:
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not an integer")

    if not 0 <= port <= 65_535:
        raise argparse.ArgumentTypeError(f"{port} is out of range (0-65355)")

    return port


def origin(value: str) -> str:
    # This is good enough for this small project
    result = urlparse(value)
    if not all([result.scheme, result.netloc]):
        raise argparse.ArgumentTypeError(f"{value} is not a valid origin url")

    return value
