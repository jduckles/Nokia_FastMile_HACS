"""Config flow for UniFi PoE Control integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_PORT_NAME,
    CONF_PORT_NUMBER,
    CONF_SITE,
    CONF_SWITCH_MAC,
    DEFAULT_PORT,
    DEFAULT_SITE,
)
from .unifi_api import UniFiAPI, UniFiAPIError

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    api = UniFiAPI(
        host=data[CONF_HOST],
        api_key=data[CONF_API_KEY],
        port=data.get(CONF_PORT, DEFAULT_PORT),
        site=data.get(CONF_SITE, DEFAULT_SITE),
    )

    try:
        result = await api.test_connection()
        if not result.get("success"):
            raise CannotConnect(result.get("error", "Unknown error"))

        return {
            "title": f"UniFi PoE ({data[CONF_HOST]})",
            "poe_devices": result.get("poe_devices", []),
        }
    finally:
        await api.close()


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class UniFiPoEConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for UniFi PoE Control."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}
        self._poe_devices: list[dict[str, Any]] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - controller connection."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                self._data = user_input
                self._poe_devices = info.get("poe_devices", [])

                if not self._poe_devices:
                    errors["base"] = "no_poe_devices"
                else:
                    # Go to device/port selection step
                    return await self.async_step_device()

            except CannotConnect as err:
                _LOGGER.error("Cannot connect: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_API_KEY): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(CONF_SITE, default=DEFAULT_SITE): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "api_key_info": "Create an API key in UniFi Settings → Admins & Users → API Keys"
            },
        )

    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle device and port selection step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Parse the combined device_port selection (mac:port_idx:port_name)
            device_port = user_input.get("device_port", "")
            parts = device_port.split(":", 2)
            if len(parts) >= 2:
                self._data[CONF_SWITCH_MAC] = parts[0]
                self._data[CONF_PORT_NUMBER] = int(parts[1])
                self._data[CONF_PORT_NAME] = parts[2] if len(parts) > 2 else f"Port {parts[1]}"

            # Create unique ID based on device MAC and port
            await self.async_set_unique_id(
                f"{self._data[CONF_SWITCH_MAC]}_{self._data[CONF_PORT_NUMBER]}"
            )
            self._abort_if_unique_id_configured()

            title = f"{self._data.get(CONF_PORT_NAME, 'Port')} PoE"
            return self.async_create_entry(title=title, data=self._data)

        # Build device/port options - show all PoE ports from all devices
        port_options = []
        for device in self._poe_devices:
            device_name = device["name"]
            device_mac = device["mac"]
            device_model = device["model"]
            for port in device.get("poe_ports", []):
                port_idx = port["port_idx"]
                port_name = port["name"]
                poe_power = port.get("poe_power", "0")
                # Value format: mac:port_idx:port_name
                value = f"{device_mac}:{port_idx}:{port_name}"
                label = f"{device_name} - {port_name} (Port {port_idx}, {poe_power}W)"
                port_options.append(
                    selector.SelectOptionDict(value=value, label=label)
                )

        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema(
                {
                    vol.Required("device_port"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=port_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=errors,
            description_placeholders={
                "port_info": "Select the PoE port to control"
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return UniFiPoEOptionsFlowHandler(config_entry)


class UniFiPoEOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for UniFi PoE Control."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PORT_NAME,
                        default=self.config_entry.data.get(CONF_PORT_NAME, ""),
                    ): str,
                }
            ),
        )
