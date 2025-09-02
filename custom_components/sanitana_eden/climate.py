"""Climate platform for sanitana_eden."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .const import DOMAIN
from .coordinator import SanitanaEdenDataUpdateCoordinator
from .entity import SanitanaEdenEntity

from homeassistant.components.climate import (
    ClimateEntityDescription,
    ClimateEntity,
)
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACMode,
    HVACAction,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

@dataclass(kw_only=True, frozen=True)
class SanitanaEdenClimateEntityDescription(ClimateEntityDescription):
    """Describes Sanitana Eden water heater entity."""

    has_entity_name: bool = True


ENTITY_DESCRIPTIONS = (
    SanitanaEdenClimateEntityDescription(
        key="sanitana_eden",
        name=None,
        translation_key="sanitana_eden",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate platform."""

    coordinator: SanitanaEdenDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SanitanaEdenClimateEntity(coordinator, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SanitanaEdenClimateEntity(SanitanaEdenEntity, ClimateEntity):
    """ClimateEntity for the Sanitana Eden."""

    coordinator: SanitanaEdenDataUpdateCoordinator
    def __init__(
        self,
        coordinator: SanitanaEdenDataUpdateCoordinator,
        entity_description: SanitanaEdenClimateEntityDescription,
    ) -> None:
        """Initialize the climate class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id: str | None = coordinator.config_entry.unique_id
        if entity_description.name is not None and self._attr_unique_id is not None:
            self._attr_unique_id += "_" + entity_description.key

        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_min_temp = 35.0
        self._attr_max_temp = 50.0
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
        )

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.device.steam.current_temperature

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        return self.coordinator.device.steam.temperature

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current operation ie. eco, electric, performance, ..."""
        return HVACMode.HEAT if self.coordinator.device.steam.is_on else HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current running hvac action."""
        return (
            HVACAction.HEATING
            if self.coordinator.device.steam.is_on
            else HVACAction.OFF
        )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set target temperature."""
        if temperature := kwargs.get(ATTR_TEMPERATURE):
            await self.coordinator.device.steam.async_set_temperature(temperature)
            self.async_schedule_update_ha_state()

    async def async_set_hvac_mode(self, /, hvac_mode: HVACMode) -> None:
        """Set target operation mode."""
        if hvac_mode == HVACMode.OFF and self.coordinator.device.steam.is_on:
            await self.coordinator.device.steam.async_turn_off()
        elif hvac_mode == HVACMode.HEAT and not self.coordinator.device.steam.is_on:
            await self.coordinator.device.steam.async_turn_on()

    async def async_turn_on(self, **_) -> None:
        """Turn the entity on."""
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self, **_) -> None:
        """Turn the entity off."""
        await self.async_set_hvac_mode(HVACMode.OFF)
