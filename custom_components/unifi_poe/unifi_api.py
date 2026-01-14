"""UniFi Controller API client for PoE control."""
import logging
import asyncio
from typing import Any
import aiohttp
import ssl

_LOGGER = logging.getLogger(__name__)


class UniFiAPIError(Exception):
    """Exception for UniFi API errors."""
    pass


class UniFiAPI:
    """UniFi Controller API client."""

    def __init__(
        self,
        host: str,
        api_key: str,
        port: int = 443,
        site: str = "default",
        verify_ssl: bool = False,
    ) -> None:
        """Initialize the UniFi API client."""
        self.host = host
        self.api_key = api_key
        self.port = port
        self.site = site
        self.verify_ssl = verify_ssl
        self._session: aiohttp.ClientSession | None = None
        self._devices_cache: dict[str, Any] = {}

    @property
    def base_url(self) -> str:
        """Get the base URL for API requests."""
        return f"https://{self.host}:{self.port}/proxy/network/api"

    @property
    def site_url(self) -> str:
        """Get the site-specific URL for API requests."""
        return f"{self.base_url}/s/{self.site}"

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        return {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            if self.verify_ssl:
                connector = aiohttp.TCPConnector()
            else:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                connector = aiohttp.TCPConnector(ssl=ssl_context)

            self._session = aiohttp.ClientSession(
                connector=connector,
                headers=self._get_headers(),
            )
        return self._session

    async def close(self) -> None:
        """Close the API session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
    ) -> dict[str, Any]:
        """Make an API request."""
        session = await self._get_session()
        url = f"{self.site_url}/{endpoint}"

        _LOGGER.debug("Making %s request to %s", method, url)

        try:
            async with session.request(method, url, json=data) as response:
                response_text = await response.text()
                _LOGGER.debug("Response status: %s, body: %s", response.status, response_text[:500])

                if response.status == 401:
                    raise UniFiAPIError("Authentication failed - invalid API key")
                elif response.status == 403:
                    raise UniFiAPIError("Access forbidden - check API key permissions")
                elif response.status >= 400:
                    raise UniFiAPIError(f"API error: {response.status} - {response_text}")

                try:
                    result = await response.json()
                    return result
                except Exception:
                    return {"raw": response_text}

        except aiohttp.ClientError as err:
            raise UniFiAPIError(f"Connection error: {err}") from err

    async def get_devices(self) -> list[dict[str, Any]]:
        """Get all devices from the controller."""
        result = await self._request("GET", "stat/device")
        devices = result.get("data", [])

        # Cache devices by MAC
        for device in devices:
            mac = device.get("mac", "").lower()
            if mac:
                self._devices_cache[mac] = device

        return devices

    async def get_switches(self) -> list[dict[str, Any]]:
        """Get all switches from the controller."""
        devices = await self.get_devices()
        return [d for d in devices if d.get("type") == "usw"]

    async def get_device_by_mac(self, mac: str) -> dict[str, Any] | None:
        """Get a device by MAC address."""
        mac = mac.lower().replace("-", ":").replace("_", ":")

        # Check cache first
        if mac in self._devices_cache:
            return self._devices_cache[mac]

        # Fetch fresh data
        await self.get_devices()
        return self._devices_cache.get(mac)

    async def get_port_table(self, device_mac: str) -> list[dict[str, Any]]:
        """Get port table for a specific device."""
        device = await self.get_device_by_mac(device_mac)
        if not device:
            raise UniFiAPIError(f"Device not found: {device_mac}")

        return device.get("port_table", [])

    async def get_port_overrides(self, device_mac: str) -> list[dict[str, Any]]:
        """Get port overrides for a specific device."""
        device = await self.get_device_by_mac(device_mac)
        if not device:
            raise UniFiAPIError(f"Device not found: {device_mac}")

        return device.get("port_overrides", [])

    async def set_port_poe_mode(
        self,
        device_mac: str,
        port_idx: int,
        poe_mode: str,
    ) -> bool:
        """Set PoE mode for a specific port."""
        # Clear cache to get fresh data
        mac_normalized = device_mac.lower().replace("-", ":").replace("_", ":")
        self._devices_cache.pop(mac_normalized, None)

        device = await self.get_device_by_mac(device_mac)
        if not device:
            raise UniFiAPIError(f"Device not found: {device_mac}")

        device_id = device.get("_id")
        if not device_id:
            raise UniFiAPIError("Device ID not found")

        # Get default network ID from device
        default_network_id = device.get("last_connection_network_id", "")

        # Get existing port overrides (make deep copy to avoid mutation issues)
        port_overrides = []
        for override in device.get("port_overrides", []):
            port_overrides.append(dict(override))

        # Find or create override for this port
        port_override = None
        for override in port_overrides:
            if override.get("port_idx") == port_idx:
                port_override = override
                break

        if port_override is None:
            # Create new override with required fields
            port_override = {
                "port_idx": port_idx,
                "native_networkconf_id": default_network_id,
                "forward": "all",
            }
            port_overrides.append(port_override)

        # Update PoE mode
        port_override["poe_mode"] = poe_mode

        # Send update
        data = {"port_overrides": port_overrides}

        try:
            result = await self._request("PUT", f"rest/device/{device_id}", data)
            _LOGGER.debug("Set PoE mode result: %s", result)
            # Clear cache after successful update
            self._devices_cache.pop(mac_normalized, None)
            return True
        except UniFiAPIError as err:
            _LOGGER.error("Failed to set PoE mode: %s", err)
            return False

    async def restart_poe_port(
        self,
        device_mac: str,
        port_idx: int,
        delay: float = 5.0,
    ) -> bool:
        """Restart PoE on a specific port using power-cycle command."""
        _LOGGER.info(
            "Power cycling PoE on port %d of device %s",
            port_idx,
            device_mac,
        )

        # Normalize MAC address
        mac_normalized = device_mac.lower().replace("-", ":").replace("_", ":")

        # Try the direct power-cycle command first (faster, ~2 second cycle)
        try:
            data = {
                "cmd": "power-cycle",
                "mac": mac_normalized,
                "port_idx": port_idx,
            }
            result = await self._request("POST", "cmd/devmgr", data)
            _LOGGER.debug("Power cycle result: %s", result)

            if result.get("meta", {}).get("rc") == "ok":
                _LOGGER.info("Successfully power cycled PoE on port %d", port_idx)
                return True
            else:
                _LOGGER.warning(
                    "Power cycle command returned: %s, falling back to manual cycle",
                    result.get("meta", {}).get("msg", "unknown")
                )
        except UniFiAPIError as err:
            _LOGGER.warning("Power cycle command failed: %s, falling back to manual cycle", err)

        # Fallback: Manual off/on cycle
        _LOGGER.info("Using manual PoE off/on cycle for port %d", port_idx)

        # Get current PoE mode
        self._devices_cache.pop(mac_normalized, None)
        device = await self.get_device_by_mac(device_mac)
        if not device:
            raise UniFiAPIError(f"Device not found: {device_mac}")

        # Find current PoE mode from port table
        port_table = device.get("port_table", [])
        current_mode = "auto"  # Default

        for port in port_table:
            if port.get("port_idx") == port_idx:
                current_mode = port.get("poe_mode", "auto")
                break

        # Turn off PoE
        _LOGGER.info("Disabling PoE on port %d", port_idx)
        success = await self.set_port_poe_mode(device_mac, port_idx, "off")
        if not success:
            _LOGGER.error("Failed to disable PoE on port %d", port_idx)
            return False

        # Wait
        _LOGGER.debug("Waiting %s seconds before re-enabling PoE", delay)
        await asyncio.sleep(delay)

        # Turn PoE back on
        _LOGGER.info("Re-enabling PoE on port %d with mode: %s", port_idx, current_mode)
        success = await self.set_port_poe_mode(device_mac, port_idx, current_mode)
        if not success:
            _LOGGER.error("Failed to re-enable PoE on port %d", port_idx)
            return False

        _LOGGER.info("Successfully restarted PoE on port %d", port_idx)
        return True

    async def get_poe_devices(self) -> list[dict[str, Any]]:
        """Get all devices that have PoE-capable ports."""
        devices = await self.get_devices()
        poe_devices = []

        for device in devices:
            port_table = device.get("port_table", [])
            poe_ports = [p for p in port_table if p.get("port_poe", False)]
            if poe_ports:
                poe_devices.append({
                    "device": device,
                    "poe_ports": poe_ports,
                })

        return poe_devices

    async def test_connection(self) -> dict[str, Any]:
        """Test connection to the controller."""
        try:
            devices = await self.get_devices()

            # Find all devices with PoE-capable ports
            poe_devices = []
            for device in devices:
                port_table = device.get("port_table", [])
                poe_ports = [p for p in port_table if p.get("port_poe", False)]
                if poe_ports:
                    poe_devices.append({
                        "name": device.get("name", "Unknown"),
                        "mac": device.get("mac", ""),
                        "model": device.get("model", "Unknown"),
                        "type": device.get("type", "unknown"),
                        "poe_ports": [
                            {
                                "port_idx": p.get("port_idx"),
                                "name": p.get("name", f"Port {p.get('port_idx')}"),
                                "poe_mode": p.get("poe_mode", "N/A"),
                                "poe_power": p.get("poe_power", "0"),
                            }
                            for p in poe_ports
                        ],
                    })

            return {
                "success": True,
                "device_count": len(devices),
                "poe_device_count": len(poe_devices),
                "poe_devices": poe_devices,
            }
        except UniFiAPIError as err:
            return {"success": False, "error": str(err)}
        except Exception as err:
            return {"success": False, "error": f"Unexpected error: {err}"}
