# Nokia FastMile 5G Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Complete Home Assistant integration for Nokia FastMile 5G receivers with comprehensive monitoring and control capabilities.

## Features

- **Device Information**: Model, serial number, firmware version, uptime
- **WAN Connection**: Status, external IP, gateway monitoring
- **5G Cellular Stats**: RSRP, RSRQ, SNR, signal strength
- **LTE/4G Cellular Stats**: RSSI, RSRP, SNR
- **Connected Devices**: Track number of connected devices
- **Device Control**: Reboot button
- **Easy Configuration**: UI-based configuration flow
- **Local Polling**: No cloud dependency, all local communication

## Sensors

The integration provides 15+ sensors:

### Device Sensors
- Model
- Firmware Version
- Serial Number
- Uptime (seconds)
- Uptime (formatted)

### WAN Sensors
- WAN Status
- External IP Address
- Gateway

### 5G Cellular Sensors
- RSRP (Reference Signal Received Power)
- RSRQ (Reference Signal Received Quality)
- SNR (Signal-to-Noise Ratio)
- Signal Strength (0-5)

### LTE/4G Cellular Sensors
- RSSI (Received Signal Strength Indicator)
- RSRP
- SNR

### Other
- Connected Devices Count

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/yourusername/nokia-fastmile-ha`
6. Select "Integration" as the category
7. Click "Add"
8. Find "Nokia FastMile 5G" in the integration list and install it
9. Restart Home Assistant
10. Go to Configuration > Integrations
11. Click "+ Add Integration"
12. Search for "Nokia FastMile 5G"

### Manual Installation

1. Copy the `custom_components/nokia_fastmile` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant
3. Go to Configuration > Integrations
4. Click "+ Add Integration"
5. Search for "Nokia FastMile 5G"

## Configuration

1. After installation, go to Configuration > Integrations
2. Click "+ Add Integration"
3. Search for "Nokia FastMile 5G"
4. Enter your device details:
   - **Device IP Address**: Usually `192.168.192.1`
   - **Username**: Usually `admin`
   - **Password**: Your device password (found on device sticker)

## Options

You can configure the following options by clicking "Configure" on the integration:

- **Update interval**: How often to poll the device (default: 60 seconds)

## Signal Metrics Explained

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

## Example Dashboard

```yaml
type: entities
title: Nokia FastMile 5G
entities:
  - entity: sensor.nokia_fastmile_wan_status
  - entity: sensor.nokia_fastmile_external_ip_address
  - entity: sensor.nokia_fastmile_uptime_formatted
  - type: divider
  - entity: sensor.nokia_fastmile_5g_rsrp
  - entity: sensor.nokia_fastmile_5g_snr
  - entity: sensor.nokia_fastmile_5g_signal_strength
  - type: divider
  - entity: sensor.nokia_fastmile_lte_rsrp
  - entity: sensor.nokia_fastmile_lte_snr
  - type: divider
  - entity: sensor.nokia_fastmile_connected_devices
  - entity: button.nokia_fastmile_reboot
```

## Troubleshooting

### Cannot Connect

1. Verify the device IP address (default: 192.168.192.1)
2. Check username and password
3. Ensure you can access the web interface at `http://192.168.192.1/`
4. Verify Home Assistant can reach the device network

### Sensors Show "Unavailable"

1. Check Home Assistant logs for errors
2. Verify the device is online and accessible
3. Try reloading the integration
4. Adjust the update interval if polling too frequently

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## License

This integration is provided free to use and modify for personal use.
