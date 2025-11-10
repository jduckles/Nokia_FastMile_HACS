# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-10

### Added
- Initial release of Nokia FastMile 5G integration
- Device information sensors (model, firmware, serial, uptime)
- WAN connection sensors (status, external IP, gateway)
- 5G cellular sensors (RSRP, RSRQ, SNR, signal strength)
- LTE/4G cellular sensors (RSSI, RSRP, SNR)
- Connected devices count sensor
- Reboot button for device control
- UI-based configuration flow
- Options flow for configurable polling interval
- HACS compatibility
- Full English translations
- Comprehensive documentation

### Features
- Local polling (no cloud dependency)
- Automatic device discovery
- Real-time signal strength monitoring
- Configurable update interval
- Device diagnostics
- Home Assistant device registry integration

### Supported Devices
- Nokia FastMile 5G Receiver (5G14-B)
- Compatible with firmware version 1.25.02.00.0216

## [Unreleased]

### Planned
- Additional cell tower information (Band, PCI, EARFCN)
- Data usage statistics
- Network speed testing integration
- Historical signal strength tracking
- Advanced device configuration options
- Support for additional Nokia FastMile models
