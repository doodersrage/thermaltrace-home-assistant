"""Config flow for ThermalTrace."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ThermalTraceAuthError, ThermalTraceClient, ThermalTraceApiError
from .const import (
    CONF_BASE_URL,
    CONF_INGEST_KEY,
    CONF_INBOUND_SECRET,
    CONF_INBOUND_TOKEN,
    CONF_SCAN_INTERVAL,
    CONF_SHARE_TOKEN,
    DEFAULT_BASE_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
        vol.Required(CONF_SHARE_TOKEN): str,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=60, max=3600)
        ),
        vol.Optional(CONF_INBOUND_TOKEN): str,
        vol.Optional(CONF_INBOUND_SECRET): str,
        vol.Optional(CONF_INGEST_KEY): str,
    }
)


def _clean(data: dict[str, Any]) -> dict[str, Any]:
    cleaned = {
        CONF_BASE_URL: data[CONF_BASE_URL].strip().rstrip("/"),
        CONF_SHARE_TOKEN: data[CONF_SHARE_TOKEN].strip(),
        CONF_SCAN_INTERVAL: int(data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
    }
    for key in (CONF_INBOUND_TOKEN, CONF_INBOUND_SECRET, CONF_INGEST_KEY):
        value = (data.get(key) or "").strip()
        if value:
            cleaned[key] = value
    return cleaned


class ThermalTraceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ThermalTrace."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            data = _clean(user_input)
            if not data[CONF_SHARE_TOKEN]:
                errors["base"] = "invalid_share_token"
            else:
                session = async_get_clientsession(self.hass)
                client = ThermalTraceClient(
                    session,
                    data[CONF_BASE_URL],
                    share_token=data[CONF_SHARE_TOKEN],
                )
                try:
                    payload = await client.async_get_readings()
                except ThermalTraceAuthError:
                    errors["base"] = "invalid_share_token"
                except ThermalTraceApiError as err:
                    _LOGGER.debug("Validation failed: %s", err)
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(data[CONF_SHARE_TOKEN])
                    self._abort_if_unique_id_configured()
                    title = payload.get("label") or "ThermalTrace"
                    return self.async_create_entry(title=title, data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @config_entries.callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return ThermalTraceOptionsFlowHandler(config_entry)


class ThermalTraceOptionsFlowHandler(config_entries.OptionsFlow):
    """Update scan interval and optional webhook/ingest settings."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        if user_input is not None:
            merged = _clean({**self.config_entry.data, **user_input})
            self.hass.config_entries.async_update_entry(self.config_entry, data=merged)
            return self.async_create_entry(title="", data={})

        data = self.config_entry.data
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_BASE_URL, default=data.get(CONF_BASE_URL, DEFAULT_BASE_URL)
                    ): str,
                    vol.Optional(
                        CONF_SHARE_TOKEN, default=data.get(CONF_SHARE_TOKEN, "")
                    ): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ): vol.All(int, vol.Range(min=60, max=3600)),
                    vol.Optional(
                        CONF_INBOUND_TOKEN, default=data.get(CONF_INBOUND_TOKEN, "")
                    ): str,
                    vol.Optional(
                        CONF_INBOUND_SECRET, default=data.get(CONF_INBOUND_SECRET, "")
                    ): str,
                    vol.Optional(
                        CONF_INGEST_KEY, default=data.get(CONF_INGEST_KEY, "")
                    ): str,
                }
            ),
        )
