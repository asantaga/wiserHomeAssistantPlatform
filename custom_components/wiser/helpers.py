"""Helper functions for Wiser integration."""

from collections.abc import Callable
from functools import reduce
from inspect import signature
import logging
from typing import Any

from aioWiserHeatAPI.const import TEXT_UNKNOWN
from aioWiserHeatAPI.devices import PRODUCT_TYPE_CONFIG
from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom

from homeassistant.core import HomeAssistant

from .const import DOMAIN, ENTITY_PREFIX, MANUFACTURER, MANUFACTURER_SCHNEIDER

_LOGGER = logging.getLogger(__name__)


def _get_class_by_product_type(product_type: str):
    """Return object class for product type."""
    return PRODUCT_TYPE_CONFIG.get(product_type, {}).get("class")


def get_callable_value(data, device, func: Callable):
    """Get return value from lambda callable."""
    no_of_params = len(signature(func).parameters)
    try:
        if no_of_params == 2:
            return func(device, data.wiserhub)
        return func(device)
    except AttributeError:
        return None


def get_config_entry_id_by_name(hass: HomeAssistant, name) -> str | None:
    """Get a config entry id from a config entry name."""
    entry = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.title == name
    ]
    if entry:
        return entry[0].entry_id
    return None


def get_device_by_node_id(data, node_id: int):
    """Get a device from a zigbee node id."""
    return data.wiserhub.devices.get_by_node_id(node_id)


def get_entities(data, entity_descs: tuple, entity_class) -> list:
    """Get entities to add from entity description tuple."""
    entities = []

    for entity_desc in entity_descs:
        if entity_desc.device_collection:
            # Add all entities from device collection
            if getattrd(data.wiserhub, entity_desc.device_collection):
                entities.extend(
                    [
                        entity_class(data, entity_desc, device)
                        for device in getattrd(
                            data.wiserhub, entity_desc.device_collection
                        ).all
                        if entity_desc.supported(device, data.wiserhub)
                        and value_attr_exist(device, entity_desc)
                    ]
                )
        else:
            # Add individual entities
            device = getattrd(data.wiserhub, entity_desc.device)
            if entity_desc.supported(device, data.wiserhub) and value_attr_exist(
                device, entity_desc
            ):
                entities.append(
                    entity_class(
                        data,
                        entity_desc,
                        device,
                    )
                )
    return entities


def get_entity_name(data, device: Any = None, name: str | None = None):
    """Return name for Wier device."""
    if not device or device.id == 0:
        return f"{ENTITY_PREFIX} Hub"

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
            | _get_class_by_product_type("DimmableLight"),
        ):
            device_room = data.wiserhub.rooms.get_by_device_id(device.id)
            # If device not allocated to a room return type and id only
            if device_room:
                return f"{ENTITY_PREFIX} {device.product_type} {device_room.name} {device.name}"
            return f"{ENTITY_PREFIX} {device.product_type} {device.name}"

        if isinstance(device, _get_class_by_product_type("SmokeAlarmDevice")):
            device_room = data.wiserhub.rooms.get_by_device_id(device.id)
            if device_room:
                return f"{ENTITY_PREFIX} {device.product_type} {device_room.name}"
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
            if device.name != TEXT_UNKNOWN:
                return f"{ENTITY_PREFIX} {device.name}"
            return f"{ENTITY_PREFIX} {device.id}"

        return f"{ENTITY_PREFIX} {device.serial_number}"

    if isinstance(device, _WiserRoom):
        return f"{ENTITY_PREFIX} {device.name}"

    # return f"{ENTITY_PREFIX} HeatHub ({data.wiserhub.system.name})"
    return f"{ENTITY_PREFIX} Hub"


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


def get_identifier(data, device: _WiserDevice | _WiserRoom | None = None):
    """Get identifier for Wiser device."""
    return f"{data.wiserhub.system.name} {get_entity_name(data, device)}"


def get_instance_count(hass: HomeAssistant) -> int:
    """Get instance of integrations loaded."""
    entries = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if not entry.disabled_by
    ]
    return len(entries)


def get_room_name(data, room_id):
    """Get room name that device belongs to."""
    return f"{ENTITY_PREFIX} {data.wiserhub.rooms.get_by_id(room_id).name}"


def get_unique_id(data, device_type, entity_type, device_id):
    """Get unique id for device."""

    return f"{data.wiserhub.system.name}-{device_type}-{entity_type}-{device_id}"


def get_vendor_name(device) -> str:
    """Get correct vendor name for device."""
    if isinstance(
        device,
        _get_class_by_product_type("Shutter")
        | _get_class_by_product_type("OnOffLight")
        | _get_class_by_product_type("DimmableLight")
        | _get_class_by_product_type("PowerTagE"),
    ):
        return MANUFACTURER_SCHNEIDER
    return MANUFACTURER


def getattrd(obj, name):
    """Return dot notation attribute lookup."""
    try:
        return reduce(getattr, name.split("."), obj)
    except AttributeError:
        return None


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


def value_attr_exist(device, entity_desc) -> bool:
    """Check if an attribute exists for device."""
    if entity_desc.value_fn:
        try:
            r = entity_desc.value_fn(device)
            return bool(r is not None and r != TEXT_UNKNOWN)
        except AttributeError:
            return False
    return True
