#!/usr/bin/env python3
"""
Nokia FastMile 5G Receiver Monitoring Script
Queries cellular status information from the Nokia FastMile device
"""

import requests
from requests.auth import HTTPBasicAuth
import json
from typing import Dict, Optional
import sys

class NokiaFastMileMonitor:
    def __init__(self, host: str = "192.168.192.1", username: str = "admin", password: str = ""):
        """
        Initialize the Nokia FastMile Monitor

        Args:
            host: IP address of the Nokia FastMile device
            username: Admin username
            password: Admin password
        """
        self.host = host
        self.auth = HTTPBasicAuth(username, password)
        self.base_url = f"http://{host}"
        self.session = requests.Session()
        self.session.auth = self.auth

    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make an HTTP request to the device

        Args:
            endpoint: The CGI endpoint to call
            method: HTTP method (GET or POST)
            data: Data to send with POST requests

        Returns:
            Response data as dictionary or None if request fails
        """
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
            except json.JSONDecodeError:
                # If not JSON, return the text
                return {"raw_response": response.text}

        except requests.exceptions.RequestException as e:
            print(f"Error accessing {endpoint}: {e}", file=sys.stderr)
            return None

    def get_dashboard_status(self) -> Optional[Dict]:
        """Get dashboard status information"""
        return self._make_request("dashboard_status_web_app.cgi", "POST", {"Page": "", "entry": ""})

    def get_overview_status(self) -> Optional[Dict]:
        """Get overview status information"""
        return self._make_request("overview_status_web_app.cgi", "POST", {"Page": "", "entry": ""})

    def get_cell_management(self) -> Optional[Dict]:
        """Get cell management information (5G/4G cells)"""
        return self._make_request("cell_management_get_web_app.cgi", "POST", {"Page": "", "entry": "0"})

    def get_radio_receiver_status(self) -> Optional[Dict]:
        """Get radio receiver status"""
        return self._make_request("radio_receiver_status_web_app.cgi", "POST", {"Page": "", "entry": ""})

    def get_fastmile_statistics(self) -> Optional[Dict]:
        """Get FastMile statistics"""
        return self._make_request("fastmile_statistics_status_web_app.cgi", "POST", {"Page": "", "entry": ""})

    def get_wan_internet_status(self) -> Optional[Dict]:
        """Get WAN internet status"""
        return self._make_request("wan_internet_status_web_app.cgi", "POST", {"Page": "", "entry": ""})

    def get_device_status(self) -> Optional[Dict]:
        """Get device status"""
        return self._make_request("dashboard_device_status_web_app.cgi", "POST", {"Page": "", "entry": ""})

    def get_prelogin_status(self) -> Optional[Dict]:
        """Get prelogin status - contains cellular and device information"""
        return self._make_request("prelogin_status_web_app.cgi", "GET")

    def get_cellular_stats(self) -> Optional[Dict]:
        """
        Get 5G and LTE cellular statistics

        Returns:
            Dictionary with 5G and LTE stats
        """
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

    def get_device_info(self) -> Optional[Dict]:
        """
        Get device information including model, serial number, firmware version, and uptime

        Returns:
            Dictionary with device information
        """
        status = self.get_prelogin_status()
        if not status or "device_info" not in status or len(status["device_info"]) == 0:
            return None

        return status["device_info"][0]

    def get_wan_info(self) -> Optional[Dict]:
        """
        Get WAN connection information

        Returns:
            Dictionary with WAN connection details
        """
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
        """
        Get list of connected devices

        Returns:
            List of connected devices
        """
        status = self.get_prelogin_status()
        if not status:
            return None

        devices = []

        # Get active devices
        if "device_cfg" in status:
            devices.extend(status["device_cfg"])

        return devices if devices else None

    def get_all_status(self) -> Dict:
        """
        Get all available status information

        Returns:
            Dictionary with all status information
        """
        return self.get_prelogin_status()

    def reboot_device(self) -> bool:
        """
        Reboot the Nokia FastMile device

        Returns:
            True if reboot command was sent successfully, False otherwise
        """
        try:
            url = f"{self.base_url}/reboot_web_app.cgi"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {"TODO_REBOOT": "1"}

            response = self.session.post(url, data=data, headers=headers, timeout=10)

            # Check if request was accepted (device may return various status codes when rebooting)
            if response.status_code in [200, 202, 204]:
                return True
            return False
        except requests.exceptions.RequestException as e:
            print(f"Error sending reboot command: {e}", file=sys.stderr)
            return False


def format_uptime(seconds: int) -> str:
    """Convert seconds to human-readable format"""
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"


def main():
    """Main function to demonstrate usage"""
    # Configuration
    HOST = "192.168.192.1"
    USERNAME = "admin"
    PASSWORD = "eca67293bd"

    print("Nokia FastMile 5G Receiver Monitor")
    print("=" * 50)

    # Initialize monitor
    monitor = NokiaFastMileMonitor(HOST, USERNAME, PASSWORD)

    # Get device information
    print("\nDEVICE INFORMATION:")
    print("-" * 50)
    device_info = monitor.get_device_info()
    if device_info:
        print(f"  Model: {device_info.get('ModelName', 'N/A')}")
        print(f"  Vendor: {device_info.get('Vendor', 'N/A')}")
        print(f"  Serial Number: {device_info.get('SerialNumber', 'N/A')}")
        print(f"  Hardware Version: {device_info.get('HardwareVersion', 'N/A')}")
        print(f"  Software Version: {device_info.get('SoftwareVersion', 'N/A')}")
        uptime_seconds = device_info.get('UpTime', 0)
        print(f"  Uptime: {format_uptime(uptime_seconds)} ({uptime_seconds} seconds)")
    else:
        print("  Failed to retrieve device information")

    # Get WAN information
    print("\nWAN CONNECTION:")
    print("-" * 50)
    wan_info = monitor.get_wan_info()
    if wan_info and "connection" in wan_info:
        conn = wan_info["connection"]
        print(f"  Status: {conn.get('ConnectionStatus', 'N/A')}")
        print(f"  Type: {conn.get('ConnectionType', 'N/A')}")
        print(f"  External IP: {conn.get('ExternalIPAddress', 'N/A')}")
        print(f"  Subnet Mask: {conn.get('SubnetMask', 'N/A')}")
        print(f"  Gateway: {conn.get('DefaultGateway', 'N/A')}")
        print(f"  DNS Servers: {conn.get('DNSServers', 'N/A')}")
        print(f"  NAT Enabled: {'Yes' if conn.get('NATEnabled', 0) == 1 else 'No'}")
    else:
        print("  Failed to retrieve WAN information")

    # Get cellular statistics
    print("\n5G CELLULAR STATS:")
    print("-" * 50)
    cellular_stats = monitor.get_cellular_stats()
    if cellular_stats and "5g" in cellular_stats:
        stats_5g = cellular_stats["5g"]
        print(f"  RSRP: {stats_5g.get('RSRPCurrent', 'N/A')} dBm")
        print(f"  RSRP Strength Index: {stats_5g.get('RSRPStrengthIndexCurrent', 'N/A')}/5")
        print(f"  RSRQ: {stats_5g.get('RSRQCurrent', 'N/A')} dB")
        print(f"  SNR: {stats_5g.get('SNRCurrent', 'N/A')} dB")
        print(f"  Signal Strength Level: {stats_5g.get('SignalStrengthLevel', 'N/A')}/5")
        print(f"  Frequency Range: FR{stats_5g.get('FrequencyRange', 'N/A')}")
        print(f"  Rank Indicator: {stats_5g.get('RankIndicator', 'N/A')}")
    else:
        print("  No 5G stats available")

    print("\nLTE/4G CELLULAR STATS:")
    print("-" * 50)
    if cellular_stats and "lte" in cellular_stats:
        stats_lte = cellular_stats["lte"]
        print(f"  RSSI: {stats_lte.get('RSSICurrent', 'N/A')} dBm")
        print(f"  RSRP: {stats_lte.get('RSRPCurrent', 'N/A')} dBm")
        print(f"  RSRP Strength Index: {stats_lte.get('RSRPStrengthIndexCurrent', 'N/A')}/5")
        print(f"  RSRQ: {stats_lte.get('RSRQCurrent', 'N/A')} dB")
        print(f"  SNR: {stats_lte.get('SNRCurrent', 'N/A')} dB")
        print(f"  Signal Strength Level: {stats_lte.get('SignalStrengthLevel', 'N/A')}/5")
        print(f"  Rank Indicator: {stats_lte.get('RankIndicator', 'N/A')}")
    else:
        print("  No LTE stats available")

    # Get connected devices
    print("\nCONNECTED DEVICES:")
    print("-" * 50)
    devices = monitor.get_connected_devices()
    if devices:
        print(f"  Total Devices: {len(devices)}")
        for i, device in enumerate(devices, 1):
            print(f"\n  Device {i}:")
            print(f"    IP Address: {device.get('IPAddress', 'N/A')}")
            print(f"    MAC Address: {device.get('MACAddress', 'N/A')}")
            print(f"    Interface: {device.get('InterfaceType', 'N/A')}")
            print(f"    Active: {'Yes' if device.get('Active', 0) == 1 else 'No'}")
    else:
        print("  No connected devices found")

    # Output JSON for programmatic use
    print("\n" + "=" * 50)
    print("JSON OUTPUT (for Home Assistant):")
    print("-" * 50)
    output = {
        "device_info": device_info,
        "wan_info": wan_info,
        "cellular_stats": cellular_stats,
        "connected_devices": devices
    }
    print(json.dumps(output, indent=2))

    print("\n" + "=" * 50)
    print("Complete!")
    print("\nFor Home Assistant integration:")
    print("1. Use this script with a command_line sensor")
    print("2. Parse the JSON output to create individual sensors")
    print("3. Use nokia_fastmile_reboot.py to reboot the device")


if __name__ == "__main__":
    main()
