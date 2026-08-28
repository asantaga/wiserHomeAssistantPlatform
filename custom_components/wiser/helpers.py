from aioWiserHeatAPI.wiserhub import (
    WiserHubConnectionError,
    WiserHubAuthenticationError,
    WiserHubRESTError,
)
from homeassistant.core import HomeAssistant
from .const import DOMAIN, ENTITY_PREFIX, MANUFACTURER
import logging
import re

_LOGGER = logging.getLogger(__name__)


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


def get_hub_entity_object_id(data, entity_name):
    """Return the MAC-derived entity portion of a new hub object ID."""
    entity_slug = re.sub(r"[^a-z0-9]+", "_", str(entity_name).lower()).strip("_")
    # Home Assistant adds the area and device portions. Supplying them here too
    # would produce IDs such as ``wiser_heathub_wiser_heathub_...`` when users
    # recreate entity IDs from the device page.
    return f"{get_hub_mac_suffix(data).lower()}_{entity_slug}"


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
    if device_type == "device":
        device = data.wiserhub.devices.get_by_id(device_id)

        if device_id == 0:
            return get_hub_device_name(data)

        if device.product_type == "iTRV":
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
                return f"{ENTITY_PREFIX} Thermostat"
            return f"{ENTITY_PREFIX} Thermostat {device.id}"

        if device.product_type == "UnderFloorHeating":
            return f"{ENTITY_PREFIX} {device.name}"

        if device.product_type in ["HeatingActuator", "CFMT"]:
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
            if device_room:
                return f"{ENTITY_PREFIX} {device_room.name} {device.name}"
            return f"{ENTITY_PREFIX} {device.name} {device.id}"

        if device.product_type == "BoilerInterface":
            return f"{ENTITY_PREFIX} {device.product_type} {device.name}"

        if device.product_type == "TemperatureHumiditySensor":
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
            if device_room:
                return f"{ENTITY_PREFIX} {device.product_type} {device_room.name} {device.name}"
            return f"{ENTITY_PREFIX} {device.product_type} {device.name}"

        return f"{ENTITY_PREFIX} {device.serial_number}"

    elif device_type == "room":
        return f"{ENTITY_PREFIX} Room"

    else:
        return f"{ENTITY_PREFIX} {device_type}"


def get_legacy_device_name(data, device_id):
    """Return a physical device name used by historical entity unique IDs."""
    device = data.wiserhub.devices.get_by_id(device_id)
    if device.product_type != "TemperatureHumiditySensor":
        return get_device_name(data, device_id)

    device_room = data.wiserhub.rooms.get_by_device_id(device_id)
    if device_room:
        return (
            f"{ENTITY_PREFIX} {device.product_type} "
            f"{device_room.name} {device.name}"
        )
    return f"{ENTITY_PREFIX} {device.product_type} {device.name}"


def get_identifier(data, device_id, device_type="device"):
    if device_type == "room":
        return f"{data.wiserhub.system.name} room {device_id}"
    if device_id == 0 and device_type == "device":
        # Preserve the historical Controller identifier for registry migration.
        device_name = f"{ENTITY_PREFIX} HeatHub ({data.wiserhub.system.name})"
    elif device_type == "device" and (
        device := data.wiserhub.devices.get_by_id(device_id)
    ).product_type == "RoomStat":
        # Preserve the existing name-derived identifier while modernising the
        # RoomStat's display name.
        device_room = data.wiserhub.rooms.get_by_device_id(device_id)
        if device_room:
            device_name = f"{ENTITY_PREFIX} RoomStat {device_room.name}"
        else:
            device_name = f"{ENTITY_PREFIX} RoomStat {device.id}"
    elif (
        device_type == "device"
        and device.product_type == "TemperatureHumiditySensor"
    ):
        # Preserve the former name-derived identifier while modernising the
        # physical sensor's display name.
        device_name = get_legacy_device_name(data, device_id)
    else:
        device_name = get_device_name(data, device_id, device_type)
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


def get_unique_id(data, device_type, entity_type, device_id):
    return f"{data.wiserhub.system.name}-{device_type}-{entity_type}-{device_id}"


def get_room_name(data, room_id):
    return f"{ENTITY_PREFIX} {data.wiserhub.rooms.get_by_id(room_id).name}"


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
