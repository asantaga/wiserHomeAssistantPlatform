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


async def async_set_parameter(system, endpoint, parameter, value):
    """Write using the same endpoint selection as the API's OpenTherm reader."""
    endpoint = endpoint.strip().strip("/")
    parameter = parameter.strip()
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
