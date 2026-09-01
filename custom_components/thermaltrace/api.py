"""ThermalTrace HTTP client."""

from __future__ import annotations

import json
import logging
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import DEFAULT_BASE_URL
from .signing import sign_body

_LOGGER = logging.getLogger(__name__)


class ThermalTraceAuthError(Exception):
    """Authentication or authorization failure."""


class ThermalTraceApiError(Exception):
    """API request failed."""


class ThermalTraceClient:
    """Minimal async client for share links, ingest, and inbound webhooks."""

    def __init__(
        self,
        session: ClientSession,
        base_url: str = DEFAULT_BASE_URL,
        share_token: str | None = None,
        inbound_token: str | None = None,
        inbound_secret: str | None = None,
        ingest_key: str | None = None,
    ) -> None:
        self._session = session
        self.base_url = base_url.rstrip("/")
        self.share_token = (share_token or "").strip()
        self.inbound_token = (inbound_token or "").strip() or None
        self.inbound_secret = (inbound_secret or "").strip() or None
        self.ingest_key = (ingest_key or "").strip() or None

    async def async_get_readings(self) -> dict[str, Any]:
        """Fetch latest readings from a share link."""
        if not self.share_token:
            raise ThermalTraceApiError("Share token is not configured")

        url = f"{self.base_url}/api/share/{self.share_token}/readings"
        try:
            async with self._session.get(url, timeout=30) as response:
                if response.status == 404:
                    raise ThermalTraceAuthError("Invalid or expired share token")
                if response.status == 429:
                    raise ThermalTraceApiError("Rate limited by ThermalTrace")
                if response.status >= 400:
                    text = await response.text()
                    raise ThermalTraceApiError(f"HTTP {response.status}: {text[:200]}")
                return await response.json()
        except ClientError as err:
            raise ThermalTraceApiError(str(err)) from err

    async def async_push_readings(self, payload: dict[str, Any]) -> None:
        """POST JSON readings to a push device ingest key."""
        if not self.ingest_key:
            raise ThermalTraceApiError("Ingest key is not configured")

        url = f"{self.base_url}/api/ingest/{self.ingest_key}"
        try:
            async with self._session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30,
            ) as response:
                if response.status == 401:
                    raise ThermalTraceAuthError("Invalid ingest device key")
                if response.status >= 400:
                    text = await response.text()
                    raise ThermalTraceApiError(f"HTTP {response.status}: {text[:200]}")
        except ClientError as err:
            raise ThermalTraceApiError(str(err)) from err

    async def async_inbound_action(
        self,
        action: str,
        *,
        hours: int | None = None,
        days: int | None = None,
    ) -> dict[str, Any]:
        """Call a signed inbound webhook action."""
        if not self.inbound_token or not self.inbound_secret:
            raise ThermalTraceApiError("Inbound webhook token/secret not configured")

        body: dict[str, Any] = {"action": action}
        if hours is not None:
            body["hours"] = hours
        if days is not None:
            body["days"] = days

        raw = json.dumps(body, separators=(",", ":"))
        signature = sign_body(self.inbound_secret, raw)
        url = f"{self.base_url}/api/inbound/{self.inbound_token}"

        try:
            async with self._session.post(
                url,
                data=raw,
                headers={
                    "Content-Type": "application/json",
                    "X-GarageTemp-Signature": signature,
                },
                timeout=30,
            ) as response:
                if response.status == 401:
                    raise ThermalTraceAuthError("Invalid inbound webhook or signature")
                if response.status >= 400:
                    text = await response.text()
                    raise ThermalTraceApiError(f"HTTP {response.status}: {text[:200]}")
                return await response.json()
        except ClientError as err:
            raise ThermalTraceApiError(str(err)) from err
