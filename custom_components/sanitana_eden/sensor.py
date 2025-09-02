"""Sensor platform for sanitana_eden."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from aio_sanitana_eden import SanitanaEden
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SanitanaEdenDataUpdateCoordinator
from .entity import SanitanaEdenEntity


@dataclass(kw_only=True, frozen=True)
class SanitanaEdenSensorEntityDescription(SensorEntityDescription):
    """Describes Sanitana Eden sensor entity."""

    has_entity_name: bool = True
    value_fn: Callable[[SanitanaEden], float]


ENTITY_DESCRIPTIONS = (
    SanitanaEdenSensorEntityDescription(
        key="steam_remaining",
        name="Steam Remaining",
        translation_key="steam_remaining",
        value_fn=lambda device: device.steam.remaining * 100.0,
        icon="mdi:timer-sand",
        native_unit_of_measurement="%",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor platform."""

    coordinator: SanitanaEdenDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SanitanaEdenSensorEntity(coordinator, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SanitanaEdenSensorEntity(SanitanaEdenEntity, SensorEntity):
    """SwitchEntity for the Sanitana Eden."""

    coordinator: SanitanaEdenDataUpdateCoordinator
    entity_description: SanitanaEdenSensorEntityDescription

    def __init__(
        self,
        coordinator: SanitanaEdenDataUpdateCoordinator,
        entity_description: SanitanaEdenSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id: str | None = coordinator.config_entry.unique_id
        if entity_description.name is not None and self._attr_unique_id is not None:
            self._attr_unique_id += "_" + entity_description.key

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the sensor."""
        return self.entity_description.value_fn(self.coordinator.device)
