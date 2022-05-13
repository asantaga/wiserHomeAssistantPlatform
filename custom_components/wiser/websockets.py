import logging
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from homeassistant.components import websocket_api
from homeassistant.core import callback
from homeassistant.components.websocket_api import async_register_command, ActiveConnection
from . import const

_LOGGER = logging.getLogger(__name__)

async def async_register_websockets(hass):
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedules".format(const.DOMAIN),
            vol.Optional("hub_id"): cv.string,
        }
    )
    @websocket_api.async_response
    async def websocket_get_schedules(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Publish scheduler list data."""
        wiser_hub_entry_id = None

        for index, entry_id in enumerate(hass.data[const.DOMAIN]):
            if not msg.get("hub_id") and not index:
                wiser_hub_entry_id = entry_id
            elif msg.get("hub_id") and hass.data[const.DOMAIN][entry_id]["data"].wiserhub.system.name == msg["hub_id"]:
                wiser_hub_entry_id = entry_id
                
        if wiser_hub_entry_id:
            wiserhub = hass.data[const.DOMAIN][wiser_hub_entry_id]["data"]
            schedules = wiserhub.async_get_schedules()
            connection.send_result(msg["id"],schedules)
        else:
            connection.send_error(
                msg["id"], "invalid_heat_hub", "Invalid Wiser HeatHub name"
            )


    hass.components.websocket_api.async_register_command(websocket_get_schedules)