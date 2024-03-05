"""
Climate Platform Device for Wiser Rooms.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
import logging
import math
from .events import fire_events
import voluptuous as vol

from homeassistant.components.climate import (
    HVACAction,
    HVACMode,
    ClimateEntityFeature,
)
from homeassistant.components.climate import ClimateEntity
from homeassistant.const import (
    ATTR_TEMPERATURE,
    EVENT_HOMEASSISTANT_START,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature
)
from homeassistant.core import callback, CoreState, HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from aioWiserHeatAPI.const import TEXT_BOOST, WISER_BOOST_DURATION, WiserPresetOptionsEnum
from aioWiserHeatAPI.wiserhub import TEMP_MINIMUM, TEMP_MAXIMUM, TEMP_OFF
from aioWiserHeatAPI.devices import _WiserRoomStat, _WiserSmartValve
from .const import (
    DATA,
    DOMAIN,
    MANUFACTURER,
    ROOM,
    HOT_WATER,
    WISER_BOOST_PRESETS,
    WISER_HW_HEAT_MODES,
    WISER_HW_AUTO_MODES,
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
ATTR_SOURCE = "source"
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

TARGET_TEMP_SOURCES = {
    "HVAC": "HVAC",
    "Sensor": "Sensor",
    "Other": "Other",
}

TEMP_HW_MAXIMUM = 80

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

    if coordinator.wiserhub.hotwater and coordinator.enable_hw_climate and coordinator.hw_sensor_entity_id:
        _LOGGER.debug("Setting up Hot Water climate entity")
        wiser_hotwater = WiserHotWater(hass, coordinator)
        async_add_entities([wiser_hotwater], True)


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

        # Climate devices (iTRVs and Roomstats)
        attrs["number_of_trvs"] = len(
            [
                device
                for device in self._room.devices
                if isinstance(device, (_WiserSmartValve))
            ]
        )
        attrs["number_of_trvs_locked"] = len(
            [
                device
                for device in self._room.devices
                if isinstance(device, (_WiserSmartValve)) and device.device_lock_enabled
            ]
        )
        attrs["is_roomstat_locked"] = (
            len(
                [
                    device
                    for device in self._room.devices
                    if isinstance(device, (_WiserRoomStat))
                    and device.device_lock_enabled
                ]
            )
            > 0
        )

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


class WiserHotWater(CoordinatorEntity, ClimateEntity, WiserScheduleEntity):
    """WiserHotWater ClientEntity Object."""

    def __init__(self, hass: HomeAssistant, coordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._hass = hass
        self._data = coordinator
        self._hotwater = self._data.wiserhub.hotwater
        self._hvac_modes_list = [modes for modes in HVAC_MODE_HASS_TO_WISER.keys()]
        self._hotwater_id = self._hotwater.id
        self._is_heating = self._hotwater.is_heating
        self._schedule = self._hotwater.schedule
        self._boosted_time = 0

        self._current_temperature = None

        self._auto_mode = self._data.hw_auto_mode
        self._heat_mode = self._data.hw_heat_mode
        self._sensor_entity_id = self._data.hw_sensor_entity_id
        self._target_temperature = self._data.hw_target_temperature

        _LOGGER.debug(f"{self._data.wiserhub.system.name} {self.name} initailise")

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._sensor_entity_id], self._async_sensor_changed
            )
        )

        @callback
        def _async_startup(*_):
            """Init on startup."""
            sensor_state = self.hass.states.get(self._sensor_entity_id)
            if sensor_state and sensor_state.state not in (
                STATE_UNAVAILABLE,
                STATE_UNKNOWN,
            ):
                self._async_update_temp(sensor_state)
                self.async_write_ha_state()

        if self.hass.state == CoreState.running:
            _async_startup()
        else:
            self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, _async_startup)

    async def async_force_update(self):
        _LOGGER.debug(f"Hub update initiated by {self.name}")
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug(f"{self.name} updating")

        previous_hotwater_values = self._hotwater
        previous_hvac_mode = self.hvac_mode
        self._hotwater = self._data.wiserhub.hotwater
        self._schedule = self._hotwater.schedule
        hvac_mode = self.hvac_mode

        _LOGGER.debug(f"{self.name} hvac mode is {hvac_mode} (was {previous_hvac_mode})")
        _LOGGER.debug(f"{self.name} heating is {self._hotwater.is_heating} (was {previous_hotwater_values.is_heating})")

        if not self._hotwater.is_boosted:
            self._boosted_time = 0

        self.async_write_ha_state()

        fire_events(
            self._hass,
            self.entity_id,
            previous_hotwater_values,
            self._hotwater,
        )

    @property
    def current_temperature(self):
        """Return current temperature."""
        return self._current_temperature

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._hotwater_id, "Hot Water"),
            "identifiers": {
                (DOMAIN, get_identifier(self._data, self._hotwater_id, "hot_water"))
            },
            "manufacturer": MANUFACTURER,
            "model": HOT_WATER.title(),
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def icon(self):
        """Return icon to show if hotwater is heating, not heating or set to off."""
        if self.hvac_mode == HVACMode.OFF:
            return "mdi:snowflake"
        elif self._hotwater.is_heating:
            return "mdi:fire"
        else:
            return "mdi:fire-off"

    @property
    def hvac_action(self):
        """Return hvac action from data."""
        return HVACAction.HEATING if self._hotwater.is_heating else HVACAction.IDLE

    @property
    def is_hvac_mode_heat(self):
        return (
            self._hotwater.mode == "Manual"
            and (
                self._hotwater.is_heating
                or (
                    self._heat_mode == WISER_HW_HEAT_MODES["Override"]
                    and self._hotwater.is_override
                )
            )
        )

    @property
    def hvac_mode(self):
        if self._hotwater.mode == "Manual" and not self.is_hvac_mode_heat:
            return HVACMode.OFF
        return HVAC_MODE_WISER_TO_HASS[self._hotwater.mode]

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return self._hvac_modes_list

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new operation mode."""
        _LOGGER.debug(f"Setting HVAC mode to {hvac_mode} for {self.name}")

        # Hot Water only has Wiser modes Auto and Manual so we use overrides to differentiate
        # between HVACMode.HEAT and HVACMode.OFF.
        if hvac_mode == HVACMode.OFF:
            # Cancel any overrides before we switch to Manual as otherwise we'll end up switching
            # to HEAT in Override mode.
            await self._hotwater.cancel_overrides()
            await self._hotwater.set_mode("Manual")
            # Actually turn off the heating
            await self._hotwater.override_state("Off")
            await self.async_force_update()
            self.async_write_ha_state()
        elif hvac_mode == HVACMode.HEAT:
            if self._heat_mode == WISER_HW_HEAT_MODES["Override"] and not self._hotwater.is_boosted:
                await self._hotwater.set_mode("Auto")
                await self._hotwater.override_state("Off")
            await self._hotwater.set_mode("Manual")
            await self.async_set_temperature(**{
              "entity_id": self.entity_id,
              ATTR_TEMPERATURE: self._target_temperature,
              ATTR_SOURCE: TARGET_TEMP_SOURCES["HVAC"],
            })
        elif hvac_mode == HVACMode.AUTO:
            # Cancel the override if in Override mode and previously in HEAT mode
            if self._heat_mode == WISER_HW_HEAT_MODES["Override"] and self.hvac_mode == HVACMode.HEAT:
                await self._hotwater.cancel_overrides()
            await self._hotwater.set_mode("Auto")
            await self.async_set_temperature(**{
              "entity_id": self.entity_id,
              ATTR_TEMPERATURE: self._target_temperature,
              ATTR_SOURCE: TARGET_TEMP_SOURCES["HVAC"],
            })
        else:
            _LOGGER.error(f"Invalid HVAC mode. Options are {self.hvac_modes}")
            return
        return True

    @property
    def max_temp(self):
        """Return max temp from data."""
        return TEMP_HW_MAXIMUM

    @property
    def min_temp(self):
        """Return min temp from data."""
        return TEMP_MINIMUM

    @property
    def name(self):
        """Return Name of device."""
        return get_device_name(self._data, self._hotwater_id, "Hot Water")

    @property
    def preset_mode(self):
        """Get current preset mode."""
        try:
            if self._hotwater.is_boosted:
                if int(self._hotwater.boost_time_remaining / 60) != 0:
                    return f"{STATUS_BOOST} {int(self._hotwater.boost_time_remaining/60)}m"
                else:
                    return STATUS_BOOST
            # Ignore the override if in Override and HEAT mode
            elif (
                    self._heat_mode == WISER_HW_HEAT_MODES["Override"]
                    and self.hvac_mode == HVACMode.HEAT
                    and self._hotwater.current_control_source == "FromManualOverride"
            ):
                return STATUS_BLANK
            else:
                return WISER_PRESET_TO_HASS[self._hotwater.current_control_source]
        except KeyError:
            return STATUS_BLANK

    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        return [mode.value for mode in WiserPresetOptionsEnum]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Async call to set preset mode ."""
        _LOGGER.debug(f"Setting Preset Mode {preset_mode} for {self._hotwater.name}")
        try:
            # Is it valid preset option?
            if preset_mode in self.preset_modes:
                if preset_mode == WiserPresetOptionsEnum.cancel_overrides.value:
                    # Redirect calls to cancel_overrides to cancel boost if we are in Heat Override mode.
                    if (
                        self._heat_mode == WISER_HW_HEAT_MODES["Override"]
                        and self._hotwater.mode == "Manual"
                        and self._hotwater.is_override
                    ):
                        await self._hotwater.cancel_boost()
                    else:
                        await self._hotwater.cancel_overrides()
                elif preset_mode == WiserPresetOptionsEnum.advance_schedule.value:
                    await self._hotwater.schedule_advance()
                elif preset_mode.lower().startswith(TEXT_BOOST.lower()):
                    # Lookup boost duration
                    duration = WISER_BOOST_DURATION[preset_mode]
                    _LOGGER.info(
                        f"Boosting for {duration}"
                    )
                    await self._hotwater.boost(duration)
            else:
                raise ValueError(
                    f"{preset_mode} is not a valid preset.  Valid presets are {self.preset_modes}"
                )
        except ValueError as ex:
            _LOGGER.error(ex)

        await self.async_force_update()

    @property
    def hotwater(self):
        """Return hotwater"""
        return self._hotwater

    @property
    def state(self):
        """Return state"""
        return self.hvac_mode

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        # Generic attributes
        attrs = super().state_attributes

        # Settings
        attrs["away_mode_supressed"] = self._hotwater.away_mode_suppressed

        # Status
        attrs["is_boosted"] = self._hotwater.is_boosted
        attrs["is_override"] = self._hotwater.is_override
        attrs["is_heating"] = self._hotwater.is_heating
        attrs["current_control_source"] = self._hotwater.current_control_source
        attrs["control_output_state"] = "On" if self._hotwater.is_heating else "Off"

        # If boosted show boost end time
        if self._hotwater.is_boosted:
            attrs["boost_end"] = self._hotwater.boost_end_time

        attrs["boost_time_remaining"] = int(self._hotwater.boost_time_remaining / 60)

        # Hot Water can have no schedule
        if self._hotwater.schedule:
            attrs["schedule_id"] = self._hotwater.schedule.id
            attrs["schedule_name"] = self._hotwater.schedule.name
            attrs["current_schedule_temp"] = self._hotwater.schedule.current_setting
            attrs["next_day_change"] = str(self._hotwater.schedule.next.day)
            attrs["next_schedule_change"] = str(self._hotwater.schedule.next.time)
            attrs["next_schedule_datetime"] = str(self._hotwater.schedule.next.datetime)
            attrs["next_schedule_temp"] = self._hotwater.schedule.next.setting

        return attrs

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def target_temperature(self):
        """Return target temp."""
        if (
            self.hvac_mode == HVACMode.OFF
            or self._target_temperature == TEMP_OFF
        ):
            return None

        return self._target_temperature

    @property
    def target_temperature_step(self) -> float | None:
        """Return the supported step of target temperature."""
        return 0.5

    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if self._current_temperature is None:
            return False

        target_temperature = kwargs.get(ATTR_TEMPERATURE)
        if target_temperature is None:
            return False

        self._target_temperature = target_temperature

        source = kwargs.get(ATTR_SOURCE, TARGET_TEMP_SOURCES["Other"])

        if self._data.setpoint_mode == WISER_SETPOINT_MODES["Boost"] or (
            self._data.setpoint_mode == WISER_SETPOINT_MODES["BoostAuto"]
            and self.state == HVACMode.AUTO
        ):
            _LOGGER.debug(
                f"Setting temperature for {self.name} to {target_temperature} using boost"
            )
            await self._async_set_temperature(self.hvac_mode, source, self._data.hw_boost_time)
        else:
            _LOGGER.debug(
                f"Setting temperature for {self.name} to {target_temperature}"
            )
            await self._async_set_temperature(self.hvac_mode, source)
        return True

    async def _async_set_temperature(self, hvac_mode, source, duration=None):
        """Set hotwater state based on temperature"""
        _LOGGER.debug(f"Set temperature for HVAC mode {hvac_mode}")

        if hvac_mode == HVACMode.OFF:
            await self._hotwater.cancel_overrides()
            await self.async_force_update()
            #self.async_write_ha_state()
            # As a temperature has been set update to HEAT mode
            hvac_mode = HVACMode.HEAT

        # If we are in Override mode and HEAT mode we have to switch to Auto to ensure overrides
        # are tracked in Manual (otherwise override_state just turns Heating on or off instead of
        # adding an override)
        if hvac_mode == HVACMode.HEAT and self._heat_mode == WISER_HW_HEAT_MODES["Override"]:
            await self._hotwater.set_mode(HVAC_MODE_HASS_TO_WISER[HVACMode.AUTO])

        if self._current_temperature < self._target_temperature:
            _LOGGER.debug(f"Setting state for {self.name} to On as current {self._current_temperature}C < target {self._target_temperature}C")
            # In HEAT mode ensure that the Heating is on
            if hvac_mode == HVACMode.HEAT:
                if duration is not None:
                    await self._hotwater.override_state_for_duration("On", duration)
                else:
                    await self._hotwater.override_state("On")
            # In AUTO mode revert back to the schedule unless Once mode is active and the source
            # is the temperature sensor
            elif hvac_mode == HVACMode.AUTO and not (
                self._auto_mode == WISER_HW_AUTO_MODES["Once"] and source == TARGET_TEMP_SOURCES["Sensor"]
            ):
                await self._hotwater.cancel_overrides()

        # Always add an Idle override when the temperature has reached or risen above the target
        # temperature
        if self._current_temperature >= self._target_temperature:
            _LOGGER.debug(f"Setting state for {self.name} to Off as current {self._current_temperature}C >= target {self._target_temperature}C")
            await self._hotwater.override_state("Off")

        # If we are in Override mode and HEAT mode then revert from Auto to Manual now we have set
        # the override
        if hvac_mode == HVACMode.HEAT and self._heat_mode == WISER_HW_HEAT_MODES["Override"]:
            await self._hotwater.set_mode(HVAC_MODE_HASS_TO_WISER[hvac_mode])

        await self.async_force_update()
        self.async_write_ha_state()

    @property
    def temperature_unit(self):
        """Return temp units."""
        return UnitOfTemperature.CELSIUS

    @property
    def unique_id(self):
        """Return unique Id."""
        return (
            f"{self._data.wiserhub.system.name}-WiserHotWater-{self._hotwater_id}-{self.name}"
        )

    async def _async_sensor_changed(self, event) -> None:
        """Handle temperature changes."""
        new_state = event.data["new_state"]
        if new_state is None or new_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return

        self._async_update_temp(new_state)
        await self.async_force_update()
        self.async_write_ha_state()

    @callback
    def _async_update_temp(self, state) -> None:
        """Update thermostat with latest state from sensor."""
        try:
            previous_temperature = self._current_temperature
            current_temperature = float(state.state)
            if not math.isfinite(current_temperature):
                raise ValueError(f"Sensor has illegal state {state.state}")
            self._current_temperature = current_temperature
            # Only update the climate entity if the temperature has updated and we are not in OFF mode
            if (
                previous_temperature != current_temperature
                and self.hvac_mode != HVACMode.OFF
            ):
                self._hass.loop.create_task(self.async_set_temperature(**{
                    "entity_id": self.entity_id,
                    ATTR_TEMPERATURE: self._target_temperature,
                    ATTR_SOURCE: TARGET_TEMP_SOURCES["Sensor"],
                }))


        except ValueError as ex:
            _LOGGER.error("Unable to update from sensor: %s", ex)
