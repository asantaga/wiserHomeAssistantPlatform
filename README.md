# Wiser Home Assistant Integration v3.3.10

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![downloads](https://shields.io/github/downloads/asantaga/wiserHomeAssistantPlatform/latest/total?style=for-the-badge)](https://github.com/asantaga/wiserHomeAssistantPlatform)
[![version](https://shields.io/github/v/release/asantaga/wiserHomeAssistantPlatform?style=for-the-badge)](https://github.com/asantaga/wiserHomeAssistantPlatform)

This repository contains a Home Assistant integration for the awesome Drayton Wiser Heating solution.  This integration works locally with your wiser hub and does not rely on the cloud.

It also supports some European versions of the Wiser Hub under the Schneider Electric brand, including support for lights and blinds.

For the latest version of the Wiser Home Assistant Platform please install via HACS. If you want bleeding edge then checkout the dev branch, or look out for beta releases via HACS. Depending on what you choose you may need to use the Manual Code Installation as described in the Wiki.

Detailed information about this integration has now been moved to our [Wiki pages](https://github.com/asantaga/wiserHomeAssistantPlatform/wiki)

For more information checkout the AMAZING community thread available on
[https://community.home-assistant.io/t/drayton-wiser-home-assistant-integration/80965](https://community.home-assistant.io/t/drayton-wiser-home-assistant-integration/80965)

## What's New in 3.3?

- Improved support for Opentherm boilers with flow and return temp sensors and many attributes.
- Support of heating actuator floor sensors
- TRV passive mode (inspired by @robertwigley).  An inbuilt automation in the integration to create passive TRVs that will only heat when other rooms are heating.  Integration automations must be enabled to support this.
- Improved data in Wiser events
- Improved error handling for setting schedules from YAML files
- Improved zigbee network card

## Change log

- v3.3.10
  - bump api to v1.3.8 to fix passive mode error if room trv/roomstat goes offline
  - make battery sensor unavailable if no battery info provided by hub (previously showed 0%)
  - add uptime and last reset reason to Hub signal sensor
  - make LTS sensors normal sensors instead of diagnostic sensors so they show in Area card - issue #381
  - save schedule service will now create directory for file if it doesn't exist
  - correct relative modulation level magnitude

- v3.3.9
  - bump api to v1.3.5 to fix warning regarding async not awaited on extra config

- v3.3.8
  - Fix extra key issue preventing loading on HA 2023.8.0 and above

- v3.3.7
  - Fix issue with zigbee card unable to save layout in stack card
  - Updated libraries for schedule card to fix security vulnerabilities
  - Fix colours missing on on/off schedule in schedule card
  - Minor UI improvements in schedule card

- v3.3.6
  - Improved Zigbee network card

- v3.3.5
  - Fix for eroneous current temp if lost signal with TRV - issue #369
  - Reduced log error level for failed update form hub to warning

A full change log can be seen on our wiki [here](https://github.com/asantaga/wiserHomeAssistantPlatform/wiki/Full-Change-Log)
