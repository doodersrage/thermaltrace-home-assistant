"""HMAC signing for ThermalTrace inbound webhooks."""

from __future__ import annotations

import hashlib
import hmac


def sign_body(secret: str, body: str) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"
