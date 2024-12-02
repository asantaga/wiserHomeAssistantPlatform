from aioWiserHeatAPI.wiserhub import (
    WiserHubConnectionError,
    WiserHubAuthenticationError,
    WiserHubRESTError,
)
from homeassistant.core import HomeAssistant
from .const import DOMAIN, ENTITY_PREFIX
import logging

_LOGGER = logging.getLogger(__name__)


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
            return f"{ENTITY_PREFIX} HeatHub ({data.wiserhub.system.name})"

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
            # If device not allocated to a room return type and id only
            if device_room:
                return f"{ENTITY_PREFIX} {device.product_type} {device_room.name}"
            return f"{ENTITY_PREFIX} {device.product_type} {device.id}"

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
        room = data.wiserhub.rooms.get_by_id(device_id)
        return f"{ENTITY_PREFIX} {room.name}"

    else:
        return f"{ENTITY_PREFIX} {device_type}"


def get_identifier(data, device_id, device_type="device"):
    return (
        f"{data.wiserhub.system.name} {get_device_name(data, device_id, device_type)}"
    )


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
