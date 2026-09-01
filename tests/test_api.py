"""Tests for ThermalTrace signing helper."""

from __future__ import annotations

import hashlib
import hmac
import importlib.util
from pathlib import Path


def _sign_body(secret: str, body: str) -> str:
    path = (
        Path(__file__).resolve().parents[1]
        / "custom_components"
        / "thermaltrace"
        / "signing.py"
    )
    spec = importlib.util.spec_from_file_location("thermaltrace_signing", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.sign_body(secret, body)


def test_sign_body_matches_thermaltrace_format() -> None:
    secret = "gts_testsecret"
    body = '{"action":"snooze","hours":24}'
    expected = hmac.new(
        secret.encode(),
        body.encode(),
        hashlib.sha256,
    ).hexdigest()
    assert _sign_body(secret, body) == f"sha256={expected}"
