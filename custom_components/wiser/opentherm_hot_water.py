"""OpenTherm domestic-hot-water control for Wiser."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from math import isfinite
from uuid import uuid4

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    ATTR_UNIT_OF_MEASUREMENT,
    STATE_OFF,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import (
    async_call_later,
    async_track_point_in_time,
    async_track_state_change_event,
)
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.unit_conversion import TemperatureConverter

from .const import (
    ATTR_HUB,
    ATTR_OPENTHERM_ENDPOINT,
    ATTR_OPENTHERM_PARAM,
    ATTR_OPENTHERM_REQUEST_ID,
    ATTR_OPENTHERM_TEMPERATURE,
    CONF_OPENTHERM_HOT_WATER_CONTROL,
    CONF_OPENTHERM_HOT_WATER_MANUAL_TEMP,
    CONF_OPENTHERM_HOT_WATER_PRESETS,
    CONF_OPENTHERM_HOT_WATER_SENSOR_ENTITY_ID,
    DATA,
    DEFAULT_OPENTHERM_HOT_WATER_MANUAL_TEMP,
    DEFAULT_OPENTHERM_HOT_WATER_PRESET_TEMP,
    DOMAIN,
    EVENT_OPENTHERM_COMMAND_FAILED,
    OPENTHERM_HOT_WATER_SCHEDULE,
    OPENTHERM_HOT_WATER_DEFAULT_BOOSTS,
    WISER_SERVICES,
)
from .entity import WiserEntityMixin
from .helpers import get_hub_device_info, get_unique_id
from .local_schedule import LOCAL_HOT_WATER_SCHEDULE_ID
from .opentherm_detection import (
    opentherm_hot_water_control_is_supported,
    opentherm_hot_water_limits,
    opentherm_is_detected,
)

_LOGGER = logging.getLogger(__name__)

MODE_MANUAL = "Manual"
MODE_AUTO = "Auto"


def _normalize_presets(value, minimum=35.0, maximum=55.0):
    """Return safe preset dictionaries from stored options."""
    if not isinstance(value, list):
        return []
    presets = []
    for item in value:
        if not isinstance(item, dict):
            continue
        try:
            temperature = float(item["temperature"])
            duration = int(item.get("duration_minutes", 0))
        except (KeyError, TypeError, ValueError):
            continue
        name = str(item.get("name", "")).strip()
        icon = str(item.get("icon", "")).strip()
        if (
            not name
            or name.casefold() in {"off", "manual", "auto", "custom"}
            or not 0 <= duration <= 999
        ):
            continue
        temperature = min(max(temperature, minimum), maximum)
        presets.append(
            {
                "name": name,
                "icon": icon,
                "temperature": temperature,
                "duration_minutes": duration,
            }
        )
    return presets


def _default_presets(minimum=35.0, maximum=55.0):
    """Return the original control's default timed boost presets."""
    return [
        {
            "name": f"Boost {duration} Mins",
            "icon": f"mdi:numeric-{index}",
            "temperature": min(
                max(DEFAULT_OPENTHERM_HOT_WATER_PRESET_TEMP, minimum), maximum
            ),
            "duration_minutes": duration,
        }
        for index, duration in enumerate(
            OPENTHERM_HOT_WATER_DEFAULT_BOOSTS, start=1
        )
    ]


def _finite_float(value):
    """Return a finite float, or None for unavailable API data."""
    if isinstance(value, bool):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if isfinite(parsed) else None


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up optional OpenTherm hot-water control."""
    if not config_entry.options.get(CONF_OPENTHERM_HOT_WATER_CONTROL, False):
        return

    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    opentherm = data.wiserhub.system.opentherm
    if not opentherm_is_detected(config_entry, opentherm):
        return
    if not opentherm_hot_water_control_is_supported(config_entry, opentherm):
        _LOGGER.warning(
            "OpenTherm hot-water control is enabled but the boiler does not "
            "report a writable DHW setpoint"
        )
        return

    schedule = hass.data[DOMAIN][config_entry.entry_id].get(
        OPENTHERM_HOT_WATER_SCHEDULE
    )
    if schedule is None:
        return

    async_add_entities([WiserOpenThermHotWater(data, config_entry, schedule)])


class WiserOpenThermHotWater(
    WiserEntityMixin, CoordinatorEntity, RestoreEntity, WaterHeaterEntity
):
    """Control the boiler DHW setpoint through the Wiser OpenTherm endpoint."""

    _attr_has_entity_name = True
    _attr_translation_key = "opentherm_hot_water"
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    if not hasattr(WaterHeaterEntity, "native_temperature_unit"):
        _attr_temperature_unit = _attr_native_temperature_unit
    _attr_target_temperature_step = 0.5
    _attr_supported_features = (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE
        | WaterHeaterEntityFeature.OPERATION_MODE
        | WaterHeaterEntityFeature.ON_OFF
    )

    def __init__(self, data, config_entry, schedule):
        """Initialize the entity."""
        super().__init__(data)
        self._data = data
        self._entry_id = config_entry.entry_id
        self._schedule = schedule
        self._minimum, self._maximum = opentherm_hot_water_limits(
            data.wiserhub.system.opentherm
        )
        self._manual_temperature = float(
            config_entry.options.get(
                CONF_OPENTHERM_HOT_WATER_MANUAL_TEMP,
                DEFAULT_OPENTHERM_HOT_WATER_MANUAL_TEMP,
            )
        )
        self._manual_temperature = min(
            max(self._manual_temperature, self.min_temp), self.max_temp
        )
        self._presets = _normalize_presets(
            config_entry.options.get(
                CONF_OPENTHERM_HOT_WATER_PRESETS,
                _default_presets(self._minimum, self._maximum),
            ),
            self._minimum,
            self._maximum,
        )
        self._temperature_sensor_entity_id = config_entry.options.get(
            CONF_OPENTHERM_HOT_WATER_SENSOR_ENTITY_ID
        )
        self._operation = MODE_AUTO
        self._last_schedule_request = None
        self._target_write_in_progress = False
        self._cancel_schedule_timer = None
        self._cancel_boost_timer = None
        self._boost_deadline = None
        self._pending_request_id = None
        self._pending_previous_operation = None
        self._pending_previous_boost_seconds = None
        self._attr_unique_id = get_unique_id(
            data,
            "water_heater",
            "opentherm_hot_water",
            data.wiserhub.system.name,
        )

    @property
    def device_info(self):
        """Attach the entity to the physical HeatHub."""
        return get_hub_device_info(self._data)

    @property
    def _opentherm(self):
        return self._data.wiserhub.system.opentherm

    @property
    def available(self):
        """Require current coordinator and OpenTherm connectivity."""
        return bool(
            super().available
            and self._opentherm
            and self._opentherm.connection_status == "Connected"
            and getattr(
                getattr(self._opentherm, "boiler_parameters", None),
                "hw_setpoint_read_write",
                None,
            )
            is True
        )

    @property
    def native_current_temperature(self):
        """Return the measured domestic-hot-water temperature."""
        if self._temperature_sensor_entity_id:
            sensor_state = self.hass.states.get(
                self._temperature_sensor_entity_id
            )
            if sensor_state and sensor_state.state not in (
                STATE_UNAVAILABLE,
                STATE_UNKNOWN,
            ):
                sensor_temperature = _finite_float(sensor_state.state)
                if sensor_temperature is not None:
                    unit = sensor_state.attributes.get(
                        ATTR_UNIT_OF_MEASUREMENT,
                        UnitOfTemperature.CELSIUS,
                    )
                    try:
                        return TemperatureConverter.convert(
                            sensor_temperature,
                            unit,
                            UnitOfTemperature.CELSIUS,
                        )
                    except (TypeError, ValueError):
                        pass
        operational_data = getattr(self._opentherm, "operational_data", None)
        return _finite_float(getattr(operational_data, "hw_temperature", None))

    if not hasattr(WaterHeaterEntity, "native_current_temperature"):
        current_temperature = native_current_temperature

    @property
    def native_target_temperature(self):
        """Return the setpoint reported by Wiser."""
        boiler_parameters = getattr(self._opentherm, "boiler_parameters", None)
        value = getattr(boiler_parameters, "hw_setpoint", None)
        if value is None:
            value = getattr(self._opentherm, "hw_flow_setpoint", None)
        return _finite_float(value)

    if not hasattr(WaterHeaterEntity, "native_target_temperature"):
        target_temperature = native_target_temperature

    @property
    def min_temp(self):
        """Return the boiler-reported lower bound when available."""
        return self._minimum

    @property
    def max_temp(self):
        """Return the boiler-reported upper bound when available."""
        return self._maximum

    @property
    def operation_list(self):
        """Return the operations rendered by the hot-water mode control."""
        return [
            STATE_OFF,
            MODE_MANUAL,
            MODE_AUTO,
            *(preset["name"] for preset in self._presets),
        ]

    @property
    def current_operation(self):
        """Return the selected operating mode."""
        return self._operation

    @property
    def extra_state_attributes(self):
        """Expose the selected schedule and its next transition."""
        _, next_event = self._schedule.current()
        return {
            # Used by Wiser's card feature to scope its icon mode control to
            # this water heater rather than every water_heater entity in HA.
            "wiser_opentherm_hot_water": True,
            "custom_ui_more_info": "opentherm-hot-water-control-more-info",
            "opentherm_presets": self._presets,
            "schedule_id": LOCAL_HOT_WATER_SCHEDULE_ID,
            "schedule_name": self._schedule.name,
            "next_schedule_event": next_event,
        }

    async def async_added_to_hass(self):
        """Restore mode, subscribe to changes, and start the local schedule."""
        await super().async_added_to_hass()
        if self._temperature_sensor_entity_id:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass,
                    [self._temperature_sensor_entity_id],
                    self._async_temperature_sensor_changed,
                )
            )
        previous = await self.async_get_last_state()
        reset_expired_boost = False
        if previous:
            restored_mode = {
                "manual": MODE_MANUAL,
                "heat": MODE_MANUAL,
                "auto": MODE_AUTO,
                "off": STATE_OFF,
            }.get(previous.state.lower())
            preset = self._preset_for_mode(previous.state)
            if preset is not None:
                # Timed boosts cannot be resumed without a saved deadline.
                restored_mode = (
                    MODE_MANUAL
                    if preset["duration_minutes"]
                    else preset["name"]
                )
                reset_expired_boost = bool(preset["duration_minutes"])
            if restored_mode in self.operation_list:
                self._operation = restored_mode

        self.async_on_remove(
            self._schedule.async_add_listener(self._async_schedule_changed)
        )
        self.async_on_remove(
            self.hass.bus.async_listen(
                EVENT_OPENTHERM_COMMAND_FAILED,
                self._async_command_failed,
            )
        )
        if self._operation == MODE_AUTO:
            self.hass.async_create_task(self._async_apply_schedule_safely())
        elif reset_expired_boost:
            # A timed boost has no persisted deadline. Restore Manual and write
            # its configured target so the boiler cannot remain at boost heat.
            self.hass.async_create_task(self._async_finish_boost_safely())
        self._schedule_next_transition()

    @callback
    def _async_temperature_sensor_changed(self, _event):
        """Publish a changed external hot-water temperature reading."""
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Reconcile a scheduled target if its transition timer was missed."""
        if self._operation == MODE_AUTO and not self._target_write_in_progress:
            temperature = self._scheduled_temperature()
            if (
                temperature is not None
                and (MODE_AUTO, temperature) != self._last_schedule_request
            ):
                self.hass.async_create_task(
                    self._async_apply_schedule_safely()
                )
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self):
        """Cancel the pending schedule transition."""
        if self._cancel_schedule_timer is not None:
            self._cancel_schedule_timer()
            self._cancel_schedule_timer = None
        self._cancel_active_boost()
        await super().async_will_remove_from_hass()

    def _preset_for_mode(self, mode):
        """Return the configured preset matching an operation name."""
        return next(
            (preset for preset in self._presets if preset["name"] == mode),
            None,
        )

    def _cancel_active_boost(self):
        """Cancel a pending timed-preset return."""
        if self._cancel_boost_timer is not None:
            self._cancel_boost_timer()
            self._cancel_boost_timer = None
        self._boost_deadline = None

    def _remaining_boost_seconds(self):
        """Return the remaining timed-preset duration, if any."""
        if self._boost_deadline is None:
            return None
        return max(
            0,
            self._boost_deadline - asyncio.get_running_loop().time(),
        )

    @callback
    def _async_command_failed(self, event):
        """Restore the prior UI operation after confirmed boiler rejection."""
        if event.data.get("request_id") != self._pending_request_id:
            return
        failed_temperature = _finite_float(event.data.get("requested"))
        previous_operation = self._pending_previous_operation
        previous_boost_seconds = self._pending_previous_boost_seconds
        self._pending_request_id = None
        self._pending_previous_operation = None
        self._pending_previous_boost_seconds = None
        if previous_operation not in self.operation_list:
            return
        self._cancel_active_boost()
        self._operation = previous_operation
        # A scheduled command has already had its one service-level retry.
        # Remember that failed request so coordinator reconciliation does not
        # send it repeatedly; a different schedule block will still be sent.
        self._last_schedule_request = (
            (MODE_AUTO, failed_temperature)
            if previous_operation == MODE_AUTO
            and failed_temperature is not None
            else None
        )
        previous_preset = self._preset_for_mode(previous_operation)
        if (
            previous_preset is not None
            and previous_preset["duration_minutes"]
            and previous_boost_seconds
        ):
            self._start_boost(previous_boost_seconds / 60)
        self.async_write_ha_state()

    @callback
    def _async_boost_finished(self, _now):
        """Return a completed timed preset to Manual mode."""
        self._cancel_boost_timer = None
        self._boost_deadline = None
        self.hass.async_create_task(self._async_finish_boost_safely())

    async def _async_finish_boost_safely(self):
        """Apply the Manual setpoint after a timed preset expires."""
        try:
            await self.async_set_operation_mode(MODE_MANUAL)
        except HomeAssistantError as err:
            _LOGGER.warning("Unable to end OpenTherm hot-water boost: %s", err)

    def _start_boost(self, minutes):
        """Start the return timer for a timed preset."""
        self._cancel_active_boost()
        if minutes:
            self._boost_deadline = (
                asyncio.get_running_loop().time() + minutes * 60
            )
            self._cancel_boost_timer = async_call_later(
                self.hass,
                minutes * 60,
                self._async_boost_finished,
            )

    @callback
    def _async_schedule_changed(self) -> None:
        """Apply a saved integration-owned schedule change."""
        if self._operation == MODE_AUTO:
            self._last_schedule_request = None
            self.hass.async_create_task(self._async_apply_schedule_safely())
        self._schedule_next_transition()
        self.async_write_ha_state()

    @callback
    def _schedule_next_transition(self) -> None:
        """Wake the entity when the next local schedule slot starts."""
        if self._cancel_schedule_timer is not None:
            self._cancel_schedule_timer()
            self._cancel_schedule_timer = None
        _, next_event = self._schedule.current()
        if next_event is None:
            return
        # Run just beyond the minute boundary so schedule evaluation cannot
        # observe the previous slot if wall-clock and event-loop time differ by
        # a few milliseconds. Coordinator updates provide a second recovery
        # path if Home Assistant sleeps through this absolute-time callback.
        self._cancel_schedule_timer = async_track_point_in_time(
            self.hass,
            self._async_schedule_transition,
            next_event + timedelta(seconds=1),
        )

    @callback
    def _async_schedule_transition(self, _now) -> None:
        """Apply a due slot and arm the following transition."""
        self._cancel_schedule_timer = None
        self._last_schedule_request = None
        if self._operation == MODE_AUTO:
            self.hass.async_create_task(self._async_apply_schedule_safely())
        self._schedule_next_transition()
        self.async_write_ha_state()

    def _scheduled_temperature(self):
        """Resolve the current integration-owned schedule setpoint."""
        temperature, _ = self._schedule.current()
        return temperature

    async def _async_apply_schedule_safely(self):
        """Apply a background schedule transition without leaking task errors."""
        try:
            await self._async_apply_schedule()
        except HomeAssistantError as err:
            _LOGGER.warning("Unable to apply OpenTherm hot-water schedule: %s", err)

    async def _async_apply_schedule(
        self, previous_operation=None, previous_boost_seconds=None
    ):
        """Apply the active block once, including attribute-only transitions."""
        temperature = self._scheduled_temperature()
        request = (MODE_AUTO, temperature)
        if temperature is None or request == self._last_schedule_request:
            return
        self._last_schedule_request = request
        try:
            await self._async_set_target(
                temperature,
                previous_operation=previous_operation,
                previous_boost_seconds=previous_boost_seconds,
            )
        except HomeAssistantError:
            self._last_schedule_request = None
            raise

    async def _async_set_target(
        self,
        temperature,
        previous_operation=None,
        previous_boost_seconds=None,
    ):
        """Use Wiser's existing serialized write and confirmation path."""
        if not self.min_temp <= temperature <= self.max_temp:
            raise HomeAssistantError(
                f"Hot-water target must be between {self.min_temp:g} and "
                f"{self.max_temp:g} °C"
            )
        request_id = uuid4().hex
        self._pending_request_id = request_id
        self._pending_previous_operation = (
            self._operation
            if previous_operation is None
            else previous_operation
        )
        self._pending_previous_boost_seconds = (
            self._remaining_boost_seconds()
            if previous_boost_seconds is None
            else previous_boost_seconds
        )
        # The service refreshes the coordinator before returning. Suppress
        # Auto reconciliation during that refresh so it cannot race this
        # foreground write and send the schedule target prematurely.
        self._target_write_in_progress = True
        try:
            await self.hass.services.async_call(
                DOMAIN,
                WISER_SERVICES["SERVICE_SEND_OPENTHERM_COMMAND"],
                {
                    ATTR_HUB: self._entry_id,
                    ATTR_OPENTHERM_ENDPOINT: "preDefinedRemoteBoilerParameters",
                    ATTR_OPENTHERM_PARAM: "dhwSetpoint",
                    ATTR_OPENTHERM_TEMPERATURE: temperature,
                    ATTR_OPENTHERM_REQUEST_ID: request_id,
                },
                blocking=True,
                context=self._context,
            )
        except HomeAssistantError:
            if self._pending_request_id == request_id:
                self._pending_request_id = None
                self._pending_previous_operation = None
                self._pending_previous_boost_seconds = None
            raise
        finally:
            self._target_write_in_progress = False

    async def async_set_temperature(self, **kwargs):
        """Set a target, retaining Auto as an override until its next slot."""
        temperature = _finite_float(kwargs.get(ATTR_TEMPERATURE))
        if temperature is None:
            return
        auto_override = self._operation == MODE_AUTO
        previous_schedule_request = self._last_schedule_request
        if auto_override:
            # Mark the current block before writing because the OpenTherm
            # service refreshes the coordinator while the call is in flight.
            self._last_schedule_request = (
                MODE_AUTO,
                self._scheduled_temperature(),
            )
        try:
            await self._async_set_target(temperature)
        except HomeAssistantError:
            self._last_schedule_request = previous_schedule_request
            raise
        self._cancel_active_boost()
        if auto_override:
            # Treat a temperature adjustment in Auto like Wiser's native
            # temporary override. Mark the current schedule block as handled
            # so coordinator refreshes do not immediately replace it. The next
            # scheduled callback clears this marker and applies its setpoint.
            self._last_schedule_request = (
                MODE_AUTO,
                self._scheduled_temperature(),
            )
        else:
            self._operation = MODE_MANUAL
            self._last_schedule_request = None
        self.async_write_ha_state()

    async def async_set_operation_mode(self, operation_mode):
        """Select off, manual, or scheduled operation."""
        if operation_mode not in self.operation_list:
            raise HomeAssistantError(
                f"Unsupported hot-water operation mode: {operation_mode}"
            )
        preset = self._preset_for_mode(operation_mode)
        previous_operation = self._operation
        previous_boost_seconds = self._remaining_boost_seconds()
        if operation_mode == STATE_OFF:
            await self._async_set_target(self.min_temp)
        elif operation_mode == MODE_MANUAL:
            await self._async_set_target(self._manual_temperature)
        elif preset is not None:
            await self._async_set_target(preset["temperature"])
        elif operation_mode != MODE_AUTO:
            raise HomeAssistantError(
                f"Unknown hot-water preset: {operation_mode}"
            )
        self._cancel_active_boost()
        self._operation = operation_mode
        self._last_schedule_request = None
        if operation_mode == MODE_AUTO:
            try:
                await self._async_apply_schedule(
                    previous_operation=previous_operation,
                    previous_boost_seconds=previous_boost_seconds,
                )
            except HomeAssistantError:
                # Auto changes the local operation before applying its first
                # schedule target. Restore the prior UI mode if that initial
                # foreground command could not be sent at all.
                self._operation = previous_operation
                self._last_schedule_request = None
                self.async_write_ha_state()
                raise
        elif preset is not None:
            self._start_boost(preset["duration_minutes"])
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        """Resume automatic scheduled operation."""
        await self.async_set_operation_mode(MODE_AUTO)

    async def async_turn_off(self, **kwargs):
        """Apply the configured minimum/off setpoint."""
        await self.async_set_operation_mode(STATE_OFF)
