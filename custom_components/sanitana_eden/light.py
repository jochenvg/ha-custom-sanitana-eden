"""Light platform for sanitana_eden."""
from __future__ import annotations
from dataclasses import dataclass

from typing import Any

from homeassistant.components.light import (
    ColorMode,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SanitanaEdenDataUpdateCoordinator
from .entity import SanitanaEdenEntity


@dataclass(kw_only=True, frozen=True)
class SanitanaEdenLightEntityDescription(LightEntityDescription):
    """Describes Sanitana Eden light entity."""

    has_entity_name: bool = True


ENTITY_DESCRIPTIONS = (
    SanitanaEdenLightEntityDescription(
        key="sanitana_eden",
        name=None,
        translation_key="sanitana_eden",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up light platform."""

    coordinator: SanitanaEdenDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SanitanaEdenLightEntity(coordinator, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SanitanaEdenLightEntity(SanitanaEdenEntity, LightEntity):
    """LightEntity for the Sanitana Eden."""

    coordinator: SanitanaEdenDataUpdateCoordinator
    entity_description: SanitanaEdenLightEntityDescription

    def __init__(
        self,
        coordinator: SanitanaEdenDataUpdateCoordinator,
        entity_description: SanitanaEdenLightEntityDescription,
    ) -> None:
        """Initialize the light class."""
        super().__init__(coordinator)
        self.entity_description = entity_description  # type: ignore
        self._attr_unique_id: str | None = coordinator.config_entry.unique_id
        if entity_description.name is not None and self._attr_unique_id is not None:
            self._attr_unique_id += "_" + entity_description.key

        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_color_mode = ColorMode.RGB

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self.coordinator.device.light.is_on

    @property
    def brightness(self) -> int:
        """Return the brightness of this light between 0..255."""
        return self.coordinator.device.light.brightness

    @property
    def rgb_color(self) -> tuple[int, ...]:
        """Return the rgb color value [int, int, int]."""
        return self.coordinator.device.light.rgb_color

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on light."""
        await self.coordinator.device.light.async_turn_on(**kwargs)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off light."""
        await self.coordinator.device.light.async_turn_off(**kwargs)
