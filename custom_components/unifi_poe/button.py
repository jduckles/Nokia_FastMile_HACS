"""Button platform for UniFi PoE Control."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_PORT_NAME, CONF_PORT_NUMBER, CONF_SWITCH_MAC
from .unifi_api import UniFiAPI

_LOGGER = logging.getLogger(__name__)


BUTTON_TYPES = (
    ButtonEntityDescription(
        key="restart_poe",
        name="Restart PoE",
        icon="mdi:restart",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up UniFi PoE buttons."""
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    coordinator = data["coordinator"]

    entities = []
    for description in BUTTON_TYPES:
        entities.append(
            UniFiPoEButton(
                coordinator=coordinator,
                api=api,
                entry=entry,
                description=description,
            )
        )

    async_add_entities(entities)


class UniFiPoEButton(CoordinatorEntity, ButtonEntity):
    """Representation of a UniFi PoE restart button."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        api: UniFiAPI,
        entry: ConfigEntry,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.api = api
        self.entry = entry
        self.entity_description = description

        self._switch_mac = entry.data[CONF_SWITCH_MAC]
        self._port_idx = int(entry.data[CONF_PORT_NUMBER])
        self._port_name = entry.data.get(CONF_PORT_NAME, f"Port {self._port_idx}")

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

    async def async_press(self) -> None:
        """Handle button press - restart PoE on port."""
        _LOGGER.info(
            "Restarting PoE on port %d (%s)",
            self._port_idx,
            self._port_name,
        )

        try:
            success = await self.api.restart_poe_port(
                device_mac=self._switch_mac,
                port_idx=self._port_idx,
                delay=5.0,
            )

            if success:
                _LOGGER.info(
                    "Successfully restarted PoE on port %d (%s)",
                    self._port_idx,
                    self._port_name,
                )
            else:
                _LOGGER.error(
                    "Failed to restart PoE on port %d (%s)",
                    self._port_idx,
                    self._port_name,
                )
        except Exception as err:
            _LOGGER.error(
                "Error restarting PoE on port %d (%s): %s",
                self._port_idx,
                self._port_name,
                err,
            )
            raise
