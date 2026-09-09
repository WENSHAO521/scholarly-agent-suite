"""Lightweight local file cache (PART XIV). No Redis, no database — one
JSON file per cache key under .cache/<adapter>/. Never committed (see
.gitignore) and never keys on credentials.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Optional


def build_key(adapter: str, operation: str, params: dict) -> str:
    normalized = json.dumps(params, sort_keys=True, default=str)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:32]
    return "%s__%s__%s" % (adapter, operation, digest)


@dataclass
class FileCache:
    root: str
    ttl_seconds: float = 24 * 3600

    def _path(self, adapter: str, key: str) -> str:
        return os.path.join(self.root, adapter, "%s.json" % key)

    def get(self, adapter: str, key: str, bypass: bool = False) -> Optional[Any]:
        if bypass:
            return None
        path = self._path(adapter, key)
        if not os.path.isfile(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            envelope = json.load(f)
        age = time.time() - envelope.get("cached_at", 0)
        if age > self.ttl_seconds:
            return None
        return envelope.get("value")

    def set(self, adapter: str, key: str, value: Any) -> None:
        path = self._path(adapter, key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        envelope = {"cached_at": time.time(), "value": value}
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(envelope, f)
        os.replace(tmp_path, path)

    def clear(self, adapter: Optional[str] = None) -> None:
        target = os.path.join(self.root, adapter) if adapter else self.root
        if not os.path.isdir(target):
            return
        for dirpath, _dirnames, filenames in os.walk(target, topdown=False):
            for fname in filenames:
                os.remove(os.path.join(dirpath, fname))
