"""Hash-chained audit log for transparent advising experiments."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _hash(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def append_record(path: str | Path, record: dict[str, Any]) -> dict[str, Any]:
    """Append one hash-chained audit record."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    previous_hash = "GENESIS"
    if path.exists() and path.read_text(encoding="utf-8").strip():
        previous_hash = json.loads(path.read_text(encoding="utf-8").strip().splitlines()[-1])["record_hash"]
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "previous_hash": previous_hash,
        "record": record,
    }
    payload["record_hash"] = _hash(payload)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")
    return payload


def verify_log(path: str | Path) -> dict[str, Any]:
    """Verify hash chaining for an audit log."""
    path = Path(path)
    if not path.exists():
        return {"valid": True, "records": 0}
    previous = "GENESIS"
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        payload = json.loads(line)
        expected_hash = payload.pop("record_hash")
        if payload.get("previous_hash") != previous:
            return {"valid": False, "records": count, "error": "previous_hash_mismatch"}
        actual_hash = _hash(payload)
        if actual_hash != expected_hash:
            return {"valid": False, "records": count, "error": "record_hash_mismatch"}
        previous = expected_hash
        count += 1
    return {"valid": True, "records": count}
