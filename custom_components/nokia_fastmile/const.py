"""Constants for the Nokia FastMile 5G integration."""

DOMAIN = "nokia_fastmile"

# Configuration
CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Default values
DEFAULT_HOST = "192.168.192.1"
DEFAULT_USERNAME = "admin"
DEFAULT_SCAN_INTERVAL = 60

# API endpoints
ENDPOINT_PRELOGIN_STATUS = "prelogin_status_web_app.cgi"
ENDPOINT_REBOOT = "reboot_web_app.cgi"

# Platforms
PLATFORMS = ["sensor", "button"]

# Attributes
ATTR_DEVICE_INFO = "device_info"
ATTR_WAN_INFO = "wan_info"
ATTR_CELLULAR_STATS = "cellular_stats"
ATTR_CONNECTED_DEVICES = "connected_devices"
