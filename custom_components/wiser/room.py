import asyncio
import inspect
from datetime import datetime
from typing import Union

from aioWiserHeatAPI.helpers.capabilities import _WiserClimateCapabilities

from . import _LOGGER
from .const import (
    DEFAULT_BOOST_DELTA,
    TEMP_MINIMUM,
    TEMP_OFF,
    TEXT_BOOST,
    TEXT_MANUAL,
    TEXT_OFF,
    TEXT_ON,
    TEXT_UNKNOWN,
    WISER_BOOST_DURATION,
    WISERROOM,
    WiserHeatingModeEnum,
    WiserPresetOptionsEnum,
)
from .devices import _WiserDeviceCollection
from .helpers.misc import is_value_in_list
from .helpers.temp import _WiserTemperatureFunctions as tf
from .rest_controller import WiserRestActionEnum, _WiserRestController
from .schedule import _WiserSchedule, _WiserScheduleCollection


class _WiserRoom(object):
    """Class representing a Wiser Room entity"""

    def __init__(
        self,
        wiser_rest_controller: _WiserRestController,
        room: dict,
        schedule: _WiserSchedule,
        devices: list,
        enable_automations: bool,
    ):
        self._wiser_rest_controller = wiser_rest_controller
        self._data = room
        self._schedule = schedule
        self._devices = devices
        self._enable_automations = enable_automations
        self._extra_config = (
            self._wiser_rest_controller._extra_config.config(
                "Rooms", str(self.id)
            )
            if self._wiser_rest_controller._extra_config
            else None
        )
        self._mode = self._effective_heating_mode(
            self._data.get("Mode"), self.current_target_temperature
        )

        self._name = room.get("Name")
        self._include_in_summer_comfort = room.get(
            "IncludeInSummerComfort", False
        )
        self._window_detection_active = room.get(
            "WindowDetectionActive", TEXT_UNKNOWN
        )

        self._default_extra_config = {
            "passive_mode": False,
            "min": 14,
            "max": 18,
        }

        # Add device id to schedule
        if self._schedule:
            self.schedule._assignments.append(
                {"id": self.id, "name": self.name}
            )

    def _effective_heating_mode(self, mode: str, temp: float) -> str:
        if mode.casefold() == TEXT_MANUAL.casefold() and temp == TEMP_OFF:
            return WiserHeatingModeEnum.off.value
        elif mode.casefold() == TEXT_MANUAL.casefold():
            return WiserHeatingModeEnum.manual.value
        return WiserHeatingModeEnum.auto.value

    async def _send_command(
        self,
        cmd: dict,
        method: WiserRestActionEnum = WiserRestActionEnum.PATCH,
    ):
        """
        Send control command to the room
        param cmd: json command structure
        return: boolen
        """
        result = await self._wiser_rest_controller._send_command(
            WISERROOM.format(self.id), cmd, method
        )
        if result:
            _LOGGER.debug(
                "Wiser room - {} command successful - {}".format(
                    inspect.stack()[1].function, result
                )
            )
            return True
        return False

    async def _update_extra_config(self, key: str, value) -> bool:
        if self._wiser_rest_controller._extra_config:
            try:
                await self._wiser_rest_controller._extra_config.async_update_config(
                    "Rooms", str(self.id), {key: value}
                )
                return True
            except Exception:
                return False
        return False

    @property
    def is_passive_mode(self) -> bool:
        return (
            True
            if self._enable_automations
            and self.passive_mode_enabled
            and self.mode != WiserHeatingModeEnum.off.value
            and not self.is_boosted
            and not self.is_away_mode
            else False
        )

    @property
    def passive_mode_enabled(self) -> bool:
        if self._extra_config and "passive_mode" in self._extra_config:
            # Migrate from initial version of extra config
            if (
                self._extra_config["passive_mode"] == "Disabled"
                or self._extra_config["passive_mode"] == False
            ):
                return False
            else:
                return True
        return self._default_extra_config["passive_mode"]

    @property
    def passive_mode_lower_temp(self) -> float:
        if self._extra_config and "min" in self._extra_config:
            return min(self._extra_config["min"], self.passive_mode_upper_temp)
        return min(
            self._default_extra_config["min"], self.passive_mode_upper_temp
        )

    @property
    def passive_mode_upper_temp(self) -> float:
        if (
            self.is_passive_mode
            and self.mode == WiserHeatingModeEnum.auto.value
            and self.schedule
        ):
            return self.schedule.current_setting
        else:
            if self._extra_config and "max" in self._extra_config:
                return self._extra_config["max"]
            return self._default_extra_config["max"]

    async def set_passive_mode(self, enable: bool):
        if await self._update_extra_config("passive_mode", enable):
            if not self.is_away_mode:
                # Set to min of temp range when initialised
                if enable and self.mode != WiserHeatingModeEnum.off.value:
                    await self.set_target_temperature(
                        self.passive_mode_lower_temp
                    )

                # Set target temp back to last manual temp if in manual mode
                if (
                    not enable
                ) and self.mode == WiserHeatingModeEnum.manual.value:
                    await self.set_target_temperature(
                        self.stored_manual_target_temperature
                    )
        else:
            _LOGGER.error(
                "Unable to set passive mode.  This maybe caused by an issue with your extra config file."
            )

    async def set_passive_mode_lower_temp(self, temp):
        if not await self._update_extra_config("min", temp):
            _LOGGER.error(
                "Unable to set passive lower temp.  This maybe caused by an issue with your extra config file."
            )

    async def set_passive_mode_upper_temp(self, temp):
        if not await self._update_extra_config("max", temp):
            _LOGGER.error(
                "Unable to set passive mode upper temp.  This maybe caused by an issue with your extra config file."
            )

    @property
    def available_modes(self) -> list:
        """Get available heating modes"""
        return [mode.value for mode in WiserHeatingModeEnum]

    @property
    def available_presets(self) -> list:
        """Get available preset modes"""
        # Remove advance schedule if no schedule exists or in passive mode
        if self.is_passive_mode or not self.schedule:
            return [
                mode.value
                for mode in WiserPresetOptionsEnum
                if mode != WiserPresetOptionsEnum.advance_schedule
            ]
        return [mode.value for mode in WiserPresetOptionsEnum]

    @property
    def away_mode_suppressed(self) -> str:
        """Get if away mode is suppressed for room"""
        return self._data.get("AwayModeSuppressed", TEXT_UNKNOWN)

    @property
    def boost_end_time(self) -> datetime:
        """Get boost end timestamp"""
        if self._data.get("OverrideTimeoutUnixTime", 0) == 0:
            return None
        return datetime.fromtimestamp(
            self._data.get("OverrideTimeoutUnixTime", 0)
        )

    @property
    def boost_time_remaining(self) -> datetime:
        """Get boost time remaining"""
        if self.is_boosted:
            return (self.boost_end_time - datetime.now()).total_seconds()
        else:
            return 0

    @property
    def boost_temperature_delta(self) -> float:
        return self._wiser_rest_controller._api_parameters.boost_temp_delta

    @property
    def capabilities(self) -> _WiserClimateCapabilities:
        """Get room climate capabilities"""
        if capabilities := self._data.get("ClimateCapabilities"):
            return _WiserClimateCapabilities(self, capabilities)

    @property
    def comfort_mode_score(self) -> int:
        """Get room heating comfort mode score"""
        return self._data.get("ComfortModeScore", 0)

    @property
    def control_direction(self) -> str:
        """Get room heating control direction Heat or Cool"""
        return self._data.get("ControlDirection", TEXT_UNKNOWN)

    @property
    def current_target_temperature(self) -> float:
        """Get current target temperature for the room"""
        return tf._from_wiser_temp(
            self._data.get("DisplayedSetPoint", TEMP_MINIMUM)
        )

    @property
    def current_temperature(self) -> float:
        """Get current temperature of the room"""
        return tf._from_wiser_temp(
            self._data.get("CalculatedTemperature", TEMP_MINIMUM), "current"
        )

    @property
    def current_humidity(self) -> int:
        """Get current humidity of the room if room has a roomstat"""
        for device in self.devices:
            if hasattr(device, "current_humidity"):
                return device.current_humidity
        return None

    @property
    def demand_type(self) -> str:
        """Get room heating control direction"""
        return self._data.get("DemandType", TEXT_UNKNOWN)

    @property
    def devices(self) -> list:
        """Get devices associated with the room"""
        return self._devices

    @property
    def displayed_setpoint(self) -> float:
        """Get room heating displayed setpoint"""
        return tf._from_wiser_temp(
            self._data.get("DisplayedSetPoint", TEMP_MINIMUM), "current"
        )

    @property
    def heating_actuator_ids(self) -> list:
        """Get list of heating actuator ids associated with room"""
        return sorted(self._data.get("HeatingActuatorIds", []))

    @property
    def heating_rate(self) -> str:
        """Get room heating rate"""
        return self._data.get("HeatingRate", TEXT_UNKNOWN)

    @property
    def heating_type(self) -> str:
        """Get room heating type"""
        return self._data.get("HeatingType", TEXT_UNKNOWN)

    @property
    def heating_mode(self) -> str:
        return self._effective_heating_mode(
            self._data.get("Mode"), self.current_target_temperature
        )

    @property
    def id(self) -> int:
        """Get the id of the room"""
        return self._data.get("id")

    @property
    def is_away_mode(self) -> bool:
        """Get if the room temperature is currently set by away mode"""
        return (
            True
            if "Away"
            in self._data.get(
                "SetpointOrigin",
                self._data.get("SetPointOrigin", TEXT_UNKNOWN),
            )
            else False
        )

    @property
    def is_boosted(self) -> bool:
        """Get if the room temperature is currently boosted"""
        return (
            True
            if "Boost"
            in self._data.get(
                "SetpointOrigin",
                self._data.get("SetPointOrigin", TEXT_UNKNOWN),
            )
            else False
        )

    @property
    def is_override(self) -> bool:
        """Get if the room has an override"""
        return (
            True
            if self._data.get("OverrideType", TEXT_UNKNOWN)
            not in [TEXT_UNKNOWN, "None"]
            else False
        )

    @property
    def is_heating(self) -> bool:
        """Get if the room is currently heating"""
        return (
            True
            if self._data.get("ControlOutputState", TEXT_OFF) == TEXT_ON
            else False
        )

    @property
    def manual_target_temperature(self) -> float:
        """Get current target temperature for manual mode"""
        return tf._from_wiser_temp(
            self._data.get("ManualSetPoint", TEMP_MINIMUM)
        )

    @property
    def mode(self) -> str:
        """Get or set current mode for the room (Off, Manual, Auto)"""
        return self._mode

    async def set_mode(self, mode: Union[WiserHeatingModeEnum, str]) -> bool:
        if type(mode) == WiserHeatingModeEnum:
            mode = mode.value

        if is_value_in_list(mode, self.available_modes):
            # Cancel any overrides on mode change
            if self.is_override:
                await self.cancel_overrides()

            if mode == WiserHeatingModeEnum.off.value:
                await self.set_manual_temperature(TEMP_OFF)
            elif mode == WiserHeatingModeEnum.manual.value:
                if await self._send_command(
                    {"Mode": WiserHeatingModeEnum.manual.value}
                ):
                    if self.current_target_temperature == TEMP_OFF:
                        await self.set_target_temperature(
                            self.stored_manual_target_temperature
                        )
            elif mode == WiserHeatingModeEnum.auto.value:
                await self._send_command(
                    {"Mode": WiserHeatingModeEnum.auto.value}
                )

            self._mode = mode
            return True
        else:
            raise ValueError(
                f"{mode} is not a valid Room mode.  Valid modes are {self.available_modes}"
            )

    @property
    def name(self) -> str:
        """Get or set the name of the room"""
        return self._name

    async def set_name(self, name: str):
        if await self._send_command({"Name": name.title()}):
            self._name = name.title()
            return True

    @property
    def number_of_heating_actuators(self) -> int:
        """Get number of heating actuators associated with room"""
        return len(self._data.get("HeatingActuatorIds", []))

    @property
    def number_of_smartvalves(self) -> int:
        """Get number of smartvalves associated with room"""
        return len(self._data.get("SmartValveIds", []))

    @property
    def override_target_temperature(self) -> float:
        """Get the override target temperature of the room"""
        return self._data.get("OverrideSetpoint", 0)

    @property
    def override_type(self) -> str:
        """Get the current override type for the room"""
        return self._data.get("OverrideType", "None")

    @property
    def percentage_demand(self) -> int:
        """Get the percentage demand of the room"""
        return self._data.get("PercentageDemand", 0)

    @property
    def preset_mode(self) -> str:
        """Get the current preset mode"""
        if self.is_boosted:
            return TEXT_BOOST
        else:
            return None

    async def set_preset(self, preset: WiserPresetOptionsEnum | str):
        """Set the preset mode"""
        if isinstance(preset, WiserPresetOptionsEnum):
            preset = preset.value

        # Is it valid preset option?
        if preset in self.available_presets:
            if preset == WiserPresetOptionsEnum.cancel_overrides.value:
                await self.cancel_overrides()
            elif preset == WiserPresetOptionsEnum.advance_schedule.value:
                await self.schedule_advance()
            elif preset.lower().startswith(TEXT_BOOST.lower()):
                # Lookup boost duration
                duration = WISER_BOOST_DURATION[preset]
                _LOGGER.debug(
                    f"Boosting by {self.boost_temperature_delta}C for {duration} mins"
                )
                await self.boost(self.boost_temperature_delta, duration)
        else:
            raise ValueError(
                f"{preset} is not a valid preset.  Valid presets are {self.available_presets}"
            )

    @property
    def roomstat_id(self) -> int:
        """Get the id of the roomstat"""
        return self._data.get("RoomStatId", None)

    @property
    def schedule(self) -> _WiserSchedule:
        """Get the schedule for the room"""
        return self._schedule

    @property
    def schedule_id(self) -> int:
        """Get the schedule id for the room"""
        return self._data.get("ScheduleId")

    @property
    def scheduled_target_temperature(self) -> float:
        """Get the scheduled target temperature for the room"""
        return tf._from_wiser_temp(
            self._data.get("ScheduledSetPoint", TEMP_MINIMUM)
        )

    @property
    def smartvalve_ids(self) -> list:
        """Get list of smartvalve ids associated with room"""
        return sorted(self._data.get("SmartValveIds", []))

    @property
    def stored_manual_target_temperature(self) -> float:
        if self._extra_config and "manual_temp" in self._extra_config:
            return self._extra_config["manual_temp"]
        elif (
            self._wiser_rest_controller._api_parameters.stored_manual_target_temperature_alt_source.lower()
            == "current"
        ):
            return self.current_temperature
        elif (
            self._wiser_rest_controller._api_parameters.stored_manual_target_temperature_alt_source.lower()
            == "scheduled"
            and self.schedule
        ):
            return self.scheduled_target_temperature
        return TEMP_MINIMUM

    @property
    def target_temperature_origin(self) -> str:
        """Get the origin of the target temperature setting for the room"""
        return self._data.get(
            "SetpointOrigin", self._data.get("SetpointOrigin", TEXT_UNKNOWN)
        )

    @property
    def underfloor_heating_id(self) -> int:
        """Get the id of the underfloor heating controller"""
        return self._data.get("UnderFloorHeatingId", None)

    @property
    def underfloor_heating_relay_ids(self) -> int:
        """Get the id of the underfloor heating controller relay ids"""
        return sorted(self._data.get("UfhRelayIds", []))

    # Added by LGO
    @property
    def include_in_summer_comfort(self) -> bool:
        """Get the status of participate to the summer comfort"""
        return self._data.get("IncludeInSummerComfort")

    async def set_include_in_summer_comfort(self, enabled: bool):
        """Set the status of participate to the summer comfort"""
        if await self._send_command({"IncludeInSummerComfort": enabled}):
            self._include_in_summer_comfort = enabled
            return True

    @property
    def hvac_mode(self) -> str:
        """Get the HVAC mode of the room"""
        return self._data.get("HVACMode", TEXT_UNKNOWN)

    @property
    def floor_sensor_state(self) -> str:
        """Get the state of the floor sensor"""
        return self._data.get("FloorSensorState", TEXT_UNKNOWN)

    @property
    def occupancy(self) -> str:
        """Get the occupancy of the room"""
        return self._data.get("Occupancy", TEXT_UNKNOWN)

    @property
    def occupancy_capable(self) -> bool:
        """Get the occupancy of the room"""
        return self._data.get("OccupancyCapable", False)

    @property
    def occupied_heating_set_point(self) -> int:
        """Get the setpoint when the room is occupied"""
        return self._data.get("OccupiedHeatingSetPoint", 85)

    @property
    def unoccupied_heating_set_point(self) -> int:
        """Get the setpoint when the room is unoccupied"""
        return self._data.get("UnoccupiedHeatingSetPoint", 65)

    @property
    def climate_demand_for_ui(self) -> int:
        """Get the climate demand for UI"""
        return self._data.get("ClimateDemandForUI", 0)

    # End Added by LGO

    @property
    def window_detection_active(self) -> bool:
        """Get or set if window detection is active"""
        return self._window_detection_active

    async def set_window_detection_active(self, enabled: bool):
        if await self._send_command({"WindowDetectionActive": enabled}):
            self._window_detection_active = enabled
            return True

    @property
    def window_state(self) -> str:
        """
        Get the currently detected window state for the room.
        Window detection needs to be active
        """
        return self._data.get("WindowState", TEXT_UNKNOWN)

    async def delete(self):
        """
        Delete room from wiserhub
        """
        return await self._send_command(None, WiserRestActionEnum.DELETE)

    async def boost(self, inc_temp: float, duration: int) -> bool:
        """
        Boost the target temperature of the room
        param inc_temp: increase target temperature over current temperature by 0C to 5C
        param duration: the duration to boost the room temperature in minutes
        return: boolean
        """
        if duration == 0:
            return await self.cancel_boost()
        return await self._send_command(
            {
                "RequestOverride": {
                    "Type": "Boost",
                    "DurationMinutes": duration,
                    "IncreaseSetPointBy": tf._to_wiser_temp(
                        inc_temp, "boostDelta"
                    ),
                }
            }
        )

    async def cancel_boost(self) -> bool:
        """
        Cancel the target temperature boost of the room
        return: boolean
        """
        if self.is_boosted:
            return await self.cancel_overrides()
        else:
            return True

    async def set_target_temperature(self, temp: float) -> bool:
        """
        Set the target temperature of the room to override current schedule temp or in manual mode
        param temp: the temperature to set in C
        return: boolean
        """
        # Set manual temp in stored config
        if (
            self.mode == WiserHeatingModeEnum.manual.value
            and not self.is_passive_mode
            and temp != TEMP_OFF
        ):
            await self._update_extra_config("manual_temp", temp)

        return await self._send_command(
            {
                "RequestOverride": {
                    "Type": "Manual",
                    "SetPoint": tf._to_wiser_temp(temp),
                }
            }
        )

    async def set_target_temperature_for_duration(
        self, temp: float, duration: int
    ) -> bool:
        """
        Set the target temperature of the room to override current schedule temp or in manual mode
        param temp: the temperature to set in C
        return: boolean
        """
        # Set manual temp in stored config
        if (
            self.mode == WiserHeatingModeEnum.manual.value
            and not self.is_passive_mode
        ):
            await self._update_extra_config("manual_temp", temp)

        return await self._send_command(
            {
                "RequestOverride": {
                    "Type": "Manual",
                    "DurationMinutes": duration,
                    "SetPoint": tf._to_wiser_temp(temp),
                }
            }
        )

    async def set_manual_temperature(self, temp: float) -> bool:
        """
        Set the mode to manual with target temperature for the room
        param temp: the temperature to set in C
        return: boolean
        """
        if self.mode != WiserHeatingModeEnum.manual.value:
            await self.set_mode(WiserHeatingModeEnum.manual.value)
        return await self.set_target_temperature(temp)

    async def schedule_advance(self) -> bool:
        """
        Advance room schedule to the next scheduled time and temperature setting
        return: boolean
        """
        if await self.cancel_boost():
            return await self.set_target_temperature(
                self.schedule.next.setting
            )

    async def cancel_overrides(self) -> bool:
        """
        Cancel all overrides and set room schedule to the current temperature setting for the mode
        return: boolean
        """
        return await self._send_command({"RequestOverride": {"Type": "None"}})


class _WiserRoomCollection:
    """Class holding all wiser room objects"""

    def __init__(
        self,
        wiser_rest_controller: _WiserRestController,
        room_data: dict,
        schedules: _WiserScheduleCollection,
        devices: _WiserDeviceCollection,
        enable_automations: bool,
    ):
        super().__init__()
        self._wiser_rest_controller = wiser_rest_controller
        self._room_data = room_data
        self._schedules = schedules
        self._devices = devices
        self._enable_automations = enable_automations
        self._rooms: list(_WiserRoom) = []
        self._build()

    def _build(self):
        # Add room objects
        for room in self._room_data:
            schedule = [
                schedule
                for schedule in self._schedules
                if schedule.id == room.get("ScheduleId")
            ]
            devices = self._devices.get_by_room_id(room.get("id", 0))
            self._rooms.append(
                _WiserRoom(
                    self._wiser_rest_controller,
                    room,
                    schedule[0] if len(schedule) > 0 else None,
                    devices,
                    self._enable_automations,
                )
            )

    @property
    def all(self) -> list:
        """Returns list of room objects"""
        return self._rooms

    @property
    def count(self) -> int:
        """Number of rooms"""
        return len(self._rooms)

    async def add(self, name):
        """
        Add new room
        param name: name of room
        """
        return await self._wiser_rest_controller._send_command(
            WISERROOM, {"name": name}, WiserRestActionEnum.POST
        )

    def get_by_id(self, id: int) -> _WiserRoom:
        """
        Gets a room object for the room by id of room
        param id: the id of the room
        return: _WiserRoom object
        """
        try:
            return [room for room in self._rooms if room.id == id][0]
        except IndexError:
            return None

    def get_by_name(self, name: str) -> _WiserRoom:
        """
        Gets a room object for the room by name of room
        param name: the name of the room
        return: _WiserRoom object
        """
        try:
            return [
                room
                for room in self._rooms
                if room.name.lower() == name.lower()
            ][0]
        except IndexError:
            return None

    def get_by_schedule_id(self, schedule_id: int) -> _WiserRoom:
        """
        Gets a room object for the room a schedule id belongs to
        param schedule_id: the id of the schedule
        return: _WiserRoom object
        """
        return [
            room for room in self._rooms if room.schedule_id == schedule_id
        ][0]

    def get_by_device_id(self, device_id: int) -> _WiserRoom:
        """
        Gets a room object for the room a device id belongs to
        param device_id: the id of the device
        return: _WiserRoom object
        """
        for room in self._rooms:
            for device in room.devices:
                if device.id == device_id:
                    return room
        return None
