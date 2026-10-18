"""Track whether a Wiser hub has a confirmed OpenTherm connection."""

from math import isfinite

from .const import (
    CONF_OPENTHERM_EVER_CONNECTED,
    CONF_OPENTHERM_HOT_WATER_CAPABLE,
    CONF_OPENTHERM_HOT_WATER_CONTROL,
)
from .helpers import get_unique_id
from .opentherm import (
    OPENTHERM_BINARY_SENSOR_KEYS,
    OPENTHERM_SENSOR_NAMES,
)


def opentherm_is_detected(config_entry, opentherm) -> bool:
    """Return whether OpenTherm is connected now or has connected before.

    This sticky predicate controls entity creation and registry visibility so a
    temporary outage does not discard entities or history. Entity availability
    deliberately continues to require live OpenTherm data.
    """
    return bool(
        opentherm
        and (
            config_entry.data.get(CONF_OPENTHERM_EVER_CONNECTED, False)
            or getattr(opentherm, "connection_status", None) == "Connected"
        )
    )


def opentherm_hot_water_control_is_supported(config_entry, opentherm) -> bool:
    """Return whether this entry has confirmed writable DHW support.

    An already-enabled option also counts as prior confirmation. This preserves
    the entity across an upgrade or restart where the first OpenTherm response
    is incomplete, before the new sticky capability flag has been stored.
    """
    boiler_parameters = getattr(opentherm, "boiler_parameters", None)
    return bool(
        opentherm
        and (
            getattr(boiler_parameters, "hw_setpoint_read_write", None) is True
            or config_entry.data.get(CONF_OPENTHERM_HOT_WATER_CAPABLE, False)
            or config_entry.options.get(CONF_OPENTHERM_HOT_WATER_CONTROL, False)
        )
    )


def opentherm_hot_water_limits(opentherm) -> tuple[float, float]:
    """Return a valid boiler DHW setpoint range with safe fallbacks."""
    boiler_parameters = getattr(opentherm, "boiler_parameters", None)
    try:
        minimum = float(
            getattr(boiler_parameters, "hw_setpoint_lower_bound", None)
        )
        maximum = float(
            getattr(boiler_parameters, "hw_setpoint_upper_bound", None)
        )
    except (TypeError, ValueError):
        return 35.0, 55.0
    if not isfinite(minimum) or not isfinite(maximum) or minimum > maximum:
        return 35.0, 55.0
    return minimum, maximum


def opentherm_entity_unique_ids(data):
    """Return the entity-registry IDs reserved for OpenTherm entities."""
    sensor_types = {
        "LTS Boiler Flow Temperature",
        "LTS Boiler Return Temperature",
    }
    binary_sensor_types = {
        f"opentherm_{key}" for key in OPENTHERM_BINARY_SENSOR_KEYS
    }

    for key in OPENTHERM_SENSOR_NAMES:
        if key in OPENTHERM_BINARY_SENSOR_KEYS or key in {
            "ch_flow_temperature",
            "ch_return_temperature",
        }:
            continue
        sensor_types.add(
            "relative_modulation_level"
            if key == "relative_modulation_level"
            else f"opentherm_{key}"
        )

    unique_ids = {
        ("sensor", get_unique_id(data, "sensor", sensor_type, 0))
        for sensor_type in sensor_types
    }
    unique_ids.update(
        (
            "binary_sensor",
            get_unique_id(data, "binary_sensor", sensor_type, 0),
        )
        for sensor_type in binary_sensor_types
    )
    return unique_ids
