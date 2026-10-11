from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

CACHE_DIR = Path(".cache")


@dataclass
class CachedResponse:
    status: int
    headers: list[tuple[str, str]]
    body: bytes


def hash_request_path(path: str) -> str:
    return hashlib.sha256(path.encode()).hexdigest()


def ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _atomic_write(path: Path, data: bytes) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def get_cached_response(path_hash: str) -> CachedResponse | None:
    try:
        meta = json.loads((CACHE_DIR / f"{path_hash}.json").read_text())
        body = (CACHE_DIR / f"{path_hash}.body").read_bytes()
        return CachedResponse(
            status=meta["status"],
            headers=[(name, value) for name, value in meta["headers"]],
            body=body,
        )
    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
        return None


def set_cached_response(path_hash: str, response: CachedResponse):
    _atomic_write(CACHE_DIR / f"{path_hash}.body", response.body)
    meta = {"status": response.status, "headers": response.headers}
    _atomic_write(CACHE_DIR / f"{path_hash}.json", json.dumps(meta).encode())


def clear_cache():
    shutil.rmtree(CACHE_DIR)
    ensure_cache_dir()
