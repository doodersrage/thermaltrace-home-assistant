"""The ThermalTrace integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ThermalTraceApiError, ThermalTraceClient
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
    SERVICE_CLEAR_SNOOZE,
    SERVICE_CLEAR_VACATION,
    SERVICE_PUSH,
    SERVICE_SNOOZE,
    SERVICE_STATUS,
    SERVICE_VACATION,
)
from .coordinator import ThermalTraceCoordinator

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]

SERVICE_PUSH_SCHEMA = vol.Schema({vol.Required("payload"): dict})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    client = ThermalTraceClient(
        session,
        entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL),
        share_token=entry.data.get(CONF_SHARE_TOKEN, ""),
        inbound_token=entry.data.get(CONF_INBOUND_TOKEN),
        inbound_secret=entry.data.get(CONF_INBOUND_SECRET),
        ingest_key=entry.data.get(CONF_INGEST_KEY),
    )
    coordinator = ThermalTraceCoordinator(
        hass,
        client,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"coordinator": coordinator, "client": client}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await _async_register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _async_register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_SNOOZE):
        return

    async def snooze(call: ServiceCall) -> None:
        client = _client_for_call(hass, call)
        hours = int(call.data.get("hours", 24))
        await client.async_inbound_action(SERVICE_SNOOZE, hours=hours)

    async def vacation(call: ServiceCall) -> None:
        client = _client_for_call(hass, call)
        days = int(call.data.get("days", 7))
        await client.async_inbound_action(SERVICE_VACATION, days=days)

    async def clear_snooze(call: ServiceCall) -> None:
        client = _client_for_call(hass, call)
        await client.async_inbound_action(SERVICE_CLEAR_SNOOZE)

    async def clear_vacation(call: ServiceCall) -> None:
        client = _client_for_call(hass, call)
        await client.async_inbound_action(SERVICE_CLEAR_VACATION)

    async def status(call: ServiceCall) -> None:
        client = _client_for_call(hass, call)
        result = await client.async_inbound_action(SERVICE_STATUS)
        hass.states.async_set(
            f"{DOMAIN}.status",
            "ok",
            attributes=result,
        )

    async def push(call: ServiceCall) -> None:
        client = _client_for_call(hass, call)
        payload = call.data["payload"]
        await client.async_push_readings(payload)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SNOOZE,
        snooze,
        schema=vol.Schema({
            vol.Optional("hours", default=24): vol.All(int, vol.Range(min=1, max=168)),
        }),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_VACATION,
        vacation,
        schema=vol.Schema({
            vol.Optional("days", default=7): vol.All(int, vol.Range(min=1, max=90)),
        }),
    )
    hass.services.async_register(DOMAIN, SERVICE_CLEAR_SNOOZE, clear_snooze)
    hass.services.async_register(DOMAIN, SERVICE_CLEAR_VACATION, clear_vacation)
    hass.services.async_register(DOMAIN, SERVICE_STATUS, status)
    hass.services.async_register(DOMAIN, SERVICE_PUSH, push, schema=SERVICE_PUSH_SCHEMA)


def _client_for_call(hass: HomeAssistant, call: ServiceCall) -> ThermalTraceClient:
    entry_id = call.data.get("config_entry")
    domain_data: dict[str, Any] = hass.data.get(DOMAIN, {})
    if entry_id and entry_id in domain_data:
        return domain_data[entry_id]["client"]
    if len(domain_data) == 1:
        return next(iter(domain_data.values()))["client"]
    raise ThermalTraceApiError(
        "Multiple ThermalTrace config entries — pass config_entry in service data"
    )
