"""ThermalTrace sensors."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_DEVICE, ATTR_KIND, ATTR_KEY, ATTR_RECORDED_AT, DOMAIN
from .coordinator import ThermalTraceCoordinator

NUMERIC_KINDS = {
    "temperature",
    "humidity",
    "co2",
    "pressure",
    "pm25",
    "voc",
    "level",
    "energy",
    "generic",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ThermalTraceCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities: list[ThermalTraceSensor] = []

    for row in coordinator.data.get("readings", []):
        kind = row.get("kind")
        if kind not in NUMERIC_KINDS:
            continue
        if row.get("value_num") is None and row.get("value_text") is None:
            continue
        entities.append(ThermalTraceSensor(coordinator, entry, row))

    async_add_entities(entities)


class ThermalTraceSensor(CoordinatorEntity[ThermalTraceCoordinator], SensorEntity):
    """Sensor backed by a ThermalTrace share-link reading."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ThermalTraceCoordinator,
        entry: ConfigEntry,
        row: dict,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._row = row
        device = row.get("device") or "device"
        key = row.get("key") or "sensor"
        kind = row.get("kind") or "generic"
        label = row.get("label") or key

        self._attr_unique_id = f"{entry.unique_id}_{device}_{key}_{kind}"
        self._attr_name = label

        self._apply_device_class(kind, row.get("unit"))
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id, device)},
            name=device,
            manufacturer="ThermalTrace",
            configuration_url=entry.data.get("base_url", "https://thermaltrace.dev"),
        )
        self._attr_extra_state_attributes = {
            ATTR_DEVICE: device,
            ATTR_KEY: key,
            ATTR_KIND: kind,
            ATTR_RECORDED_AT: row.get("recorded_at"),
        }

    def _apply_device_class(self, kind: str, unit: str | None) -> None:
        if kind == "temperature":
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_state_class = SensorStateClass.MEASUREMENT
            if unit and unit.upper() in {"C", "°C"}:
                self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
            else:
                self._attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
        elif kind == "humidity":
            self._attr_device_class = SensorDeviceClass.HUMIDITY
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_native_unit_of_measurement = PERCENTAGE
        elif kind == "pressure":
            self._attr_device_class = SensorDeviceClass.PRESSURE
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_native_unit_of_measurement = UnitOfPressure.HPA
        elif kind == "co2":
            self._attr_device_class = SensorDeviceClass.CO2
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION
        elif kind == "pm25":
            self._attr_device_class = SensorDeviceClass.PM25
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_native_unit_of_measurement = "µg/m³"
        elif kind in {"level", "energy"}:
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_native_unit_of_measurement = unit or PERCENTAGE
        else:
            self._attr_native_unit_of_measurement = unit

    @property
    def available(self) -> bool:
        return super().available and self._current_row is not None

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
    def native_value(self):
        row = self._current_row
        if not row:
            return None
        if row.get("value_num") is not None:
            return row.get("value_num")
        return row.get("value_text")

    @property
    def extra_state_attributes(self) -> dict:
        row = self._current_row or self._row
        return {
            ATTR_DEVICE: row.get("device"),
            ATTR_KEY: row.get("key"),
            ATTR_KIND: row.get("kind"),
            ATTR_RECORDED_AT: row.get("recorded_at"),
        }
