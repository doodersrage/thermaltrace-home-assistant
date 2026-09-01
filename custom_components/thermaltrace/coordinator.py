"""Data update coordinator."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ThermalTraceApiError, ThermalTraceAuthError, ThermalTraceClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ThermalTraceCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll share-link readings."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: ThermalTraceClient,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.async_get_readings()
        except ThermalTraceAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except ThermalTraceApiError as err:
            raise UpdateFailed(str(err)) from err
