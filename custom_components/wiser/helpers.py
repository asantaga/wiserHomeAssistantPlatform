from collections import Counter

from aioWiserHeatAPI.wiserhub import (
    WiserHubConnectionError,
    WiserHubAuthenticationError,
    WiserHubRESTError,
)
from homeassistant.const import MAJOR_VERSION, MINOR_VERSION
from homeassistant.core import HomeAssistant
from .const import DOMAIN, ENTITY_PREFIX, MANUFACTURER
import logging
import re
from uuid import UUID, uuid5

_LOGGER = logging.getLogger(__name__)

# Capability sensor types emitted per light by WiserStateIsDimmable
# (binary_sensor.py), needed to rebuild the pre-fix name-based unique_ids in
# build_light_unique_id_migration().
LIGHT_BINARY_SENSOR_TYPES = (
    "Is Dimmable",
    "Is LED Indicator Supported",
    "Is Output Mode Supported",
    "Is Power On Behaviour Supported",
)

# This namespace is part of the entity registry identity contract and must never
# be changed after release.
ENTITY_UNIQUE_ID_NAMESPACE = UUID("8d42a4e1-b77b-4dda-a964-137b67c6257f")


def active_wiser_rooms(data):
    """Return rooms that still have a device or controller assigned."""
    return [
        room
        for room in data.wiserhub.rooms.all
        if str(getattr(room, "_data", {}).get("Invalid", "")).casefold()
        != "nothingassigned"
    ]


def get_hub_mac_suffix(data):
    """Return the last three octets of the physical hub MAC address."""
    mac_address = data.wiserhub.system.network.mac_address
    compact_mac = re.sub(r"[^0-9A-Fa-f]", "", str(mac_address))
    return compact_mac[-6:].upper()


def get_hub_device_name(data):
    """Return the context-aware display name for the physical HeatHub."""
    if getattr(data, "_wiser_show_hub_suffix", False):
        return f"{ENTITY_PREFIX} HeatHub ({get_hub_mac_suffix(data)})"
    return f"{ENTITY_PREFIX} HeatHub"


def get_hub_entity_object_id(data, entity_name, device_name=None):
    """Return the MAC-derived entity portion of a new hub object ID."""
    entity_slug = re.sub(r"[^a-z0-9]+", "_", str(entity_name).lower()).strip("_")
    # Home Assistant adds the area and effective device name around this value.
    # The integration's multi-hub device name already contains the MAC suffix,
    # so omit it here to avoid ``..._04f8a0_04f8a0_away_mode``.
    device_name = device_name or get_hub_device_name(data)
    compact_device_name = re.sub(r"[^0-9A-Fa-f]", "", str(device_name))
    mac_suffix = get_hub_mac_suffix(data)
    if mac_suffix.casefold() in compact_device_name.casefold():
        return entity_slug
    # A user may rename the device and remove the visible MAC. Add it to the
    # entity portion so resetting the entity ID still retains the hub identity.
    return f"{mac_suffix.lower()}_{entity_slug}"


def hub_error_handler(func):
    """Decorator to handle hub errors"""

    async def wrapper(*args, **kwargs):
        try:
            await func(*args, **kwargs)
        except (
            WiserHubConnectionError,
            WiserHubAuthenticationError,
            WiserHubRESTError,
        ) as ex:
            _LOGGER.warning(ex)

    return wrapper


def get_device_name(data, device_id, device_type="device"):
    legacy_naming = getattr(data, "legacy_naming", False)
    if device_type == "device":
        device = data.wiserhub.devices.get_by_id(device_id)

        if device_id == 0:
            return get_hub_device_name(data)

        if device.product_type == "iTRV":
            if not legacy_naming:
                return f"{ENTITY_PREFIX} {device.product_type}"
            device_room = data.wiserhub.rooms.get_by_device_id(device_id)
            # If device not allocated to a room return type and id only
            if device_room:
                # To enable creating seperate devices for multiple TRVs in a room - issue #194
                if device_room.number_of_smartvalves > 1:
                    # Get index of iTRV in room so they are numbered 1,2 etc instead of device id
                    # 1 is lowest device id, 2 next lowest etc
                    sv_index = device_room.smartvalve_ids.index(device.id) + 1
                    return f"{ENTITY_PREFIX} {device.product_type} {device_room.name}-{sv_index}"
                return f"{ENTITY_PREFIX} {device.product_type} {device_room.name}"
            return f"{ENTITY_PREFIX} {device.product_type} {device.id}"

        if device.product_type == "RoomStat":
            device_room = data.wiserhub.rooms.get_by_device_id(device_id)
            if device_room:
                if legacy_naming:
                    return f"{ENTITY_PREFIX} Thermostat {device_room.name}"
                return f"{ENTITY_PREFIX} Thermostat"
            return f"{ENTITY_PREFIX} Thermostat {device.id}"

        if device.product_type == "UnderFloorHeating":
            return f"{ENTITY_PREFIX} {device.name}"

        if device.product_type in ["HeatingActuator", "CFMT"]:
            if not legacy_naming:
                return f"{ENTITY_PREFIX} {device.product_type}"
            device_room = data.wiserhub.rooms.get_by_device_id(device_id)
            # If device not allocated to a room return type and id only
            if device_room:
                # To enable creating seperate devices for multiple Heating Actuators in a room
                if device_room.number_of_heating_actuators > 1:
                    # Get index of iTRV in room so they are numbered 1,2 etc instead of device id
                    # 1 is lowest device id, 2 next lowest etc
                    ha_index = device_room.heating_actuator_ids.index(device.id) + 1
                    return f"{ENTITY_PREFIX} {device.product_type} {device_room.name}-{ha_index}"
                device_room = data.wiserhub.rooms.get_by_device_id(device_id)
                return f"{ENTITY_PREFIX} {device.product_type} {device_room.name}"
            return f"{ENTITY_PREFIX} {device.product_type} {device.id}"

        if device.product_type == "SmartPlug":
            return f"{ENTITY_PREFIX} {device.name}"

        if device.product_type in ["PowerTagE", "LoadControl"]:
            return f"{ENTITY_PREFIX} {device.name}"

        if device.product_type in ["SmokeAlarmDevice", "ButtonPanel"]:
            device_room = data.wiserhub.rooms.get_by_id(device.room_id)
            if legacy_naming and device_room:
                return f"{ENTITY_PREFIX} {device_room.name} {device.name}"
            return f"{ENTITY_PREFIX} {device.name} {device.id}"

        if device.product_type == "BoilerInterface":
            return f"{ENTITY_PREFIX} {device.product_type} {device.name}"

        if device.product_type == "TemperatureHumiditySensor":
            if legacy_naming:
                device_room = data.wiserhub.rooms.get_by_device_id(device_id)
                suffix = device_room.name if device_room else device.name
                return f"{ENTITY_PREFIX} Temperature/Humidity Sensor {suffix}"
            return f"{ENTITY_PREFIX} Temperature/Humidity Sensor"

        if device.product_type in [
            "Shutter",
            "OnOffLight",
            "DimmableLight",
            "WindowDoorSensor",
            "WaterLeakageSensor",
            "MotionLightSensor",
            "TemperatureHumiditySensor",
        ]:
            device_room = data.wiserhub.rooms.get_by_device_id(device_id)
            # If device not allocated to a room return type and id only
            if legacy_naming and device_room:
                return f"{ENTITY_PREFIX} {device.product_type} {device_room.name} {device.name}"
            return f"{ENTITY_PREFIX} {device.product_type} {device.name}"

        return f"{ENTITY_PREFIX} {device.serial_number}"

    elif device_type == "room":
        if legacy_naming:
            room = data.wiserhub.rooms.get_by_id(device_id)
            return f"{ENTITY_PREFIX} {room.name}"
        return f"{ENTITY_PREFIX} Room"

    else:
        return f"{ENTITY_PREFIX} {device_type}"


def get_legacy_device_name(data, device_id):
    """Return a physical device name used by historical entity unique IDs."""
    device = data.wiserhub.devices.get_by_id(device_id)
    device_room = data.wiserhub.rooms.get_by_device_id(device_id)

    if device.product_type == "iTRV":
        if device_room:
            if device_room.number_of_smartvalves > 1:
                index = device_room.smartvalve_ids.index(device.id) + 1
                return (
                    f"{ENTITY_PREFIX} {device.product_type} "
                    f"{device_room.name}-{index}"
                )
            return f"{ENTITY_PREFIX} {device.product_type} {device_room.name}"
        return f"{ENTITY_PREFIX} {device.product_type} {device.id}"

    if device.product_type == "RoomStat":
        if device_room:
            return f"{ENTITY_PREFIX} Thermostat {device_room.name}"
        return f"{ENTITY_PREFIX} Thermostat {device.id}"

    if device.product_type in {"HeatingActuator", "CFMT"}:
        if device_room:
            if device_room.number_of_heating_actuators > 1:
                index = device_room.heating_actuator_ids.index(device.id) + 1
                return (
                    f"{ENTITY_PREFIX} {device.product_type} "
                    f"{device_room.name}-{index}"
                )
            return f"{ENTITY_PREFIX} {device.product_type} {device_room.name}"
        return f"{ENTITY_PREFIX} {device.product_type} {device.id}"

    if device.product_type in {"SmokeAlarmDevice", "ButtonPanel"}:
        if device_room:
            return f"{ENTITY_PREFIX} {device_room.name} {device.name}"
        return f"{ENTITY_PREFIX} {device.name} {device.id}"

    if device.product_type == "TemperatureHumiditySensor" and device_room:
        return (
            f"{ENTITY_PREFIX} {device.product_type} "
            f"{device_room.name} {device.name}"
        )
    if device.product_type in {
        "Shutter",
        "OnOffLight",
        "DimmableLight",
        "WindowDoorSensor",
        "WaterLeakageSensor",
        "MotionLightSensor",
        "TemperatureHumiditySensor",
    }:
        if device_room:
            return (
                f"{ENTITY_PREFIX} {device.product_type} "
                f"{device_room.name} {device.name}"
            )
        return f"{ENTITY_PREFIX} {device.product_type} {device.name}"

    return get_device_name(data, device_id)


def get_identifier(data, device_id, device_type="device"):
    if device_type == "room":
        return f"{data.wiserhub.system.name} room {device_id}"
    if device_id == 0 and device_type == "device":
        # Preserve the historical Controller identifier for registry migration.
        device_name = f"{ENTITY_PREFIX} HeatHub ({data.wiserhub.system.name})"
    elif device_type == "device":
        # A physical device can move between rooms or be renamed without
        # becoming a new Home Assistant device.
        return f"{data.wiserhub.system.name} device {device_id}"
    else:
        device_name = get_device_name(data, device_id, device_type)
    return f"{data.wiserhub.system.name} {device_name}"


def get_legacy_device_identifier(data, device_id):
    """Return the former name-derived identifier for a physical device."""
    device = data.wiserhub.devices.get_by_id(device_id)
    if device.product_type == "RoomStat":
        device_room = data.wiserhub.rooms.get_by_device_id(device_id)
        if device_room:
            device_name = f"{ENTITY_PREFIX} RoomStat {device_room.name}"
        else:
            device_name = f"{ENTITY_PREFIX} RoomStat {device.id}"
    elif device.product_type == "TemperatureHumiditySensor":
        device_name = get_legacy_device_name(data, device_id)
    elif device.product_type == "iTRV":
        device_room = data.wiserhub.rooms.get_by_device_id(device_id)
        if device_room:
            if device_room.number_of_smartvalves > 1:
                index = device_room.smartvalve_ids.index(device.id) + 1
                device_name = (
                    f"{ENTITY_PREFIX} {device.product_type} "
                    f"{device_room.name}-{index}"
                )
            else:
                device_name = (
                    f"{ENTITY_PREFIX} {device.product_type} {device_room.name}"
                )
        else:
            device_name = f"{ENTITY_PREFIX} {device.product_type} {device.id}"
    else:
        device_name = get_legacy_device_name(data, device_id)
    return f"{data.wiserhub.system.name} {device_name}"


def get_legacy_room_identifier(data, room_id):
    """Return the former name-derived identifier for a Wiser room device."""
    room = data.wiserhub.rooms.get_by_id(room_id)
    return f"{data.wiserhub.system.name} {ENTITY_PREFIX} {room.name}"


def get_device_area_info(data, device_id):
    """Return a Wiser room as a Home Assistant creation-time area suggestion."""
    room = data.wiserhub.rooms.get_by_device_id(device_id)
    if room is None:
        return {}
    return {"suggested_area": room.name}


def get_hub_device_info(data):
    """Return device registry information for the physical HeatHub."""
    return {
        "name": get_hub_device_name(data),
        "identifiers": {(DOMAIN, data.wiserhub.system.name)},
        "manufacturer": MANUFACTURER,
        "model": data.wiserhub.system.model,
        "sw_version": data.wiserhub.system.firmware_version,
    }


def get_hub_via_device_info(data):
    """Return the HeatHub parent supported by this Home Assistant version."""
    if (MAJOR_VERSION, MINOR_VERSION) >= (2026, 8):
        hub_device_id = getattr(data, "hub_device_id", None)
        if hub_device_id is not None:
            return {"via_device_id": hub_device_id}
    return {"via_device": (DOMAIN, data.wiserhub.system.name)}


def get_legacy_unique_id(data, device_type, entity_type, device_id):
    """Return the entity unique ID used before deterministic UUIDs."""
    return f"{data.wiserhub.system.name}-{device_type}-{entity_type}-{device_id}"


def get_uuid_unique_id(legacy_unique_id: str) -> str:
    """Return the deterministic UUIDv5 replacement for a legacy unique ID."""
    return str(uuid5(ENTITY_UNIQUE_ID_NAMESPACE, legacy_unique_id))


def get_unique_id(data, device_type, entity_type, device_id):
    """Return a deterministic UUIDv5 entity unique ID."""
    return get_uuid_unique_id(
        get_legacy_unique_id(data, device_type, entity_type, device_id)
    )


def get_physical_entity_unique_id(data, domain, device_id, entity_type):
    """Return a name-independent unique ID for a physical-device entity."""
    return get_unique_id(data, domain, entity_type, device_id)


def get_room_entity_unique_id(data, room_id, entity_type):
    """Return a room-name-independent unique ID for a room entity."""
    return get_unique_id(data, "room", entity_type, room_id)


def get_light_binary_sensor_unique_id(data, light, sensor_type):
    """Return the stable per-channel ID for a light capability sensor."""
    return get_unique_id(
        data,
        "binary_sensor",
        sensor_type,
        light.light_id,
    )


def build_physical_entity_unique_id_migration(
    data,
    previous_room_names=None,
    legacy_device_names_by_id=None,
    device_ids=None,
) -> dict:
    """Map mutable-name physical entity IDs to immutable device-based IDs."""
    mapping = {}
    previous_room_names = previous_room_names or {}
    legacy_device_names_by_id = legacy_device_names_by_id or {}
    binary_sensor_types = (
        "Smoke Alarm",
        "Heat Alarm",
        "Tamper Alarm",
        "Fault Warning",
        "Remote Alarm",
        "Battery Defect",
        "Controllable",
        "PCM Mode",
        "Is Tilt Supported",
        "Is Open",
        "Is Closed",
        "Active",
    )

    for device in data.wiserhub.devices.all:
        if device_ids is not None and device.id not in device_ids:
            continue
        device_names = set(legacy_device_names_by_id.get(device.id, ()))
        device_names.add(get_legacy_device_name(data, device.id))
        product_type = device.product_type
        room = data.wiserhub.rooms.get_by_device_id(device.id)
        possible_room_names = {room.name} if room is not None else set()
        if room is not None and (
            previous_name := previous_room_names.get(str(room.id))
        ):
            possible_room_names.add(previous_name)

        if product_type == "RoomStat":
            for room_name in possible_room_names:
                mapping[
                    get_unique_id(
                        data,
                        "sensor",
                        f"LTS Humidity {room_name}",
                        device.id,
                    )
                ] = get_physical_entity_unique_id(
                    data, "sensor", device.id, "humidity"
                )

        power_device_names = possible_room_names or {
            f"{product_type} {device.id}"
        }
        historical_power_types = {
            "Power": "power",
            "Total Power": "energy",
            "Equipment Power ": "power",
            "Equipment Total Energy ": "energy",
            "Power ": "power",
            "Energy Delivered ": "energy",
            "Energy Received ": "energy_received",
        }
        for power_device_name in power_device_names:
            historical_power_types.update(
                {
                    f"LTS Power {power_device_name}": "power",
                    f"LTS Energy {power_device_name}": "energy",
                }
            )
        for old_entity_type, new_entity_type in historical_power_types.items():
            mapping[
                get_unique_id(data, "sensor", old_entity_type, device.id)
            ] = get_physical_entity_unique_id(
                data, "sensor", device.id, new_entity_type
            )

        # Light capability sensors are keyed by channel ``light_id`` and have
        # their own migration below. A multi-gang dimmer shares one physical
        # device ID, so treating these as ordinary physical-device sensors
        # would merge distinct channels.
        if product_type not in {"DimmableLight", "OnOffLight"}:
            for device_name in device_names:
                for sensor_type in binary_sensor_types:
                    old_name = f"{device_name} {sensor_type}"
                    mapping[
                        get_unique_id(
                            data, "binary_sensor", sensor_type, old_name
                        )
                    ] = get_physical_entity_unique_id(
                        data, "binary_sensor", device.id, sensor_type
                    )

        if product_type == "Shutter":
            for device_name in device_names:
                old_cover_id = get_uuid_unique_id(
                    f"{data.wiserhub.system.name}-Wisershutter-"
                    f"{device.id}-{device_name} Control"
                )
                mapping[old_cover_id] = get_physical_entity_unique_id(
                    data, "cover", device.id, "control"
                )
                for label, entity_type in (
                    ("Away Mode Closes", "away_mode_closes"),
                    ("Respect Summer Comfort", "respect_summer_comfort"),
                ):
                    mapping[
                        get_unique_id(
                            data,
                            product_type,
                            f"{device_name} {label}",
                            device.id,
                        )
                    ] = get_physical_entity_unique_id(
                        data, "switch", device.id, entity_type
                    )

        if product_type in {"HeatingActuator", "CFMT"}:
            for device_name in device_names:
                mapping[
                    get_unique_id(
                        data,
                        "system",
                        "number",
                        f"{device_name} Floor Temp Offset",
                    )
                ] = get_physical_entity_unique_id(
                    data, "number", device.id, "floor_temperature_offset"
                )

        if product_type in {"SmartPlug", "PowerTagC"}:
            for device_name in device_names:
                mapping[
                    get_unique_id(
                        data,
                        product_type,
                        f"{device_name} Switch",
                        device.id,
                    )
                ] = get_physical_entity_unique_id(
                    data, "switch", device.id, "outlet"
                )
                mapping[
                    get_unique_id(
                        data,
                        product_type,
                        f"{device_name} Away Mode Turns Off",
                        device.id,
                    )
                ] = get_physical_entity_unique_id(
                    data, "switch", device.id, "away_mode_turns_off"
                )

        if hasattr(device, "interacts_with_room_climate"):
            suffix = "Interacts With Room Climate"
            for device_name in device_names:
                old_id = get_legacy_unique_id(
                    data,
                    product_type,
                    f"{device_name} {suffix}",
                    device.id,
                )
                mapping[get_uuid_unique_id(old_id)] = (
                    get_physical_entity_unique_id(
                        data,
                        "switch",
                        device.id,
                        "interacts_with_room_climate",
                    )
                )

        for ancillary in getattr(device, "threshold_sensors", ()):
            suffix = f"{ancillary.quantity} Interacts With Room Climate"
            for device_name in device_names:
                old_id = get_legacy_unique_id(
                    data,
                    product_type,
                    f"{device_name} {suffix}",
                    device.id,
                )
                mapping[get_uuid_unique_id(f"{old_id}_{ancillary.id}")] = (
                    get_physical_entity_unique_id(
                        data,
                        "switch",
                        device.id,
                        f"{ancillary.quantity.lower()}_"
                        f"interacts_with_room_climate_{ancillary.id}",
                    )
                )

    return mapping


def build_light_unique_id_migration(data) -> dict:
    """Map pre-#683 light unique_ids to the new per-channel light_id scheme.

    The multi-gang dimmer fix keys every light-derived entity on the unique
    per-channel ``light_id`` (hub Lighting section) instead of the physical
    device ``id`` (hub Devices section). Those id spaces differ even for
    single-gang lights, so the unique_ids of the light, its mode/LED/power-on
    selects, its away-mode switch and its four capability binary_sensors all
    change on update. Returns ``{old_unique_id: new_unique_id}`` so the caller
    can rename the existing registry entries and preserve them.

    Multi-gang dimmer channels are skipped: before the fix their light and
    select platforms crashed and their other entities collided on unique_id,
    so their pre-fix registry state is ambiguous. They are left to orphan.
    """
    lights = data.wiserhub.devices.lights.all
    if not lights:
        return {}

    # A physical device id shared by more than one light == multi-gang dimmer.
    device_id_counts = Counter(light.id for light in lights)

    mapping: dict[str, str] = {}
    for light in lights:
        if device_id_counts[light.id] > 1:
            continue  # multi-gang: pre-fix state ambiguous, skip

        old_id = light.id
        new_id = light.light_id
        ptype = light.product_type
        old_name = get_legacy_device_name(data, old_id)
        new_name = f"{ENTITY_PREFIX} {light.name}"

        # light (name-based -> light_id-based)
        mapping[get_unique_id(data, "device", "light", f"{old_name} Light")] = (
            get_unique_id(data, "device", "light", new_id)
        )

        # light selects (id-based; entity_type stable, only the id changes)
        for kind in ("mode-select", "led-indicator", "power_on_behaviour_select"):
            mapping[get_unique_id(data, ptype, kind, old_id)] = get_unique_id(
                data, ptype, kind, new_id
            )

        # away-mode switch (both name and id embedded in the unique_id)
        mapping[
            get_unique_id(data, ptype, f"{old_name} Away Mode Turns Off", old_id)
        ] = get_physical_entity_unique_id(
            data, "switch", new_id, "light_away_mode_turns_off"
        )
        mapping[
            get_unique_id(data, ptype, f"{new_name} Away Mode Turns Off", new_id)
        ] = get_physical_entity_unique_id(
            data, "switch", new_id, "light_away_mode_turns_off"
        )

        # capability binary_sensors (name-based)
        for stype in LIGHT_BINARY_SENSOR_TYPES:
            mapping[
                get_unique_id(data, "binary_sensor", stype, f"{old_name} {stype}")
            ] = get_light_binary_sensor_unique_id(data, light, stype)

    # Drop no-ops where the two id spaces happen to coincide for a light.
    return {old: new for old, new in mapping.items() if old != new}


def get_instance_count(hass: HomeAssistant) -> int:
    entries = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if not entry.disabled_by
    ]
    return len(entries)


def is_wiser_config_id(hass: HomeAssistant, config_id):
    entry = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.entry_id == config_id
    ]
    if entry:
        return True
    return False


def get_config_entry_id_by_name(hass: HomeAssistant, name) -> str or None:
    entry = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.title == name
    ]
    if entry:
        return entry[0].entry_id
    return None
