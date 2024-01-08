"""Config flow for Sanitana Eden."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import asdict
from typing import Any

import voluptuous as vol
from aio_sanitana_eden import DeviceConnectionError, async_get_info, SanitanaEdenInfo
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.device_registry import format_mac


from .const import DOMAIN, NAME


class SanitanaEdenConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a Sanitana Eden config flow."""

    VERSION = 0
    MINOR_VERSION = 1

    _name = ""
    _host = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle config step initiated by the user."""

        errors: dict[str, str] = {}
        if user_input is not None:
            self._name = user_input[CONF_NAME]
            self._host = user_input[CONF_HOST]
            try:
                info: SanitanaEdenInfo = await async_get_info(self._host)
            except DeviceConnectionError:
                errors["base"] = "cannot_connect"
            else:
                if info.mac_ap is None or info.mac_sta is None or info.port is None:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(format_mac(info.mac_ap))
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=self._name,
                        data={
                            **asdict(info),
                            **user_input,
                        },
                    )

        fields: dict[Any, type] = OrderedDict()
        fields[vol.Required(CONF_NAME, default=self._name or NAME)] = str  # type: ignore
        fields[vol.Required(CONF_HOST, default=self._host or vol.UNDEFINED)] = str  # type: ignore

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(fields),
            errors=errors,
        )
