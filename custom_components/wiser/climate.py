"""Climate Platform Device for Wiser Rooms.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
from collections.abc import Callable
from dataclasses import dataclass
from inspect import signature
import logging
import sys
from typing import Any

from aioWiserHeatAPI.const import TEXT_OFF, TEXT_UNKNOWN, WiserTempLimitsEnum
from aioWiserHeatAPI.heating_actuator import _WiserHeatingActuator
from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom
from aioWiserHeatAPI.wiserhub import TEMP_OFF
import voluptuous as vol

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_platform
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DATA,
    DOMAIN,
    LEGACY_NAMES,
    WISER_BOOST_PRESETS,
    WISER_SERVICES,
    WISER_SETPOINT_MODES,
)
from .entity import WiserBaseEntity
from .events import fire_events
from .helpers import getattrd

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


@dataclass
class WiserEntityExtraAttribute:
    """Class to hold extra attributes definition."""

    name: str
    value_fn: Callable[[Any], float | str | bool]


@dataclass
class WiserClimateEntityPreset:
    """Class to hold preset definition entries."""

    name: str
    set_fn: Callable[[Any], float | str]


@dataclass
class WiserClimateEntityExtraDescription:
    """Class to hold climate entity description keys."""

    key: str | None = None
    name_fn: Callable[[Any], str] | str | None = None
    available_fn: Callable[[Any], bool] | None = None
    legacy_name_fn: Callable[[Any], str] | None = None
    legacy_type: str = None
    icon_fn: Callable[[Any], str] | None = None
    device: str | None = None
    device_collection: list | None = None
    entity_class: Any | None = None


@dataclass
class WiserClimateEntityDescription(
    ClimateEntityDescription, WiserClimateEntityExtraDescription
):
    """A class that describes Wiser climate entities."""


WISER_CLIMATES: tuple[WiserClimateEntityDescription, ...] = (
    WiserClimateEntityDescription(
        key="room_climate",
        legacy_name_fn=lambda x: f"Wiser {x.name}",
        name="Climate",
        device_collection="rooms",
        entity_class="WiserClimate",
    ),
    WiserClimateEntityDescription(
        key="floor_climate",
        name="Floor",
        device_collection="heating_actuators",
        available_fn=lambda x: x.floor_temperature_sensor.sensor_type != "Not_Fitted",
        entity_class="WiserFloorClimate",
    ),
)


def _attr_exist(
    data: dict,
    device: _WiserDevice,
    sensor_desc: WiserClimateEntityDescription,
) -> bool:
    """Check if an attribute exists for device."""
    try:
        no_of_params = len(signature(sensor_desc.value_fn).parameters)
        if no_of_params == 2:
            r = sensor_desc.value_fn(data, device)
        else:
            r = sensor_desc.value_fn(device)
        if r is not None and r != TEXT_UNKNOWN:
            return True
        return False
    except AttributeError:
        return False


def str_to_class(class_name: str):
    """Get class from string."""
    return getattr(sys.modules[__name__], class_name)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    wiser_climates = []

    for climate_desc in WISER_CLIMATES:
        # get device or device collection
        if climate_desc.device_collection and getattrd(
            data.wiserhub, climate_desc.device_collection
        ):
            for device in getattrd(data.wiserhub, climate_desc.device_collection).all:
                if device:
                    _LOGGER.info("Adding %s", device.name)
                    wiser_climates.append(
                        str_to_class(climate_desc.entity_class)(
                            data,
                            climate_desc,
                            device,
                        )
                    )
        elif climate_desc.device and getattrd(data.wiserhub, climate_desc.device):
            device = getattrd(data.wiserhub, climate_desc.device)
            if device:
                wiser_climates.append(
                    str_to_class(climate_desc.entity_class)(
                        data,
                        climate_desc,
                        device,
                    )
                )

    async_add_entities(wiser_climates)

    # Setup services
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        WISER_SERVICES["SERVICE_BOOST_HEATING"],
        {
            vol.Required(ATTR_TIME_PERIOD, default=data.boost_time): vol.Coerce(int),
            vol.Any(
                vol.Optional(ATTR_TEMPERATURE_DELTA, default=0),
                vol.Optional(ATTR_TEMPERATURE, default=0),
            ): vol.Coerce(float),
        },
        "async_boost_heating",
    )


class WiserClimate(WiserBaseEntity, ClimateEntity):
    """Wiser climate entity."""

    entity_description: WiserClimateEntityDescription
    _enable_turn_on_off_backwards_compatibility = False

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WiserClimateEntityDescription,
        device: _WiserDevice | _WiserRoom | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description, device, "climate")

        self._boosted_time = 0
        # self.passive_temperature_increment = self._device.passive_temperature_increment

        _LOGGER.debug("%s %s initialise", self._data.wiserhub.system.name, self.name)

    async def async_force_update(self):
        """Force update from hub."""
        _LOGGER.debug("Hub update initiated by %s", self.name)
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        previous_room_values = self._device

        super()._handle_coordinator_update()

        # self.passive_temperature_increment = self._data.passive_temperature_increment

        if not self._device.is_boosted:
            self._boosted_time = 0

        fire_events(
            self._data.hass,
            self.entity_id,
            previous_room_values,
            self._device,
        )

    @property
    def current_temperature(self):
        """Return current temp from data."""
        return self._device.current_temperature

    @property
    def current_humidity(self):
        """Return current temp from data."""
        return self._device.current_humidity

    @property
    def icon(self):
        """Return icon to show if radiator is heating, not heating or set to off."""
        if self._device.mode == TEXT_OFF:
            return "mdi:radiator-off"
        elif self._device.is_heating:
            return "mdi:radiator"
        else:
            return "mdi:radiator-disabled"

    @property
    def hvac_action(self):
        """Return hvac action from data."""
        return HVACAction.HEATING if self._device.is_heating else HVACAction.IDLE

    @property
    def hvac_mode(self):
        """Return current HVAC mode."""
        return HVAC_MODE_WISER_TO_HASS[self._device.mode]

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return list(HVAC_MODE_HASS_TO_WISER.keys())

    async def async_set_hvac_mode(self, hvac_mode):
        """Set HVAC mode."""
        _LOGGER.debug("Setting HVAC mode to %s for %s", hvac_mode, self.name)
        try:
            await self._device.set_mode(HVAC_MODE_HASS_TO_WISER[hvac_mode])
            await self.async_force_update()
        except KeyError:
            _LOGGER.error("Invalid HVAC mode.  Options are %s", self.hvac_modes)

    @property
    def max_temp(self):
        """Return max temp from data."""
        return WiserTempLimitsEnum.heating.value.get("max")

    @property
    def min_temp(self):
        """Return min temp from data."""
        return WiserTempLimitsEnum.heating.value.get("min")

    @property
    def preset_mode(self):
        """Get current preset mode."""
        try:
            if self._device.is_passive_mode:
                return TEXT_PASSIVE
            elif self._device.preset_mode == "Boost":
                if int(self._device.boost_time_remaining / 60) != 0:
                    return (
                        f"{STATUS_BOOST} {int(self._device.boost_time_remaining/60)}m"
                    )
                else:
                    return STATUS_BOOST
            else:
                return WISER_PRESET_TO_HASS[self._device.target_temperature_origin]
        except KeyError:
            return STATUS_BLANK

    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        return self._device.available_presets

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Async call to set preset mode ."""
        _LOGGER.debug("Setting Preset Mode %s for %s", preset_mode, self._device.name)
        try:
            await self._device.set_preset(preset_mode)
        except ValueError as ex:
            _LOGGER.error(ex)

        await self.async_force_update()

    @property
    def state(self):
        """Return state."""
        return HVAC_MODE_WISER_TO_HASS[self._device.mode]

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return (
            PASSIVE_MODE_SUPPORT_FLAGS
            if self._device.is_passive_mode
            else SUPPORT_FLAGS
        )

    @property
    def target_temperature(self):
        """Return target temp."""
        if (
            self._device.mode == TEXT_OFF
            or self._device.current_target_temperature == TEMP_OFF
        ):
            return None

        return self._device.current_target_temperature

    @property
    def target_temperature_step(self) -> float | None:
        """Return the supported step of target temperature."""
        return 0.5

    @property
    def target_temperature_high(self) -> float | None:
        """Return the highbound target temperature we try to reach."""
        return self._device.passive_mode_upper_temp

    @property
    def target_temperature_low(self) -> float | None:
        """Return the lowbound target temperature we try to reach."""
        return self._device.passive_mode_lower_temp

    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if self._device.is_passive_mode and not self._device.is_boosted:
            if kwargs.get("target_temp_low", None):
                await self._device.set_passive_mode_lower_temp(
                    kwargs.get("target_temp_low")
                )
            if kwargs.get("target_temp_high", None) and self.hvac_mode == HVACMode.HEAT:
                await self._device.set_passive_mode_upper_temp(
                    kwargs.get("target_temp_high")
                )
        else:
            target_temperature = kwargs.get(ATTR_TEMPERATURE)
            if target_temperature is None:
                return False

            if self._device.setpoint_mode == WISER_SETPOINT_MODES["Boost"] or (
                self._device.setpoint_mode == WISER_SETPOINT_MODES["BoostAuto"]
                and self.state == HVACMode.AUTO
            ):
                _LOGGER.debug(
                    "Setting temperature for %s to %s using boost",
                    self.name,
                    target_temperature,
                )
                await self._device.set_target_temperature_for_duration(
                    target_temperature, self._data.boost_time
                )
            else:
                _LOGGER.debug(
                    "Setting temperature for %s to %s%s",
                    self.name,
                    target_temperature,
                    UnitOfTemperature.CELSIUS,
                )
                await self._device.set_target_temperature(target_temperature)
        await self.async_force_update()
        return True

    @property
    def temperature_unit(self):
        """Return temp units."""
        return UnitOfTemperature.CELSIUS

    @callback
    async def async_boost_heating(
        self, time_period: int, temperature_delta=0, temperature=0
    ) -> None:
        """Boost heating for room."""
        # If neither temperature_delta or temperature set then use config boost temp. Issue #216
        if temperature_delta == 0 and temperature == 0:
            temperature_delta = self._data.boost_temp

        if temperature_delta > 0:
            _LOGGER.debug(
                "Boosting heating for %s by %s%s for %sm",
                self.name,
                temperature_delta,
                UnitOfTemperature.CELSIUS,
                time_period,
            )
            await self._device.boost(temperature_delta, time_period)
        if temperature > 0 and temperature_delta == 0:
            _LOGGER.debug(
                "Boosting heating for %s by %s%s to %sm",
                self.name,
                temperature,
                UnitOfTemperature.CELSIUS,
                time_period,
            )
            await self._device.set_target_temperature_for_duration(
                temperature, time_period
            )
        await self.async_force_update()

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        attrs = {}
        # Settings
        attrs["window_state"] = self._device.window_state
        attrs["window_detection_active"] = self._device.window_detection_active
        attrs["away_mode_supressed"] = self._device.away_mode_suppressed
        attrs["heating_type"] = self._device.heating_type
        attrs["number_of_heating_actuators"] = self._device.number_of_heating_actuators
        attrs["demand_type"] = self._device.demand_type

        # Status
        attrs["target_temperature_origin"] = self._device.target_temperature_origin
        attrs["is_boosted"] = self._device.is_boosted
        attrs["is_override"] = self._device.is_override
        attrs["is_heating"] = self._device.is_heating
        attrs["is_passive"] = self._device.is_passive_mode
        attrs["control_output_state"] = "On" if self._device.is_heating else "Off"
        attrs["heating_rate"] = self._device.heating_rate

        # If boosted show boost end time
        if self._device.is_boosted:
            attrs["boost_end"] = self._device.boost_end_time

        attrs["boost_time_remaining"] = int(self._device.boost_time_remaining / 60)
        attrs["percentage_demand"] = self._device.percentage_demand
        attrs["comfort_mode_score"] = self._device.comfort_mode_score
        attrs["control_direction"] = self._device.control_direction
        attrs["displayed_setpoint"] = self._device.displayed_setpoint

        # Room can have no schedule
        if self._device.schedule:
            attrs["schedule_id"] = self._device.schedule.id
            attrs["schedule_name"] = self._device.schedule.name
            attrs["current_schedule_temp"] = self._device.schedule.current_setting
            attrs["next_day_change"] = str(self._device.schedule.next.day)
            attrs["next_schedule_change"] = str(self._device.schedule.next.time)
            attrs["next_schedule_datetime"] = str(self._device.schedule.next.datetime)
            attrs["next_schedule_temp"] = self._device.schedule.next.setting

        # if self._device.is_passive_mode:
        #    attrs["passive_mode_temp_increment"] = self.passive_temperature_increment
        return attrs


class WiserFloorClimate(WiserBaseEntity, ClimateEntity):
    """Wiser temp probe climate entity object."""

    entity_description: WiserClimateEntityDescription
    _attr_has_entity_name = False if LEGACY_NAMES else True
    _enable_turn_on_off_backwards_compatibility = False

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WiserClimateEntityDescription,
        device: _WiserHeatingActuator | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description, device, "climate")

        _LOGGER.debug("%s %s initialise", self._data.wiserhub.system.name, self.name)

    async def async_force_update(self):
        """Force update form hub."""
        _LOGGER.debug("Hub update initiated by %s", self.name)
        await self._data.async_refresh()

    @property
    def current_temperature(self):
        """Return current temp from data."""
        return self._device.floor_temperature_sensor.measured_temperature

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
        return WiserTempLimitsEnum.floorHeatingMin.value.get("max")

    @property
    def min_temp(self):
        """Return min temp from data."""
        return WiserTempLimitsEnum.floorHeatingMin.value.get("min")

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        if (
            kwargs.get("target_temp_low", None)
            != self._device.floor_temperature_sensor.minimum_temperature
        ):
            await self._device.floor_temperature_sensor.set_minimum_temperature(
                kwargs.get("target_temp_low")
            )
            await self.async_force_update()

        if (
            kwargs.get("target_temp_high", None)
            != self._device.floor_temperature_sensor.maximum_temperature
        ):
            await self._device.floor_temperature_sensor.set_maximum_temperature(
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
        """Return the highbound target temperature we try to reach."""
        return self._device.floor_temperature_sensor.maximum_temperature

    @property
    def target_temperature_low(self) -> float | None:
        """Return the lowbound target temperature we try to reach."""
        return self._device.floor_temperature_sensor.minimum_temperature

    @property
    def temperature_unit(self):
        """Return temp units."""
        return UnitOfTemperature.CELSIUS
