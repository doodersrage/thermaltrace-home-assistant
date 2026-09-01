"""ThermalTrace binary sensors (doors, leaks, motion, power)."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_DEVICE, ATTR_KIND, ATTR_KEY, ATTR_RECORDED_AT, DOMAIN
from .coordinator import ThermalTraceCoordinator

BINARY_KINDS = {
    "door": BinarySensorDeviceClass.DOOR,
    "flood": BinarySensorDeviceClass.MOISTURE,
    "motion": BinarySensorDeviceClass.MOTION,
    "power": BinarySensorDeviceClass.POWER,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ThermalTraceCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities: list[ThermalTraceBinarySensor] = []

    for row in coordinator.data.get("readings", []):
        kind = row.get("kind")
        if kind not in BINARY_KINDS:
            continue
        if row.get("value_bool") is None:
            continue
        entities.append(ThermalTraceBinarySensor(coordinator, entry, row))

    async_add_entities(entities)


class ThermalTraceBinarySensor(
    CoordinatorEntity[ThermalTraceCoordinator], BinarySensorEntity
):
    """Binary sensor from ThermalTrace readings."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ThermalTraceCoordinator,
        entry: ConfigEntry,
        row: dict,
    ) -> None:
        super().__init__(coordinator)
        self._row = row
        device = row.get("device") or "device"
        key = row.get("key") or "sensor"
        kind = row.get("kind") or "generic"
        label = row.get("label") or key

        self._attr_unique_id = f"{entry.unique_id}_{device}_{key}_{kind}_bool"
        self._attr_name = label
        self._attr_device_class = BINARY_KINDS.get(kind)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id, device)},
            name=device,
            manufacturer="ThermalTrace",
            configuration_url=entry.data.get("base_url", "https://thermaltrace.dev"),
        )

    @property
    def _current_row(self) -> dict | None:
        for row in self.coordinator.data.get("readings", []):
            if (
                row.get("device") == self._row.get("device")
                and row.get("key") == self._row.get("key")
                and row.get("kind") == self._row.get("kind")
            ):
                return row
        return None

    @property
    def is_on(self) -> bool | None:
        row = self._current_row
        if not row or row.get("value_bool") is None:
            return None
        return bool(row.get("value_bool"))

    @property
    def extra_state_attributes(self) -> dict:
        row = self._current_row or self._row
        return {
            ATTR_DEVICE: row.get("device"),
            ATTR_KEY: row.get("key"),
            ATTR_KIND: row.get("kind"),
            ATTR_RECORDED_AT: row.get("recorded_at"),
        }
