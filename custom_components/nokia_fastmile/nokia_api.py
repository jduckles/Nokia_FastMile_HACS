"""Nokia FastMile API client."""
import base64
import hashlib
import json
import logging
import os
import re
from typing import Any, Dict, Optional

import requests
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

_LOGGER = logging.getLogger(__name__)


class NokiaFastMileAPI:
    """API client for Nokia FastMile 5G receiver."""

    def __init__(self, host: str, username: str, password: str):
        """Initialize the API client."""
        self.host = host
        self.username = username
        self.password = password
        self.base_url = f"http://{host}"
        self.session = requests.Session()
        self._session_id: Optional[str] = None
        self._nonce: Optional[str] = None
        self._server_pubkey: Optional[str] = None
        self._shared_secret: Optional[bytes] = None

    def _generate_key_pair(self) -> tuple[bytes, bytes]:
        """Generate a simple key pair for encryption."""
        # Generate 32 random bytes for our secret
        private_key = os.urandom(32)
        # Use SHA256 hash as public key representation
        public_key = hashlib.sha256(private_key).digest()
        return private_key, public_key

    def _derive_shared_secret(self, private_key: bytes, server_pubkey: str) -> bytes:
        """Derive shared secret from server public key."""
        server_key_bytes = base64.b64decode(server_pubkey)
        # Simple key derivation using HKDF-like approach
        combined = private_key + server_key_bytes
        return hashlib.sha256(combined).digest()

    def _encrypt_payload(self, data: dict) -> tuple[str, str]:
        """Encrypt payload using AES-256-GCM."""
        if not self._shared_secret:
            raise ValueError("No shared secret available")

        # Generate random IV (12 bytes for GCM)
        iv = os.urandom(12)

        # Create cipher
        cipher = Cipher(
            algorithms.AES(self._shared_secret),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # Encrypt the JSON payload
        plaintext = json.dumps(data).encode('utf-8')
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Combine IV + ciphertext + tag
        encrypted = iv + ciphertext + encryptor.tag

        # Return base64 encoded ciphertext and key info
        ct = base64.urlsafe_b64encode(encrypted).decode('utf-8').rstrip('=')
        ck = base64.urlsafe_b64encode(self._shared_secret).decode('utf-8').rstrip('=')

        return ct, ck

    def _decrypt_response(self, ct: str, ck: str) -> Optional[dict]:
        """Decrypt response payload."""
        try:
            # Pad base64 if needed
            ct_padded = ct + '=' * (4 - len(ct) % 4) if len(ct) % 4 else ct
            ck_padded = ck + '=' * (4 - len(ck) % 4) if len(ck) % 4 else ck

            # Decode
            encrypted = base64.urlsafe_b64decode(ct_padded)
            key = base64.urlsafe_b64decode(ck_padded)[:32]  # Use first 32 bytes

            # Extract IV (first 12 bytes), ciphertext, and tag (last 16 bytes)
            iv = encrypted[:12]
            tag = encrypted[-16:]
            ciphertext = encrypted[12:-16]

            # Decrypt
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            return json.loads(plaintext.decode('utf-8'))
        except Exception as err:
            _LOGGER.debug("Failed to decrypt response: %s", err)
            return None

    def _parse_encrypted_response(self, response_text: str) -> Optional[dict]:
        """Parse and decrypt an encrypted response."""
        # Parse the response format: encrypted=1&ct=...&ck=...
        if 'encrypted=1' not in response_text:
            return None

        ct_match = re.search(r'ct=([^&\s]+)', response_text)
        ck_match = re.search(r'ck=([^&\s.]+)', response_text)

        if ct_match and ck_match:
            return self._decrypt_response(ct_match.group(1), ck_match.group(1))
        return None

    def _login(self) -> bool:
        """Authenticate and get session credentials."""
        try:
            # Step 1: Get initial nonce/challenge from login page
            login_url = f"{self.base_url}/login_web_app.cgi"

            # Generate our key pair
            private_key, public_key = self._generate_key_pair()
            public_key_b64 = base64.urlsafe_b64encode(public_key).decode('utf-8').rstrip('=')

            # Send login request
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json, text/plain, */*",
            }

            login_data = {
                "name": self.username,
                "pswd": self.password,
                "pubkey": public_key_b64,
            }

            response = self.session.post(
                login_url,
                data=login_data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                # Try to extract session ID from cookies
                if 'sid' in self.session.cookies:
                    self._session_id = self.session.cookies['sid']
                    _LOGGER.debug("Login successful, session ID obtained")

                    # Try to get server public key from response
                    try:
                        resp_data = response.json()
                        if 'pubkey' in resp_data:
                            self._server_pubkey = resp_data['pubkey']
                            self._shared_secret = self._derive_shared_secret(
                                private_key, self._server_pubkey
                            )
                    except (ValueError, KeyError):
                        # Use password-derived key as fallback
                        self._shared_secret = hashlib.sha256(
                            self.password.encode('utf-8')
                        ).digest()

                    return True

                # Check for session ID in response body
                try:
                    resp_data = response.json()
                    if 'sid' in resp_data:
                        self._session_id = resp_data['sid']
                        self.session.cookies.set('sid', self._session_id)
                        _LOGGER.debug("Login successful, session ID from response")
                        return True
                except ValueError:
                    pass

                # Even without explicit session, cookies might work
                _LOGGER.debug("Login returned 200, proceeding without explicit session")
                return True

            _LOGGER.error("Login failed with status %s", response.status_code)
            return False

        except requests.exceptions.RequestException as err:
            _LOGGER.error("Login request failed: %s", err)
            return False

    def _ensure_session(self) -> bool:
        """Ensure we have an active session."""
        if self._session_id:
            return True
        return self._login()

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
        """Reboot the Nokia FastMile device.

        This method authenticates with the device and sends a reboot command
        via the reboot_web_app.cgi endpoint, matching the web UI behavior.
        """
        try:
            # Ensure we have an active session
            if not self._ensure_session():
                _LOGGER.warning("Failed to establish session, trying without session")

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json, text/plain, */*",
                "Origin": self.base_url,
                "Referer": f"{self.base_url}/",
            }

            # Method 1: Try reboot_web_app.cgi (matches web UI)
            url = f"{self.base_url}/reboot_web_app.cgi"
            data = {"Page": "REBOOT", "Action": "Reboot"}

            _LOGGER.debug("Sending reboot command to %s", url)
            response = self.session.post(url, data=data, headers=headers, timeout=30)

            # Check response - device returns 200 with encrypted confirmation
            if response.status_code == 200:
                response_text = response.text
                _LOGGER.debug("Reboot response: %s", response_text[:200])

                # Check for encrypted success response
                if 'encrypted=1' in response_text:
                    _LOGGER.info("Reboot command accepted (encrypted response)")
                    return True

                # Check for plain success indicators
                if 'success' in response_text.lower() or 'reboot' in response_text.lower():
                    _LOGGER.info("Reboot command sent successfully")
                    return True

                # 200 OK is generally success even without explicit confirmation
                _LOGGER.info("Reboot command sent (HTTP 200)")
                return True

            # Method 2: Try command_web_app.cgi as fallback
            _LOGGER.debug("First attempt got status %s, trying command endpoint", response.status_code)
            url = f"{self.base_url}/command_web_app.cgi"
            data = {"action": "reboot"}
            response = self.session.post(url, data=data, headers=headers, timeout=30)

            if response.status_code in [200, 202, 204]:
                _LOGGER.info("Reboot command sent via command endpoint")
                return True

            # Method 3: Try maintenance endpoint
            _LOGGER.debug("Trying maintenance endpoint")
            url = f"{self.base_url}/maintenance_web_app.cgi"
            data = {"action": "reboot", "type": "system"}
            response = self.session.post(url, data=data, headers=headers, timeout=30)

            if response.status_code in [200, 202, 204]:
                _LOGGER.info("Reboot command sent via maintenance endpoint")
                return True

            _LOGGER.error("All reboot attempts failed. Last status: %s", response.status_code)
            return False

        except requests.exceptions.Timeout:
            # Timeout often means the device is already rebooting
            _LOGGER.info("Request timed out - device may be rebooting")
            return True
        except requests.exceptions.ConnectionError:
            # Connection error might mean device started rebooting
            _LOGGER.info("Connection lost - device may be rebooting")
            return True
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error sending reboot command: %s", err)
            return False
