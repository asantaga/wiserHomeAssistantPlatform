"""Climate Platform Device for Wiser Rooms.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import logging
from typing import Any

from aioWiserHeatAPI.const import TEXT_OFF, WiserTempLimitsEnum
from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom
from aioWiserHeatAPI.roomstat import _WiserRoomStat
from aioWiserHeatAPI.smartvalve import _WiserSmartValve
from aioWiserHeatAPI.wiserhub import TEMP_OFF
import voluptuous as vol

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
    async_get_current_platform,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DATA,
    DOMAIN,
    LEGACY_NAMES,
    WISER_BOOST_PRESETS,
    WISER_SERVICES,
    WISER_SETPOINT_MODES,
)
from .entity import WiserBaseEntity, WiserBaseEntityDescription, WiserDeviceAttribute
from .events import fire_events
from .helpers import get_entities

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
    | ClimateEntityFeature.TURN_OFF
)
PASSIVE_MODE_SUPPORT_FLAGS = (
    ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
    | ClimateEntityFeature.PRESET_MODE
    | ClimateEntityFeature.TURN_OFF
)


@dataclass(frozen=True, kw_only=True)
class WiserClimateEntityDescription(
    ClimateEntityDescription, WiserBaseEntityDescription
):
    """A class that describes Wiser climate entities."""

    current_temp_fn: Callable[[Any], Awaitable[None]] | None = None
    current_humidity_fn: Callable[[Any], Awaitable[None]] | None = None
    set_target_temp_fn: Callable[[Any], Awaitable[None]] | None = None
    set_high_target_temp_fn: Callable[[Any], Awaitable[None]] | None = None
    set_low_target_temp_fn: Callable[[Any], Awaitable[None]] | None = None
    hvac_modes: list[str] | None = None
    hvac_modes_fn: Callable[[Any], Awaitable[None]] | None = None
    hvac_mode_fn: Callable[[Any], Awaitable[None]] | None = None
    hvac_action_fn: Callable[[Any], Awaitable[None]] | None = None
    set_hvac_mode_fn: Callable[[Any], Awaitable[None]] | None = None
    preset_modes_fn: Callable[[Any], Awaitable[None]] | None = None
    preset_mode_fn: Callable[[Any], Awaitable[None]] | None = None
    set_preset_mode_fn: Callable[[Any], Awaitable[None]] | None = None
    supported_features: int = 0
    supported_features_fn: Callable[[Any], Awaitable[None]] | None = None
    target_temp_fn: Callable[[Any], Awaitable[None]] | None = None
    target_temp_high_fn: Callable[[Any], Awaitable[None]] | None = None
    target_temp_low_fn: Callable[[Any], Awaitable[None]] | None = None
    target_temp_step: float | None = 1
    max_temp: int = 0
    min_temp: int = 0
    entity_class: Any | None = None
    temperature_unit: UnitOfTemperature = UnitOfTemperature.CELSIUS


WISER_CLIMATES: tuple[WiserClimateEntityDescription, ...] = (
    WiserClimateEntityDescription(
        key="room_climate",
        name="Climate",
        device_collection="rooms",
        supported=lambda room, hub: room.target_temperature_origin != "FromNoControl",
        supported_features_fn=lambda x: PASSIVE_MODE_SUPPORT_FLAGS
        if x.is_passive_mode
        else SUPPORT_FLAGS,
        max_temp=WiserTempLimitsEnum.heating.value.get("max"),
        min_temp=WiserTempLimitsEnum.heating.value.get("min"),
        # Current Values
        current_temp_fn=lambda x: x.current_temperature,
        current_humidity_fn=lambda x: x.current_humidity,
        # HVAC
        hvac_action_fn=lambda x: HVACAction.HEATING
        if x.is_heating
        else HVACAction.IDLE,
        hvac_modes=list(HVAC_MODE_HASS_TO_WISER),
        hvac_mode_fn=lambda x: HVAC_MODE_WISER_TO_HASS[x.mode],
        set_hvac_mode_fn=lambda x, m: x.set_mode(m),
        # Presets
        preset_modes_fn=lambda x: x.available_presets,
        # Target Temps
        target_temp_step=0.5,
        target_temp_fn=lambda x: x.current_target_temperature,
        target_temp_high_fn=lambda x: x.passive_mode_upper_temp,
        target_temp_low_fn=lambda x: x.passive_mode_lower_temp,
        set_low_target_temp_fn=lambda x, t: x.set_passive_mode_lower_temp(t),
        set_high_target_temp_fn=lambda x, t: x.set_passive_mode_upper_temp(t),
        extra_state_attributes=[
            WiserDeviceAttribute("window_state"),
            WiserDeviceAttribute("window_detection_active"),
            WiserDeviceAttribute("away_mode_suppressed"),
            WiserDeviceAttribute("heating_type"),
            WiserDeviceAttribute("number_of_heating_actuators"),
            WiserDeviceAttribute("demand_type"),
            WiserDeviceAttribute("target_temperature_origin"),
            WiserDeviceAttribute("is_boosted"),
            WiserDeviceAttribute("is_override"),
            WiserDeviceAttribute("is_heating"),
            WiserDeviceAttribute("is_passive_mode"),
            WiserDeviceAttribute(
                "control_output_state", lambda x: "On" if x.is_heating else "Off"
            ),
            WiserDeviceAttribute("heating_rate"),
            WiserDeviceAttribute("boost_end_time"),
            WiserDeviceAttribute(
                "boost_time_remaining", lambda x: int(x.boost_time_remaining / 60)
            ),
            WiserDeviceAttribute("percentage_demand"),
            WiserDeviceAttribute("comfort_mode_score"),
            WiserDeviceAttribute("control_direction"),
            WiserDeviceAttribute("displayed_setpoint"),
            WiserDeviceAttribute("schedule_id", "schedule.id"),
            WiserDeviceAttribute("schedule_name", "schedule.name"),
            WiserDeviceAttribute("next_day_change", "schedule.next.day"),
            WiserDeviceAttribute("next_schedule_change", "schedule.next.time"),
            WiserDeviceAttribute("next_schedule_datetime", "schedule.next.datetime"),
            WiserDeviceAttribute("next_schedule_state", "schedule.next.setting"),
            WiserDeviceAttribute("passive_temperature_increment"),
            WiserDeviceAttribute(
                "number_of_trvs",
                lambda x: len(
                    [
                        device
                        for device in x.devices
                        if isinstance(device, (_WiserSmartValve))
                    ]
                ),
            ),
            WiserDeviceAttribute(
                "number_of_trvs_locked",
                lambda x: len(
                    [
                        device
                        for device in x.devices
                        if isinstance(device, (_WiserSmartValve))
                        and device.device_lock_enabled
                    ]
                ),
            ),
            WiserDeviceAttribute(
                "is_roomstat_locked",
                lambda x: len(
                    [
                        device
                        for device in x.devices
                        if isinstance(device, (_WiserRoomStat))
                        and device.device_lock_enabled
                    ]
                )
                > 0,
            ),
        ],
    ),
    WiserClimateEntityDescription(
        key="floor_climate",
        name="Floor",
        device_collection="devices.heating_actuators",
        supported=lambda dev, hub: dev.floor_temperature_sensor.sensor_type
        != "Not_Fitted",
        supported_features=ClimateEntityFeature.TARGET_TEMPERATURE_RANGE,
        max_temp=WiserTempLimitsEnum.floorHeatingMin.value.get("max"),
        min_temp=WiserTempLimitsEnum.floorHeatingMin.value.get("min"),
        current_temp_fn=lambda x: x.floor_temperature_sensor.measured_temperature,
        hvac_mode_fn=lambda x: HVACMode.HEAT,  # Need to make this work
        target_temp_high_fn=lambda x: x.floor_temperature_sensor.maximum_temperature,
        target_temp_low_fn=lambda x: x.floor_temperature_sensor.minimum_temperature,
        set_low_target_temp_fn=lambda x,
        t: x.floor_temperature_sensor.set_minimum_temperature(t),
        set_high_target_temp_fn=lambda x,
        t: x.floor_temperature_sensor.set_maximun_temperature(t),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Add the Wiser System Switch entities."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    entities = get_entities(data, WISER_CLIMATES, WiserClimate)
    async_add_entities(entities)

    # Setup services
    platform = async_get_current_platform()

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

    return True


class WiserClimate(WiserBaseEntity, ClimateEntity):
    """Wiser climate entity."""

    entity_description: WiserClimateEntityDescription
    _attr_has_entity_name = not LEGACY_NAMES
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
        return self.entity_description.current_temp_fn(self._device)

    @property
    def current_humidity(self):
        """Return current humidity from data."""
        if self.entity_description.current_humidity_fn:
            return self.entity_description.current_humidity_fn(self._device)
        return None

    @property
    def icon(self):
        """Return icon to show if radiator is heating, not heating or set to off."""
        if self._device.mode == TEXT_OFF:
            return "mdi:radiator-off"
        if self._device.is_heating:
            return "mdi:radiator"
        return "mdi:radiator-disabled"

    @property
    def hvac_action(self):
        """Return hvac action from data."""
        if self.entity_description.hvac_action_fn:
            return self.entity_description.hvac_action_fn(self._device)
        return None

    @property
    def hvac_mode(self):
        """Return current HVAC mode."""
        if self.entity_description.hvac_mode_fn:
            return self.entity_description.hvac_mode_fn(self._device)
        return None

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        if self.entity_description.hvac_modes_fn:
            return self.entity_description.hvac_modes_fn(self._device)
        return self.entity_description.hvac_modes

    async def async_set_hvac_mode(self, hvac_mode):
        """Set HVAC mode."""
        _LOGGER.debug("Setting HVAC mode to %s for %s", hvac_mode, self.name)
        if self.entity_description.set_hvac_mode_fn:
            try:
                hvac_mode = HVAC_MODE_HASS_TO_WISER[hvac_mode]
                await self.entity_description.set_hvac_mode_fn(self._device, hvac_mode)
                await self.async_force_update()
            except KeyError:
                _LOGGER.error("Invalid HVAC mode.  Options are %s", self.hvac_modes)

    @property
    def max_temp(self):
        """Return max temp from data."""
        return self.entity_description.max_temp

    @property
    def min_temp(self):
        """Return min temp from data."""
        return self.entity_description.min_temp

    @property
    def preset_mode(self):
        """Get current preset mode."""
        try:
            if self._device.is_passive_mode:
                return TEXT_PASSIVE
            if self._device.preset_mode == "Boost":
                if int(self._device.boost_time_remaining / 60) != 0:
                    return (
                        f"{STATUS_BOOST} {int(self._device.boost_time_remaining/60)}m"
                    )
                return STATUS_BOOST
            return WISER_PRESET_TO_HASS[self._device.target_temperature_origin]
        except KeyError:
            return STATUS_BLANK

    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        if self.entity_description.preset_modes_fn:
            return self.entity_description.preset_modes_fn(self._device)
        return None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Async call to set preset mode ."""
        _LOGGER.debug("Setting Preset Mode %s for %s", preset_mode, self._device.name)
        try:
            if self.entity_description.set_preset_mode_fn:
                await self.entity_description.set_preset_mode_fn(self._device)
        except ValueError as ex:
            _LOGGER.error(ex)
        await self.async_force_update()

    @property
    def supported_features(self):
        """Return the list of supported features."""
        if self.entity_description.supported_features_fn:
            return self.entity_description.supported_features_fn(self._device)
        return self.entity_description.supported_features

    @property
    def target_temperature(self):
        """Return target temp."""
        if (
            self.entity_description.target_temp_fn
            and self._device.mode != TEXT_OFF
            and self._device.current_target_temperature != TEMP_OFF
        ):
            return self.entity_description.target_temp_fn(self._device)
        return None

    @property
    def target_temperature_step(self) -> float | None:
        """Return the supported step of target temperature."""
        return self.entity_description.target_temp_step

    @property
    def target_temperature_high(self) -> float | None:
        """Return the highbound target temperature we try to reach."""
        if self.entity_description.target_temp_high_fn:
            return self.entity_description.target_temp_high_fn(self._device)
        return None

    @property
    def target_temperature_low(self) -> float | None:
        """Return the lowbound target temperature we try to reach."""
        if self.entity_description.target_temp_low_fn:
            return self.entity_description.target_temp_low_fn(self._device)
        return None

    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if self._device.is_passive_mode and not self._device.is_boosted:
            if (
                kwargs.get("target_temp_low", None)
                and self.entity_description.set_low_target_temp_fn
            ):
                await self.entity_description.set_low_target_temp_fn(
                    self._device, kwargs.get("target_temp_low")
                )

            if (
                kwargs.get("target_temp_high", None)
                and self.hvac_mode == HVACMode.HEAT
                and self.entity_description.set_high_target_temp_fn
            ):
                await self.entity_description.set_high_target_temp_fn(
                    self._device, kwargs.get("target_temp_high")
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
