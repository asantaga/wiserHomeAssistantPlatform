import asyncio

from homeassistant.components.switch import SwitchDevice
from .const import _LOGGER, DOMAIN, WISER_SWITCHES
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import (
    ATTR_ENTITY_ID,
)
from homeassistant.core import callback


from .const import _LOGGER, DOMAIN


ATTR_PLUG_MODE="plug_mode"
ATTR_HOTWATER_MODE="hotwater_mode"

SERVICE_SET_SMARTPLUG_MODE="set_smartplug_mode"
SERVICE_SET_HOTWATER_MODE="set_hotwater_mode"


SET_PLUG_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_PLUG_MODE, default="Auto"): vol.Coerce(str),
    }
)

SET_HOTWATER_MODE_SCHEMA = vol.Schema(
    {

        vol.Required(ATTR_HOTWATER_MODE, default="auto"): vol.Coerce(str),
    }
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Add the Wiser System Switch entities"""
    data = hass.data[DOMAIN]

    # Add System Switches
    wiser_switches = [
        WiserSwitch(hass, data, switchType, hubKey)  for switchType, hubKey in WISER_SWITCHES.items()
    ]
    async_add_entities(wiser_switches)

    # Add SmartPlugs (if any)
    if data.wiserhub.getSmartPlugs() is not None:
        wiser_smart_plugs = [
            WiserSmartPlug(hass, data, plug.get("id"), plug.get("Name")) for plug in data.wiserhub.getSmartPlugs()
        ]
        async_add_entities(wiser_smart_plugs)



    @callback
    def set_smartplug_mode(service):
        device_found=False
        entity_id = service.data[ATTR_ENTITY_ID]
        smart_plug_mode = service.data[ATTR_PLUG_MODE]
        print("data = {} {}".format(entity_id,smart_plug_mode))

        for smart_plug in wiser_smart_plugs:

            if smart_plug.entity_id == entity_id:
                device_found=True
                hass.async_create_task(
                    smart_plug.set_smartplug_mode(smart_plug_mode)
                )
            smart_plug.schedule_update_ha_state(True)
            break

    @callback
    def set_hotwater_mode(service):
        hotwater_mode = service.data[ATTR_HOTWATER_MODE]
        hass.async_create_task(
            data.set_hotwater_mode(hotwater_mode)
        )


    """ Register Services """
    hass.services.async_register(
        DOMAIN, SERVICE_SET_SMARTPLUG_MODE, set_smartplug_mode,schema=SET_PLUG_MODE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_HOTWATER_MODE, set_hotwater_mode,schema=SET_HOTWATER_MODE_SCHEMA,
    )
    return True

"""
Switch to set the status of the Wiser Operation Mode (Away/Normal)
"""



class WiserSwitch(SwitchDevice):
    def __init__(self, hass, data, switchType, hubKey):
        """Initialize the sensor."""
        _LOGGER.info("Wiser {} Switch Init".format(switchType))
        self.data = data
        self._force_update = False
        self.hass = hass
        self.hub_key = hubKey
        self.switch_type = switchType
        self.awayTemperature = None

    async def async_update(self):
        _LOGGER.debug("Wiser {} Switch Update requested".format(self.switch_type))
        if self._force_update:
            await self.data.async_update(no_throttle=True)
            self._force_update = False
        else:
            await self.data.async_update()

        if self.switch_type == "Away Mode":
            self.awayTemperature = round(
                self.data.wiserhub.getSystem().get("AwayModeSetPointLimit") / 10, 1
            )

    @property
    def name(self):
        """Return the name of the Device """
        return "Wiser " + self.switch_type

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def is_on(self):
        """Return true if device is on."""
        status = self.data.wiserhub.getSystem().get(self.hub_key)
        _LOGGER.debug("{}: {}".format(self.switch_type, status))
        if self.switch_type == "Away Mode":
            return status and status.lower() == "away"
        else:
            return status

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        if self.switch_type == "Away Mode":
            await self.data.set_away_mode(True, self.awayTemperature)
        else:
            await self.data.set_system_switch(self.hub_key, True)
        return True

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        if self.switch_type == "Away Mode":
            await self.data.set_away_mode(False, self.awayTemperature)
        else:
            await self.data.set_system_switch(self.hub_key, False)
        return True



class WiserSmartPlug(SwitchDevice):
    def __init__(self, hass, data, plugId, name):
        """Initialize the sensor."""
        _LOGGER.info("Wiser {} SmartPlug Init".format(name))
        self.plug_name = name
        self.smart_plug_id = plugId
        self.data = data
        self._force_update = False
        self.hass = hass
        self._is_on = False


    async def async_update(self):
        _LOGGER.debug(" SmartPlug {} Status requested".format(self.plug_name))
        if self._force_update:
            await self.data.async_update(no_throttle=True)
            self._force_update = False
        else:
            await self.data.async_update()
        #Update status
        smartPlugs = self.data.wiserhub.getSmartPlugs()
        for plug in smartPlugs:
            if plug.get("id") == self.smart_plug_id:
                self._is_on = True if plug.get("OutputState") == "On" else False
                
    @property
    def name(self):
        """Return the name of the SmartPlug """
        return self.plug_name

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def is_on(self):
        """Return true if device is on."""
        _LOGGER.debug(
            "Smartplug {} is currently {}".format(self.smart_plug_id, self._is_on)
        )
        return self._is_on

    @property
    def device_state_attributes(self):
        attrs = {}
        device_data = self.data.wiserhub.getSmartPlug(self.smart_plug_id)
        attrs["ManualState"] = device_data.get("ManualState")
        attrs["Name"] = device_data.get("Name")
        attrs["Mode"] = device_data.get("Mode")
        attrs["AwayAction"] = device_data.get("AwayAction")
        attrs["OutputState"] = device_data.get("OutputState")
        attrs["ControlSource"] = device_data.get("ControlSource")
        attrs["ScheduledState"] = device_data.get("ScheduledState")
        return attrs

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self.data.set_smart_plug_state(self.smart_plug_id, "On")
        return True

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self.data.set_smart_plug_state(self.smart_plug_id, "Off")
        return True

    async def set_smartplug_mode(self,plug_mode):
        _LOGGER.debug(
            "Setting Smartplug {} Mode to {} ".format(self.smart_plug_id, plug_mode)
        )
        self.data.wiserhub.setSmartPlugMode(self.smart_plug_id,plug_mode)
        self._force_update = True



