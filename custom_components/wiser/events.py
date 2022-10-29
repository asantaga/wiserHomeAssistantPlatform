import logging

from homeassistant.const import (
    CONF_ATTRIBUTE,
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_ENTITY_ID,
    CONF_TYPE,
)

from homeassistant.components.climate.const import DOMAIN as DOMAIN_CLIMATE


_LOGGER = logging.getLogger(__name__)

CONF_VALUE = "value"

WISER_EVENT = "wiser_event"

WISER_EVENTS = [
    {
        CONF_DOMAIN: DOMAIN_CLIMATE,
        CONF_ATTRIBUTE: "is_heating",
        CONF_VALUE: True,
        CONF_TYPE: "started_heating",
    },
    {
        CONF_DOMAIN: DOMAIN_CLIMATE,
        CONF_ATTRIBUTE: "is_heating",
        CONF_VALUE: False,
        CONF_TYPE: "stopped_heating",
    },
    {
        CONF_DOMAIN: DOMAIN_CLIMATE,
        CONF_ATTRIBUTE: "is_boosted",
        CONF_VALUE: True,
        CONF_TYPE: "boosted",
    },
]


def fire_events(hass, entity_id: str, old_state: dict, new_state: dict):
    for event in WISER_EVENTS:
        if hasattr(old_state, event[CONF_ATTRIBUTE]):
            if (
                getattr(old_state, event[CONF_ATTRIBUTE])
                != getattr(new_state, event[CONF_ATTRIBUTE])
            ) and getattr(new_state, event[CONF_ATTRIBUTE]) == event[CONF_VALUE]:

                message = {CONF_ENTITY_ID: entity_id, CONF_TYPE: event[CONF_TYPE]}

                _LOGGER.debug(
                    f"Firing wiser event with type {event[CONF_TYPE]} for {entity_id}"
                )
                hass.bus.fire(
                    WISER_EVENT,
                    message,
                )
