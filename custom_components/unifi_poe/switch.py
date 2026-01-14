"""Switch platform for UniFi PoE Control."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_PORT_NAME, CONF_PORT_NUMBER, CONF_SWITCH_MAC
from .unifi_api import UniFiAPI

_LOGGER = logging.getLogger(__name__)


SWITCH_TYPES = (
    SwitchEntityDescription(
        key="poe_enabled",
        name="PoE Enabled",
        icon="mdi:ethernet",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up UniFi PoE switches."""
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    coordinator = data["coordinator"]

    entities = []
    for description in SWITCH_TYPES:
        entities.append(
            UniFiPoESwitch(
                coordinator=coordinator,
                api=api,
                entry=entry,
                description=description,
            )
        )

    async_add_entities(entities)


class UniFiPoESwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a UniFi PoE on/off switch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        api: UniFiAPI,
        entry: ConfigEntry,
        description: SwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.api = api
        self.entry = entry
        self.entity_description = description

        self._switch_mac = entry.data[CONF_SWITCH_MAC]
        self._port_idx = int(entry.data[CONF_PORT_NUMBER])
        self._port_name = entry.data.get(CONF_PORT_NAME, f"Port {self._port_idx}")
        self._previous_mode = "auto"  # Store previous mode for restoring

        # Entity attributes
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = f"{self._port_name} {description.name}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        device_data = self.coordinator.data.get("device", {}) if self.coordinator.data else {}

        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=f"{self._port_name} PoE Control",
            manufacturer="Ubiquiti",
            model=device_data.get("model", "UniFi Switch"),
            sw_version=device_data.get("version", "Unknown"),
            configuration_url=f"https://{self.api.host}:{self.api.port}",
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if PoE is enabled on the port."""
        if not self.coordinator.data:
            return None

        port_data = self.coordinator.data.get("port", {})
        if not port_data:
            return None

        poe_mode = port_data.get("poe_mode", "auto")

        # Store previous non-off mode for restoring later
        if poe_mode != "off":
            self._previous_mode = poe_mode

        return poe_mode != "off"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}

        port_data = self.coordinator.data.get("port", {})
        if not port_data:
            return {}

        return {
            "poe_mode": port_data.get("poe_mode"),
            "poe_power": port_data.get("poe_power"),
            "poe_voltage": port_data.get("poe_voltage"),
            "poe_current": port_data.get("poe_current"),
            "port_idx": self._port_idx,
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on PoE on the port."""
        _LOGGER.info(
            "Enabling PoE on port %d (%s) with mode: %s",
            self._port_idx,
            self._port_name,
            self._previous_mode,
        )

        try:
            success = await self.api.set_port_poe_mode(
                device_mac=self._switch_mac,
                port_idx=self._port_idx,
                poe_mode=self._previous_mode,
            )

            if success:
                _LOGGER.info(
                    "Successfully enabled PoE on port %d (%s)",
                    self._port_idx,
                    self._port_name,
                )
                # Refresh data
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error(
                    "Failed to enable PoE on port %d (%s)",
                    self._port_idx,
                    self._port_name,
                )
        except Exception as err:
            _LOGGER.error(
                "Error enabling PoE on port %d (%s): %s",
                self._port_idx,
                self._port_name,
                err,
            )
            raise

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off PoE on the port."""
        _LOGGER.info(
            "Disabling PoE on port %d (%s)",
            self._port_idx,
            self._port_name,
        )

        try:
            success = await self.api.set_port_poe_mode(
                device_mac=self._switch_mac,
                port_idx=self._port_idx,
                poe_mode="off",
            )

            if success:
                _LOGGER.info(
                    "Successfully disabled PoE on port %d (%s)",
                    self._port_idx,
                    self._port_name,
                )
                # Refresh data
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error(
                    "Failed to disable PoE on port %d (%s)",
                    self._port_idx,
                    self._port_name,
                )
        except Exception as err:
            _LOGGER.error(
                "Error disabling PoE on port %d (%s): %s",
                self._port_idx,
                self._port_name,
                err,
            )
            raise
