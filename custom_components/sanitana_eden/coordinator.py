"""DataUpdateCoordinator for sanitana_eden."""
from __future__ import annotations

from datetime import timedelta

from aio_sanitana_eden import SanitanaEden
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, LOGGER


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class SanitanaEdenDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize."""
        self.device = SanitanaEden(
            config_entry.data.get("host"), config_entry.data.get("port")
        )
        self.config_entry = config_entry
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    async def async_setup(self) -> None:
        """Set up async tasks."""
        self._remove_listener = self.device.async_add_listener(self.sanitana_update)
        await self.device.async_setup()

    async def async_shutdown(self) -> None:
        """Shut down async tasks."""
        self._remove_listener()
        await self.device.async_shutdown()

    async def _async_update_data(self):
        """Update data via library."""
        try:
            # await self.device.async_update()
            pass
        except Exception as exception:
            raise UpdateFailed(exception) from exception

    @callback
    def sanitana_update(self):
        """Process update from the device."""
        self.async_set_updated_data(None)
