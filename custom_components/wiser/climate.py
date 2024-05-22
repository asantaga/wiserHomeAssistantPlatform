"""Climate Platform Device for Wiser Rooms.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import logging
from typing import Any

from aioWiserHeatAPI.const import (
    TEMP_MINIMUM,
    TEXT_OFF,
    TEXT_ON,
    WiserHotWaterClimateModeEnum,
    WiserTempLimitsEnum,
)
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
from homeassistant.const import (
    ATTR_TEMPERATURE,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
    async_get_current_platform,
)
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DATA,
    DEFAULT_HW_MAX_TEMP,
    DOMAIN,
    LEGACY_NAMES,
    WISER_BOOST_PRESETS,
    WISER_SERVICES,
    WISER_SETPOINT_MODES,
)
from .entity import (
    WiserAttribute,
    WiserBaseEntity,
    WiserBaseEntityDescription,
    WiserDeviceAttribute,
    WiserV2DeviceAttribute,
)
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
        set_preset_mode_fn=lambda x, m: x.set_preset(m),
        # Target Temps
        target_temp_step=0.5,
        target_temp_fn=lambda x: x.current_target_temperature,
        target_temp_high_fn=lambda x: x.passive_mode_upper_temp,
        target_temp_low_fn=lambda x: x.passive_mode_lower_temp,
        set_low_target_temp_fn=lambda x, t: x.set_passive_mode_lower_temp(t),
        set_high_target_temp_fn=lambda x, t: x.set_passive_mode_upper_temp(t),
        set_target_temp_fn=lambda x, t: x.set_target_temperature(t),
        extra_state_attributes=[
            WiserDeviceAttribute("hvac_mode"),
            WiserDeviceAttribute("name"),
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
            # V2 only attrs
            WiserV2DeviceAttribute(
                "heating_supported", "capabilities.heating_supported"
            ),
            WiserV2DeviceAttribute(
                "cooling_supported", "capabilities.cooling_supported"
            ),
            WiserV2DeviceAttribute("include_in_summer_comfort"),
            WiserV2DeviceAttribute("occupancy_capable"),
            WiserV2DeviceAttribute("occupancy"),
            WiserV2DeviceAttribute("occupied_heating_set_point"),
            WiserV2DeviceAttribute("unoccupied_heating_set_point"),
            WiserV2DeviceAttribute("climate_demand_for_ui"),
        ],
    ),
    WiserClimateEntityDescription(
        key="floor_climate",
        name="Floor",
        device_collection="devices.heating_actuators",
        supported=lambda dev, hub: hasattr(dev.floor_temperature_sensor, "sensor_type")
        and dev.floor_temperature_sensor.sensor_type != "Not_Fitted",
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

WISER_HW_CLIMATES: tuple[WiserClimateEntityDescription, ...] = (
    WiserClimateEntityDescription(
        key="hotwater_climate",
        name="Hot Water",
        device="hotwater",
        supported_features_fn=lambda x: SUPPORT_FLAGS,
        supported=lambda dev, hub: hub.hotwater is not None,
        max_temp=DEFAULT_HW_MAX_TEMP,
        min_temp=TEMP_MINIMUM,
        # HVAC
        hvac_action_fn=lambda x: HVACAction.HEATING
        if x.is_heating
        else HVACAction.IDLE,
        hvac_modes=list(HVAC_MODE_HASS_TO_WISER),
        hvac_mode_fn=lambda x: HVAC_MODE_WISER_TO_HASS[x.mode],
        set_hvac_mode_fn=lambda x, m: x.set_mode(m),
        # Presets
        preset_modes_fn=lambda x: x.available_presets,
        set_preset_mode_fn=lambda x, m: x.set_preset(m),
        # Target Temps
        target_temp_fn=lambda x: x.current_target_temperature,
        set_target_temp_fn=lambda x, t: x.set_target_temperature(t),
        target_temp_step=0.5,
        extra_state_attributes=[
            WiserDeviceAttribute("away_mode_suppressed"),
            WiserDeviceAttribute("is_boosted"),
            WiserDeviceAttribute("is_override"),
            WiserDeviceAttribute("is_heating"),
            WiserDeviceAttribute(
                "control_output_state", lambda x: "On" if x.is_heating else "Off"
            ),
            WiserDeviceAttribute("boost_end_time"),
            WiserDeviceAttribute(
                "boost_time_remaining", lambda x: int(x.boost_time_remaining / 60)
            ),
            WiserDeviceAttribute("schedule_id", "schedule.id"),
            WiserDeviceAttribute("schedule_name", "schedule.name"),
            WiserDeviceAttribute("next_day_change", "schedule.next.day"),
            WiserDeviceAttribute("next_schedule_change", "schedule.next.time"),
            WiserDeviceAttribute("next_schedule_datetime", "schedule.next.datetime"),
            WiserDeviceAttribute("next_schedule_state", "schedule.next.setting"),
            WiserAttribute("keep_heating", "_keep_heating"),
        ],
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

    entities = get_entities(data, WISER_HW_CLIMATES, WiserHotWaterClimate)
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

    @callback
    def _handle_coordinator_update(self) -> None:
        previous_room_values = self._device
        if not self._device.is_boosted:
            self._boosted_time = 0
        super()._handle_coordinator_update()

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
                await self.async_force_update(1)
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
            if (
                hasattr(self._device, "is_passive_mode")
                and self._device.is_passive_mode
            ):
                return TEXT_PASSIVE
            if self._device.preset_mode == "Boost":
                if int(self._device.boost_time_remaining / 60) != 0:
                    return (
                        f"{STATUS_BOOST} {int(self._device.boost_time_remaining/60)}m"
                    )
                return STATUS_BOOST
            return WISER_PRESET_TO_HASS[self._device.setpoint_origin]
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
                await self.entity_description.set_preset_mode_fn(
                    self._device, preset_mode
                )
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


class WiserHotWaterClimate(WiserClimate):
    """Class to manage hotwater climate entity."""

    _current_temperature: float | None = None
    _keep_heating: bool = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WiserClimateEntityDescription,
        device: _WiserDevice | _WiserRoom | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description, device)

        self._boosted_time = 0
        self._keep_heating = self._device.is_heating

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._data.hw_sensor_entity_id], self._async_sensor_changed
            )
        )

    async def _async_sensor_changed(self, event) -> None:
        """Handle temperature changes."""
        sensor_state = self.hass.states.get(self._data.hw_sensor_entity_id)
        _LOGGER.error(sensor_state)
        if sensor_state is None or sensor_state.state in (
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        ):
            return

        self._current_temperature = float(sensor_state.state)
        _LOGGER.error("Updated temp sensor value - %s", self._current_temperature)
        await self.automation_routine()
        self.async_write_ha_state()

    def _handle_coordinator_update_actions(self) -> None:
        """Add extra actions here."""
        if self._device.is_heating and not self._keep_heating:
            self._keep_heating = True

    @property
    def current_temperature(self) -> float:
        """Return current temperature."""
        return self._current_temperature

    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if target := kwargs.get(ATTR_TEMPERATURE):
            await self._device.set_target_temperature(target)
            await self.automation_routine()

    async def async_set_hvac_mode(self, hvac_mode):
        """Set HW HVAC mode."""
        await super().async_set_hvac_mode(hvac_mode)
        await self.automation_routine()

    async def automation_routine(self):
        """Run hotwater automation routine."""
        # TODO: Work with advance schedule.
        # TODO: Work with boost
        if self.hvac_mode in [HVACMode.HEAT, HVACMode.AUTO]:
            if self.should_heat() and not self._device.is_heating:
                await self._device.override_state(TEXT_ON)
            elif not self.should_heat() and self._device.is_heating:
                await self._device.override_state(TEXT_OFF)
                if (
                    self.hvac_mode == HVACMode.HEAT
                    and self._data.hw_heat_mode == "Once"
                ):
                    self._keep_heating = False

        await self.async_force_update()

    def should_heat(self) -> bool:
        """Return if hw should be heating."""
        # TODO: Sort out delta to work correctly
        if self.current_temperature < (
            self.target_temperature - self._data.hw_heating_delta
        ):
            _LOGGER.error(
                "Mode: %s, Curr: %s, Tar: %s, Is: %s, Ov: %s",
                self.hvac_mode,
                self.current_temperature,
                self.target_temperature,
                self._device.is_heating,
                self._device.is_override,
            )
            if self.hvac_mode == HVACMode.HEAT:
                if self._data.hw_heat_mode == "Normal" or (
                    self._data.hw_heat_mode == "Once" and self._keep_heating
                ):
                    return True

            elif self.hvac_mode == HVACMode.AUTO:
                if self._device.schedule.current_setting == TEXT_ON and (
                    self._data.hw_auto_mode == "Normal"
                    or (
                        self._data.hw_auto_mode == "Once"
                        and not self._device.is_override
                    )
                ):
                    return True
        return False
