"""Constants for the UniFi PoE Control integration."""

DOMAIN = "unifi_poe"

# Configuration keys
CONF_API_KEY = "api_key"
CONF_PORT_NAME = "port_name"
CONF_PORT_NUMBER = "port_number"
CONF_SITE = "site"
CONF_SWITCH_MAC = "switch_mac"

# Defaults
DEFAULT_PORT = 443
DEFAULT_SITE = "default"
DEFAULT_SCAN_INTERVAL = 30

# Platforms
PLATFORMS = ["button", "switch"]

# PoE modes
POE_MODE_OFF = "off"
POE_MODE_AUTO = "auto"
POE_MODE_PASV24 = "pasv24"
POE_MODE_PASSTHROUGH = "passthrough"
