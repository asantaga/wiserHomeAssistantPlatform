# Changelog

All notable changes to the Wiser Home Assistant integration, newest release first.

For releases before v3.3.5, see the [Full Change Log](https://github.com/asantaga/wiserHomeAssistantPlatform/wiki/Full-Change-Log) on our wiki.

## v4.0.0-rc1

### Breaking changes

- The device registry is restructured. The separate virtual controller device is merged into the physical hub device, and Wiser room devices move to stable identifiers. In both cases the old device is removed and its entities are reassigned to the surviving device. Entity IDs and history are preserved, but anything that targets a Wiser *device* rather than an entity - device-based automations and scripts, or dashboard cards pointing at a device - needs repointing - PR [#693](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/693).
- Entity unique IDs migrate to deterministic UUIDv5. The migration runs automatically on upgrade and renames registry entries in place, so entity IDs, history, and customisations are preserved. Every target is checked before any change is applied, so it cannot partially apply, but it aborts if it finds a unique ID collision - take a backup before upgrading - PR [#693](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/693).

### Added

- Added configurable OpenTherm monitoring and controls, including relative modulation, a Delta-T sensor, expanded telemetry, and categorized diagnostics - PR [#697](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/697).
- Added a configurable Wiser Schedules sidebar panel - PR [#708](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/708).
- Added a Wiser Zigbee sidebar panel with a custom sidebar icon - PR [#708](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/708).
- Added a Hot Water on/off switch entity - issue [#626](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/626), PR [#682](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/682).
- Added a UFH controller measured-temperature sensor - issue [#628](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/628).
- Added optimistic light state for instant UI feedback on toggles, kept stable across rapid repeated toggles - PR [#684](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/684).
- Added British English translations and corrected the German, French, and English integration translations - PR [#708](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/708).

### Changed

- Entity naming now follows Home Assistant conventions, using `has_entity_name` so Home Assistant composes each displayed name from the device name plus the entity name. Existing entity IDs are not renamed. A new **Legacy naming** option controls whether Wiser room names are included in device names; it is switched on automatically for existing installations, so your device names stay as they are unless you turn it off. New installations on Home Assistant 2026.8 and later default it to off - PR [#693](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/693), PR [#700](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/700).
- Wiser devices are now placed in Home Assistant areas matching their Wiser room, creating the area if it does not exist. This applies only to devices that have no area yet, so any area you assigned manually is left untouched - PR [#693](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/693), PR [#700](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/700).
- Sidebar panel visibility is now configured through the integration's UI options - PR [#708](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/708).
- Card versions are now detected from the installed card bundles instead of being pinned in the integration, so card updates no longer need an integration release - PR [#708](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/708).

### Fixed

- Reintroduced the previous Power and Energy entities, corrected equipment data naming on v2 hubs, and added an active state for the window/door sensor - issue [#677](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/677), PR [#690](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/690).
- Fixed multi-gang dimmer lights breaking select, binary_sensor, switch, and sensor entities - issue [#681](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/681), PR [#683](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/683).
- Preserved light entities across the multi-gang unique_id migration - issue [#681](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/681), PR [#683](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/683).
- Fixed the device signal sensor to emit once per physical device instead of once per light channel on multi-gang dimmers - issue [#681](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/681), PR [#683](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/683).
- Fixed the room **Window Detection Active** binary sensor being presented as a physical window sensor. It carried a `window` device class, so Home Assistant displayed it as Open/Closed as though it reported a real window, when it actually reports whether the room's window-detection feature is switched on. It now shows a plain on/off state. The underlying state values are unchanged, so automations that test for `on`/`off` keep working - only the displayed wording and icon change - PR [#703](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/703).
- Fixed away mode and frost protection reporting distinct target temperatures, and the frost protection target now honours the configured value - PR [#693](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/693).
- Fixed the hot water switch to report against the hub as its parent device - PR [#704](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/704).
- Fixed a Zigbee sidebar route conflict that could stop the integration setting up - PR [#708](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/708).
- Fixed the boiler capacity and estimated boiler output sensors to use a gas burner icon - PR [#701](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/701).
- Fix for issue [#662](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/662) - PR [#680](https://github.com/asantaga/wiserHomeAssistantPlatform/pull/680).

## v3.4.20

- Added equipment data to smart plugs, heating actuators, and PowerTag E devices.
- Added LED-indicator support for on/off and dimmable lights.
- Added seasonal-comfort controls, including the target lift for shutters.
- Added an option to hide the hot-water schedule in the Wiser Schedule Card.
- Fixed the controller signal sensor to use the HeatHub name - issue [#639](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/639).
- Fixed schedule deletion and schedule-name inputs on current Home Assistant releases - issue [#461](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/461).

## v3.4.19

- Fixed: Breaking change in HA 2026.2 causes integration not to load - issue [#643](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/643)
- Fixed: V2 hubs with firmware lower than 4.42.23 cannot connect on https

## v3.4.18

- Fixed no long term stats for temp/humidity sensors issue [#598](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/598)
- Fixed deprecated ZeroconfServiceInfo - issue [#612](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/612)
- Fixed error 500 when selecting integration config - issue [#613](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/613)
- Fixed unable to create new schedule card - issue [#616](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/616)
- Fixed schedule card badges are misaligned - issue [#615](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/615)
- Changed: Communication to v2 hub now uses https over internal network
- Bumped schedule card to v1.5.0
- Bumped api to v1.7.0

## v3.4.17

- Fixed hot water climate does not respect away mode - issue [#579](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/579)
- Fixed deprecation error sets option flow config_entry explicitly - issue [#595](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/595)
- Fixed schedule card unable to edit - issue [#607](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/607)

## v3.4.16

- Fix incorrect identifer on hub device
- Fix deprecation warning for access to lovelace resource parameters
- Fix error on unloading services for hubs without hot water control
- Fix deprecation warning for ZeroconfServiceInfo
- Bump api to v1.6.6 to support SSL for future firmware

## v3.4.15

- Added experimental hw climate mode to operate differently. See wiki for details
- Changed min/max hw climate temp range from 40-80C to 10-80C - issue [#545](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/545)
- Fixed issue whereby hw climate errors if temp sensor not available after HA start - issue [#541](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/541)
- Fixed issue whereby hw climate config requires some entry in the temp sensor select option, even if not enabled - issue [#544](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/544)
- Fixed issue whereby hw min does not change when setting both via service call if temps are 1C or less different - issue [#547](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/547)

## v3.4.14

- Fixed issue causing integration not to load in some circumstances due to failed config entry migration - issue #539
- Added binary sensor active state sensor

## v3.4.13

- Added support for PowerTag C - issue #528
- BREAKING CHANGE - refactored HW climate automation - issues #481, #490. See wiki for updated instructions
- Added illuminance, humidity and temp sensors to devices with threshold sensors - issue #531
- Added support for 2 gang light switch - issue #529
- Added interacts with room climate switch to supported devices
- Fixed support for Binary sensors with threshold sensors - issue #530
- Fixed incompatibility with Python3.13 and HA2024.12 - issue #535
- Fixed events not correctly firing for climate changes - issue #526
- Fixed error when saving schedule with an off slot - issue #536
- Changed all hot water related sensors to now belong to a hot water device
- Bumped aiowiserheatapi to v1.6.3

## v3.4.12

- Fixed issue assigning schedules with non ascii characters in name - issue #509
- Fixed error when using HotWater climate automation - issue #517
- Fixed wiser http path not registering - issue #521
- Fixed issue causing integration to fail loading with BoilerInterface - issue #523
- Added support for ButtonPanel (Wiser Odace) - issue #524
- Bump api to v1.5.19 to resolve issues #509, #523, #524

## v3.4.11

- Bump api to v1.5.18 to reduce Payload not completed errors
- Fix typo in dimable light color mode - issue #518

## v3.4.10

- Fixed error loading sensors - issue #513

## v3.4.9 (Pulled)

- Fixed smoke alarm naming issue - issue #496
- Set humidity to Unavailable if no value - issue #503
- Add support for BoilerInterface - issue #499
- Add support for WindowDoorSensor for v2 hub
- Add support for CFMT device for v2 hub - issue #507

## v3.4.8

- Fix deprecation warning no waiting on setups - [#485](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/485)
- Fix color mode issue - [#479](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/479)
- Added smoke alarm sensors - [#457](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/457)
- Fixed missing save layout button in zigbee card - [#488](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/488)

## v3.4.7

- Bump api to v1.5.14 to improve handling of hub connection errors
- Fix - improve handling of hub update failures - [#434](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/434)
- Fix - set entity values to unknown if not provided in the hub update - [#471](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/471)
- Fix - removed use of async_add_job - [#463](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/463)
- Fix - add color modes to lights - [#458](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/458)
- Fix - use default boost temp with presets - [#467](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/467)
- Add ability to unassign a schedule via the assign schedule service - [#470](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/470)

## v3.4.6

- Bump api to v1.5.13 to improve retry handling to include hub conneciton error
- Prevent entities going unavailable if hub update failed
- Fix issue with floor temp offset slider not loading
- Fix hass.components.websocket_api deprecation warning in HA 2024.3 (issue [#455](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/455))
- Fix unique ids not unique error when changing configuration options
- Add new automation to control hot water with a climate entity and an external temperature sensor on your water tank by @markchalloner. See wiki for more info.

## v3.4.5

- Bump api to v1.5.12 to improve performance of improved retry handling
- Fixed issue caused by v3.4.4 that heating actuators and power tags error on load (issue [#449](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/449), [#450](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/450))
- Fixed error setting up integration in config flow caused by session parameter being passed when no longer required (issue [#446](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/446))
- Fixed issue on 3 channel hubs with Heating sensor names
- Fixed issue with signal sensor showing unknown on startup until first refresh
- Changed preset icon to HA standard

## v3.4.4

- Bump api to v1.5.11
- Improved api retry handling for inconsitant errors coming from the hub causing errors in the log and entities to go unavailable (issues [#434](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/434), #436, #439)
- Fixed Validation of translation placeholders error for German language (issue [#434](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/434)
- Fixed diagnostic download failure (issue [#444](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/444))
- Fixed error with wall plugs not providing power data (issue [#446](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/446))
- Set state of target temp sensors to Unavailable when the climate HVAC mode is off (issue [#447](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/447), #378)
- Added ability to set a different IP port for hub - PR#430 - thanks @simick
- Enabled statistics on batteries - PR#445 - thanks @msalway
- Added number_of_trvs, number_of_trvs_locked and is_roomstat_locked attributes to climate entities (issue [#374](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/374))

## v3.4.3

- Fixed Warning error in logs caused by new HA2024.2 requirement to explicity support Turn On/Off for climate entities (issue [#435](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/435))
- Bump api to v1.5.7 to fix issue setting lower target temp when in passive mode

## v3.4.2

- Reverted to using aiohttp for communication and resolved issues caused by HA2023.12
- Bumped api to v1.5.5
- Fixed issue where hub communication would error due to command characters in payload (issue [#418](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/418))
- Updated schedule card to allow hiding of hot water schedule (issue [#415](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/415))
- Included version in card resources to improve updating of new versions
- Added more v2 hub features and attributes
- Improved error handling/logging when hub offline and command is issued

## v3.4.1

- Corrected error deleting schedule
- Handle space at end of secret key and prevent error (issue [#409](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/409))
- Updated schedule card to v1.3.2 - fixed some UI bugs, added ability to hide info and assignments via config (issue [#404](https://github.com/asantaga/wiserHomeAssistantPlatform/issues/404))

## v3.4.0beta

- Fixed issue in HA 2023.12 with errors reading hub
- Add PowerTagE support (v2 hub)
- Add tilt functions for shutters (v2 hub)
- Fixed issue whereby non ASCII chars are removed in device/room names - issues #396

## v3.3.11

- Add check for overrides to prevent turning off away modewhen selecting cancel overrides when none exist (Wiser hub bug)
- Correct sensor device class and native values to fix history not displaying issue in HA 2023.11

## v3.3.10

- bump api to v1.3.8 to fix passive mode error if room trv/roomstat goes offline
- make battery sensor unavailable if no battery info provided by hub (previously showed 0%)
- add uptime and last reset reason to Hub signal sensor
- make LTS sensors normal sensors instead of diagnostic sensors so they show in Area card - issue #381
- save schedule service will now create directory for file if it doesn't exist
- correct relative modulation level magnitude

## v3.3.9

- bump api to v1.3.5 to fix warning regarding async not awaited on extra config

## v3.3.8

- Fix extra key issue preventing loading on HA 2023.8.0 and above

## v3.3.7

- Fix issue with zigbee card unable to save layout in stack card
- Updated libraries for schedule card to fix security vulnerabilities
- Fix colours missing on on/off schedule in schedule card
- Minor UI improvements in schedule card

## v3.3.6

- Improved Zigbee network card

## v3.3.5

- Fix for eroneous current temp if lost signal with TRV - issue #369
- Reduced log error level for failed update form hub to warning
