"""Helper functions for Wiser integration."""
from dataclasses import dataclass
from functools import reduce
from typing import Any

from aioWiserHeatAPI.devices import PRODUCT_TYPE_CONFIG
from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom

from homeassistant.core import HomeAssistant

from .const import DOMAIN, ENTITY_PREFIX


@dataclass
class WiserAttribute:
    """Class to hold attribute definition."""

    path: str


@dataclass
class WiserHubAttribute(WiserAttribute):
    """Hub attribute definition."""


@dataclass
class WiserDeviceAttribute(WiserAttribute):
    """Device attribute definition."""


def _get_class_by_product_type(product_type: str):
    """Return object class for product type."""
    return PRODUCT_TYPE_CONFIG.get(product_type, {}).get("class")


def get_entity_name(data, device: Any = None):
    """Return name for Wier device."""
    if not device:
        # This is a system entity
        return f"{ENTITY_PREFIX} HeatHub ({data.wiserhub.system.name})"

    if isinstance(device, _WiserDevice):
        if isinstance(device, _get_class_by_product_type("iTRV")):
            device_room = data.wiserhub.rooms.get_by_device_id(device.id)
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

        if isinstance(device, _get_class_by_product_type("HeatingActuator")):
            device_room = data.wiserhub.rooms.get_by_device_id(device.id)
            # If device not allocated to a room return type and id only
            if device_room:
                # To enable creating seperate devices for multiple Heating Actuators in a room
                if device_room.number_of_heating_actuators > 1:
                    # Get index of iTRV in room so they are numbered 1,2 etc instead of device id
                    # 1 is lowest device id, 2 next lowest etc
                    ha_index = device_room.heating_actuator_ids.index(device.id) + 1
                    return f"{ENTITY_PREFIX} {device.product_type} {device_room.name}-{ha_index}"
                device_room = data.wiserhub.rooms.get_by_device_id(device.id)
                return f"{ENTITY_PREFIX} {device.product_type} {device_room.name}"
            return f"{ENTITY_PREFIX} {device.product_type} {device.id}"

        if isinstance(
            device,
            _get_class_by_product_type("Shutter")
            | _get_class_by_product_type("OnOffLight")
            | _get_class_by_product_type("DimmableLight")
            | _get_class_by_product_type("SmokeAlarmDevice"),
        ):
            device_room = data.wiserhub.rooms.get_by_device_id(device.id)
            # If device not allocated to a room return type and id only
            if device_room:
                return f"{ENTITY_PREFIX} {device.product_type} {device_room.name} {device.name}"
            return f"{ENTITY_PREFIX} {device.product_type} {device.name}"

        if isinstance(device, _get_class_by_product_type("RoomStat")):
            device_room = data.wiserhub.rooms.get_by_device_id(device.id)
            # If device not allocated to a room return type and id only
            if device_room:
                return f"{ENTITY_PREFIX} {device.product_type} {device_room.name}"
            return f"{ENTITY_PREFIX} {device.product_type} {device.name}"

        if isinstance(
            device,
            _get_class_by_product_type("UnderFloorHeating")
            | _get_class_by_product_type("SmartPlug")
            | _get_class_by_product_type("PowerTagE"),
        ):
            return f"{ENTITY_PREFIX} {device.name}"

        return f"{ENTITY_PREFIX} {device.serial_number}"

    elif isinstance(device, _WiserRoom):
        return f"{ENTITY_PREFIX} {device.name}"

    else:
        return f"{ENTITY_PREFIX} HeatHub ({data.wiserhub.system.name})"


def get_identifier(data, device: _WiserDevice | _WiserRoom | None = None):
    """Get identifier for Wiser device."""
    return f"{data.wiserhub.system.name} {get_entity_name(data, device)}"


def get_unique_id(data, device_type, entity_type, device_id):
    """Get unique id for device."""

    return f"{data.wiserhub.system.name}-{device_type}-{entity_type}-{device_id}"


def get_room_name(data, room_id):
    """Get room name that device belongs to."""
    return f"{ENTITY_PREFIX} {data.wiserhub.rooms.get_by_id(room_id).name}"


def get_device_by_node_id(data, node_id: int):
    """Get a device from a zigbee node id."""
    return data.wiserhub.devices.get_by_node_id(node_id)


def get_hot_water_operation_mode(device) -> str:
    """Get hotwater operation mode."""
    preset = None
    mode = "Manual" if device.mode != "Auto" else "Auto"
    if device.is_boosted:
        preset = f"Boost {int(device.boost_time_remaining/60)}m"
    elif device.is_override:
        preset = "Override"
    elif device.is_away_mode:
        preset = "Away Mode"

    return f"{mode}{' - ' + preset if preset else ''}"


def get_instance_count(hass: HomeAssistant) -> int:
    """Get instance of integrations loaded."""
    entries = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if not entry.disabled_by
    ]
    return len(entries)


def is_wiser_config_id(hass: HomeAssistant, config_id):
    """Get of config id belongs to Wiser integration."""
    entry = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.entry_id == config_id
    ]
    if entry:
        return True
    return False


def get_config_entry_id_by_name(hass: HomeAssistant, name) -> str or None:
    """Get a config entry id from a config entry name."""
    entry = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.title == name
    ]
    if entry:
        return entry[0].entry_id
    return None


def getattrd(obj, name):
    """Return dot notation attribute lookup."""
    try:
        return reduce(getattr, name.split("."), obj)
    except AttributeError:
        return None
