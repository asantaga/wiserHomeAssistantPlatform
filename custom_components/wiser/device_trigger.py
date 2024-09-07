"""Provides device automations for Wiser."""
import voluptuous as vol

from homeassistant.components.device_automation import DEVICE_TRIGGER_BASE_SCHEMA
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_DOMAIN,
    CONF_ENTITY_ID,
    CONF_PLATFORM,
    CONF_TYPE,
)
from homeassistant.core import CALLBACK_TYPE, HomeAssistant
from homeassistant.components.homeassistant.triggers import event as event_trigger
from homeassistant.helpers import config_validation as cv, entity_registry
from homeassistant.helpers.trigger import TriggerActionType, TriggerInfo
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .events import WISER_EVENTS, WISER_EVENT

DEVICE = "device"
SUPPORTED_DOMAINS = {event[CONF_DOMAIN] for event in WISER_EVENTS}

TRIGGER_TYPES = {event[CONF_TYPE] for event in WISER_EVENTS}

TRIGGER_SCHEMA = DEVICE_TRIGGER_BASE_SCHEMA.extend(
    {
        vol.Required(CONF_ENTITY_ID): cv.entity_id,
        vol.Required(CONF_TYPE): vol.In(TRIGGER_TYPES),
    }
)


async def async_get_triggers(
    hass: HomeAssistant, device_id: str
) -> list[dict[str, str]]:
    """List device triggers for Climate devices."""
    registry = entity_registry.async_get(hass)

    for entry in entity_registry.async_entries_for_device(registry, device_id):
        if entry.domain not in SUPPORTED_DOMAINS:
            continue

        trigger_types = set(
            [
                event_type[CONF_TYPE]
                for event_type in WISER_EVENTS
                if event_type[CONF_DOMAIN] == entry.domain
            ]
        )

        return [
            {
                CONF_PLATFORM: DEVICE,
                CONF_DEVICE_ID: device_id,
                CONF_DOMAIN: DOMAIN,
                CONF_ENTITY_ID: entry.entity_id,
                CONF_TYPE: trigger_type,
            }
            for trigger_type in trigger_types
        ]


async def async_attach_trigger(
    hass: HomeAssistant,
    config: ConfigType,
    action: TriggerActionType,
    trigger_info: TriggerInfo,
) -> CALLBACK_TYPE:
    """Attach a trigger."""
    event_config = event_trigger.TRIGGER_SCHEMA(
        {
            event_trigger.CONF_PLATFORM: "event",
            event_trigger.CONF_EVENT_TYPE: WISER_EVENT,
            event_trigger.CONF_EVENT_DATA: {
                CONF_ENTITY_ID: config[CONF_ENTITY_ID],
                CONF_TYPE: config[CONF_TYPE],
            },
        }
    )
    return await event_trigger.async_attach_trigger(
        hass, event_config, action, trigger_info, platform_type="device"
    )
