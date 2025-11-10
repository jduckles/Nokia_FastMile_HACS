# Nokia FastMile 5G Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/yourusername/nokia-fastmile-ha.svg)](https://github.com/yourusername/nokia-fastmile-ha/releases)
[![License](https://img.shields.io/github/license/yourusername/nokia-fastmile-ha.svg)](LICENSE)

A complete Home Assistant custom integration for monitoring and controlling Nokia FastMile 5G receivers.

## Features

✅ **Comprehensive Monitoring**
- Device information (model, firmware, serial, uptime)
- WAN connection status and IP information
- 5G cellular statistics (RSRP, RSRQ, SNR, signal strength)
- LTE/4G cellular statistics (RSSI, RSRP, SNR)
- Connected devices count

✅ **Device Control**
- Reboot button for remote restart

✅ **Easy Setup**
- UI-based configuration flow
- No YAML required
- Automatic device discovery

✅ **Local & Fast**
- All communication is local (no cloud)
- Configurable polling interval
- Real-time updates

## Screenshots

![Configuration Flow](docs/config_flow.png)
![Sensors](docs/sensors.png)

## Installation

### HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed
2. In HACS, go to "Integrations"
3. Click the three dots menu (⋮) in the top right
4. Select "Custom repositories"
5. Add this URL: `https://github.com/yourusername/nokia-fastmile-ha`
6. Select category: "Integration"
7. Click "Add"
8. Find "Nokia FastMile 5G" and click "Download"
9. Restart Home Assistant
10. Add the integration via UI (see Configuration below)

### Manual Installation

1. Download the latest release from [releases](https://github.com/yourusername/nokia-fastmile-ha/releases)
2. Extract the files
3. Copy the `custom_components/nokia_fastmile` folder to your Home Assistant `custom_components` directory
4. Restart Home Assistant
5. Add the integration via UI (see Configuration below)

## Configuration

1. In Home Assistant, go to **Configuration** → **Integrations**
2. Click the **+ Add Integration** button
3. Search for **Nokia FastMile 5G**
4. Enter your device credentials:
   - **Device IP Address**: Usually `192.168.192.1`
   - **Username**: Usually `admin`
   - **Password**: Found on your device sticker (or your custom password)
5. Click **Submit**

### Options

After adding the integration, you can configure options:

1. Go to **Configuration** → **Integrations**
2. Find **Nokia FastMile 5G**
3. Click **Configure**
4. Adjust settings:
   - **Update interval**: Polling frequency in seconds (default: 60)

## Available Entities

### Sensors

| Entity ID | Name | Description |
|-----------|------|-------------|
| `sensor.nokia_fastmile_model` | Model | Device model name |
| `sensor.nokia_fastmile_firmware_version` | Firmware Version | Current firmware version |
| `sensor.nokia_fastmile_serial_number` | Serial Number | Device serial number |
| `sensor.nokia_fastmile_uptime` | Uptime | Uptime in seconds |
| `sensor.nokia_fastmile_uptime_formatted` | Uptime (Formatted) | Human-readable uptime |
| `sensor.nokia_fastmile_wan_status` | WAN Status | Connection status |
| `sensor.nokia_fastmile_external_ip_address` | External IP | Public IP address |
| `sensor.nokia_fastmile_gateway` | Gateway | Gateway IP address |
| `sensor.nokia_fastmile_5g_rsrp` | 5G RSRP | 5G signal power (dBm) |
| `sensor.nokia_fastmile_5g_rsrq` | 5G RSRQ | 5G signal quality (dB) |
| `sensor.nokia_fastmile_5g_snr` | 5G SNR | 5G signal-to-noise ratio (dB) |
| `sensor.nokia_fastmile_5g_signal_strength` | 5G Signal Strength | Overall signal strength (0-5) |
| `sensor.nokia_fastmile_lte_rssi` | LTE RSSI | LTE signal strength (dBm) |
| `sensor.nokia_fastmile_lte_rsrp` | LTE RSRP | LTE signal power (dBm) |
| `sensor.nokia_fastmile_lte_snr` | LTE SNR | LTE signal-to-noise (dB) |
| `sensor.nokia_fastmile_connected_devices` | Connected Devices | Number of connected devices |

### Buttons

| Entity ID | Name | Description |
|-----------|------|-------------|
| `button.nokia_fastmile_reboot` | Reboot | Reboot the device |

## Usage Examples

### Automations

**Reboot on poor signal:**

```yaml
automation:
  - alias: "Reboot Nokia FastMile on poor 5G signal"
    trigger:
      - platform: numeric_state
        entity_id: sensor.nokia_fastmile_5g_rsrp
        below: -110
        for:
          minutes: 10
    action:
      - service: button.press
        target:
          entity_id: button.nokia_fastmile_reboot
```

**Notify on WAN disconnect:**

```yaml
automation:
  - alias: "Notify on WAN disconnect"
    trigger:
      - platform: state
        entity_id: sensor.nokia_fastmile_wan_status
        to: "Disconnected"
    action:
      - service: notify.mobile_app
        data:
          message: "Nokia FastMile WAN connection lost!"
```

### Lovelace Cards

**Simple entity card:**

```yaml
type: entities
title: Nokia FastMile 5G
entities:
  - sensor.nokia_fastmile_wan_status
  - sensor.nokia_fastmile_external_ip_address
  - sensor.nokia_fastmile_5g_rsrp
  - sensor.nokia_fastmile_5g_snr
  - sensor.nokia_fastmile_connected_devices
  - button.nokia_fastmile_reboot
```

**Gauge card for signal strength:**

```yaml
type: gauge
entity: sensor.nokia_fastmile_5g_signal_strength
min: 0
max: 5
name: 5G Signal Strength
severity:
  green: 3
  yellow: 2
  red: 0
```

## Signal Metrics Guide

### Understanding 5G Metrics

**RSRP (Reference Signal Received Power)**
- Measures the power of the 5G signal
- **Excellent**: > -80 dBm
- **Good**: -80 to -90 dBm
- **Fair**: -90 to -100 dBm
- **Poor**: < -100 dBm

**RSRQ (Reference Signal Received Quality)**
- Measures the quality of the 5G signal
- **Excellent**: > -10 dB
- **Good**: -10 to -15 dB
- **Fair**: -15 to -20 dB
- **Poor**: < -20 dB

**SNR (Signal-to-Noise Ratio)**
- Ratio of signal power to noise
- **Excellent**: > 20 dB
- **Good**: 13 to 20 dB
- **Fair**: 0 to 13 dB
- **Poor**: < 0 dB

### Understanding LTE Metrics

**RSSI (Received Signal Strength Indicator)**
- Overall signal strength
- **Excellent**: > -65 dBm
- **Good**: -65 to -75 dBm
- **Fair**: -75 to -85 dBm
- **Poor**: < -85 dBm

## Troubleshooting

### Integration won't load

1. Check Home Assistant logs: **Configuration** → **Logs**
2. Verify Python `requests` library is installed
3. Restart Home Assistant completely
4. Try removing and re-adding the integration

### Cannot connect during setup

1. Verify device IP address (default: `192.168.192.1`)
2. Test web interface: Open `http://192.168.192.1/` in browser
3. Confirm username and password are correct
4. Check network connectivity from Home Assistant to device
5. Ensure device is powered on and fully booted

### Sensors show "Unavailable"

1. Check if device is online
2. Verify network connectivity
3. Review Home Assistant logs for errors
4. Try reloading the integration
5. Reduce polling frequency (increase scan_interval)

### Reboot button doesn't work

1. Check Home Assistant logs for errors
2. Verify you have admin access to the device
3. Test reboot manually via web interface
4. Ensure device firmware supports remote reboot

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/nokia-fastmile-ha.git
cd nokia-fastmile-ha

# Install development dependencies
pip install -r requirements_dev.txt

# Run tests
pytest

# Run linting
pylint custom_components/nokia_fastmile
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/nokia-fastmile-ha/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/nokia-fastmile-ha/discussions)
- **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)

## Compatibility

- **Home Assistant**: 2023.1.0 or newer
- **Python**: 3.9 or newer
- **Nokia FastMile Models**:
  - Nokia FastMile 5G Receiver (5G14-B)
  - Other models may work but are untested

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the Home Assistant community
- Inspired by other device integration projects
- Built with ❤️ for the Home Assistant ecosystem

## Disclaimer

This integration is not affiliated with, endorsed by, or supported by Nokia Corporation. Use at your own risk.
