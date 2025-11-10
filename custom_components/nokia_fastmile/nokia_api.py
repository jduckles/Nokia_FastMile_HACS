"""Nokia FastMile API client."""
import logging
from typing import Any, Dict, Optional

import requests
from requests.auth import HTTPBasicAuth

_LOGGER = logging.getLogger(__name__)


class NokiaFastMileAPI:
    """API client for Nokia FastMile 5G receiver."""

    def __init__(self, host: str, username: str, password: str):
        """Initialize the API client."""
        self.host = host
        self.auth = HTTPBasicAuth(username, password)
        self.base_url = f"http://{host}"
        self.session = requests.Session()
        self.session.auth = self.auth

    def _make_request(
        self, endpoint: str, method: str = "GET", data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Make an HTTP request to the device."""
        url = f"{self.base_url}/{endpoint}"
        try:
            if method == "POST":
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                response = self.session.post(url, data=data, headers=headers, timeout=10)
            else:
                response = self.session.get(url, timeout=10)

            response.raise_for_status()

            # Try to parse as JSON
            try:
                return response.json()
            except ValueError:
                # If not JSON, return the text
                return {"raw_response": response.text}

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error accessing %s: %s", endpoint, err)
            return None

    def get_prelogin_status(self) -> Optional[Dict]:
        """Get prelogin status - contains all device information."""
        return self._make_request("prelogin_status_web_app.cgi", "GET")

    def get_device_info(self) -> Optional[Dict]:
        """Get device information including uptime."""
        status = self.get_prelogin_status()
        if not status or "device_info" not in status or len(status["device_info"]) == 0:
            return None
        return status["device_info"][0]

    def get_cellular_stats(self) -> Optional[Dict]:
        """Get 5G and LTE cellular statistics."""
        status = self.get_prelogin_status()
        if not status:
            return None

        result = {}

        # Extract 5G stats
        if "cell_5G_stats_cfg" in status and len(status["cell_5G_stats_cfg"]) > 0:
            result["5g"] = status["cell_5G_stats_cfg"][0].get("stat", {})

        # Extract LTE/4G stats
        if "cell_LTE_stats_cfg" in status and len(status["cell_LTE_stats_cfg"]) > 0:
            result["lte"] = status["cell_LTE_stats_cfg"][0].get("stat", {})

        # Extract WAN mode
        if "WAN" in status and len(status["WAN"]) > 0:
            result["wan_mode"] = status["WAN"][0]

        return result

    def get_wan_info(self) -> Optional[Dict]:
        """Get WAN connection information."""
        status = self.get_prelogin_status()
        if not status:
            return None

        result = {}

        if "wan_conns" in status and len(status["wan_conns"]) > 0:
            wan_conn = status["wan_conns"][0]
            if "ipConns" in wan_conn and len(wan_conn["ipConns"]) > 0:
                result["connection"] = wan_conn["ipConns"][0]

        if "wan_ip_status" in status and len(status["wan_ip_status"]) > 0:
            result["status"] = status["wan_ip_status"][0]

        return result if result else None

    def get_connected_devices(self) -> Optional[list]:
        """Get list of connected devices."""
        status = self.get_prelogin_status()
        if not status:
            return None

        devices = []

        # Get active devices
        if "device_cfg" in status:
            devices.extend(status["device_cfg"])

        return devices if devices else None

    def get_all_status(self) -> Dict[str, Any]:
        """Get all available status information."""
        return {
            "device_info": self.get_device_info(),
            "wan_info": self.get_wan_info(),
            "cellular_stats": self.get_cellular_stats(),
            "connected_devices": self.get_connected_devices(),
        }

    def reboot_device(self) -> bool:
        """Reboot the Nokia FastMile device."""
        try:
            url = f"{self.base_url}/reboot_web_app.cgi"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {"TODO_REBOOT": "1"}

            response = self.session.post(url, data=data, headers=headers, timeout=10)

            # Check if request was accepted
            if response.status_code in [200, 202, 204, 500]:
                return True
            return False
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error sending reboot command: %s", err)
            return False
