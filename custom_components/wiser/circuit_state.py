"""Shared heating-channel and hot-water circuit state logic.

Used by both the circuit text sensors and the circuit binary sensors so the
two always agree. Kept free of Home Assistant imports.
"""

from __future__ import annotations

from aioWiserHeatAPI.const import TEXT_OFF, TEXT_ON, TEXT_UNKNOWN


def heating_channel_context(data) -> dict:
    """Return current boiler data and persisted OpenTherm detection."""
    system = getattr(data.wiserhub, "system", None)
    entry = getattr(data, "config_entry", None)
    # This persisted flag also identifies OpenTherm during a startup outage.
    detected = bool(
        entry and entry.data.get("opentherm_ever_connected", False)
    )
    return {
        "opentherm": getattr(system, "opentherm", None),
        "opentherm_detected": detected,
    }


def _uses_opentherm(opentherm, detected) -> bool:
    return bool(
        detected
        or (
            opentherm is not None
            and (
                getattr(opentherm, "enabled", False)
                or getattr(opentherm, "connection_status", None) == "Connected"
                or getattr(opentherm, "is_configured", False)
            )
        )
    )


def heating_channel_is_available(
    channel, opentherm=None, *, opentherm_detected=False
) -> bool:
    """Require live boiler connectivity on a known OpenTherm installation."""
    if channel is None:
        return False
    if _uses_opentherm(opentherm, opentherm_detected):
        return bool(
            opentherm is not None
            and getattr(opentherm, "enabled", False)
            and getattr(opentherm, "connection_status", None) == "Connected"
        )
    return True


def heating_channel_output_state(
    channel, opentherm=None, *, opentherm_detected=False
) -> str:
    """Return boiler CH activity for OpenTherm, or channel output for relays.

    Read SlaveStatus directly so missing values remain unknown with API 1.7.9
    as well as newer versions. Boiler activity needs no room-demand gate.
    """
    if not heating_channel_is_available(
        channel, opentherm, opentherm_detected=opentherm_detected
    ):
        return TEXT_UNKNOWN
    if _uses_opentherm(opentherm, opentherm_detected):
        operational_data = getattr(opentherm, "operational_data", None)
        status = getattr(operational_data, "slave_status", None)
        if isinstance(status, bool) or not isinstance(status, int):
            return TEXT_UNKNOWN
        return TEXT_ON if status & (1 << 1) else TEXT_OFF
    if channel.heating_relay_status != TEXT_UNKNOWN:
        return channel.heating_relay_status
    return channel.demand_on_off_output


def hot_water_output_state(hotwater) -> str:
    """Return the raw on/off state of the hot water circuit."""
    if hotwater is None:
        return TEXT_UNKNOWN
    return hotwater.current_state


def output_state_is_on(raw_state: str | None) -> bool | None:
    """Map a raw API on/off state to a boolean, or None when not on or off."""
    if raw_state == TEXT_ON:
        return True
    if raw_state == TEXT_OFF:
        return False
    return None
