"""Switch platform for sanitana_eden."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from aio_sanitana_eden import SanitanaEden
from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SanitanaEdenDataUpdateCoordinator
from .entity import SanitanaEdenEntity


@dataclass(kw_only=True, frozen=True)
class SanitanaEdenNumberEntityDescription(NumberEntityDescription):
    """Describes Sanitana Eden switch entity."""

    has_entity_name: bool = True
    value_fn: Callable[[SanitanaEden], float]
    set_fn: Callable[[SanitanaEden, float], Awaitable[None]]


ENTITY_DESCRIPTIONS = (
    SanitanaEdenNumberEntityDescription(
        key="radio_frequency",
        name="Radio Frequency",
        translation_key="radio_frequency",
        value_fn=lambda device: device.radio.frequency,
        set_fn=lambda device, frequency: device.radio.async_set_frequency(frequency),
        native_max_value=108.0,
        native_min_value=87.5,
        native_step=0.01,
        native_unit_of_measurement="MHz",
        icon="mdi:radio-fm",
        device_class=NumberDeviceClass.FREQUENCY,
    ),
    SanitanaEdenNumberEntityDescription(
        key="radio_volume",
        name="Radio Volume",
        translation_key="radio_volume",
        value_fn=lambda device: device.radio.volume,
        set_fn=lambda device, volume: device.radio.async_set_volume(volume),
        native_max_value=63.0,
        native_min_value=0.0,
        native_step=1.0,
        icon="mdi:knob",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up switch platform."""

    coordinator: SanitanaEdenDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SanitanaEdenNumberEntity(coordinator, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SanitanaEdenNumberEntity(SanitanaEdenEntity, NumberEntity):
    """NumberEntity for the Sanitana Eden."""

    coordinator: SanitanaEdenDataUpdateCoordinator
    entity_description: SanitanaEdenNumberEntityDescription

    def __init__(
        self,
        coordinator: SanitanaEdenDataUpdateCoordinator,
        entity_description: SanitanaEdenNumberEntityDescription,
    ) -> None:
        """Initialize the number class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id: str | None = coordinator.config_entry.unique_id
        if entity_description.name is not None and self._attr_unique_id is not None:
            self._attr_unique_id += "_" + entity_description.key

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the number."""
        return self.entity_description.value_fn(self.coordinator.device)

    async def async_set_native_value(self, value: float) -> None:
        """Set native value."""
        await self.entity_description.set_fn(self.coordinator.device, value)
