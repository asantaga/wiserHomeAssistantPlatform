"""Track whether a Wiser hub has a confirmed OpenTherm connection."""

from .const import CONF_OPENTHERM_EVER_CONNECTED
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
