"""Support for Nokia FastMile 5G buttons."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

BUTTON_TYPES: tuple[ButtonEntityDescription, ...] = (
    ButtonEntityDescription(
        key="reboot",
        name="Reboot",
        icon="mdi:restart",
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Nokia FastMile buttons based on a config entry."""
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        NokiaFastMileButton(api, coordinator, description, entry)
        for description in BUTTON_TYPES
    ]

    async_add_entities(entities)


class NokiaFastMileButton(ButtonEntity):
    """Representation of a Nokia FastMile button."""

    def __init__(self, api, coordinator, description: ButtonEntityDescription, entry: ConfigEntry):
        """Initialize the button."""
        self.api = api
        self.coordinator = coordinator
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Nokia FastMile ({entry.data.get('host')})",
            "manufacturer": "Nokia",
            "model": coordinator.data.get("device_info", {}).get("ModelName", "FastMile 5G Receiver") if coordinator.data.get("device_info") else "FastMile 5G Receiver",
            "sw_version": coordinator.data.get("device_info", {}).get("SoftwareVersion") if coordinator.data.get("device_info") else None,
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        if self.entity_description.key == "reboot":
            _LOGGER.info("Rebooting Nokia FastMile device")
            success = await self.hass.async_add_executor_job(self.api.reboot_device)
            if success:
                _LOGGER.info("Reboot command sent successfully")
            else:
                _LOGGER.error("Failed to send reboot command")
