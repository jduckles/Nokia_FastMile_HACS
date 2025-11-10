#!/usr/bin/env python3
"""
Nokia FastMile 5G Receiver Reboot Script
Sends a reboot command to the Nokia FastMile device
"""

import requests
from requests.auth import HTTPBasicAuth
import sys
import time

def reboot_device(host: str = "192.168.192.1", username: str = "admin", password: str = ""):
    """
    Reboot the Nokia FastMile device

    Args:
        host: IP address of the Nokia FastMile device
        username: Admin username
        password: Admin password

    Returns:
        True if reboot command was sent successfully, False otherwise
    """
    print(f"Attempting to reboot Nokia FastMile at {host}...")

    try:
        url = f"http://{host}/command_web_app.cgi"
        auth = HTTPBasicAuth(username, password)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Try the command endpoint first
        data = {"action": "reboot"}

        print("Sending reboot command...")
        response = requests.post(url, data=data, headers=headers, auth=auth, timeout=10)

        # Check if request was accepted
        if response.status_code in [200, 202, 204]:
            print("Reboot command sent successfully!")
            print("The device will reboot in a few seconds and will be unavailable for approximately 1-2 minutes.")
            return True
        else:
            # Try alternative endpoint
            print(f"First attempt got status {response.status_code}, trying alternative method...")
            url = f"http://{host}/reboot_web_app.cgi"
            data = {"Page": "REBOOT", "Action": "Reboot"}
            response = requests.post(url, data=data, headers=headers, auth=auth, timeout=10)

            if response.status_code in [200, 202, 204, 500]:  # 500 might indicate device is rebooting
                print("Reboot command sent successfully!")
                print("The device will reboot in a few seconds and will be unavailable for approximately 1-2 minutes.")
                return True
            else:
                print(f"Failed to send reboot command. Status code: {response.status_code}")
                return False

    except requests.exceptions.Timeout:
        print("Request timed out - the device may be rebooting already.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending reboot command: {e}")
        return False


def main():
    """Main function"""
    # Configuration
    HOST = "192.168.192.1"
    USERNAME = "admin"
    PASSWORD = "eca67293bd"

    print("=" * 50)
    print("Nokia FastMile 5G Receiver Reboot Utility")
    print("=" * 50)
    print()

    # Confirm reboot
    response = input("Are you sure you want to reboot the device? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Reboot cancelled.")
        sys.exit(0)

    print()

    # Perform reboot
    success = reboot_device(HOST, USERNAME, PASSWORD)

    if success:
        print()
        print("=" * 50)
        print("Reboot initiated successfully!")
        print("=" * 50)
        print()
        print("The device is now rebooting. Please wait 1-2 minutes before")
        print("attempting to reconnect.")
        sys.exit(0)
    else:
        print()
        print("=" * 50)
        print("Failed to reboot device!")
        print("=" * 50)
        print()
        print("Please check:")
        print("1. Device IP address is correct")
        print("2. Username and password are correct")
        print("3. Device is accessible on the network")
        sys.exit(1)


if __name__ == "__main__":
    main()
