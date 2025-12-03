#!/usr/bin/env python3
"""
Nokia FastMile 5G Receiver Reboot Script
Sends a reboot command to the Nokia FastMile device
"""

import requests
import sys
import time


def login_and_get_session(host: str, username: str, password: str) -> requests.Session:
    """
    Login to the device and return a session with cookies.

    Args:
        host: IP address of the Nokia FastMile device
        username: Admin username
        password: Admin password

    Returns:
        requests.Session with authentication cookies
    """
    session = requests.Session()
    base_url = f"http://{host}"

    # Attempt login to get session cookie
    login_url = f"{base_url}/login_web_app.cgi"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json, text/plain, */*",
    }
    login_data = {
        "name": username,
        "pswd": password,
    }

    try:
        response = session.post(login_url, data=login_data, headers=headers, timeout=10)
        if response.status_code == 200:
            print("Login successful")
        else:
            print(f"Login returned status {response.status_code}, continuing anyway...")
    except requests.exceptions.RequestException as e:
        print(f"Login attempt failed: {e}, continuing anyway...")

    return session


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
        # Get authenticated session
        session = login_and_get_session(host, username, password)
        base_url = f"http://{host}"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json, text/plain, */*",
            "Origin": base_url,
            "Referer": f"{base_url}/",
        }

        # Method 1: Try reboot_web_app.cgi (matches web UI)
        url = f"{base_url}/reboot_web_app.cgi"
        data = {"Page": "REBOOT", "Action": "Reboot"}

        print("Sending reboot command via reboot_web_app.cgi...")
        response = session.post(url, data=data, headers=headers, timeout=30)

        if response.status_code == 200:
            response_text = response.text
            if 'encrypted=1' in response_text:
                print("Reboot command accepted (encrypted response received)")
                print("The device will reboot shortly and be unavailable for 1-2 minutes.")
                return True
            print("Reboot command sent successfully!")
            print("The device will reboot shortly and be unavailable for 1-2 minutes.")
            return True

        # Method 2: Try command_web_app.cgi
        print(f"First attempt got status {response.status_code}, trying command endpoint...")
        url = f"{base_url}/command_web_app.cgi"
        data = {"action": "reboot"}
        response = session.post(url, data=data, headers=headers, timeout=30)

        if response.status_code in [200, 202, 204]:
            print("Reboot command sent successfully via command endpoint!")
            print("The device will reboot shortly and be unavailable for 1-2 minutes.")
            return True

        # Method 3: Try maintenance endpoint
        print("Trying maintenance endpoint...")
        url = f"{base_url}/maintenance_web_app.cgi"
        data = {"action": "reboot", "type": "system"}
        response = session.post(url, data=data, headers=headers, timeout=30)

        if response.status_code in [200, 202, 204]:
            print("Reboot command sent via maintenance endpoint!")
            print("The device will reboot shortly and be unavailable for 1-2 minutes.")
            return True

        print(f"All reboot attempts failed. Last status code: {response.status_code}")
        return False

    except requests.exceptions.Timeout:
        print("Request timed out - the device may be rebooting already.")
        return True
    except requests.exceptions.ConnectionError:
        print("Connection lost - the device may be rebooting.")
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
