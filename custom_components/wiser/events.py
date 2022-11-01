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
CONF_EVENT_DATA = "event_data"
VALUE_INC = "inc"
VALUE_DEC = "dec"
VALUE_DIFF = "diff"

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
    {
        CONF_DOMAIN: DOMAIN_CLIMATE,
        CONF_ATTRIBUTE: "current_target_temperature",
        CONF_VALUE: VALUE_INC,
        CONF_TYPE: "target_temperature_increased",
    },
    {
        CONF_DOMAIN: DOMAIN_CLIMATE,
        CONF_ATTRIBUTE: "current_target_temperature",
        CONF_VALUE: VALUE_DEC,
        CONF_TYPE: "target_temperature_decreased",
    },
]

WISER_COMMON_EVENT_DATA = {}

"""
WISER_COMMON_EVENT_DATA = {
    DOMAIN_CLIMATE: [
        "current_temperature",
        "current_target_temperature",
        "is_boosted",
    ],
}
"""


def fire_events(hass, entity_id: str, old_state: dict, new_state: dict):
    for event in WISER_EVENTS:
        fire_event = False

        if hasattr(old_state, event[CONF_ATTRIBUTE]):
            if (
                (
                    event[CONF_VALUE] == VALUE_DIFF
                    and getattr(new_state, event[CONF_ATTRIBUTE])
                    != getattr(old_state, event[CONF_ATTRIBUTE])
                )
                or (
                    event[CONF_VALUE] == VALUE_INC
                    and getattr(new_state, event[CONF_ATTRIBUTE])
                    > getattr(old_state, event[CONF_ATTRIBUTE])
                )
                or (
                    event[CONF_VALUE] == VALUE_DEC
                    and getattr(new_state, event[CONF_ATTRIBUTE])
                    < getattr(old_state, event[CONF_ATTRIBUTE])
                )
                or (
                    getattr(old_state, event[CONF_ATTRIBUTE])
                    != getattr(new_state, event[CONF_ATTRIBUTE])
                    and getattr(new_state, event[CONF_ATTRIBUTE]) == event[CONF_VALUE]
                )
            ):

                message = {CONF_ENTITY_ID: entity_id, CONF_TYPE: event[CONF_TYPE]}
                old_state_attr = {}
                new_state_attr = {}

                # Get common event data for domain and specific data for event type
                event_data = list(
                    WISER_COMMON_EVENT_DATA.get(entity_id.split(".")[0], [])
                ) + list(event.get(CONF_EVENT_DATA, []))

                if event_data:
                    for attr in event_data:
                        if hasattr(old_state, attr):
                            old_state_attr[attr] = getattr(old_state, attr)
                        if hasattr(new_state, attr):
                            new_state_attr[attr] = getattr(new_state, attr)

                    if old_state_attr:
                        message["old_state"] = old_state_attr

                    if new_state_attr:
                        message["new_state"] = new_state_attr

                _LOGGER.debug(
                    f"Firing wiser event with type {event[CONF_TYPE]} for {entity_id}"
                )
                hass.bus.fire(
                    WISER_EVENT,
                    message,
                )
