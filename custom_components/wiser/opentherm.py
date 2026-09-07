"""Compatibility helpers for OpenTherm writes in aioWiserHeatAPI 1.7.3."""

import json
import math
import re

from aioWiserHeatAPI.const import (
    OPENTHERMV2_MIN_VERSION,
    WISERHUBOPENTHERM,
    WISERHUBOPENTHERMV2,
)
from aioWiserHeatAPI.rest_controller import WiserRestActionEnum


# Parameters exposed by the action UI that live below the OpenTherm root.
# Explicit endpoints remain supported for backwards-compatible YAML calls.
OPENTHERM_PARAMETER_ENDPOINTS = {
    "dhwSetpoint": "preDefinedRemoteBoilerParameters",
    "maxChSetpoint": "preDefinedRemoteBoilerParameters",
}

# Feedback fields for the temperature parameters exposed by the action UI.
# Values written by the API use tenths of a degree; these fields report °C.
OPENTHERM_PARAMETER_FEEDBACK = {
    "chFlowActiveLowerSetpoint": ("", ("ch_flow_active_lower_setpoint",)),
    "chFlowActiveUpperSetpoint": ("", ("ch_flow_active_upper_setpoint",)),
    "dhwFlowSetpoint": ("", ("hw_flow_setpoint",)),
    "dhwSetpoint": (
        "preDefinedRemoteBoilerParameters",
        ("boiler_parameters", "hw_setpoint"),
    ),
    "maxChSetpoint": (
        "preDefinedRemoteBoilerParameters",
        ("boiler_parameters", "ch_setpoint"),
    ),
}


# Attributes currently exposed on the boiler flow-temperature entity.  Keeping
# the paths in one place lets the options flow discover what a particular hub
# reports and lets the sensor platform expose selected values as entities.
OPENTHERM_SENSOR_PATHS = {
    "ch_flow_active_lower_setpoint": ("ch_flow_active_lower_setpoint",),
    "ch_flow_active_upper_setpoint": ("ch_flow_active_upper_setpoint",),
    "ch1_flow_enabled": ("ch1_flow_enabled",),
    "ch1_flow_setpoint": ("ch1_flow_setpoint",),
    "ch2_flow_enabled": ("ch2_flow_enabled",),
    "ch2_flow_setpoint": ("ch2_flow_setpoint",),
    "connection_status": ("connection_status",),
    "hw_enabled": ("hw_enabled",),
    "hw_flow_setpoint": ("hw_flow_setpoint",),
    "operating_mode": ("operating_mode",),
    "tracked_room_id": ("tracked_room_id",),
    "room_setpoint": ("room_setpoint",),
    "room_temperature": ("room_temperature",),
    "ch_flow_temperature": ("operational_data", "ch_flow_temperature"),
    "ch_pressure_bar": ("operational_data", "ch_pressure_bar"),
    "ch_return_temperature": ("operational_data", "ch_return_temperature"),
    # Delta-T is derived from this flow reading and the return reading. Its
    # discovery check below explicitly requires both source attributes.
    "delta_t": ("operational_data", "ch_flow_temperature"),
    "relative_modulation_level": ("operational_data", "relative_modulation_level"),
    "hw_temperature": ("operational_data", "hw_temperature"),
    "hw_flow_rate": ("operational_data", "hw_flow_rate"),
    "slave_status": ("operational_data", "slave_status"),
    "boiler_fault": ("operational_data", "slave_status"),
    "central_heating_active": ("operational_data", "slave_status"),
    "hot_water_active": ("operational_data", "slave_status"),
    "flame_active": ("operational_data", "slave_status"),
    "flame_statistics": ("operational_data", "slave_status"),
    "cooling_active": ("operational_data", "slave_status"),
    "central_heating_2_active": ("operational_data", "slave_status"),
    "diagnostic_event": ("operational_data", "slave_status"),
    "boiler_ch_max_setpoint_read_write": (
        "boiler_parameters",
        "ch_max_setpoint_read_write",
    ),
    "boiler_ch_max_setpoint_transfer_enable": (
        "boiler_parameters",
        "ch_max_setpoint_transfer_enable",
    ),
    "boiler_ch_setpoint": ("boiler_parameters", "ch_setpoint"),
    "boiler_ch_setpoint_lower_bound": (
        "boiler_parameters",
        "ch_setpoint_lower_bound",
    ),
    "boiler_ch_setpoint_upper_bound": (
        "boiler_parameters",
        "ch_setpoint_upper_bound",
    ),
    "boiler_hw_setpoint_read_write": (
        "boiler_parameters",
        "hw_setpoint_read_write",
    ),
    "boiler_hw_setpoint_transfer_enable": (
        "boiler_parameters",
        "hw_setpoint_transfer_enable",
    ),
    "boiler_hw_setpoint": ("boiler_parameters", "hw_setpoint"),
    "boiler_hw_setpoint_lower_bound": (
        "boiler_parameters",
        "hw_setpoint_lower_bound",
    ),
    "boiler_hw_setpoint_upper_bound": (
        "boiler_parameters",
        "hw_setpoint_upper_bound",
    ),
}

# These are the two OpenTherm entities that existed before the configurable
# attribute sensors.  All additional entities are opt-in.
DEFAULT_OPENTHERM_SENSOR_KEYS = frozenset(
    {"ch_flow_temperature", "ch_return_temperature"}
)

OPENTHERM_BINARY_SENSOR_KEYS = frozenset(
    {
        "ch1_flow_enabled",
        "ch2_flow_enabled",
        "hw_enabled",
        "boiler_ch_max_setpoint_read_write",
        "boiler_ch_max_setpoint_transfer_enable",
        "boiler_hw_setpoint_read_write",
        "boiler_hw_setpoint_transfer_enable",
        "boiler_fault",
        "central_heating_active",
        "hot_water_active",
        "flame_active",
        "cooling_active",
        "central_heating_2_active",
        "diagnostic_event",
    }
)

# These selectable sensors are calculated from another OpenTherm entity rather
# than exposing the current value of an API attribute directly.
OPENTHERM_DERIVED_SENSOR_KEYS = frozenset({"delta_t", "flame_statistics"})

# OpenTherm Data-ID 0, low-byte (slave status) flags. Bit 7 is reserved.
OPENTHERM_SLAVE_STATUS_BITS = {
    "boiler_fault": 0,
    "central_heating_active": 1,
    "hot_water_active": 2,
    "flame_active": 3,
    "cooling_active": 4,
    "central_heating_2_active": 5,
    "diagnostic_event": 6,
}

OPENTHERM_SENSOR_CATEGORIES = {
    "opentherm_readings": (
        "ch_flow_temperature",
        "ch_pressure_bar",
        "ch_return_temperature",
        "delta_t",
        "hw_flow_rate",
        "hw_temperature",
        "relative_modulation_level",
        "room_temperature",
    ),
    "opentherm_central_heating": (
        "boiler_ch_max_setpoint_read_write",
        "boiler_ch_max_setpoint_transfer_enable",
        "boiler_ch_setpoint",
        "boiler_ch_setpoint_lower_bound",
        "boiler_ch_setpoint_upper_bound",
        "ch_flow_active_lower_setpoint",
        "ch_flow_active_upper_setpoint",
        "ch1_flow_enabled",
        "ch1_flow_setpoint",
        "ch2_flow_enabled",
        "ch2_flow_setpoint",
        "room_setpoint",
    ),
    "opentherm_hot_water": (
        "boiler_hw_setpoint",
        "boiler_hw_setpoint_lower_bound",
        "boiler_hw_setpoint_read_write",
        "boiler_hw_setpoint_transfer_enable",
        "boiler_hw_setpoint_upper_bound",
        "hw_enabled",
        "hw_flow_setpoint",
    ),
    "opentherm_status": (
        "boiler_fault",
        "central_heating_active",
        "central_heating_2_active",
        "connection_status",
        "cooling_active",
        "diagnostic_event",
        "flame_active",
        "flame_statistics",
        "hot_water_active",
        "operating_mode",
        "slave_status",
        "tracked_room_id",
    ),
}

OPENTHERM_SENSOR_NAMES = {
    "ch_flow_active_lower_setpoint": "CH flow active lower setpoint",
    "ch_flow_active_upper_setpoint": "CH flow active upper setpoint",
    "ch1_flow_enabled": "CH1 flow enabled",
    "ch1_flow_setpoint": "CH1 flow setpoint",
    "ch2_flow_enabled": "CH2 flow enabled",
    "ch2_flow_setpoint": "CH2 flow setpoint",
    "connection_status": "Connection status",
    "hw_enabled": "Hot water enabled",
    "hw_flow_setpoint": "Hot water flow setpoint",
    "operating_mode": "Operating mode",
    "tracked_room_id": "Tracked room ID",
    "room_setpoint": "Room setpoint",
    "room_temperature": "Room temperature",
    "ch_flow_temperature": "Boiler flow temperature",
    "ch_pressure_bar": "CH pressure",
    "ch_return_temperature": "Boiler return temperature",
    "delta_t": "Delta-T",
    "relative_modulation_level": "Relative modulation level",
    "hw_temperature": "Hot water temperature",
    "hw_flow_rate": "Hot water flow rate",
    "slave_status": "OpenTherm slave status",
    "boiler_fault": "Boiler fault",
    "central_heating_active": "Central heating active",
    "hot_water_active": "Hot water active",
    "flame_active": "Flame active",
    "flame_statistics": "Flame statistics",
    "cooling_active": "Cooling active",
    "central_heating_2_active": "Central heating 2 active",
    "diagnostic_event": "Diagnostic event",
    "boiler_ch_max_setpoint_read_write": "Boiler CH maximum setpoint read/write",
    "boiler_ch_max_setpoint_transfer_enable": (
        "Boiler CH maximum setpoint transfer enabled"
    ),
    "boiler_ch_setpoint": "Boiler CH setpoint",
    "boiler_ch_setpoint_lower_bound": "Boiler CH setpoint lower bound",
    "boiler_ch_setpoint_upper_bound": "Boiler CH setpoint upper bound",
    "boiler_hw_setpoint_read_write": "Boiler hot water setpoint read/write",
    "boiler_hw_setpoint_transfer_enable": (
        "Boiler hot water setpoint transfer enabled"
    ),
    "boiler_hw_setpoint": "Boiler hot water setpoint",
    "boiler_hw_setpoint_lower_bound": "Boiler hot water setpoint lower bound",
    "boiler_hw_setpoint_upper_bound": "Boiler hot water setpoint upper bound",
}


def _path_value(value, path):
    """Return a nested OpenTherm value using public API attributes."""
    for part in path:
        value = getattr(value, part)
    return value


def relative_modulation_level(opentherm):
    """Read modulation as percent, preserving zero and fractional readings."""
    # aioWiserHeatAPI 1.7.3's convenience property returns None for zero and
    # truncates fractions. The raw OpenTherm value is in tenths of a percent.
    raw = opentherm.operational_data.json_data.get("RelativeModulationLevel")
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        return None
    if not 0 <= raw <= 1000:
        return None
    return raw / 10


def opentherm_sensor_value(opentherm, key):
    """Return the current value for a selectable OpenTherm sensor."""
    if key == "delta_t":
        flow = opentherm.operational_data.ch_flow_temperature
        return_temperature = opentherm.operational_data.ch_return_temperature
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            for value in (flow, return_temperature)
        ):
            return None
        return round(flow - return_temperature, 1)
    if key == "relative_modulation_level":
        return relative_modulation_level(opentherm)
    if key in OPENTHERM_SLAVE_STATUS_BITS:
        slave_status = _path_value(opentherm, OPENTHERM_SENSOR_PATHS[key])
        if isinstance(slave_status, bool) or not isinstance(slave_status, int):
            return None
        return bool(slave_status & (1 << OPENTHERM_SLAVE_STATUS_BITS[key]))
    return _path_value(opentherm, OPENTHERM_SENSOR_PATHS[key])


def opentherm_sensor_is_enabled(configured, key):
    """Return whether a sensor is selected, including legacy option mappings."""
    if configured is None:
        return key in DEFAULT_OPENTHERM_SENSOR_KEYS
    if isinstance(configured, dict):
        return configured.get(key, key in DEFAULT_OPENTHERM_SENSOR_KEYS)
    return key in configured


def detected_opentherm_sensor_keys(opentherm):
    """Return selectable attributes supported by this OpenTherm response."""
    detected = []
    for key, path in OPENTHERM_SENSOR_PATHS.items():
        if key == "delta_t":
            continue
        try:
            # Detection is based on field availability, not its current value.
            # A valid sensor may report None while the boiler is idle.
            _path_value(opentherm, path)
        except (AttributeError, TypeError):
            continue
        detected.append(key)
    if {
        "ch_flow_temperature",
        "ch_return_temperature",
    }.issubset(detected):
        detected.append("delta_t")
    return detected


def _firmware_release(version):
    """Extract the numeric release from Wiser versions with optional build IDs."""
    if not isinstance(version, str):
        raise ValueError("Wiser system firmware version is missing")
    match = re.fullmatch(
        r"(\d+)\.(\d+)\.(\d+)(?:-[A-Za-z0-9][A-Za-z0-9._-]*)?", version.strip()
    )
    if match is None:
        raise ValueError(f"Invalid Wiser system firmware version: {version!r}")
    return tuple(int(part) for part in match.groups())


def parse_parameter_value(value):
    """Accept UI text or YAML scalars without sending numbers as JSON strings."""
    if isinstance(value, str):
        value = value.strip()
        if not value:
            raise ValueError("OpenTherm parameter value must not be empty")
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            # Some parameters accept textual enum values.
            pass
    if not isinstance(value, (str, bool, int, float)):
        raise ValueError("OpenTherm parameter value must be a number, boolean or text")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("OpenTherm parameter value must be finite")
    return value


def opentherm_parameter_feedback(system, endpoint, parameter):
    """Return reported feedback for a known parameter, or ``None``."""
    feedback = OPENTHERM_PARAMETER_FEEDBACK.get(parameter)
    if feedback is None:
        return None

    expected_endpoint, path = feedback
    effective_endpoint = endpoint.strip().strip("/") or OPENTHERM_PARAMETER_ENDPOINTS.get(
        parameter, ""
    )
    if effective_endpoint != expected_endpoint:
        return None

    try:
        reported = _path_value(system.opentherm, path)
    except (AttributeError, TypeError):
        return None
    if (
        isinstance(reported, bool)
        or not isinstance(reported, (int, float))
        or not math.isfinite(reported)
    ):
        return None

    return reported


def opentherm_parameter_matches(system, endpoint, parameter, value):
    """Return whether reported feedback matches a known temperature write.

    ``None`` means that the write cannot be verified safely, so callers must
    not retry it automatically.
    """
    parsed_value = parse_parameter_value(value)
    if isinstance(parsed_value, bool) or not isinstance(parsed_value, (int, float)):
        return None

    reported = opentherm_parameter_feedback(system, endpoint, parameter)
    if reported is None:
        return None

    return math.isclose(reported, parsed_value / 10, abs_tol=0.05)


async def async_set_parameter(system, endpoint, parameter, value):
    """Write using the same endpoint selection as the API's OpenTherm reader."""
    parameter = parameter.strip()
    endpoint = endpoint.strip().strip("/") or OPENTHERM_PARAMETER_ENDPOINTS.get(
        parameter, ""
    )
    if endpoint and not re.fullmatch(r"[A-Za-z0-9_]+(?:/[A-Za-z0-9_]+)*", endpoint):
        raise ValueError("OpenTherm endpoint must be a relative parameter path")
    if not re.fullmatch(r"[A-Za-z0-9_]+", parameter):
        raise ValueError("Invalid OpenTherm parameter name")
    command = {parameter: parse_parameter_value(value)}
    url = WISERHUBOPENTHERM
    if system.hardware_generation == 2:
        # Routing follows System.ActiveSystemVersion, not the controller
        # device's ActiveFirmwareVersion (which can be a different version).
        # The API threshold is its own Version object, not packaging.Version.
        # Compare releases only; e.g. 4.48.2-3735f20 has release (4, 48, 2).
        if _firmware_release(system.active_system_version) >= _firmware_release(
            OPENTHERMV2_MIN_VERSION.version
        ):
            url = WISERHUBOPENTHERMV2

    # The pinned API's public setter hardcodes the legacy URL. Keep this
    # workaround local, retaining its authenticated transport and retry logic.
    # Remove it once the upstream setter supports firmware-specific routing.
    await system.opentherm._wiser_rest_controller._do_hub_action(
        WiserRestActionEnum.PATCH, f"{url}{endpoint}", command
    )
