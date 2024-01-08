"""Switch platform for sanitana_eden."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from aio_sanitana_eden import SanitanaEden
from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SanitanaEdenDataUpdateCoordinator
from .entity import SanitanaEdenEntity


@dataclass(kw_only=True, frozen=True)
class SanitanaEdenSwitchEntityDescription(SwitchEntityDescription):
    """Describes Sanitana Eden switch entity."""

    has_entity_name: bool = True
    value_fn: Callable[[SanitanaEden], bool]
    turn_on_fn: Callable[[SanitanaEden], Awaitable[None]]
    turn_off_fn: Callable[[SanitanaEden], Awaitable[None]]


ENTITY_DESCRIPTIONS = (
    SanitanaEdenSwitchEntityDescription(
        key="radio",
        name="Radio",
        translation_key="radio",
        value_fn=lambda device: device.radio.is_on,
        turn_on_fn=lambda device: device.radio.async_turn_on(),
        turn_off_fn=lambda device: device.radio.async_turn_off(),
        icon="mdi:radio",
    ),
    SanitanaEdenSwitchEntityDescription(
        key="bluetooth",
        name="Bluetooth",
        translation_key="bluetooth",
        value_fn=lambda device: device.bluetooth.is_on,
        turn_on_fn=lambda device: device.bluetooth.async_turn_on(),
        turn_off_fn=lambda device: device.bluetooth.async_turn_off(),
        icon="mdi:bluetooth",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up switch platform."""

    coordinator: SanitanaEdenDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SanitanaEdenSwitchEntity(coordinator, entity_description)
        for entity_description in ENTITY_DESCRIPTIONS
    )


class SanitanaEdenSwitchEntity(SanitanaEdenEntity, SwitchEntity):
    """SwitchEntity for the Sanitana Eden."""

    coordinator: SanitanaEdenDataUpdateCoordinator
    entity_description: SanitanaEdenSwitchEntityDescription

    def __init__(
        self,
        coordinator: SanitanaEdenDataUpdateCoordinator,
        entity_description: SanitanaEdenSwitchEntityDescription,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id: str | None = coordinator.config_entry.unique_id
        if entity_description.name is not None and self._attr_unique_id is not None:
            self._attr_unique_id += "_" + entity_description.key

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self.entity_description.value_fn(self.coordinator.device)

    async def async_turn_on(self, **_) -> None:
        """Turn on switch."""
        await self.entity_description.turn_on_fn(self.coordinator.device)
        # await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_) -> None:
        """Turn off switch."""
        await self.entity_description.turn_off_fn(self.coordinator.device)
        # await self.coordinator.async_request_refresh()
