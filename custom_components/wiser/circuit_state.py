"""Shared heating-channel and hot-water circuit state logic.

Used by both the circuit text sensors and the circuit binary sensors so the
two always agree. Kept free of Home Assistant imports.
"""

from __future__ import annotations

from aioWiserHeatAPI.const import TEXT_OFF, TEXT_ON, TEXT_UNKNOWN


def heating_channel_output_state(channel) -> str:
    """Return the raw on/off state of a heating channel.

    Uses the heating relay status, falling back to the demand on/off output
    when the relay is unknown, as on OpenTherm boilers, which have no relay.
    """
    if channel.heating_relay_status != TEXT_UNKNOWN:
        return channel.heating_relay_status
    return channel.demand_on_off_output


def hot_water_output_state(hotwater) -> str:
    """Return the raw on/off state of the hot water circuit."""
    return hotwater.current_state


def output_state_is_on(raw_state: str | None) -> bool | None:
    """Map a raw API on/off state to a boolean, or None when not on or off."""
    if raw_state == TEXT_ON:
        return True
    if raw_state == TEXT_OFF:
        return False
    return None
