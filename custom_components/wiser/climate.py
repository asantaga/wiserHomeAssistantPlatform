"""
Climate Platform Device for Wiser Rooms.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
import logging
from .events import fire_events
import voluptuous as vol

from homeassistant.components.climate import (
    HVACAction,
    HVACMode,
    ClimateEntityFeature,
)
from homeassistant.components.climate import ClimateEntity
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import callback, HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from aioWiserHeatAPI.wiserhub import TEMP_MINIMUM, TEMP_MAXIMUM, TEMP_OFF
from .const import (
    DATA,
    DOMAIN,
    MANUFACTURER,
    ROOM,
    WISER_BOOST_PRESETS,
    WISER_SERVICES,
    WISER_SETPOINT_MODES,
)
from .helpers import (
    get_device_name,
    get_identifier,
    hub_error_handler,
)
from .schedules import WiserScheduleEntity

_LOGGER = logging.getLogger(__name__)

ATTR_COPYTO_ENTITY_ID = "to_entity_id"
ATTR_FILENAME = "filename"
ATTR_TIME_PERIOD = "time_period"
ATTR_TEMPERATURE_DELTA = "temperature_delta"

STATUS_AWAY = "Away Mode"
STATUS_AWAY_BOOST = "Away Boost"
STATUS_AWAY_OVERRIDE = "Away Override"
STATUS_BOOST = "Boost"
STATUS_COMFORT = "Comfort"
STATUS_ECO = "EcoIQ"
STATUS_OVERRIDE = "Override"
STATUS_BLANK = ""

TEXT_PASSIVE = "Passive"

WISER_PRESET_TO_HASS = {
    "FromAwayMode": STATUS_AWAY,
    "FromManualMode": STATUS_BLANK,
    "FromBoost": STATUS_BOOST,
    "FromManualOverrideDuringAway": STATUS_AWAY_OVERRIDE,
    "FromBoostDuringAway": STATUS_AWAY_BOOST,
    "FromManualOverride": STATUS_OVERRIDE,
    "FromEcoIQ": STATUS_ECO,
    "FromSchedule": STATUS_BLANK,
    "FromComfortMode": STATUS_COMFORT,
    "FromNoControl": STATUS_BLANK,
}

WISER_PRESETS = {
    "Advance Schedule": 0,
    "Cancel Overrides": 0,
}
WISER_PRESETS.update(WISER_BOOST_PRESETS)

HVAC_MODE_WISER_TO_HASS = {
    "Auto": HVACMode.AUTO,
    "Manual": HVACMode.HEAT,
    "Off": HVACMode.OFF,
}

HVAC_MODE_HASS_TO_WISER = {
    HVACMode.AUTO: "Auto",
    HVACMode.HEAT: "Manual",
    HVACMode.OFF: "Off",
}

SUPPORT_FLAGS = (
    ClimateEntityFeature.TARGET_TEMPERATURE
    | ClimateEntityFeature.PRESET_MODE
    | ClimateEntityFeature.TURN_ON
    | ClimateEntityFeature.TURN_OFF
)
PASSIVE_MODE_SUPPORT_FLAGS = (
    ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
    | ClimateEntityFeature.PRESET_MODE
    | ClimateEntityFeature.TURN_ON
    | ClimateEntityFeature.TURN_OFF
)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get coordinator

    if coordinator.wiserhub.rooms:
        _LOGGER.debug("Setting up Room climate entities")
        wiser_rooms = [
            WiserRoom(hass, coordinator, room.id)
            for room in coordinator.wiserhub.rooms.all
            if len(room.devices) > 0
        ]
        async_add_entities(wiser_rooms, True)

        # Add climate entity for heating actuator with temp sensor
        wiser_temp_probes = []
        _LOGGER.debug("Setting up Heating Actuator floor temp entities")
        for heating_actuator in coordinator.wiserhub.devices.heating_actuators.all:
            if (
                heating_actuator.floor_temperature_sensor
                and heating_actuator.floor_temperature_sensor.sensor_type
                != "Not_Fitted"
            ):
                wiser_temp_probes.extend(
                    [WiserTempProbe(hass, coordinator, heating_actuator.id)]
                )
        if wiser_temp_probes:
            async_add_entities(wiser_temp_probes, True)

        # Setup services
        platform = entity_platform.async_get_current_platform()

        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_BOOST_HEATING"],
            {
                vol.Required(
                    ATTR_TIME_PERIOD, default=coordinator.boost_time
                ): vol.Coerce(int),
                vol.Any(
                    vol.Optional(ATTR_TEMPERATURE_DELTA, default=0),
                    vol.Optional(ATTR_TEMPERATURE, default=0),
                ): vol.Coerce(float),
            },
            "async_boost_heating",
        )


class WiserTempProbe(CoordinatorEntity, ClimateEntity):
    """Wiser temp probe climate entity object"""

    _enable_turn_on_off_backwards_compatibility = False

    def __init__(self, hass: HomeAssistant, coordinator, actuator_id) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._hass = hass
        self._data = coordinator
        self._actuator_id = actuator_id
        self._actuator = self._data.wiserhub.devices.heating_actuators.get_by_id(
            self._actuator_id
        )

        _LOGGER.debug(f"{self._data.wiserhub.system.name} {self.name} initailise")

    async def async_force_update(self):
        _LOGGER.debug(f"Hub update initiated by {self.name}")
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug(f"{self.name} updating")
        self._actuator = self._data.wiserhub.devices.heating_actuators.get_by_id(
            self._actuator_id
        )

    @property
    def current_temperature(self):
        """Return current temp from data."""
        return self._actuator.floor_temperature_sensor.measured_temperature

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._actuator_id),
            "identifiers": {(DOMAIN, get_identifier(self._data, self._actuator_id))},
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def icon(self):
        """Return icon to show if radiator is heating, not heating or set to off."""
        return "mdi:radiator-off"

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return []

    @property
    def hvac_mode(self):
        return HVACMode.HEAT

    @property
    def max_temp(self):
        """Return max temp from data."""
        return 39

    @property
    def min_temp(self):
        """Return min temp from data."""
        return TEMP_MINIMUM

    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, self._actuator_id)} Floor Temp"

    @hub_error_handler
    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        if (
            kwargs.get("target_temp_low", None)
            != self._actuator.floor_temperature_sensor.minimum_temperature
        ):
            await self._actuator.floor_temperature_sensor.set_minimum_temperature(
                kwargs.get("target_temp_low")
            )
            await self.async_force_update()

        if (
            kwargs.get("target_temp_high", None)
            != self._actuator.floor_temperature_sensor.maximum_temperature
        ):
            await self._actuator.floor_temperature_sensor.set_maximum_temperature(
                kwargs.get("target_temp_high")
            )
            await self.async_force_update()

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return ClimateEntityFeature.TARGET_TEMPERATURE_RANGE

    @property
    def target_temperature_step(self) -> float | None:
        """Return the supported step of target temperature."""
        return 1

    @property
    def target_temperature_high(self) -> float | None:
        """Return the highbound target temperature we try to reach.
        Requires ClimateEntityFeature.TARGET_TEMPERATURE_RANGE.
        """
        return self._actuator.floor_temperature_sensor.maximum_temperature

    @property
    def target_temperature_low(self) -> float | None:
        """Return the lowbound target temperature we try to reach.
        Requires ClimateEntityFeature.TARGET_TEMPERATURE_RANGE.
        """
        return self._actuator.floor_temperature_sensor.minimum_temperature

    @property
    def temperature_unit(self):
        """Return temp units."""
        return UnitOfTemperature.CELSIUS

    @property
    def unique_id(self):
        """Return unique Id."""
        return f"{self._data.wiserhub.system.name}-WiserHeatingActuatorTempSensor-{self._actuator_id}"


class WiserRoom(CoordinatorEntity, ClimateEntity, WiserScheduleEntity):
    """WiserRoom ClientEntity Object."""

    _enable_turn_on_off_backwards_compatibility = False
    _attr_translation_key = "wiser"

    def __init__(self, hass: HomeAssistant, coordinator, room_id) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._hass = hass
        self._data = coordinator
        self._room_id = room_id
        self._room = self._data.wiserhub.rooms.get_by_id(self._room_id)
        self._hvac_modes_list = [modes for modes in HVAC_MODE_HASS_TO_WISER.keys()]
        self._is_heating = self._room.is_heating
        self._schedule = self._room.schedule
        self._boosted_time = 0

        self.passive_temperature_increment = self._data.passive_temperature_increment

        _LOGGER.debug(f"{self._data.wiserhub.system.name} {self.name} initailise")

    async def async_force_update(self):
        _LOGGER.debug(f"Hub update initiated by {self.name}")
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug(f"{self.name} updating")
        previous_room_values = self._room
        self._room = self._data.wiserhub.rooms.get_by_id(self._room_id)
        self._schedule = self._room.schedule

        self.passive_temperature_increment = self._data.passive_temperature_increment

        if not self._room.is_boosted:
            self._boosted_time = 0

        self.async_write_ha_state()

        fire_events(
            self._hass,
            self.entity_id,
            previous_room_values,
            self._room,
        )

    @property
    def current_temperature(self):
        """Return current temp from data."""
        return self._room.current_temperature

    @property
    def current_humidity(self):
        """Return current temp from data."""
        return self._room.current_humidity

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._room_id, "room"),
            "identifiers": {
                (DOMAIN, get_identifier(self._data, self._room_id, "room"))
            },
            "manufacturer": MANUFACTURER,
            "model": ROOM.title(),
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def icon(self):
        """Return icon to show if radiator is heating, not heating or set to off."""
        if self._room.mode == "Off":
            return "mdi:radiator-off"
        elif self._room.is_heating:
            return "mdi:radiator"
        else:
            return "mdi:radiator-disabled"

    @property
    def hvac_action(self):
        """Return hvac action from data."""
        return HVACAction.HEATING if self._room.is_heating else HVACAction.IDLE

    @property
    def hvac_mode(self):
        return HVAC_MODE_WISER_TO_HASS[self._room.mode]

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return self._hvac_modes_list

    @hub_error_handler
    async def async_set_hvac_mode(self, hvac_mode):
        """Set new operation mode."""
        _LOGGER.debug(f"Setting HVAC mode to {hvac_mode} for {self._room.name}")
        try:
            await self._room.set_mode(HVAC_MODE_HASS_TO_WISER[hvac_mode])
            await self.async_force_update()
            return True
        except KeyError:
            _LOGGER.error(f"Invalid HVAC mode.  Options are {self.hvac_modes}")

    @property
    def max_temp(self):
        """Return max temp from data."""
        return TEMP_MAXIMUM

    @property
    def min_temp(self):
        """Return min temp from data."""
        return TEMP_MINIMUM

    @property
    def name(self):
        """Return Name of device."""
        return get_device_name(self._data, self._room_id, "room")

    @property
    def preset_mode(self):
        """Get current preset mode."""
        try:
            if self._room.is_passive_mode:
                return TEXT_PASSIVE
            elif self._room.preset_mode == "Boost":
                if int(self._room.boost_time_remaining / 60) != 0:
                    return f"{STATUS_BOOST} {int(self._room.boost_time_remaining/60)}m"
                else:
                    return STATUS_BOOST
            else:
                return WISER_PRESET_TO_HASS[self._room.target_temperature_origin]
        except KeyError:
            return STATUS_BLANK

    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        return self._room.available_presets

    @hub_error_handler
    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Async call to set preset mode ."""
        _LOGGER.debug(f"Setting Preset Mode {preset_mode} for {self._room.name}")
        try:
            await self._room.set_preset(preset_mode)
        except ValueError as ex:
            _LOGGER.error(ex)

        await self.async_force_update()

    @property
    def room(self):
        """Return room"""
        return self._room

    @property
    def state(self):
        """Return state"""
        return HVAC_MODE_WISER_TO_HASS[self._room.mode]

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        # Generic attributes
        attrs = super().state_attributes

        # Settings
        attrs["window_state"] = self._room.window_state
        attrs["window_detection_active"] = self._room.window_detection_active
        attrs["away_mode_supressed"] = self._room.away_mode_suppressed
        attrs["heating_type"] = self._room.heating_type
        attrs["number_of_heating_actuators"] = self._room.number_of_heating_actuators
        attrs["demand_type"] = self._room.demand_type

        # Status
        attrs["target_temperature_origin"] = self._room.target_temperature_origin
        attrs["is_boosted"] = self._room.is_boosted
        attrs["is_override"] = self._room.is_override
        attrs["is_heating"] = self._room.is_heating
        attrs["is_passive"] = self._room.is_passive_mode
        attrs["control_output_state"] = "On" if self._room.is_heating else "Off"
        attrs["heating_rate"] = self._room.heating_rate

        # If boosted show boost end time
        if self._room.is_boosted:
            attrs["boost_end"] = self._room.boost_end_time

        attrs["boost_time_remaining"] = int(self._room.boost_time_remaining / 60)
        attrs["percentage_demand"] = self._room.percentage_demand
        attrs["comfort_mode_score"] = self._room.comfort_mode_score
        attrs["control_direction"] = self._room.control_direction
        attrs["displayed_setpoint"] = self._room.displayed_setpoint

        # Added by LGO
        # Climate capabilities only with Hub Vé
        if self._room.capabilities:
            attrs["heating_supported"] = self._room.capabilities.heating_supported
            attrs["cooling_supported"] = self._room.capabilities.cooling_supported
            attrs[
                "minimum_heat_set_point"
            ] = self._room.capabilities.minimum_heat_set_point
            attrs[
                "maximum_heat_set_point"
            ] = self._room.capabilities.maximum_heat_set_point
            attrs[
                "minimum_cool_set_point"
            ] = self._room.capabilities.minimum_cool_set_point
            attrs[
                "maximum_cool_set_point"
            ] = self._room.capabilities.maximum_cool_set_point
            attrs["setpoint_step"] = self._room.capabilities.setpoint_step
            attrs["ambient_temperature"] = self._room.capabilities.ambient_temperature
            attrs["temperature_control"] = self._room.capabilities.temperature_control
            attrs[
                "open_window_detection"
            ] = self._room.capabilities.open_window_detection
            attrs[
                "hydronic_channel_selection"
            ] = self._room.capabilities.hydronic_channel_selection
            attrs["on_off_supported"] = self._room.capabilities.on_off_supported

        # Summer comfort

        attrs["include_in_summer_comfort"] = self._room.include_in_summer_comfort
        attrs["floor_sensor_state"] = self._room.floor_sensor_state

        # occupancy

        attrs["occupancy_capable"] = self._room.occupancy_capable
        if self._room.occupancy_capable:
            attrs["occupancy"] = self._room.occupancy
            attrs["occupied_heating_set_point"] = self._room.occupied_heating_set_point
            attrs[
                "unoccupied_heating_set_point"
            ] = self._room.unoccupied_heating_set_point

        # End Added by LGO

        # Room can have no schedule
        if self._room.schedule:
            attrs["schedule_id"] = self._room.schedule.id
            attrs["schedule_name"] = self._room.schedule.name
            attrs["current_schedule_temp"] = self._room.schedule.current_setting
            attrs["next_day_change"] = str(self._room.schedule.next.day)
            attrs["next_schedule_change"] = str(self._room.schedule.next.time)
            attrs["next_schedule_datetime"] = str(self._room.schedule.next.datetime)
            attrs["next_schedule_temp"] = self._room.schedule.next.setting

        if self._room.is_passive_mode:
            attrs["passive_mode_temp_increment"] = self.passive_temperature_increment

        return attrs

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return (
            PASSIVE_MODE_SUPPORT_FLAGS if self._room.is_passive_mode else SUPPORT_FLAGS
        )

    @property
    def target_temperature(self):
        """Return target temp."""
        if (
            self._room.mode == "Off"
            or self._room.current_target_temperature == TEMP_OFF
        ):
            return None

        # if self._is_passive_mode and not self._room.is_boosted:
        #    return None

        return self._room.current_target_temperature

    @property
    def target_temperature_step(self) -> float | None:
        """Return the supported step of target temperature."""
        return 0.5

    @property
    def target_temperature_high(self) -> float | None:
        """Return the highbound target temperature we try to reach.
        Requires ClimateEntityFeature.TARGET_TEMPERATURE_RANGE.
        """
        return self._room.passive_mode_upper_temp

    @property
    def target_temperature_low(self) -> float | None:
        """Return the lowbound target temperature we try to reach.
        Requires ClimateEntityFeature.TARGET_TEMPERATURE_RANGE.
        """
        return self._room.passive_mode_lower_temp

    @hub_error_handler
    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if self._room.is_passive_mode and not self._room.is_boosted:
            if kwargs.get("target_temp_low", None):
                await self._room.set_passive_mode_lower_temp(
                    kwargs.get("target_temp_low")
                )
            if kwargs.get("target_temp_high", None) and self.hvac_mode == HVACMode.HEAT:
                await self._room.set_passive_mode_upper_temp(
                    kwargs.get("target_temp_high")
                )
        else:
            target_temperature = kwargs.get(ATTR_TEMPERATURE)
            if target_temperature is None:
                return False

            if self._data.setpoint_mode == WISER_SETPOINT_MODES["Boost"] or (
                self._data.setpoint_mode == WISER_SETPOINT_MODES["BoostAuto"]
                and self.state == HVACMode.AUTO
            ):
                _LOGGER.debug(
                    f"Setting temperature for {self.name} to {target_temperature} using boost"
                )
                await self._room.set_target_temperature_for_duration(
                    target_temperature, self._data.boost_time
                )
            else:
                _LOGGER.debug(
                    f"Setting temperature for {self.name} to {target_temperature}"
                )
                await self._room.set_target_temperature(target_temperature)
        await self.async_force_update()
        return True

    @property
    def temperature_unit(self):
        """Return temp units."""
        return UnitOfTemperature.CELSIUS

    @property
    def unique_id(self):
        """Return unique Id."""
        return (
            f"{self._data.wiserhub.system.name}-WiserRoom-{self._room_id}-{self.name}"
        )

    @hub_error_handler
    @callback
    async def async_boost_heating(
        self, time_period: int, temperature_delta=0, temperature=0
    ) -> None:
        """Boost heating for room"""
        # If neither temperature_delta or temperature set then use config boost temp. Issue #216
        if temperature_delta == 0 and temperature == 0:
            temperature_delta = self._data.boost_temp

        if temperature_delta > 0:
            _LOGGER.debug(
                f"Boosting heating for {self._room.name} by {temperature_delta}C for {time_period}m "
            )
            await self._room.boost(temperature_delta, time_period)
        if temperature > 0 and temperature_delta == 0:
            _LOGGER.debug(
                f"Boosting heating for {self._room.name} to {temperature}C for {time_period}m "
            )
            await self._room.set_target_temperature_for_duration(
                temperature, time_period
            )
        await self.async_force_update()
