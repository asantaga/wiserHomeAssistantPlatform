# Wiser Home Assistant Integration v4.1.1

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![downloads](https://shields.io/github/downloads/asantaga/wiserHomeAssistantPlatform/latest/total?style=for-the-badge)](https://github.com/asantaga/wiserHomeAssistantPlatform)
[![version](https://shields.io/github/v/release/asantaga/wiserHomeAssistantPlatform?style=for-the-badge)](https://github.com/asantaga/wiserHomeAssistantPlatform)
[![Latest Release](https://img.shields.io/badge/dynamic/json?style=for-the-badge&color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.wiser.total)](https://analytics.home-assistant.io/custom_integrations.json)

This repository contains a Home Assistant integration for the awesome Drayton Wiser Heating solution. This integration works locally with your wiser hub and does not rely on the cloud.

It also supports some European versions of the Wiser Hub under the Schneider Electric brand, including support for lights and blinds.

For the latest version of the Wiser Home Assistant Platform please install via HACS. If you want bleeding edge then checkout the dev branch, or look out for beta releases via HACS. Depending on what you choose you may need to use the Manual Code Installation as described in the Wiki.

**This integration requires a minimum HA version of 2025.5.**

Detailed information about this integration has now been moved to our [Wiki pages](https://github.com/asantaga/wiserHomeAssistantPlatform/wiki)

For more information checkout the AMAZING community thread available on
[https://community.home-assistant.io/t/drayton-wiser-home-assistant-integration/80965](https://community.home-assistant.io/t/drayton-wiser-home-assistant-integration/80965)

## What's New in 4.1.1?

## What's New in 4.1.0?

This release expands room control, improves the Wiser interface and adds more controls for supported devices.

- **External Room Control and Passive Mode:** Compatible Home Assistant heating devices can follow Wiser rooms, with external temperature sensor feedback, modulating or temperature-limiter strategies, and scheduled lower and upper limits.
- **Improved heating and hot water controls:** On Home Assistant 2026.7 and later, enable **Wiser climate controls** under **UI options** to show room demand, Passive Mode colours and boost countdowns in native Thermostat cards and More Info. OpenTherm hot water gains editable timed presets and clearer boost information.
- **More panel features:** Export and restore Wiser panel settings, and use the new Notifications tab to manage supported Wiser notifications and automations.
- **Expanded device controls:** More light configuration options, smart-plug LED controls, heating-actuator output types and equipment information, with translated option labels.
- **Circuit activity and signal sensors:** New **Heating active** and **Hot water active** binary sensors provide on/off history alongside the existing circuit text sensors. Heating activity follows the boiler's central-heating status on OpenTherm systems. Optional Zigbee signal strength (dBm), link quality and hub Wi-Fi signal strength (dBm) diagnostic sensors are disabled by default and can be enabled in Home Assistant.
- **Reliability and diagnostics:** Improved Passive limiter overrides, entity ID regeneration after hub renaming, and downloaded diagnostics to help investigate naming and upgrade issues. Updated to `aioWiserHeatAPI` 1.7.10.

**Upgrade notes:** Existing native Passive Mode settings migrate automatically; legacy experimental External Passive Mode needs setting up again. Light and smart-plug selectors now report translation keys such as `auto` and `manual`, so update automations that compare their states. Service calls using the previous API option values remain supported.

In **Temperature limiter** mode, the lower bound sets Wiser's target for calling for heat. The upper bound closes the assigned external valves; they reopen below the upper bound minus the configured temperature increment. **Advance Schedule** applies the next period's Passive Mode enablement, strategy and paired limits until the next scheduled transition or **Cancel Overrides**.

See the [change log](CHANGELOG.md) for full release details.

## Installing

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=asantaga&repository=wiserHomeAssistantPlatform&category=integration)

## Change log

See [CHANGELOG.md](CHANGELOG.md) for the full release history.

Releases before v3.3.5 are listed on our wiki [here](https://github.com/asantaga/wiserHomeAssistantPlatform/wiki/Full-Change-Log).

## Building

See [Building a package](CONTRIBUTING.md#building-a-package) in the contributing guide.

## Contributing

We welcome and greatly appreciate all issues, pull requests, and bug fixes. Please base your PR on the `dev` branch — all development happens there.

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to report a bug, set up a development environment, run the tests, and get a pull request merged.

Wiser Home Assistant Integration Team
