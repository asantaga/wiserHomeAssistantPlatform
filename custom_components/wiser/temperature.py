"""Temperature helpers for the Wiser integration."""


def room_target_temperature(room, frost_protection_temperature, off_temperature):
    """Return the effective target temperature exposed to Home Assistant."""
    target_temperature = room.current_target_temperature
    if room.mode == "Off" or target_temperature == off_temperature:
        return frost_protection_temperature
    return target_temperature
