# Wiser Home Assistant Integration v4.0.1

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

This is a **major** and **big** release with a lot of new features, bug fixes and changes.

- Entity and device naming now follows Home Assistant conventions, with devices associated with areas. Existing installations keep their current names automatically through the **Legacy naming** option - turn it off to adopt the new names. New installations on Home Assistant 2026.8 and later use the new names by default
- Wiser devices are assigned to Home Assistant areas matching your Wiser rooms, and room renames in the Wiser app no longer create duplicate devices
- Configurable OpenTherm monitoring and controls, plus optional OpenTherm hot water control with its own schedule. The hot water schedule is run by Home Assistant rather than the hub, so it does not change the boiler while Home Assistant is offline
- New device support, including the Schneider Mureva EV Link charger, smoke alarm operating states and scheduled setpoint sensors for rooms without heating control
- Brand new **UI**: a single **Wiser** sidebar panel with tabs for Schedules, Zigbee, Controls and Hub. It is shown by default and can be hidden with **Show Wiser in sidebar** in the integration's UI options
- New **Wiser Controls card** for dashboards, covering heating, hot water, shutters, lights and smart plugs, alongside the updated Wiser Schedule and Wiser Zigbee cards
- New **Wiser Hub panel** with an overview, live controls, diagnostics and recent history for each hub
- Cards and panels now update independently of the integration, through Home Assistant update entities
- Translations for Danish, Spanish, Finnish, Hungarian, Norwegian, Dutch, Portuguese and Swedish
- Many bug fixes see change log

See the [change log](CHANGELOG.md) for the full list of changes in this release.

Huge thanks to [@andyblac](https://github.com/andyblac) and [@lgo44](https://github.com/LGO44) for this release

### Breaking changes in 4.0

**Please take a backup before upgrading.**

- **The device registry is restructured.** The separate virtual controller device is merged into the physical hub device, and Wiser room devices move to stable identifiers. Entity IDs and history are preserved, but anything that targets a Wiser *device* rather than an entity - device-based automations and scripts, or dashboard cards pointing at a device - needs repointing. Check these after upgrading.
- **Entity unique IDs move to a new format.** This migration runs automatically and keeps your entity IDs and history. It is all-or-nothing: if it finds a conflict it stops without changing anything, and the integration will not load until it is resolved.
- **Downgrading is not supported.** To go back to 3.x, restore the backup you took before upgrading - reinstalling the older version on its own will not work.
- **Equipment power and energy sensors are now off by default**, including for existing installations. If you use them, for example in the Energy dashboard, enable **Equipment sensors** in the integration options after upgrading.
- **Room climate entities only report `demand_type` when OpenTherm is enabled.** On systems without OpenTherm this attribute is no longer present, so update any templates or automations that use it. `percentage_demand` is still reported on all systems.
- **The Heating and Hot Water circuit state sensors now report `on`/`off` instead of `On`/`Off`.** The dashboard still shows On and Off, but templates and automations that compare against `On` or `Off` need updating to the lowercase values.

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
