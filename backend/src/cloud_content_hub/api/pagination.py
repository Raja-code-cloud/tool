import base64
import hashlib
import hmac
import json
from typing import Annotated

from pydantic import Field

PageLimit = Annotated[int, Field(default=25, ge=1, le=100)]


def encode_cursor(payload: dict[str, str], secret: bytes) -> str:
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    signature = hmac.new(secret, body, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(body + signature).decode().rstrip("=")


def decode_cursor(cursor: str, secret: bytes) -> dict[str, str]:
    try:
        raw = base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4))
        body, signature = raw[:-32], raw[-32:]
        if not hmac.compare_digest(signature, hmac.new(secret, body, hashlib.sha256).digest()):
            raise ValueError("Invalid cursor signature")
        value = json.loads(body)
        if not isinstance(value, dict) or not all(
            isinstance(key, str) and isinstance(item, str) for key, item in value.items()
        ):
            raise ValueError("Invalid cursor payload")
        return value
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid cursor") from exc
