"""Support for Nokia FastMile 5G sensors."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    SIGNAL_STRENGTH_DECIBELS,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class NokiaFastMileSensorEntityDescription(SensorEntityDescription):
    """Describes Nokia FastMile sensor entity."""

    value_fn: Callable[[dict], any] | None = None


def format_uptime(seconds: int) -> str:
    """Convert seconds to human-readable format."""
    if not seconds:
        return "Unknown"
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m"


SENSOR_TYPES: tuple[NokiaFastMileSensorEntityDescription, ...] = (
    # Device sensors
    NokiaFastMileSensorEntityDescription(
        key="model",
        name="Model",
        icon="mdi:router-wireless",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("device_info", {}).get("ModelName") if data.get("device_info") else None,
    ),
    NokiaFastMileSensorEntityDescription(
        key="firmware",
        name="Firmware Version",
        icon="mdi:package-variant",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("device_info", {}).get("SoftwareVersion") if data.get("device_info") else None,
    ),
    NokiaFastMileSensorEntityDescription(
        key="serial",
        name="Serial Number",
        icon="mdi:numeric",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("device_info", {}).get("SerialNumber") if data.get("device_info") else None,
    ),
    NokiaFastMileSensorEntityDescription(
        key="uptime",
        name="Uptime",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:clock-outline",
        value_fn=lambda data: data.get("device_info", {}).get("UpTime") if data.get("device_info") else None,
    ),
    NokiaFastMileSensorEntityDescription(
        key="uptime_formatted",
        name="Uptime (Formatted)",
        icon="mdi:clock-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: format_uptime(data.get("device_info", {}).get("UpTime", 0)) if data.get("device_info") else None,
    ),
    # WAN sensors
    NokiaFastMileSensorEntityDescription(
        key="wan_status",
        name="WAN Status",
        icon="mdi:check-network",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("wan_info", {}).get("connection", {}).get("ConnectionStatus") if data.get("wan_info") and data.get("wan_info").get("connection") else None,
    ),
    NokiaFastMileSensorEntityDescription(
        key="external_ip",
        name="External IP Address",
        icon="mdi:ip-network",
        value_fn=lambda data: data.get("wan_info", {}).get("connection", {}).get("ExternalIPAddress") if data.get("wan_info") and data.get("wan_info").get("connection") else None,
    ),
    NokiaFastMileSensorEntityDescription(
        key="gateway",
        name="Gateway",
        icon="mdi:router",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("wan_info", {}).get("connection", {}).get("DefaultGateway") if data.get("wan_info") and data.get("wan_info").get("connection") else None,
    ),
    # 5G sensors
    NokiaFastMileSensorEntityDescription(
        key="5g_rsrp",
        name="5G RSRP",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:signal-cellular-3",
        value_fn=lambda data: data.get("cellular_stats", {}).get("5g", {}).get("RSRPCurrent") if data.get("cellular_stats") and data.get("cellular_stats").get("5g") else None,
    ),
    NokiaFastMileSensorEntityDescription(
        key="5g_rsrq",
        name="5G RSRQ",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:signal-cellular-3",
        value_fn=lambda data: data.get("cellular_stats", {}).get("5g", {}).get("RSRQCurrent") if data.get("cellular_stats") and data.get("cellular_stats").get("5g") else None,
    ),
    NokiaFastMileSensorEntityDescription(
        key="5g_snr",
        name="5G SNR",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:signal-variant",
        value_fn=lambda data: data.get("cellular_stats", {}).get("5g", {}).get("SNRCurrent") if data.get("cellular_stats") and data.get("cellular_stats").get("5g") else None,
    ),
    NokiaFastMileSensorEntityDescription(
        key="5g_signal_strength",
        name="5G Signal Strength",
        native_unit_of_measurement="/5",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:signal",
        value_fn=lambda data: data.get("cellular_stats", {}).get("5g", {}).get("SignalStrengthLevel") if data.get("cellular_stats") and data.get("cellular_stats").get("5g") else None,
    ),
    # LTE sensors
    NokiaFastMileSensorEntityDescription(
        key="lte_rssi",
        name="LTE RSSI",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:signal-4g",
        value_fn=lambda data: data.get("cellular_stats", {}).get("lte", {}).get("RSSICurrent") if data.get("cellular_stats") and data.get("cellular_stats").get("lte") else None,
    ),
    NokiaFastMileSensorEntityDescription(
        key="lte_rsrp",
        name="LTE RSRP",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:signal-4g",
        value_fn=lambda data: data.get("cellular_stats", {}).get("lte", {}).get("RSRPCurrent") if data.get("cellular_stats") and data.get("cellular_stats").get("lte") else None,
    ),
    NokiaFastMileSensorEntityDescription(
        key="lte_snr",
        name="LTE SNR",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:signal-variant",
        value_fn=lambda data: data.get("cellular_stats", {}).get("lte", {}).get("SNRCurrent") if data.get("cellular_stats") and data.get("cellular_stats").get("lte") else None,
    ),
    # Device count
    NokiaFastMileSensorEntityDescription(
        key="connected_devices",
        name="Connected Devices",
        native_unit_of_measurement="devices",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:devices",
        value_fn=lambda data: len(data.get("connected_devices", [])) if data.get("connected_devices") else 0,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Nokia FastMile sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        NokiaFastMileSensor(coordinator, description, entry)
        for description in SENSOR_TYPES
    ]

    async_add_entities(entities)


class NokiaFastMileSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Nokia FastMile sensor."""

    entity_description: NokiaFastMileSensorEntityDescription

    def __init__(self, coordinator, description: NokiaFastMileSensorEntityDescription, entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Nokia FastMile ({entry.data.get(CONF_HOST)})",
            "manufacturer": "Nokia",
            "model": coordinator.data.get("device_info", {}).get("ModelName", "FastMile 5G Receiver") if coordinator.data.get("device_info") else "FastMile 5G Receiver",
            "sw_version": coordinator.data.get("device_info", {}).get("SoftwareVersion") if coordinator.data.get("device_info") else None,
        }

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.native_value is not None
