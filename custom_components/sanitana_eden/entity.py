"""SanitanaEdenEntity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import (
    CONNECTION_NETWORK_MAC,
    format_mac,
)
from .coordinator import SanitanaEdenDataUpdateCoordinator
from .const import MANUFACTURER, MODEL


class SanitanaEdenEntity(CoordinatorEntity):
    """SanitanaEdenEntity class."""

    def __init__(self, coordinator: SanitanaEdenDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            connections={
                (
                    CONNECTION_NETWORK_MAC,
                    format_mac(coordinator.config_entry.data.get("mac_ap")),
                ),
                (
                    CONNECTION_NETWORK_MAC,
                    format_mac(coordinator.config_entry.data.get("mac_sta")),
                ),
            },
            name=coordinator.config_entry.data.get("name"),
            manufacturer=MANUFACTURER,
            model=MODEL,
        )
