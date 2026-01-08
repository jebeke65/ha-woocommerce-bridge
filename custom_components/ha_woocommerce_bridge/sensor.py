from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ATTR_LATEST
from .coordinator import WooBridgeCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WooBridgeCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            WooOpenOrdersSensor(coordinator, entry),
            WooLatestOrderSensor(coordinator, entry),
        ]
    )


class WooBaseSensor(CoordinatorEntity[WooBridgeCoordinator], SensorEntity):
    def __init__(self, coordinator: WooBridgeCoordinator, entry: ConfigEntry, name: str, unique_suffix: str) -> None:
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{unique_suffix}"

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.data is not None


class WooOpenOrdersSensor(WooBaseSensor):
    def __init__(self, coordinator: WooBridgeCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "WooCommerce Open Orders", "open_orders")

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        return data.get("count", 0)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        return {
            "statuses": data.get("statuses"),
            "generated_at": data.get("generated_at"),
        }


class WooLatestOrderSensor(WooBaseSensor):
    def __init__(self, coordinator: WooBridgeCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "WooCommerce Latest Open Order", "latest_open_order")

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        latest = data.get("latest")
        if not latest:
            return "none"
        return latest.get("number", "unknown")

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        latest = data.get("latest")
        return {
            ATTR_LATEST: latest,
            "generated_at": data.get("generated_at"),
        }
