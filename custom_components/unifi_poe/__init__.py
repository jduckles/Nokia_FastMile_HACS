"""UniFi PoE Control integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_SITE,
    CONF_SWITCH_MAC,
    CONF_PORT_NUMBER,
    DEFAULT_PORT,
    DEFAULT_SITE,
    DEFAULT_SCAN_INTERVAL,
)
from .unifi_api import UniFiAPI, UniFiAPIError

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BUTTON, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up UniFi PoE Control from a config entry."""
    _LOGGER.debug("Setting up UniFi PoE Control integration")

    # Create API client
    api = UniFiAPI(
        host=entry.data[CONF_HOST],
        api_key=entry.data[CONF_API_KEY],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        site=entry.data.get(CONF_SITE, DEFAULT_SITE),
    )

    # Test connection
    try:
        result = await api.test_connection()
        if not result.get("success"):
            _LOGGER.error("Failed to connect to UniFi controller: %s", result.get("error"))
            await api.close()
            return False
    except Exception as err:
        _LOGGER.error("Failed to connect to UniFi controller: %s", err)
        await api.close()
        return False

    _LOGGER.info("Successfully connected to UniFi controller at %s", entry.data[CONF_HOST])

    # Create coordinator for periodic updates
    async def async_update_data():
        """Fetch data from API."""
        try:
            device_mac = entry.data[CONF_SWITCH_MAC]
            port_idx = int(entry.data[CONF_PORT_NUMBER])

            device = await api.get_device_by_mac(device_mac)
            if not device:
                raise UpdateFailed(f"Device not found: {device_mac}")

            # Get port info
            port_table = device.get("port_table", [])
            port_info = None
            for port in port_table:
                if port.get("port_idx") == port_idx:
                    port_info = port
                    break

            return {
                "device": device,
                "port": port_info,
                "port_idx": port_idx,
            }
        except UniFiAPIError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store API and coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading UniFi PoE Control integration")

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Close API session
        data = hass.data[DOMAIN].pop(entry.entry_id)
        api = data.get("api")
        if api:
            await api.close()

    return unload_ok
