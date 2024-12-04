# Wiser Home Assistant Integration v3.4.14

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![downloads](https://shields.io/github/downloads/asantaga/wiserHomeAssistantPlatform/latest/total?style=for-the-badge)](https://github.com/asantaga/wiserHomeAssistantPlatform)
[![version](https://shields.io/github/v/release/asantaga/wiserHomeAssistantPlatform?style=for-the-badge)](https://github.com/asantaga/wiserHomeAssistantPlatform)

This repository contains a Home Assistant integration for the awesome Drayton Wiser Heating solution.  This integration works locally with your wiser hub and does not rely on the cloud.

It also supports some European versions of the Wiser Hub under the Schneider Electric brand, including support for lights and blinds.

For the latest version of the Wiser Home Assistant Platform please install via HACS. If you want bleeding edge then checkout the dev branch, or look out for beta releases via HACS. Depending on what you choose you may need to use the Manual Code Installation as described in the Wiki.

**This integration requires a minimum HA version of 2024.2.**

Detailed information about this integration has now been moved to our [Wiki pages](https://github.com/asantaga/wiserHomeAssistantPlatform/wiki)

For more information checkout the AMAZING community thread available on
[https://community.home-assistant.io/t/drayton-wiser-home-assistant-integration/80965](https://community.home-assistant.io/t/drayton-wiser-home-assistant-integration/80965)

## What's New in 3.4?

- Added support for v2 hub
- Added PowerTagE support
- Climate entity for controlling hot water with external tank temp sensor

## Installing

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=asantaga&repository=wiserHomeAssistantPlatform&category=integration)

## Change log

- v3.4.14
  - Fixed issue causing integration not to load in some circumstances due to failed config entry migration - issue #539
  - Added binary sensor active state sensor

- v3.4.13
  - Added support for PowerTag C - issue #528
  - BREAKING CHANGE - refactored HW climate automation - issues #481, #490.  See wiki for updated instructions
  - Added illuminance, humidity and temp sensors to devices with threshold sensors - issue #531
  - Added support for 2 gang light switch - issue #529
  - Added interacts with room climate switch to supported devices
  - Fixed support for Binary sensors with threshold sensors - issue #530
  - Fixed incompatibility with Python3.13 and HA2024.12 - issue #535
  - Fixed events not correctly firing for climate changes - issue #526
  - Fixed error when saving schedule with an off slot - issue #536
  - Changed all hot water related sensors to now belong to a hot water device
  - Bumped aiowiserheatapi to v1.6.3

- v3.4.12
  - Fixed issue assigning schedules with non ascii characters in name - issue #509
  - Fixed error when using HotWater climate automation - issue #517
  - Fixed wiser http path not registering - issue #521
  - Fixed issue causing integration to fail loading with BoilerInterface - issue #523
  - Added support for ButtonPanel (Wiser Odace) - issue #524
  - Bump api to v1.5.19 to resolve issues #509, #523, #524


- v3.4.11
  - Bump api to v1.5.18 to reduce Payload not completed errors
  - Fix typo in dimable light color mode - issue #518

- v3.4.10
  - Fixed error loading sensors - issue #513

- v3.4.9 (Pulled)
  - Fixed smoke alarm naming issue - issue #496
  - Set humidity to Unavailable if no value - issue #503
  - Add support for BoilerInterface - issue #499
  - Add support for WindowDoorSensor for v2 hub
  - Add support for CFMT device for v2 hub - issue #507

- v3.4.8
  - Fix deprecation warning no waiting on setups - [#485](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/485)
  - Fix color mode issue - [#479](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/479)
  - Added smoke alarm sensors - [#457](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/457)
  - Fixed missing save layout button in zigbee card - [#488](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/488)

- v3.4.7
  - Bump api to v1.5.14 to improve handling of hub connection errors
  - Fix - improve handling of hub update failures - [#434](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/434)
  - Fix - set entity values to unknown if not provided in the hub update - [#471](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/471)
  - Fix - removed use of async_add_job - [#463](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/463)
  - Fix - add color modes to lights - [#458](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/458)
  - Fix - use default boost temp with presets - [#467](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/467)
  - Add ability to unassign a schedule via the assign schedule service - [#470](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/470)

- v3.4.6
  - Bump api to v1.5.13 to improve retry handling to include hub conneciton error
  - Prevent entities going unavailable if hub update failed
  - Fix issue with floor temp offset slider not loading
  - Fix hass.components.websocket_api deprecation warning in HA 2024.3 (issue [#455](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/455))
  - Fix unique ids not unique error when changing configuration options
  - Add new automation to control hot water with a climate entity and an external temperature sensor on your water tank by @markchalloner. See wiki for more info.

- v3.4.5
  - Bump api to v1.5.12 to improve performance of improved retry handling
  - Fixed issue caused by v3.4.4 that heating actuators and power tags error on load (issue [#449](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/449), [#450](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/450))
  - Fixed error setting up integration in config flow caused by session parameter being passed when no longer required (issue [#446](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/446))
  - Fixed issue on 3 channel hubs with Heating sensor names
  - Fixed issue with signal sensor showing unknown on startup until first refresh
  - Changed preset icon to HA standard

- v3.4.4
  - Bump api to v1.5.11
  - Improved api retry handling for inconsitant errors coming from the hub causing errors in the log and entities to go unavailable (issues [#434](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/434), #436, #439)
  - Fixed Validation of translation placeholders error for German language (issue [#434](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/434)
  - Fixed diagnostic download failure (issue [#444](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/444))
  - Fixed error with wall plugs not providing power data (issue [#446](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/446))
  - Set state of target temp sensors to Unavailable when the climate HVAC mode is off (issue [#447](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/447), #378)
  - Added ability to set a different IP port for hub - PR#430 - thanks @simick
  - Enabled statistics on batteries - PR#445 - thanks @msalway
  - Added number_of_trvs, number_of_trvs_locked and is_roomstat_locked attributes to climate entities (issue [#374](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/374))

- v3.4.3
  - Fixed Warning error in logs caused by new HA2024.2 requirement to explicity support Turn On/Off for climate entities (issue [#435](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/435))
  - Bump api to v1.5.7 to fix issue setting lower target temp when in passive mode

- v3.4.2
  - Reverted to using aiohttp for communication and resolved issues caused by HA2023.12
  - Bumped api to v1.5.5
  - Fixed issue where hub communication would error due to command characters in payload (issue [#418](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/418))
  - Updated schedule card to allow hiding of hot water schedule (issue [#415](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/415))
  - Included version in card resources to improve updating of new versions
  - Added more v2 hub features and attributes
  - Improved error handling/logging when hub offline and command is issued

- v3.4.1
  - Corrected error deleting schedule
  - Handle space at end of secret key and prevent error (issue [#409](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/409))
  - Updated schedule card to v1.3.2 - fixed some UI bugs, added ability to hide info and assignments via config (issue [#404](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/404))

- v3.4.0beta
  - Fixed issue in HA 2023.12 with errors reading hub
  - Add PowerTagE support (v2 hub)
  - Add tilt functions for shutters (v2 hub)
  - Fixed issue whereby non ASCII chars are removed in device/room names - issues #396

- v3.3.11
  - Add check for overrides to prevent turning off away modewhen selecting cancel overrides when none exist (Wiser hub bug)
  - Correct sensor device class and native values to fix history not displaying issue in HA 2023.11

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
