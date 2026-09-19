# Wiser Home Assistant Integration v4.0.0-rc1

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

## What's New in 4.0?

This is a big release with a lot of bug fixes and changes.
- Entity and device naming now follows new Home Assistant conventions, where devices are associated with areas. Existing installations keep their current names automatically via the Legacy naming option - turn it off to adopt the new names
- New Wiser devices are assigned to Home Assistant areas matching your Wiser rooms
- Configurable OpenTherm monitoring and controls
- Brand new UI for Wiser Schedules and Wiser Zigbee, including optional sidebar panels
- Multiple bug fixes

Huge thanks to [@andyblac](https://github.com/andyblac) and [@lgo44](https://github.com/LGO44) for this release

### Breaking changes in 4.0

**Take a backup before upgrading.**

- **The device registry is restructured.** The separate virtual controller device is merged into the physical hub device, and Wiser room devices move to stable identifiers. Entity IDs and history are preserved, but anything that targets a Wiser *device* rather than an entity - device-based automations and scripts, or dashboard cards pointing at a device - needs repointing.
- **Entity unique IDs migrate to deterministic UUIDv5.** The migration runs automatically on upgrade and renames registry entries in place, so entity IDs, history, and customisations are preserved. It cannot partially apply, but it aborts if it finds a unique ID collision.

See the [change log](CHANGELOG.md) for the full list of changes in this release.

## What's New in 3.4?

- Added support for v2 hub
- Added support for many new v2 hub devices
- Climate entity for controlling hot water with external tank temp sensor

## Installing

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=asantaga&repository=wiserHomeAssistantPlatform&category=integration)

## Change log

See [CHANGELOG.md](CHANGELOG.md) for the full release history.

Releases before v3.3.5 are listed on our wiki [here](https://github.com/asantaga/wiserHomeAssistantPlatform/wiki/Full-Change-Log).

## Building

To build a stable release package, run:

```sh
python3 scripts/build.py --release --channel stable
```

For a prerelease package, use `--channel dev` instead. The build downloads published Schedules and Zigbee card assets from GitHub. Stable builds use stable card releases; prerelease builds use the newest published prerelease of each card, falling back to its newest stable release when none exists.

The output is `dist/wiser.zip`. The accompanying `dist/card-releases.json` records the card releases and checksums included in the package. Missing or invalid card assets fail the build.

The **Publish** GitHub Actions workflow runs the same build and attaches `wiser.zip` when an integration release is published. Preview runs provide a downloadable **wiser-package** artifact without publishing a release.
