"""WaterHeater platform for sanitana_eden."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.water_heater import (
    STATE_ELECTRIC,
    STATE_OFF,
    WaterHeaterEntity,
    WaterHeaterEntityEntityDescription,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SanitanaEdenDataUpdateCoordinator
from .entity import SanitanaEdenEntity


@dataclass(kw_only=True, frozen=True)
class SanitanaEdenWaterHeaterEntityDescription(WaterHeaterEntityEntityDescription):
    """Describes Sanitana Eden water heater entity."""

    has_entity_name: bool = True


ENTITY_DESCRIPTIONS = (
    SanitanaEdenWaterHeaterEntityDescription(
        key="sanitana_eden",
        name=None,
        translation_key="sanitana_eden",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up water heater platform."""

    coordinator: SanitanaEdenDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SanitanaEdenWaterHeaterEntity(coordinator, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SanitanaEdenWaterHeaterEntity(SanitanaEdenEntity, WaterHeaterEntity):
    """WaterHeaterEntity for the Sanitana Eden."""

    coordinator: SanitanaEdenDataUpdateCoordinator
    entity_description: SanitanaEdenWaterHeaterEntityDescription

    def __init__(
        self,
        coordinator: SanitanaEdenDataUpdateCoordinator,
        entity_description: SanitanaEdenWaterHeaterEntityDescription,
    ) -> None:
        """Initialize the water heater class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id: str | None = coordinator.config_entry.unique_id
        if entity_description.name is not None and self._attr_unique_id is not None:
            self._attr_unique_id += "_" + entity_description.key

        self._attr_target_temperature = 35.0
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_min_temp = 35.0
        self._attr_max_temp = 50.0
        self._attr_operation_list = [STATE_OFF, STATE_ELECTRIC]
        self._attr_supported_features = (
            WaterHeaterEntityFeature.TARGET_TEMPERATURE
            | WaterHeaterEntityFeature.OPERATION_MODE
            | WaterHeaterEntityFeature.ON_OFF
        )

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return float(self.coordinator.device.steam.temperature) or None

    @property
    def current_operation(self) -> str | None:
        """Return current operation ie. eco, electric, performance, ..."""
        return STATE_ELECTRIC if self.coordinator.device.steam.is_on else STATE_OFF

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set target temperature."""
        self._attr_target_temperature = kwargs.get(ATTR_TEMPERATURE)
        self.async_schedule_update_ha_state()

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set target operation mode."""
        if operation_mode == STATE_OFF:
            await self.coordinator.device.steam.async_turn_off()
        elif operation_mode == STATE_ELECTRIC:
            # await self.coordinator.device.async_steam_turn_on(self._attr_target_temperature, 15.0)
            pass

    async def async_turn_on(self, **_) -> None:
        """Turn the entity on."""
        await self.async_set_operation_mode(STATE_ELECTRIC)

    async def async_turn_off(self, **_) -> None:
        """Turn the entity off."""
        await self.async_set_operation_mode(STATE_OFF)
