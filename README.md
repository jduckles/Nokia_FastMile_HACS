# Nokia FastMile 5G Receiver Monitoring & Control

Complete monitoring and control solution for your Nokia FastMile 5G receiver, with full Home Assistant integration.

## Features

### Device Monitoring
- **Device Information**: Model, serial number, firmware version, hardware version
- **Uptime Tracking**: Monitor device uptime in seconds and formatted display
- **WAN Connection**: Status, external IP, gateway, DNS servers, NAT status
- **5G Cellular Stats**: RSRP, RSRQ, SNR, signal strength, frequency range
- **LTE/4G Cellular Stats**: RSSI, RSRP, RSRQ, SNR, signal strength
- **Connected Devices**: List of all devices connected to the router
- **Device Control**: Reboot functionality via script or Home Assistant

### Home Assistant Integration
- Comprehensive sensor suite (15+ sensors)
- Reboot button in Home Assistant UI
- JSON output for custom integrations
- Automatic polling every 60 seconds

## Files

- `nokia_fastmile_monitor.py` - Main monitoring script
- `nokia_fastmile_reboot.py` - Device reboot script
- `home_assistant_config.yaml` - Complete Home Assistant configuration
- `README.md` - This documentation

## Requirements

- Python 3.6 or higher
- `requests` library

Install requirements:
```bash
pip3 install requests
```

## Quick Start

### Test the Monitoring Script

```bash
python3 nokia_fastmile_monitor.py
```

Output includes:
- Device information (model, firmware, uptime)
- WAN connection details
- 5G and LTE cellular statistics
- Connected devices list
- JSON output for automation

### Reboot Your Device

```bash
python3 nokia_fastmile_reboot.py
```

The script will:
1. Ask for confirmation
2. Send reboot command
3. Confirm when device is rebooting

## Home Assistant Setup

### 1. Copy Scripts

Copy both Python scripts to a location accessible by Home Assistant:

```bash
# Example for Home Assistant OS or Supervised
cp nokia_fastmile_*.py /config/scripts/

# Or for Docker/Custom installations
cp nokia_fastmile_*.py /path/to/homeassistant/scripts/
```

### 2. Add Configuration

Add the contents of `home_assistant_config.yaml` to your `configuration.yaml`.

**Important**: Update the script paths in the configuration to match your installation:
- Change `/home/daniel/NokiaFastMile/` to your actual path
- Ensure Python 3 is available in Home Assistant's environment

### 3. Restart Home Assistant

After adding the configuration, restart Home Assistant to load the new sensors and button.

### 4. Available Sensors

After restart, you'll have access to:

**Device Sensors:**
- `sensor.nokia_model` - Device model name
- `sensor.nokia_firmware` - Firmware version
- `sensor.nokia_uptime` - Uptime in seconds
- `sensor.nokia_uptime_formatted` - Human-readable uptime

**WAN Sensors:**
- `sensor.nokia_wan_status` - Connection status
- `sensor.nokia_external_ip` - External IP address
- `sensor.nokia_gateway` - Gateway IP

**5G Cellular Sensors:**
- `sensor.nokia_5g_rsrp` - 5G RSRP (dBm)
- `sensor.nokia_5g_rsrq` - 5G signal quality (dB)
- `sensor.nokia_5g_snr` - 5G signal-to-noise ratio (dB)
- `sensor.nokia_5g_signal_strength` - Overall signal strength (0-5)

**LTE/4G Cellular Sensors:**
- `sensor.nokia_lte_rssi` - LTE signal strength (dBm)
- `sensor.nokia_lte_rsrp` - LTE RSRP (dBm)
- `sensor.nokia_lte_snr` - LTE SNR (dB)

**Other Sensors:**
- `sensor.nokia_connected_devices_count` - Number of connected devices

**Controls:**
- `button.nokia_fastmile_reboot` - Reboot the device

## Python API Usage

Use the `NokiaFastMileMonitor` class in your own Python scripts:

```python
from nokia_fastmile_monitor import NokiaFastMileMonitor

# Initialize
monitor = NokiaFastMileMonitor(
    host="192.168.192.1",
    username="admin",
    password="your_password"
)

# Get device information
device_info = monitor.get_device_info()
print(f"Model: {device_info['ModelName']}")
print(f"Uptime: {device_info['UpTime']} seconds")

# Get cellular statistics
cellular = monitor.get_cellular_stats()
print(f"5G RSRP: {cellular['5g']['RSRPCurrent']} dBm")
print(f"5G SNR: {cellular['5g']['SNRCurrent']} dB")

# Get WAN information
wan = monitor.get_wan_info()
print(f"External IP: {wan['connection']['ExternalIPAddress']}")

# Get connected devices
devices = monitor.get_connected_devices()
print(f"Connected devices: {len(devices)}")

# Reboot device
if monitor.reboot_device():
    print("Reboot command sent!")
```

## Available Methods

### NokiaFastMileMonitor Class

| Method | Returns | Description |
|--------|---------|-------------|
| `get_device_info()` | Dict | Device model, firmware, serial, uptime |
| `get_cellular_stats()` | Dict | 5G and LTE cellular statistics |
| `get_wan_info()` | Dict | WAN connection details |
| `get_connected_devices()` | List | List of connected devices |
| `get_all_status()` | Dict | Complete status (all data) |
| `reboot_device()` | Bool | Reboot the device |

## Cellular Signal Metrics Explained

### 5G Metrics

**RSRP (Reference Signal Received Power)**
- Excellent: > -80 dBm
- Good: -80 to -90 dBm
- Fair: -90 to -100 dBm
- Poor: < -100 dBm

**RSRQ (Reference Signal Received Quality)**
- Excellent: > -10 dB
- Good: -10 to -15 dB
- Fair: -15 to -20 dB
- Poor: < -20 dB

**SNR (Signal-to-Noise Ratio)**
- Excellent: > 20 dB
- Good: 13 to 20 dB
- Fair: 0 to 13 dB
- Poor: < 0 dB

### LTE/4G Metrics

**RSSI (Received Signal Strength Indicator)**
- Excellent: > -65 dBm
- Good: -65 to -75 dBm
- Fair: -75 to -85 dBm
- Poor: < -85 dBm

**RSRP, RSRQ, SNR**: Same ranges as 5G

## Configuration

### Changing Default Credentials

Edit the scripts to update your device credentials:

```python
HOST = "192.168.192.1"      # Your Nokia FastMile IP
USERNAME = "admin"           # Admin username
PASSWORD = "your_password"   # Your password
```

### Changing Update Interval

In `home_assistant_config.yaml`, modify the `scan_interval`:

```yaml
scan_interval: 60  # Update every 60 seconds (default)
scan_interval: 30  # Update every 30 seconds (more frequent)
scan_interval: 300 # Update every 5 minutes (less frequent)
```

## Troubleshooting

### Script Returns No Data

1. Verify device IP address (default: 192.168.192.1)
2. Check username and password
3. Ensure you can access http://192.168.192.1/ in a browser
4. Test with: `ping 192.168.192.1`

### Home Assistant Sensors Show "Unavailable"

1. Check script paths in `configuration.yaml`
2. Verify Python 3 is installed: `python3 --version`
3. Install requests library: `pip3 install requests`
4. Test scripts manually from command line
5. Check Home Assistant logs for errors

### Reboot Button Doesn't Work

1. Verify the reboot script path in shell_command
2. Test the reboot script manually
3. Check Home Assistant has permission to run scripts
4. Review Home Assistant logs for execution errors

### Permission Denied Errors

```bash
# Make scripts executable
chmod +x nokia_fastmile_monitor.py
chmod +x nokia_fastmile_reboot.py
```

## API Endpoints Used

The scripts use the following Nokia FastMile API endpoint:
- `http://192.168.192.1/prelogin_status_web_app.cgi` - Main status endpoint

This endpoint provides:
- Device information and uptime
- Cellular statistics (5G and LTE)
- WAN connection details
- Connected devices
- Network configuration

## Security Notes

- Scripts use HTTP Basic Authentication
- Keep credentials secure
- Use only on trusted networks
- Consider using environment variables for production:

```python
import os
PASSWORD = os.environ.get('NOKIA_PASSWORD', 'default_password')
```

## Advanced Usage

### Custom Polling Script

```python
import time
from nokia_fastmile_monitor import NokiaFastMileMonitor

monitor = NokiaFastMileMonitor("192.168.192.1", "admin", "password")

while True:
    stats = monitor.get_cellular_stats()
    if stats and '5g' in stats:
        rsrp = stats['5g']['RSRPCurrent']
        if rsrp < -100:
            print(f"WARNING: Poor 5G signal: {rsrp} dBm")

    time.sleep(60)  # Check every minute
```

### Data Logging

```python
import json
import datetime
from nokia_fastmile_monitor import NokiaFastMileMonitor

monitor = NokiaFastMileMonitor("192.168.192.1", "admin", "password")
data = monitor.get_all_status()

# Log to file
timestamp = datetime.datetime.now().isoformat()
with open('nokia_log.json', 'a') as f:
    json.dump({'timestamp': timestamp, 'data': data}, f)
    f.write('\n')
```

### Automated Reboot on Poor Signal

```python
from nokia_fastmile_monitor import NokiaFastMileMonitor

monitor = NokiaFastMileMonitor("192.168.192.1", "admin", "password")
stats = monitor.get_cellular_stats()

if stats and '5g' in stats:
    rsrp = stats['5g']['RSRPCurrent']
    if rsrp < -110:  # Very poor signal
        print("Signal too poor, rebooting...")
        monitor.reboot_device()
```

## Example Dashboard Card (Home Assistant)

```yaml
type: entities
title: Nokia FastMile 5G
entities:
  - entity: sensor.nokia_wan_status
  - entity: sensor.nokia_external_ip
  - entity: sensor.nokia_uptime_formatted
  - type: divider
  - entity: sensor.nokia_5g_rsrp
  - entity: sensor.nokia_5g_snr
  - entity: sensor.nokia_5g_signal_strength
  - type: divider
  - entity: sensor.nokia_lte_rsrp
  - entity: sensor.nokia_lte_snr
  - type: divider
  - entity: sensor.nokia_connected_devices_count
  - entity: button.nokia_fastmile_reboot
```

## Future Enhancements

Potential additions:
- More detailed cell information (Band, PCI, EARFCN/NRARFCN)
- Data usage statistics
- Network speed testing
- Historical signal strength tracking
- SMS functionality (if supported)
- More advanced device configuration

## Support

For issues or questions:
- Check this README
- Review script output for errors
- Check Home Assistant logs
- Verify network connectivity

## License

Free to use and modify for personal use.

## Changelog

### Version 2.0 (Current)
- Added device information monitoring
- Added uptime tracking
- Added WAN connection details
- Added connected devices list
- Added reboot functionality
- Enhanced Home Assistant integration
- Added reboot button in Home Assistant

### Version 1.0
- Initial release
- Basic 5G and LTE cellular monitoring
- Home Assistant sensor integration
