"""Track whether a Wiser hub has a confirmed OpenTherm connection."""

from .const import CONF_OPENTHERM_EVER_CONNECTED


def opentherm_is_detected(config_entry, opentherm) -> bool:
    """Return whether OpenTherm is connected now or has connected before."""
    return bool(
        opentherm
        and (
            config_entry.data.get(CONF_OPENTHERM_EVER_CONNECTED, False)
            or getattr(opentherm, "connection_status", None) == "Connected"
        )
    )
