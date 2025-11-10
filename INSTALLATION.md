# Installation Guide

This guide will walk you through installing the Nokia FastMile 5G integration in Home Assistant.

## Prerequisites

- Home Assistant 2023.1.0 or newer
- Nokia FastMile 5G receiver on your network
- Device IP address (usually `192.168.192.1`)
- Admin credentials for your device

## Method 1: HACS Installation (Recommended)

### Step 1: Install HACS

If you haven't already, install [HACS (Home Assistant Community Store)](https://hacs.xyz/docs/setup/download):

1. Navigate to `http://YOUR_HA_IP:8123/hacs/integrations`
2. Follow the HACS installation instructions

### Step 2: Add Custom Repository

1. Open HACS in Home Assistant
2. Click on **Integrations**
3. Click the **⋮** (three dots) menu in the top right corner
4. Select **Custom repositories**
5. Enter the repository URL: `https://github.com/yourusername/nokia-fastmile-ha`
6. Select **Integration** as the category
7. Click **Add**

### Step 3: Install Integration

1. In HACS, search for **Nokia FastMile 5G**
2. Click on the integration
3. Click **Download**
4. Wait for the download to complete
5. Restart Home Assistant

### Step 4: Configure Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Nokia FastMile 5G**
4. Enter your device details:
   - **Device IP Address**: `192.168.192.1` (or your custom IP)
   - **Username**: `admin` (default)
   - **Password**: Your device password
5. Click **Submit**
6. The integration will verify the connection and create all sensors

## Method 2: Manual Installation

### Step 1: Download Files

1. Download the latest release from the [Releases page](https://github.com/yourusername/nokia-fastmile-ha/releases)
2. Extract the ZIP file

### Step 2: Copy Files

1. Copy the `custom_components/nokia_fastmile` folder to your Home Assistant configuration directory:

```
your-config/
├── custom_components/
│   └── nokia_fastmile/
│       ├── __init__.py
│       ├── button.py
│       ├── config_flow.py
│       ├── const.py
│       ├── manifest.json
│       ├── nokia_api.py
│       ├── sensor.py
│       ├── strings.json
│       └── translations/
│           └── en.json
```

**Common Home Assistant paths:**
- Home Assistant OS/Supervised: `/config/`
- Docker: `/path/to/your/homeassistant/config/`
- Core: `~/.homeassistant/`

### Step 3: Restart Home Assistant

Restart Home Assistant completely:
- Via UI: **Settings** → **System** → **Restart**
- Via CLI: `ha core restart`

### Step 4: Configure Integration

Follow Step 4 from Method 1 above.

## Finding Your Device Password

### Default Password

The default password is usually printed on a sticker on your Nokia FastMile device:
- Look for a label that says "Admin Password" or "Web GUI Password"
- It's typically an alphanumeric string (e.g., `eca67293bd`)

### If You Changed the Password

If you changed the password and forgot it:
1. You may need to factory reset your device
2. Consult your device manual for reset instructions
3. After reset, use the default password from the sticker

## Verifying Installation

After configuration, verify the integration is working:

1. Go to **Settings** → **Devices & Services**
2. Find **Nokia FastMile 5G** in the list
3. Click on it to see all entities
4. Check that sensors are showing current values (not "Unavailable")

### Expected Entities

You should see approximately 17 entities:
- 5 device information sensors
- 3 WAN connection sensors
- 4 5G cellular sensors
- 3 LTE cellular sensors
- 1 connected devices sensor
- 1 reboot button

## Configuring Options

After initial setup, you can configure additional options:

1. Go to **Settings** → **Devices & Services**
2. Find **Nokia FastMile 5G**
3. Click **Configure**
4. Adjust settings:
   - **Update interval**: Default is 60 seconds

## Troubleshooting

### Integration Not Found

**Problem**: Can't find "Nokia FastMile 5G" when adding integration

**Solutions**:
1. Verify files are in the correct directory
2. Check `custom_components/nokia_fastmile/manifest.json` exists
3. Restart Home Assistant completely
4. Check Home Assistant logs for errors
5. Clear browser cache and refresh

### Cannot Connect

**Problem**: "Failed to connect" error during setup

**Solutions**:
1. Verify device IP address:
   ```bash
   ping 192.168.192.1
   ```
2. Test web interface in browser: `http://192.168.192.1/`
3. Confirm credentials are correct
4. Check network connectivity
5. Ensure device is powered on and fully booted
6. Try from another device on the same network

### Sensors Show "Unavailable"

**Problem**: Entities exist but show as "Unavailable"

**Solutions**:
1. Check Home Assistant logs: **Settings** → **System** → **Logs**
2. Verify device is still accessible
3. Try reloading the integration:
   - **Settings** → **Devices & Services**
   - Find Nokia FastMile
   - Click **⋮** → **Reload**
4. Check update interval isn't too frequent
5. Verify firmware compatibility

### Integration Won't Load

**Problem**: Integration fails to load after restart

**Solutions**:
1. Check Home Assistant logs for Python errors
2. Verify all files were copied correctly
3. Ensure `requests` library is available:
   ```bash
   pip3 show requests
   ```
4. Check manifest.json is valid JSON
5. Remove and reinstall the integration

## Network Configuration

### Accessing from Different Subnet

If Home Assistant is on a different network:

1. Ensure routing between networks
2. Check firewall rules allow HTTP (port 80)
3. Update device IP in configuration to match

### Using Custom IP Address

If your device uses a different IP:

1. During setup, enter your custom IP instead of default
2. Ensure IP is static (not DHCP)
3. Update router/DHCP reservation if needed

## Uninstalling

To remove the integration:

### Via UI

1. Go to **Settings** → **Devices & Services**
2. Find **Nokia FastMile 5G**
3. Click **⋮** (three dots)
4. Select **Delete**
5. Confirm deletion

### Manual Removal

1. Delete integration via UI (above)
2. Remove files: `custom_components/nokia_fastmile/`
3. Restart Home Assistant

## Updating

### Via HACS

1. Open HACS
2. Go to **Integrations**
3. Find **Nokia FastMile 5G**
4. Click **Update** if available
5. Restart Home Assistant

### Manual Update

1. Download new release
2. Extract and replace files in `custom_components/nokia_fastmile/`
3. Restart Home Assistant

## Getting Help

If you need assistance:

1. Check the [README](README_INTEGRATION.md) for detailed documentation
2. Review [GitHub Issues](https://github.com/yourusername/nokia-fastmile-ha/issues)
3. Ask in [Home Assistant Community](https://community.home-assistant.io/)
4. Create a new issue with:
   - Home Assistant version
   - Integration version
   - Device model and firmware
   - Relevant log excerpts
   - Steps to reproduce
