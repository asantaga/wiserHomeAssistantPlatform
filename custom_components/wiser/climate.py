"""Climate Platform Device for Wiser Rooms, UFH temp probes and HW climate control.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""

import logging

from aioWiserHeatAPI.const import (
    TEXT_BOOST,
    WISER_BOOST_DURATION,
    WiserPresetOptionsEnum,
)
from aioWiserHeatAPI.devices import _WiserRoomStat, _WiserSmartValve
from aioWiserHeatAPI.hot_water import _WiserHotwater
from aioWiserHeatAPI.wiserhub import TEMP_MAXIMUM, TEMP_MINIMUM, TEMP_OFF
import voluptuous as vol

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    EVENT_HOMEASSISTANT_START,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature,
)
from homeassistant.core import CoreState, HomeAssistant, callback
from homeassistant.helpers import entity_platform
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DATA,
    DOMAIN,
    HOT_WATER,
    HW_CLIMATE_MAX_TEMP,
    HW_CLIMATE_MIN_TEMP,
    MANUFACTURER,
    ROOM,
    WISER_BOOST_PRESETS,
    WISER_SERVICES,
    WISER_SETPOINT_MODES,
    HWCycleModes,
)
from .events import fire_events
from .helpers import get_device_name, get_identifier, hub_error_handler
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

    if (
        coordinator.wiserhub.hotwater
        and coordinator.wiserhub.hotwater.is_climate_mode
        and coordinator.hw_sensor_entity_id
    ):
        _LOGGER.debug("Setting up Hot Water climate entity")
        wiser_hotwater = WiserHotWater(hass, coordinator)
        async_add_entities([wiser_hotwater], True)


class WiserTempProbe(CoordinatorEntity, ClimateEntity):
    """Wiser temp probe climate entity object."""

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

        _LOGGER.debug("%s %s initialise", self._data.wiserhub.system.name, self.name)

    async def async_force_update(self):
        """Force update from hub."""
        _LOGGER.debug("Hub update initiated by %s", self.name)
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug("%s updating", self.name)
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
        """Return HVAC mode."""
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
            kwargs.get("target_temp_low")
            != self._actuator.floor_temperature_sensor.minimum_temperature
        ):
            await self._actuator.floor_temperature_sensor.set_minimum_temperature(
                kwargs.get("target_temp_low")
            )
            await self.async_force_update()

        if (
            kwargs.get("target_temp_high")
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
        self._hvac_modes_list = list(HVAC_MODE_HASS_TO_WISER.keys())
        self._is_heating = self._room.is_heating
        self._schedule = self._room.schedule
        self._boosted_time = 0

        self.passive_temperature_increment = self._data.passive_temperature_increment

        _LOGGER.debug("%s %s initialise", self._data.wiserhub.system.name, self.name)

    async def async_force_update(self):
        """Force update form hub."""
        _LOGGER.debug("Hub update initiated by %s", self.name)
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug("%s updating", self.name)
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
        if self._room.is_heating:
            return "mdi:radiator"
        return "mdi:radiator-disabled"

    @property
    def hvac_action(self):
        """Return hvac action from data."""
        return HVACAction.HEATING if self._room.is_heating else HVACAction.IDLE

    @property
    def hvac_mode(self):
        """Return HVAC mode."""
        return HVAC_MODE_WISER_TO_HASS[self._room.mode]

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return self._hvac_modes_list

    @hub_error_handler
    async def async_set_hvac_mode(self, hvac_mode):
        """Set new operation mode."""
        _LOGGER.debug("Setting HVAC mode to %s for %s", hvac_mode, self._room.name)
        try:
            await self._room.set_mode(HVAC_MODE_HASS_TO_WISER[hvac_mode])
            await self.async_force_update()
        except KeyError:
            _LOGGER.error("Invalid HVAC mode.  Options are %s", self.hvac_modes)
        else:
            return True

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
            if self._room.preset_mode == "Boost":
                if int(self._room.boost_time_remaining / 60) != 0:
                    return f"{STATUS_BOOST} {int(self._room.boost_time_remaining/60)}m"
                return STATUS_BOOST
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
        _LOGGER.debug("Setting Preset Mode %s for %s", preset_mode, self._room.name)
        try:
            await self._room.set_preset(preset_mode)
        except ValueError as ex:
            _LOGGER.error(ex)

        await self.async_force_update()

    @property
    def room(self):
        """Return room."""
        return self._room

    @property
    def state(self):
        """Return state."""
        return HVAC_MODE_WISER_TO_HASS[self._room.mode]

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        # Generic attributes
        attrs = super().state_attributes

        # Settings
        attrs["name"] = self._room.name
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
        # Climate capabilities only with Hub V2
        if self.data.hub_version >= 2:
            if self._room.capabilities:
                attrs["heating_supported"] = self._room.capabilities.heating_supported
                attrs["cooling_supported"] = self._room.capabilities.cooling_supported
                attrs["minimum_heat_set_point"] = (
                    self._room.capabilities.minimum_heat_set_point
                )
                attrs["maximum_heat_set_point"] = (
                    self._room.capabilities.maximum_heat_set_point
                )
                attrs["minimum_cool_set_point"] = (
                    self._room.capabilities.minimum_cool_set_point
                )
                attrs["maximum_cool_set_point"] = (
                    self._room.capabilities.maximum_cool_set_point
                )
                attrs["setpoint_step"] = self._room.capabilities.setpoint_step
                attrs["ambient_temperature"] = (
                    self._room.capabilities.ambient_temperature
                )
                attrs["temperature_control"] = (
                    self._room.capabilities.temperature_control
                )
                attrs["open_window_detection"] = (
                    self._room.capabilities.open_window_detection
                )
                attrs["hydronic_channel_selection"] = (
                    self._room.capabilities.hydronic_channel_selection
                )
                attrs["on_off_supported"] = self._room.capabilities.on_off_supported

            # Summer comfort

            attrs["include_in_summer_comfort"] = self._room.include_in_summer_comfort
            attrs["floor_sensor_state"] = self._room.floor_sensor_state

            # occupancy

            attrs["occupancy_capable"] = self._room.occupancy_capable
            if self._room.occupancy_capable:
                attrs["occupancy"] = self._room.occupancy
                attrs["occupied_heating_set_point"] = (
                    self._room.occupied_heating_set_point
                )
                attrs["unoccupied_heating_set_point"] = (
                    self._room.unoccupied_heating_set_point
                )

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
            if kwargs.get("target_temp_low"):
                await self._room.set_passive_mode_lower_temp(
                    kwargs.get("target_temp_low")
                )
            if kwargs.get("target_temp_high") and self.hvac_mode == HVACMode.HEAT:
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
                    "Setting temperature for %s to %s using boost",
                    self.name,
                    target_temperature,
                )
                await self._room.set_target_temperature_for_duration(
                    target_temperature, self._data.boost_time
                )
            else:
                _LOGGER.debug(
                    "Setting temperature for %s to %s", self.name, target_temperature
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
    async def async_boost_heating(
        self, time_period: int, temperature_delta=0, temperature=0
    ) -> None:
        """Boost heating for room."""
        # If neither temperature_delta or temperature set then use config boost temp. Issue #216
        if temperature_delta == 0 and temperature == 0:
            temperature_delta = self._data.boost_temp

        if temperature_delta > 0:
            _LOGGER.debug(
                "Boosting heating for %s by %sC for %sm",
                self._room.name,
                temperature_delta,
                time_period,
            )
            await self._room.boost(temperature_delta, time_period)
        if temperature > 0 and temperature_delta == 0:
            _LOGGER.debug(
                "Boosting heating for %s by %sC for %sm",
                self._room.name,
                temperature,
                time_period,
            )
            await self._room.set_target_temperature_for_duration(
                temperature, time_period
            )
        await self.async_force_update()


class WiserHotWater(CoordinatorEntity, ClimateEntity, WiserScheduleEntity):
    """WiserHotWater ClientEntity Object."""

    _enable_turn_on_off_backwards_compatibility = False

    def __init__(self, hass: HomeAssistant, coordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._hass = hass
        self._data = coordinator
        self._hotwater = self._data.wiserhub.hotwater
        self._hvac_modes_list = list(HVAC_MODE_HASS_TO_WISER.keys())
        self._schedule = self.hotwater.schedule
        self._boosted_time = 0
        self._keep_cycling: bool = True
        self._boost_keep_cycling: bool = True

        # Variables to support hw climate control
        self._current_temperature = None
        self._auto_mode = self._data.hw_auto_mode
        self._heat_mode = self._data.hw_heat_mode
        self._sensor_entity_id = self._data.hw_sensor_entity_id
        self._keep_cycling: bool = True
        self._boost_keep_cycling: bool = True
        # Prevent hot water turning on if in heat mode at restart
        # requires manual turn on to start if not already on
        if self.hvac_mode == HVACMode.HEAT and not self._hotwater.manual_heat:
            self._keep_cycling = False

        _LOGGER.debug("%s %s initiliase", self._data.wiserhub.system.name, self.name)

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
                self._current_temperature = float(sensor_state.state)
                self.async_write_ha_state()

        if self.hass.state == CoreState.running:
            _async_startup()
        else:
            self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, _async_startup)

    async def async_force_update(self):
        """Force update form hub."""
        _LOGGER.debug("Hub update initiated by %s", self.name)
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug("%s updating", self.name)

        previous_hotwater_values = self._hotwater
        self._hotwater = self._data.wiserhub.hotwater
        self._schedule = self.hotwater.schedule

        if not self.hotwater.is_boosted:
            self._boosted_time = 0

        # reset keep_cycling
        if not self._keep_cycling:
            if (
                self.hvac_mode == HVACMode.AUTO
                and self.hotwater.schedule.current_setting == "Off"
            ):
                # Reset in auto mode when schedule state is off
                self._keep_cycling = True
            elif self.hvac_mode == HVACMode.HEAT and (
                (not previous_hotwater_values.is_heating and self.hotwater.is_heating)
                or self.hotwater.manual_heat
            ):
                # Reset in heat mode if turned on manually
                self._keep_cycling = True

        # Reset boost keep cycling
        if not self._boost_keep_cycling and not self.hotwater.is_boosted:
            # Reset if boost ended
            self._boost_keep_cycling = True

        self.async_write_ha_state()

        self.hass.create_task(self.run_automation(), name="HW Climate Automation")

        fire_events(
            self._hass,
            self.entity_id,
            previous_hotwater_values,
            self.hotwater,
        )

    @property
    def hotwater(self) -> _WiserHotwater:
        """Return hotwater."""
        return self._hotwater

    @property
    def max_temp(self):
        """Return max temp from data."""
        return HW_CLIMATE_MAX_TEMP

    @property
    def min_temp(self):
        """Return min temp from data."""
        return HW_CLIMATE_MIN_TEMP

    @property
    def current_temperature(self):
        """Return current temperature."""
        return self._current_temperature

    @property
    def target_temperature_step(self) -> float | None:
        """Return the supported step of target temperature."""
        return 0.5

    @property
    def target_temperature_high(self):
        """Return target temp."""
        if self.hvac_mode == HVACMode.OFF:
            return None
        return self.hotwater.current_target_temperature_high

    @property
    def target_temperature_low(self):
        """Return target temp."""
        if self.hvac_mode == HVACMode.OFF:
            return None
        return self.hotwater.current_target_temperature_low

    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if low_temp := kwargs.get("target_temp_low"):
            # Low must be a minimum of 1C below high to prevent oscillating on/off
            if self.target_temperature_high - low_temp < 1:
                low_temp = self.target_temperature_high - 1
            await self.hotwater.set_target_temperature_low(low_temp)
        if high_temp := kwargs.get("target_temp_high"):
            await self.hotwater.set_target_temperature_high(high_temp)
        _LOGGER.debug(
            "Setting temperature range for %s to between %s and %s",
            self.name,
            kwargs.get("target_temp_low"),
            kwargs.get("target_temp_high"),
        )
        await self.async_force_update()
        return True

    @property
    def hvac_action(self):
        """Return hvac action from data."""
        return HVACAction.HEATING if self.hotwater.is_heating else HVACAction.IDLE

    @property
    def hvac_mode(self):
        """Return HVAC mode."""
        return HVAC_MODE_WISER_TO_HASS[self.hotwater.mode]

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return self._hvac_modes_list

    @hub_error_handler
    async def async_set_hvac_mode(self, hvac_mode):
        """Set new operation mode."""
        _LOGGER.debug("Setting HVAC mode to %s for Hot Water", hvac_mode)
        try:
            await self.hotwater.set_mode(HVAC_MODE_HASS_TO_WISER[hvac_mode])
            await self.async_force_update()
        except KeyError:
            _LOGGER.error("Invalid HVAC mode.  Options are %s", self.hvac_modes)
        else:
            return True

    @property
    def preset_mode(self):
        """Get current preset mode."""
        try:
            if self.hotwater.is_boosted:
                if int(self.hotwater.boost_time_remaining / 60) != 0:
                    return (
                        f"{STATUS_BOOST} {int(self.hotwater.boost_time_remaining/60)}m"
                    )
                return STATUS_BOOST
            return WISER_PRESET_TO_HASS[self.hotwater.current_control_source]
        except KeyError:
            return STATUS_BLANK

    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        return [mode.value for mode in WiserPresetOptionsEnum]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Async call to set preset mode ."""
        _LOGGER.debug("Setting Preset Mode %s for %s", preset_mode, self.hotwater.name)
        try:
            # Is it valid preset option?
            if preset_mode in self.preset_modes:
                if preset_mode == WiserPresetOptionsEnum.cancel_overrides.value:
                    await self.hotwater.cancel_boost()
                elif preset_mode == WiserPresetOptionsEnum.advance_schedule.value:
                    await self.hotwater.schedule_advance()
                elif preset_mode.lower().startswith(TEXT_BOOST.lower()):
                    # Lookup boost duration
                    duration = WISER_BOOST_DURATION[preset_mode]
                    _LOGGER.info("Boosting for %s", duration)
                    # If temp is already above target, set boost but with off value
                    # which will cause it to turn on when below low temp for 1 (once mode) cycle or
                    # keep cycling (continuous mode)
                    await self._hotwater.boost(
                        duration,
                        "On"
                        if self.current_temperature < self.target_temperature_high
                        else "Off",
                    )
            else:
                raise ValueError(  # noqa: TRY301
                    f"{preset_mode} is not a valid preset.  Valid presets are {self.preset_modes}"
                )
        except ValueError as ex:
            _LOGGER.error(ex)

        await self.async_force_update()

    @property
    def name(self):
        """Return Name of device."""
        return get_device_name(self._data, self.hotwater.id, "Hot Water")

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self.hotwater.id, "Hot Water"),
            "identifiers": {
                (DOMAIN, get_identifier(self._data, self.hotwater.id, "hot_water"))
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
        if self.hotwater.is_heating:
            return "mdi:fire"
        return "mdi:fire-off"

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        # Generic attributes
        attrs = super().state_attributes

        # Settings
        attrs["away_mode_supressed"] = self.hotwater.away_mode_suppressed

        # Status
        attrs["is_boosted"] = self.hotwater.is_boosted
        attrs["is_override"] = self.hotwater.is_override
        attrs["is_heating"] = self.hotwater.is_heating
        attrs["current_control_source"] = self.hotwater.current_control_source
        attrs["control_output_state"] = "On" if self.hotwater.is_heating else "Off"

        # If boosted show boost end time
        if self.hotwater.is_boosted:
            attrs["boost_end"] = self.hotwater.boost_end_time

        attrs["boost_time_remaining"] = int(self.hotwater.boost_time_remaining / 60)

        # Hot Water can have no schedule
        if self.hotwater.schedule:
            attrs["schedule_id"] = self.hotwater.schedule.id
            attrs["schedule_name"] = self.hotwater.schedule.name
            attrs["current_schedule_temp"] = self.hotwater.schedule.current_setting
            attrs["next_day_change"] = str(self.hotwater.schedule.next.day)
            attrs["next_schedule_change"] = str(self.hotwater.schedule.next.time)
            attrs["next_schedule_datetime"] = str(self.hotwater.schedule.next.datetime)
            attrs["next_schedule_temp"] = self.hotwater.schedule.next.setting

        return attrs

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return PASSIVE_MODE_SUPPORT_FLAGS

    async def run_automation(self) -> bool:
        """Run HW Climate automation."""
        _LOGGER.debug("---------------------------------------------")
        _LOGGER.debug("Running HW climate automation")

        mode = self.hvac_mode
        if self.hotwater.is_boosted:
            mode = "boost"

        _LOGGER.debug("Running automation for %s mode", mode)

        updated = False
        should_heat = self.hotwater.is_heating

        if self.hvac_mode == HVACMode.OFF:
            # HW is off.  Just return here as if turned on by app or hub, will go
            # into manual mode.
            return False

        # Reasons it should heat
        if self.current_temperature <= self.target_temperature_low or (
            self.current_temperature <= self.target_temperature_high
            and self.hotwater.is_heating
        ):
            should_heat = True

        # Now all reasons it should not heat
        if not self.hotwater.is_boosted:
            # Boost overrides all other mode settings

            if self.hvac_mode == HVACMode.HEAT:
                # Manual mode heat is set to off
                if not self.hotwater.manual_heat:
                    should_heat = False
            elif self.hvac_mode == HVACMode.AUTO:
                # Schedule is set to off
                if self.hotwater.schedule.current_setting == "Off":
                    should_heat = False

        # Cycle override - is set to once in heat mode
        if not self._keep_cycling:
            should_heat = False

        # High temp override - has reached target high temp
        if self.current_temperature >= self.target_temperature_high:
            should_heat = False

        _LOGGER.debug(
            "Status: is_heating: %s, is_boosted: %s, target_high: %s, target_low: %s, current: %s, schedule: %s, manual_heat: %s, keep_cycling: %s, should_heat: %s",
            self.hotwater.is_heating,
            self.hotwater.is_boosted,
            self.target_temperature_high,
            self.target_temperature_low,
            self.current_temperature,
            self.hotwater.schedule.current_setting,
            self.hotwater.manual_heat,
            self._keep_cycling,
            should_heat,
        )

        # Now turn on or off based on value of should heat
        if self.hotwater.is_heating is True and should_heat is False:
            if self.hotwater.is_boosted:
                if getattr(self._data, "hw_boost_mode") == HWCycleModes.ONCE:
                    self._keep_cycling = False
                    await self.hotwater.cancel_boost()
                else:
                    await self.hotwater.override_boost("Off")
            else:
                if (
                    getattr(self._data, f"hw_{self.hvac_mode}_mode")
                    == HWCycleModes.ONCE
                ):
                    # Auto and Heat mode
                    self._keep_cycling = False

                    # Heat mode - reset manual heat
                    if self.hvac_mode == HVACMode.HEAT:
                        await self.hotwater.set_manual_heat(False)

                await self.hotwater.override_state("Off")
            updated = True

        if self.hotwater.is_heating is False and should_heat is True:
            if self.hotwater.is_boosted:
                await self.hotwater.override_boost("On")
            else:
                await self.hotwater.override_state("On")
            updated = True

        if updated:
            await self.async_force_update()
        return updated

    @property
    def temperature_unit(self):
        """Return temp units."""
        return UnitOfTemperature.CELSIUS

    @property
    def unique_id(self):
        """Return unique Id."""
        return f"{self._data.wiserhub.system.name}-WiserHotWater-{self.hotwater.id}-{self.name}"

    async def _async_sensor_changed(self, event) -> None:
        """Handle temperature changes."""
        new_state = event.data["new_state"]
        if new_state is None or new_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return

        self._current_temperature = float(new_state.state)
        await self.run_automation()
        self.async_write_ha_state()
