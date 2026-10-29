"""External Room Control and Passive Mode schedule support."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
import logging
import math

from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
    ATTR_UNIT_OF_MEASUREMENT,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util
from homeassistant.util.unit_conversion import TemperatureConverter

from .const import (
    CONF_AUTOMATIONS_EXTERNAL_ROOM_CONTROL,
    CONF_EXTERNAL_ROOM_CONTROL_ASSIGNMENTS,
    CONF_EXTERNAL_TEMPERATURE_BOOST_DURATION,
    CONF_EXTERNAL_TEMPERATURE_BOOST_MODE,
    CONF_EXTERNAL_TEMPERATURE_FIXED_BOOST,
    CONF_EXTERNAL_TEMPERATURE_MAX_BOOST,
    CONF_EXTERNAL_TEMPERATURE_PROPORTIONAL_MULTIPLIER,
    CONF_EXTERNAL_TEMPERATURE_SENSOR_ASSIGNMENTS,
    CONF_EXTERNAL_TEMPERATURE_STALE_MINUTES,
    CONF_EXTERNAL_TEMPERATURE_TOLERANCE,
    CONTROL_STRATEGIES,
    CONTROL_STRATEGY_TEMPERATURE_LIMITER,
    DEFAULT_PASSIVE_CONTROL_STRATEGY,
    DEFAULT_EXTERNAL_TEMPERATURE_BOOST_DURATION,
    DEFAULT_EXTERNAL_TEMPERATURE_FIXED_BOOST,
    DEFAULT_EXTERNAL_TEMPERATURE_MAX_BOOST,
    DEFAULT_EXTERNAL_TEMPERATURE_PROPORTIONAL_MULTIPLIER,
    DEFAULT_EXTERNAL_TEMPERATURE_STALE_MINUTES,
    DEFAULT_EXTERNAL_TEMPERATURE_TOLERANCE,
    DOMAIN,
    EXTERNAL_TEMPERATURE_BOOST_FIXED,
    EXTERNAL_TEMPERATURE_BOOST_PROPORTIONAL,
)
from .helpers import room_supports_external_temperature_feedback

_LOGGER = logging.getLogger(__name__)

SERVICE_SET_TEMPERATURE = "set_temperature"
ATTR_MAX_TEMP = "max_temp"
ATTR_MIN_TEMP = "min_temp"
STORAGE_VERSION = 1
FROST_PROTECTION_TEMPERATURE = 5.0
OFF_TEMPERATURE = -20.0
MAX_SCHEDULE_TEMPERATURE = 30.0
DEFAULT_OPEN_TEMPERATURE = 25.0
WEEKDAYS = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


class ExternalRoomControlController:
    """Control assigned climates and store Passive Mode lower schedules."""

    def __init__(self, hass, config_entry, coordinator) -> None:
        """Initialise the controller from config-entry options."""
        self.hass = hass
        self.coordinator = coordinator
        options = config_entry.options.get(CONF_AUTOMATIONS_EXTERNAL_ROOM_CONTROL, {})
        configured_assignments = {
            str(room_id): list(entity_ids)
            for room_id, entity_ids in options.get(
                CONF_EXTERNAL_ROOM_CONTROL_ASSIGNMENTS, {}
            ).items()
            if entity_ids
        }
        entity_rooms: dict[str, set[str]] = {}
        for room_id, entity_ids in configured_assignments.items():
            for entity_id in entity_ids:
                entity_rooms.setdefault(entity_id, set()).add(room_id)
        duplicate_entities = {
            entity_id
            for entity_id, room_ids in entity_rooms.items()
            if len(room_ids) > 1
        }
        self.assignments = {
            room_id: [
                entity_id
                for entity_id in entity_ids
                if entity_id not in duplicate_entities
            ]
            for room_id, entity_ids in configured_assignments.items()
        }
        if duplicate_entities:
            _LOGGER.error(
                "Ignoring external climate entities assigned to multiple Wiser rooms: %s",
                ", ".join(sorted(duplicate_entities)),
            )
        configured_sensors = {
            str(room_id): str(entity_id)
            for room_id, entity_id in options.get(
                CONF_EXTERNAL_TEMPERATURE_SENSOR_ASSIGNMENTS, {}
            ).items()
            if entity_id
        }
        duplicate_sensors = {
            entity_id
            for entity_id in configured_sensors.values()
            if list(configured_sensors.values()).count(entity_id) > 1
        }
        self.temperature_sensors = {
            room_id: entity_id
            for room_id, entity_id in configured_sensors.items()
            if entity_id not in duplicate_sensors
            and not self.assignments.get(room_id)
        }
        if duplicate_sensors:
            _LOGGER.error(
                "Ignoring external temperature sensors assigned to multiple "
                "Wiser rooms: %s",
                ", ".join(sorted(duplicate_sensors)),
            )
        self.available = bool(self.assignments or self.temperature_sensors)
        self.temperature_tolerance = float(
            options.get(
                CONF_EXTERNAL_TEMPERATURE_TOLERANCE,
                DEFAULT_EXTERNAL_TEMPERATURE_TOLERANCE,
            )
        )
        self.temperature_boost_duration = int(
            options.get(
                CONF_EXTERNAL_TEMPERATURE_BOOST_DURATION,
                DEFAULT_EXTERNAL_TEMPERATURE_BOOST_DURATION,
            )
        )
        self.temperature_boost_mode = options.get(
            CONF_EXTERNAL_TEMPERATURE_BOOST_MODE,
            EXTERNAL_TEMPERATURE_BOOST_PROPORTIONAL,
        )
        self.temperature_fixed_boost = float(
            options.get(
                CONF_EXTERNAL_TEMPERATURE_FIXED_BOOST,
                DEFAULT_EXTERNAL_TEMPERATURE_FIXED_BOOST,
            )
        )
        self.temperature_proportional_multiplier = float(
            options.get(
                CONF_EXTERNAL_TEMPERATURE_PROPORTIONAL_MULTIPLIER,
                DEFAULT_EXTERNAL_TEMPERATURE_PROPORTIONAL_MULTIPLIER,
            )
        )
        self.temperature_max_boost = min(
            5.0,
            float(
                options.get(
                    CONF_EXTERNAL_TEMPERATURE_MAX_BOOST,
                    DEFAULT_EXTERNAL_TEMPERATURE_MAX_BOOST,
                )
            ),
        )
        self.temperature_stale_minutes = int(
            options.get(
                CONF_EXTERNAL_TEMPERATURE_STALE_MINUTES,
                DEFAULT_EXTERNAL_TEMPERATURE_STALE_MINUTES,
            )
        )
        self._store = Store(
            hass,
            STORAGE_VERSION,
            f"{DOMAIN}.external_room_control.{config_entry.entry_id}",
        )
        self._legacy_store = Store(
            hass,
            STORAGE_VERSION,
            f"{DOMAIN}.external_passive.{config_entry.entry_id}",
        )
        self._rooms: dict[str, dict] = {}
        self._upper_schedules: dict[str, dict] = {}
        self._lower_schedules: dict[str, dict] = {}
        self._passive_control_schedules: dict[str, dict] = {}
        self._native_passive_migrated = False
        self._closed_limiter_rooms: set[str] = set()
        self._sensor_boosts: dict[str, dict] = {}

    async def async_load(self) -> None:
        """Load Passive Mode lower schedules and migrate experimental data."""
        stored = await self._store.async_load() or {}
        rooms = stored.get("rooms", {})
        self._rooms = rooms if isinstance(rooms, dict) else {}
        upper_schedules = stored.get("upper_schedules", {})
        self._upper_schedules = (
            upper_schedules if isinstance(upper_schedules, dict) else {}
        )
        lower_schedules = stored.get("lower_schedules", {})
        self._lower_schedules = (
            lower_schedules if isinstance(lower_schedules, dict) else {}
        )
        passive_control_schedules = stored.get("passive_control_schedules", {})
        self._passive_control_schedules = (
            passive_control_schedules
            if isinstance(passive_control_schedules, dict)
            else {}
        )
        self._native_passive_migrated = bool(
            stored.get("native_passive_migrated", False)
        )
        sensor_boosts = stored.get("sensor_boosts", {})
        self._sensor_boosts = (
            sensor_boosts if isinstance(sensor_boosts, dict) else {}
        )
        storage_changed = await self._async_migrate_native_passive_data()
        for room_id in list(self._rooms):
            before = self._rooms[room_id]
            before = dict(before) if isinstance(before, dict) else None
            settings = self._settings(room_id)
            if before != settings:
                storage_changed = True
        if storage_changed:
            await self._async_save()

    async def _async_migrate_native_passive_data(self) -> bool:
        """Copy only native Passive data from the experimental legacy store."""
        if self._native_passive_migrated:
            return False

        legacy = await self._legacy_store.async_load() or {}
        legacy_lower_schedules = legacy.get("lower_schedules", {})
        if (
            isinstance(legacy_lower_schedules, dict)
            and not self._lower_schedules
            and not self._upper_schedules
        ):
            self._lower_schedules = deepcopy(legacy_lower_schedules)

        legacy_rooms = legacy.get("rooms", {})
        if isinstance(legacy_rooms, dict):
            for room_id, legacy_settings in legacy_rooms.items():
                if not isinstance(legacy_settings, dict):
                    continue
                passive_override = legacy_settings.get("passive_lower_override")
                if passive_override is not None:
                    self._settings(room_id)["passive_lower_override"] = (
                        passive_override
                    )

        self._native_passive_migrated = True
        return True

    async def _async_save(self) -> None:
        """Persist per-room settings."""
        await self._store.async_save(
            {
                "rooms": self._rooms,
                "upper_schedules": self._upper_schedules,
                "lower_schedules": self._lower_schedules,
                "passive_control_schedules": self._passive_control_schedules,
                "native_passive_migrated": self._native_passive_migrated,
                "sensor_boosts": self._sensor_boosts,
            }
        )

    async def async_migrate_legacy_schedule_ownership(self) -> bool:
        """Place the hub-owned value correctly after Passive type changes."""
        if not self._lower_schedules and not self._upper_schedules:
            return False
        schedules = getattr(self.coordinator.wiserhub, "schedules", None)
        heating_schedules = getattr(schedules, "heating_schedules", None) or []
        changed = False
        for schedule in heating_schedules:
            schedule_id = str(schedule.id)
            saved_lower = self._lower_schedules.get(schedule_id)
            saved_upper = self._upper_schedules.get(schedule_id)
            uses_external = self.schedule_uses_external_range(schedule)
            uses_native = self.schedule_uses_native_range(schedule)
            if not (
                (uses_external and saved_lower)
                or (uses_native and saved_upper)
            ):
                continue
            native_schedule = deepcopy(schedule.ws_schedule_data)
            paired_schedule = {}
            migrated_slot = False
            for day in native_schedule.get("ScheduleData", []):
                day_name = day.get("day")
                saved_day = (saved_lower if uses_external else saved_upper).get(
                    day_name, {}
                )
                paired_day = {}
                for slot in day.get("slots") or []:
                    time_value = str(slot.get("Time", ""))
                    if time_value not in saved_day:
                        continue
                    try:
                        hub_value = float(slot.get("Setpoint"))
                        local_value = float(saved_day[time_value])
                    except (TypeError, ValueError):
                        continue
                    if uses_external:
                        slot["Setpoint"] = min(local_value, hub_value)
                        paired_day[time_value] = hub_value
                    else:
                        slot["Setpoint"] = max(local_value, hub_value)
                        paired_day[time_value] = hub_value
                    migrated_slot = True
                if paired_day:
                    paired_schedule[day_name] = paired_day
            if not migrated_slot:
                continue
            await schedule.set_schedule_from_ws_data(native_schedule)
            if uses_external:
                self._upper_schedules[schedule_id] = paired_schedule
                self._lower_schedules.pop(schedule_id, None)
            else:
                self._lower_schedules[schedule_id] = paired_schedule
                self._upper_schedules.pop(schedule_id, None)
            changed = True
        if changed:
            await self._async_save()
        return changed

    def _settings(self, room_id) -> dict:
        """Return settings for a room, creating defaults when needed."""
        room_id = str(room_id)
        settings = self._rooms.get(room_id)
        if not isinstance(settings, dict):
            settings = {}
            self._rooms[room_id] = settings
        settings.setdefault("passive_upper_override", None)
        settings.setdefault("passive_lower_override", None)
        settings.setdefault("passive_override_schedule_transition", None)
        settings.setdefault("passive_schedule_original_enabled", None)
        for obsolete_key in (
            "external_passive_enabled",
            "enabled",
            "lower",
            "upper",
            "upper_override",
            "open_targets",
            "controlled_targets",
        ):
            settings.pop(obsolete_key, None)
        return settings

    @staticmethod
    def _schedule_transition_marker(room) -> str | None:
        """Return the identity of the room's next schedule transition."""
        schedule = getattr(room, "schedule", None)
        next_period = getattr(schedule, "next", None)
        transition = getattr(next_period, "datetime", None)
        if transition is None:
            return None
        if hasattr(transition, "isoformat"):
            return transition.isoformat()
        return str(transition)

    def _set_schedule_override_marker(self, settings, room) -> None:
        """Remember which schedule transition should end local overrides."""
        marker = self._schedule_transition_marker(room)
        if marker is not None:
            settings["passive_override_schedule_transition"] = marker

    @staticmethod
    def _clear_unused_schedule_override_marker(settings) -> None:
        """Discard the marker after both local overrides have ended."""
        if (
            settings.get("passive_lower_override") is None
            and settings.get("passive_upper_override") is None
        ):
            settings["passive_override_schedule_transition"] = None

    def assigned_entity_ids(self, room_id) -> list[str]:
        """Return climate entities assigned to a Wiser room."""
        return self.assignments.get(str(room_id), [])

    def has_assignment(self, room_id) -> bool:
        """Return whether a room has at least one external climate entity."""
        return bool(self.assigned_entity_ids(room_id))

    def temperature_sensor_entity_id(self, room_id) -> str | None:
        """Return the external temperature sensor assigned to a Wiser room."""
        return self.temperature_sensors.get(str(room_id))

    def has_temperature_sensor(self, room_id) -> bool:
        """Return whether a room uses external temperature feedback."""
        room = self._room(room_id)
        return bool(
            self.temperature_sensor_entity_id(room_id)
            and room is not None
            and room_supports_external_temperature_feedback(room)
        )

    def has_passive_override(self, room_id) -> bool:
        """Return whether a locally stored Passive range override is active."""
        settings = self._settings(room_id)
        return bool(
            settings.get("passive_lower_override") is not None
            or settings.get("passive_upper_override") is not None
        )

    def is_enabled(self, room_id) -> bool:
        """Return whether an assigned room is under External Room Control."""
        return bool(self.available and self.has_assignment(room_id))

    def is_active(self, room) -> bool:
        """Return whether External Room Control owns the assigned devices."""
        return self.is_enabled(room.id)

    def uses_temperature_limiter(self, room_id) -> bool:
        """Return whether an assigned room uses the Passive temperature limiter."""
        room_id = getattr(room_id, "id", room_id)
        return bool(
            self.coordinator.passive_mode_enabled
            and self.is_enabled(room_id)
            and self.coordinator.passive_room_strategy(room_id)
            == CONTROL_STRATEGY_TEMPERATURE_LIMITER
        )

    def upper_temperature(self, room_id) -> float:
        """Return the cutoff used only by an external temperature limiter."""
        settings = self._settings(room_id)
        if settings.get("passive_upper_override") is not None:
            return float(settings["passive_upper_override"])
        room = self._room(room_id)
        control = self.scheduled_passive_control(room_id)
        if control is not None and control["enabled"]:
            return float(control["upper"])
        scheduled = self._scheduled_temperature(room, self._upper_schedules)
        if scheduled is not None:
            return scheduled
        return float(room.configured_passive_mode_upper_temp)

    def passive_upper_temperature(self, room):
        """Return the cutoff used only by an external temperature limiter."""
        if not self.uses_temperature_limiter(room.id):
            return None
        override = self._settings(room.id).get("passive_upper_override")
        if override is not None:
            return float(override)
        control = self.scheduled_passive_control(room.id)
        if control is not None and control["enabled"]:
            return float(control["upper"])
        scheduled = self._scheduled_temperature(room, self._upper_schedules)
        if scheduled is not None:
            return scheduled
        return float(room.configured_passive_mode_upper_temp)

    def _room(self, room_id):
        """Return the Wiser room matching a stored or entity room ID."""
        return next(
            (
                room
                for room in self.coordinator.wiserhub.rooms.all
                if str(room.id) == str(room_id)
            ),
            None,
        )

    def _schedule_room_ids(self, schedule) -> set[str]:
        """Return live Wiser rooms assigned to a schedule."""
        assigned_ids = {
            str(room_id) for room_id in getattr(schedule, "assignment_ids", [])
        }
        schedule_id = getattr(schedule, "id", None)
        return {
            str(room.id)
            for room in self.coordinator.wiserhub.rooms.all
            if str(room.id) in assigned_ids
            or (
                schedule_id is not None
                and getattr(room, "schedule", None) is not None
                and str(room.schedule.id) == str(schedule_id)
            )
        }

    def _schedule_passive_room_ids(self, schedule) -> set[str]:
        """Return enabled Passive Mode rooms assigned to a schedule."""
        if not self.coordinator.passive_mode_enabled:
            return set()
        return {
            room_id
            for room_id in self._schedule_room_ids(schedule)
            if self._room(room_id).passive_mode_enabled
        }

    def _schedule_native_passive_room_ids(self, schedule) -> set[str]:
        """Return schedule rooms using the normal modulating Passive strategy."""
        return {
            room_id
            for room_id in self._schedule_passive_room_ids(schedule)
            if not self.uses_temperature_limiter(room_id)
        }

    def schedule_uses_external_range(self, schedule) -> bool:
        """Return whether every assigned room uses the external limiter."""
        if str(schedule.schedule_type).casefold() != "heating":
            return False
        room_ids = self._schedule_room_ids(schedule)
        return bool(
            room_ids
            and all(
                self._room(room_id).passive_mode_enabled
                and self.uses_temperature_limiter(room_id)
                for room_id in room_ids
            )
        )

    def schedule_supports_temperature_limiter(self, schedule) -> bool:
        """Return whether every assigned room supports external limiting."""
        room_ids = self._schedule_room_ids(schedule)
        return all(self.is_enabled(room_id) for room_id in room_ids)

    def passive_control_schedule_uses_temperature_limiter(self, schedule_id) -> bool:
        """Return whether a stored control schedule selects the limiter."""
        schedule = self._passive_control_schedules.get(str(schedule_id), {})
        return any(
            control.get("enabled")
            and control.get("strategy") == CONTROL_STRATEGY_TEMPERATURE_LIMITER
            for day in schedule.values()
            if isinstance(day, dict)
            for control in day.values()
            if isinstance(control, dict)
        )

    def schedule_uses_native_range(self, schedule) -> bool:
        """Return whether a schedule has native Passive Mode rooms."""
        return bool(
            self.coordinator.passive_mode_enabled
            and str(schedule.schedule_type).casefold() == "heating"
            and self._schedule_native_passive_room_ids(schedule)
        )

    def schedule_data(self, schedule) -> dict:
        """Add locally stored Passive range values to a Wiser heating schedule."""
        data = deepcopy(schedule.ws_schedule_data)
        if str(schedule.schedule_type).casefold() != "heating":
            return data
        data["Capabilities"] = {
            "PassiveControl": bool(self.coordinator.passive_mode_enabled)
        }
        if not self.coordinator.passive_mode_enabled:
            return data
        room_ids = sorted(self._schedule_room_ids(schedule))
        default_room = self._room(room_ids[0]) if room_ids else None
        data["PassiveControlDefaults"] = {
            "Enabled": bool(
                default_room
                and self.coordinator.passive_mode_enabled
                and default_room.passive_mode_enabled
            ),
            "Strategy": (
                self.coordinator.passive_room_strategies.get(
                    str(default_room.id), DEFAULT_PASSIVE_CONTROL_STRATEGY
                )
                if default_room
                else DEFAULT_PASSIVE_CONTROL_STRATEGY
            ),
        }
        passive_controls = self._passive_control_schedules.get(str(schedule.id))

        def with_passive_controls():
            if not passive_controls:
                return data
            has_scheduled_period = False
            for day in data.get("ScheduleData", []):
                saved_day = passive_controls.get(day.get("day"), {})
                for slot in day.get("slots") or []:
                    control = saved_day.get(str(slot.get("Time", "")))
                    if not isinstance(control, dict):
                        continue
                    scheduled = bool(control.get("scheduled", True))
                    slot["PassiveScheduled"] = scheduled
                    if not scheduled:
                        continue
                    has_scheduled_period = True
                    slot["Setpoint"] = control["lower"]
                    slot["UpperSetpoint"] = control["upper"]
                    slot["PassiveMode"] = control["enabled"]
                    slot["PassiveStrategy"] = control["strategy"]
            if has_scheduled_period:
                data["PassiveControl"] = True
                data["PassiveRange"] = True
                data.setdefault("PassiveRangeType", "scheduled")
                data["MinUpperSetpoint"] = FROST_PROTECTION_TEMPERATURE
                data["MaxUpperSetpoint"] = MAX_SCHEDULE_TEMPERATURE
            return data
        uses_external_range = self.schedule_uses_external_range(schedule)
        uses_native_range = (
            not uses_external_range and self.schedule_uses_native_range(schedule)
        )
        if not uses_external_range and not uses_native_range:
            return with_passive_controls()

        if uses_native_range:
            room_ids = self._schedule_native_passive_room_ids(schedule)
            default_lower = max(
                float(self._room(room_id).passive_mode_lower_temp)
                for room_id in room_ids
            )
            saved = self._lower_schedules.get(str(schedule.id), {})
            data["PassiveRange"] = True
            data["PassiveRangeType"] = "native"
            data["MinUpperSetpoint"] = FROST_PROTECTION_TEMPERATURE
            data["MaxUpperSetpoint"] = MAX_SCHEDULE_TEMPERATURE
            for day in data.get("ScheduleData", []):
                saved_day = saved.get(day.get("day"), {})
                for slot in day.get("slots") or []:
                    native_upper = slot.get("Setpoint")
                    upper = self._numeric_setpoint(native_upper)
                    if upper is None:
                        slot["UpperSetpoint"] = native_upper
                        continue
                    lower = float(saved_day.get(slot.get("Time"), default_lower))
                    slot["Setpoint"] = min(lower, upper)
                    slot["UpperSetpoint"] = upper
            return with_passive_controls()

        room_ids = self._schedule_passive_room_ids(schedule)
        default_upper = max(
            float(self._room(room_id).configured_passive_mode_upper_temp)
            for room_id in room_ids
        )
        saved = self._upper_schedules.get(str(schedule.id), {})
        data["PassiveRange"] = True
        data["PassiveRangeType"] = "external"
        data["MinUpperSetpoint"] = FROST_PROTECTION_TEMPERATURE
        data["MaxUpperSetpoint"] = MAX_SCHEDULE_TEMPERATURE
        for day in data.get("ScheduleData", []):
            saved_day = saved.get(day.get("day"), {})
            for slot in day.get("slots") or []:
                native_lower = slot.get("Setpoint")
                lower = self._numeric_setpoint(native_lower)
                if lower is None:
                    slot["UpperSetpoint"] = native_lower
                    continue
                upper = float(saved_day.get(slot.get("Time"), default_upper))
                slot["UpperSetpoint"] = max(lower, upper)
        return with_passive_controls()

    def validated_lower_schedule(self, _schedule_id, schedule_data) -> dict:
        """Validate lower values paired with native Passive upper setpoints."""
        normalized = {}
        for day in schedule_data.get("ScheduleData", []):
            day_name = day.get("day")
            if day_name not in WEEKDAYS or not isinstance(day.get("slots"), list):
                raise ValueError("Passive schedule contains an invalid day")
            normalized_day = {}
            for slot in day["slots"]:
                time_value = str(slot.get("Time", ""))
                try:
                    lower = float(slot.get("Setpoint"))
                    upper = float(slot.get("UpperSetpoint"))
                except (TypeError, ValueError) as err:
                    raise ValueError(
                        "Missing Passive Mode temperature range for "
                        f"{day_name} {time_value}"
                    ) from err
                if lower != OFF_TEMPERATURE and not (
                    FROST_PROTECTION_TEMPERATURE
                    <= lower
                    <= MAX_SCHEDULE_TEMPERATURE
                ):
                    raise ValueError(
                        "Passive Mode lower temperatures must be Off or between "
                        f"{FROST_PROTECTION_TEMPERATURE:g} and "
                        f"{MAX_SCHEDULE_TEMPERATURE:g} °C"
                    )
                if upper == OFF_TEMPERATURE:
                    if lower != OFF_TEMPERATURE:
                        raise ValueError(
                            "A Passive Mode upper temperature of Off requires "
                            f"the lower temperature to be Off at {day_name} {time_value}"
                        )
                elif not (
                    FROST_PROTECTION_TEMPERATURE
                    <= upper
                    <= MAX_SCHEDULE_TEMPERATURE
                ):
                    raise ValueError(
                        "Passive Mode upper temperatures must be Off or between "
                        f"{FROST_PROTECTION_TEMPERATURE:g} and "
                        f"{MAX_SCHEDULE_TEMPERATURE:g} °C"
                    )
                if upper < lower:
                    raise ValueError(
                        "Upper temperature must not be below the lower temperature "
                        f"at {day_name} {time_value}"
                    )
                normalized_day[time_value] = lower
            normalized[day_name] = normalized_day
        if not any(normalized.values()):
            raise ValueError("Passive schedule must contain a time slot")
        return normalized

    def validated_upper_schedule(self, _schedule_id, schedule_data) -> dict:
        """Validate external cutoffs paired with native Wiser setpoints."""
        normalized = {}
        for day in schedule_data.get("ScheduleData", []):
            day_name = day.get("day")
            if day_name not in WEEKDAYS or not isinstance(day.get("slots"), list):
                raise ValueError("Passive schedule contains an invalid day")
            normalized_day = {}
            for slot in day["slots"]:
                time_value = str(slot.get("Time", ""))
                try:
                    lower = float(slot.get("Setpoint"))
                    upper = float(slot.get("UpperSetpoint"))
                except (TypeError, ValueError) as err:
                    raise ValueError(
                        "Missing Passive Mode temperature range for "
                        f"{day_name} {time_value}"
                    ) from err
                if lower != OFF_TEMPERATURE and not (
                    FROST_PROTECTION_TEMPERATURE
                    <= lower
                    <= MAX_SCHEDULE_TEMPERATURE
                ):
                    raise ValueError(
                        "Passive Mode lower temperatures must be Off or between "
                        f"{FROST_PROTECTION_TEMPERATURE:g} and "
                        f"{MAX_SCHEDULE_TEMPERATURE:g} °C"
                    )
                if upper == OFF_TEMPERATURE:
                    if lower != OFF_TEMPERATURE:
                        raise ValueError(
                            "A Passive Mode upper temperature of Off requires "
                            f"the lower temperature to be Off at {day_name} {time_value}"
                        )
                elif not (
                    FROST_PROTECTION_TEMPERATURE
                    <= upper
                    <= MAX_SCHEDULE_TEMPERATURE
                ):
                    raise ValueError(
                        "Passive Mode upper temperatures must be Off or between "
                        f"{FROST_PROTECTION_TEMPERATURE:g} and "
                        f"{MAX_SCHEDULE_TEMPERATURE:g} °C"
                    )
                if upper < lower:
                    raise ValueError(
                        "Upper temperature must not be below the lower temperature "
                        f"at {day_name} {time_value}"
                    )
                normalized_day[time_value] = upper
            normalized[day_name] = normalized_day
        if not any(normalized.values()):
            raise ValueError("Passive schedule must contain a time slot")
        return normalized

    def validated_passive_control_schedule(self, schedule_data) -> tuple[dict, dict]:
        """Validate scheduled Passive controls and build the hub schedule."""
        normalized = {}
        native_schedule = deepcopy(schedule_data)
        for key in (
            "Capabilities",
            "PassiveControlDefaults",
            "PassiveControl",
            "PassiveRange",
            "PassiveRangeType",
            "MinUpperSetpoint",
            "MaxUpperSetpoint",
        ):
            native_schedule.pop(key, None)
        native_days = {
            day.get("day"): day for day in native_schedule.get("ScheduleData", [])
        }
        range_type = schedule_data.get("PassiveRangeType")
        has_scheduled_period = False
        for day in schedule_data.get("ScheduleData", []):
            day_name = day.get("day")
            if day_name not in WEEKDAYS or not isinstance(day.get("slots"), list):
                raise ValueError("Passive control schedule contains an invalid day")
            normalized_day = {}
            native_slots = {
                str(slot.get("Time", "")): slot
                for slot in native_days.get(day_name, {}).get("slots", [])
            }
            for slot in day["slots"]:
                time_value = str(slot.get("Time", ""))
                scheduled = slot.get("PassiveScheduled")
                if not isinstance(scheduled, bool):
                    raise ValueError(
                        "Each period must specify whether Passive mode is scheduled"
                    )
                native_slot = native_slots.get(time_value)
                if native_slot is None:
                    raise ValueError(
                        f"Passive control period is missing at {day_name} {time_value}"
                    )
                if not scheduled:
                    normalized_day[time_value] = {"scheduled": False}
                    if range_type == "native" and slot.get("UpperSetpoint") is not None:
                        native_slot["Setpoint"] = slot["UpperSetpoint"]
                    for key in (
                        "UpperSetpoint",
                        "PassiveScheduled",
                        "PassiveMode",
                        "PassiveStrategy",
                    ):
                        native_slot.pop(key, None)
                    continue
                has_scheduled_period = True
                enabled = slot.get("PassiveMode")
                strategy = slot.get("PassiveStrategy")
                if not isinstance(enabled, bool) or strategy not in CONTROL_STRATEGIES:
                    raise ValueError(
                        "Each Passive control period requires a mode and strategy"
                    )
                try:
                    lower = float(slot.get("Setpoint"))
                    upper = float(slot.get("UpperSetpoint"))
                except (TypeError, ValueError) as err:
                    raise ValueError(
                        "Missing Passive Mode temperature range for "
                        f"{day_name} {time_value}"
                    ) from err
                for label, temperature in (("Lower", lower), ("Upper", upper)):
                    if temperature != OFF_TEMPERATURE and not (
                        FROST_PROTECTION_TEMPERATURE
                        <= temperature
                        <= MAX_SCHEDULE_TEMPERATURE
                    ):
                        raise ValueError(
                            f"{label} temperature must be Off or between "
                            f"{FROST_PROTECTION_TEMPERATURE:g} and "
                            f"{MAX_SCHEDULE_TEMPERATURE:g} °C"
                        )
                if upper == OFF_TEMPERATURE and lower != OFF_TEMPERATURE:
                    raise ValueError(
                        "An upper temperature of Off requires the lower temperature "
                        f"to be Off at {day_name} {time_value}"
                    )
                if upper < lower:
                    raise ValueError(
                        "Upper temperature must not be below the lower temperature "
                        f"at {day_name} {time_value}"
                    )
                normalized_day[time_value] = {
                    "scheduled": True,
                    "enabled": enabled,
                    "strategy": strategy,
                    "lower": lower,
                    "upper": upper,
                }
                native_slot["Setpoint"] = (
                    lower
                    if strategy == CONTROL_STRATEGY_TEMPERATURE_LIMITER
                    else upper
                )
                for key in (
                    "UpperSetpoint",
                    "PassiveScheduled",
                    "PassiveMode",
                    "PassiveStrategy",
                ):
                    native_slot.pop(key, None)
            normalized[day_name] = normalized_day
        if not has_scheduled_period:
            raise ValueError("Passive control schedule must contain a time slot")
        return normalized, native_schedule

    @staticmethod
    def _numeric_setpoint(value):
        """Return a numeric setpoint, treating the Wiser Off value as absent."""
        try:
            temperature = float(value)
        except (TypeError, ValueError):
            return None
        return None if temperature < FROST_PROTECTION_TEMPERATURE else temperature

    async def async_save_upper_schedule(self, schedule_id, upper_schedule) -> None:
        """Persist a validated external limiter cutoff schedule."""
        schedule_id = str(schedule_id)
        previous = deepcopy(self._upper_schedules.get(schedule_id))
        self._upper_schedules[schedule_id] = upper_schedule
        try:
            await self._async_save()
        except Exception:
            if previous is None:
                self._upper_schedules.pop(schedule_id, None)
            else:
                self._upper_schedules[schedule_id] = previous
            raise

    async def async_save_lower_schedule(self, schedule_id, lower_schedule) -> None:
        """Persist a validated native Passive lower schedule."""
        schedule_id = str(schedule_id)
        previous = deepcopy(self._lower_schedules.get(schedule_id))
        self._lower_schedules[schedule_id] = lower_schedule
        try:
            await self._async_save()
        except Exception:
            if previous is None:
                self._lower_schedules.pop(schedule_id, None)
            else:
                self._lower_schedules[schedule_id] = previous
            raise

    async def async_save_passive_control_schedule(
        self, schedule_id, control_schedule
    ) -> None:
        """Persist mode and strategy transitions paired with a heating schedule."""
        schedule_id = str(schedule_id)
        previous = deepcopy(self._passive_control_schedules.get(schedule_id))
        self._passive_control_schedules[schedule_id] = control_schedule
        try:
            await self._async_save()
        except Exception:
            if previous is None:
                self._passive_control_schedules.pop(schedule_id, None)
            else:
                self._passive_control_schedules[schedule_id] = previous
            raise

    async def async_disable_passive_control_schedule(self, schedule_id) -> None:
        """Stop applying scheduled Passive mode and strategy transitions."""
        schedule_id = str(schedule_id)
        previous = self._passive_control_schedules.pop(schedule_id, None)
        if previous is None:
            return
        try:
            await self._async_save()
        except Exception:
            self._passive_control_schedules[schedule_id] = previous
            raise

    async def async_copy_schedule_metadata(
        self, schedule_id, to_schedule_id
    ) -> None:
        """Copy all locally stored schedule metadata without stale values."""
        source_id = str(schedule_id)
        target_id = str(to_schedule_id)
        schedule_stores = (
            self._upper_schedules,
            self._lower_schedules,
            self._passive_control_schedules,
        )
        previous = [deepcopy(schedules.get(target_id)) for schedules in schedule_stores]
        for schedules in schedule_stores:
            source = schedules.get(source_id)
            if source is None:
                schedules.pop(target_id, None)
            else:
                schedules[target_id] = deepcopy(source)
        try:
            await self._async_save()
        except Exception:
            for schedules, value in zip(schedule_stores, previous):
                if value is None:
                    schedules.pop(target_id, None)
                else:
                    schedules[target_id] = value
            raise

    async def async_delete_schedule_metadata(self, schedule_id) -> None:
        """Remove all locally stored metadata after schedule deletion."""
        schedule_id = str(schedule_id)
        changed = False
        for schedules in (
            self._upper_schedules,
            self._lower_schedules,
            self._passive_control_schedules,
        ):
            changed = schedules.pop(schedule_id, None) is not None or changed
        if changed:
            await self._async_save()

    def _special_time(self, day, value):
        """Resolve hub sunrise/sunset schedule markers for a weekday."""
        source = None
        if str(value).casefold() == "sunrise":
            source = self.coordinator.wiserhub.system.sunrise_times
        elif str(value).casefold() == "sunset":
            source = self.coordinator.wiserhub.system.sunset_times
        if source is None:
            return value
        return next(
            (
                time_value
                for day_name, time_value in source.items()
                if str(day_name).casefold() == str(day).casefold()
            ),
            "00:00",
        )

    def _scheduled_value(
        self,
        room,
        schedules,
        now: datetime | None = None,
        *,
        next_period: bool = False,
    ):
        """Evaluate a local value paired with the current or next hub slot."""
        schedule = getattr(room, "schedule", None)
        if schedule is None:
            return None
        saved = schedules.get(str(schedule.id))
        if not saved:
            return None

        transitions = []
        for day in schedule.ws_schedule_data.get("ScheduleData", []):
            day_name = day.get("day")
            if day_name not in WEEKDAYS:
                continue
            day_index = WEEKDAYS.index(day_name)
            saved_day = saved.get(day_name, {})
            for slot in day.get("slots") or []:
                time_key = str(slot.get("Time", ""))
                if time_key not in saved_day:
                    continue
                resolved_time = str(self._special_time(day_name, time_key))
                try:
                    hour, minute = (int(part) for part in resolved_time.split(":"))
                except (TypeError, ValueError):
                    continue
                transitions.append(
                    (day_index * 1440 + hour * 60 + minute, saved_day[time_key])
                )
        if not transitions:
            return None
        transitions.sort()
        current = now or dt_util.now()
        current_minute = current.weekday() * 1440 + current.hour * 60 + current.minute
        if next_period:
            future = [item for item in transitions if item[0] > current_minute]
            return deepcopy((future[0] if future else transitions[0])[1])
        previous = [item for item in transitions if item[0] <= current_minute]
        return deepcopy((previous[-1] if previous else transitions[-1])[1])

    def _scheduled_temperature(
        self,
        room,
        schedules,
        now: datetime | None = None,
        *,
        next_period: bool = False,
    ):
        """Evaluate a numeric local value paired with a hub schedule slot."""
        value = self._scheduled_value(
            room, schedules, now, next_period=next_period
        )
        return float(value) if value is not None else None

    def scheduled_passive_control(
        self, room_id, now: datetime | None = None, *, next_period: bool = False
    ) -> dict | None:
        """Return the scheduled Passive mode and strategy for a room."""
        if not self.coordinator.passive_mode_enabled:
            return None
        room = self._room(room_id)
        if room is None:
            return None
        value = self._scheduled_value(
            room,
            self._passive_control_schedules,
            now,
            next_period=next_period,
        )
        return (
            value
            if isinstance(value, dict) and value.get("scheduled", True)
            else None
        )

    def passive_lower_temperature(self, room, now: datetime | None = None):
        """Return the scheduled lower limit for either Passive range type."""
        schedule = getattr(room, "schedule", None)
        if schedule is None:
            return None
        override = self._settings(room.id).get("passive_lower_override")
        if override is not None and room.is_override:
            return min(float(override), float(room.passive_mode_upper_temp))
        control = self.scheduled_passive_control(room.id, now)
        if control is not None:
            return float(control["lower"]) if control["enabled"] else None
        if self.schedule_uses_external_range(schedule):
            try:
                return float(schedule.current_setting)
            except (TypeError, ValueError):
                return None
        if self.schedule_uses_native_range(schedule):
            return self._scheduled_temperature(room, self._lower_schedules, now)
        return None

    async def async_cancel_passive_lower_override(self, room_id) -> None:
        """Return a native Passive lower limit to its current schedule slot."""
        settings = self._settings(room_id)
        if settings.get("passive_lower_override") is None:
            return
        settings["passive_lower_override"] = None
        self._clear_unused_schedule_override_marker(settings)
        await self._async_save()

    async def async_set_passive_lower_temperature(
        self, room_id, temperature: float
    ) -> None:
        """Set a scheduled Passive lower override or the static lower value."""
        room = self._room(room_id)
        if room is None:
            return
        upper_temperature = (
            self.upper_temperature(room_id)
            if self.uses_temperature_limiter(room_id)
            else float(room.passive_mode_upper_temp)
        )
        temperature = min(float(temperature), upper_temperature)
        if (
            room.mode == "Auto"
            and room.schedule is not None
            and (
                self.schedule_uses_external_range(room.schedule)
                or self.schedule_uses_native_range(room.schedule)
            )
        ):
            await room.set_target_temperature(temperature)
            settings = self._settings(room_id)
            settings["passive_lower_override"] = temperature
            self._set_schedule_override_marker(settings, room)
            await self._async_save()
            return
        await room.set_passive_mode_lower_temp(temperature)

    async def async_set_upper_temperature(self, room_id, temperature: float) -> None:
        """Set the cutoff used only by an external temperature limiter."""
        room = self._room(room_id)
        if room is None:
            return
        if not self.uses_temperature_limiter(room_id):
            if room.mode == "Manual":
                await room.set_passive_mode_upper_temp(float(temperature))
            return
        temperature = max(float(temperature), float(room.passive_mode_lower_temp))
        settings = self._settings(room_id)
        if room.mode == "Auto" and room.schedule is not None:
            settings["passive_upper_override"] = temperature
            self._set_schedule_override_marker(settings, room)
            await self._async_save()
            return
        settings["passive_upper_override"] = temperature
        settings["passive_override_schedule_transition"] = None
        await self._async_save()

    async def async_cancel_upper_override(self, room_id) -> None:
        """Return the upper threshold to the native Passive value."""
        settings = self._settings(room_id)
        if settings.get("passive_upper_override") is None:
            return
        settings["passive_upper_override"] = None
        self._clear_unused_schedule_override_marker(settings)
        await self._async_save()

    async def async_advance_upper_schedule(self, room_id) -> None:
        """Pair Wiser Advance Schedule with the next external cutoff."""
        room = self._room(room_id)
        if room is None or not self.uses_temperature_limiter(room_id):
            return
        upper = self._scheduled_temperature(
            room, self._upper_schedules, next_period=True
        )
        if upper is None:
            return
        settings = self._settings(room_id)
        settings["passive_upper_override"] = upper
        self._set_schedule_override_marker(settings, room)
        await self._async_save()

    async def async_advance_passive_lower_schedule(self, room_id) -> None:
        """Pair Wiser's Advance Schedule override with the next lower slot."""
        room = self._room(room_id)
        schedule = getattr(room, "schedule", None)
        if room is None or schedule is None:
            return
        if self.schedule_uses_external_range(schedule):
            next_period = getattr(schedule, "next", None)
            try:
                lower = float(next_period.setting)
            except (AttributeError, TypeError, ValueError):
                return
        elif self.schedule_uses_native_range(schedule):
            lower = self._scheduled_temperature(
                room, self._lower_schedules, next_period=True
            )
        else:
            return
        if lower is None:
            return
        settings = self._settings(room_id)
        settings["passive_lower_override"] = lower
        self._set_schedule_override_marker(settings, room)
        await self._async_save()

    async def async_update(self) -> None:
        """Update external climate mirroring and temperature feedback."""
        await self._async_remove_orphaned_schedules()
        storage_changed = False
        for room in self.coordinator.wiserhub.rooms.all:
            room_id = str(room.id)
            control = self.scheduled_passive_control(room.id)
            settings = self._rooms.get(room_id)
            original = (
                settings.get("passive_schedule_original_enabled")
                if isinstance(settings, dict)
                else None
            )
            if control is not None:
                settings = self._settings(room_id)
                if original is None:
                    settings["passive_schedule_original_enabled"] = bool(
                        room.passive_mode_enabled
                    )
                    storage_changed = True
                enabled = bool(control["enabled"])
                if bool(room.passive_mode_enabled) != enabled:
                    await room.set_passive_mode(enabled)
                    if not enabled:
                        await room.cancel_overrides()
            elif original is not None:
                if bool(room.passive_mode_enabled) != bool(original):
                    await room.set_passive_mode(bool(original))
                    if not original:
                        await room.cancel_overrides()
                settings["passive_schedule_original_enabled"] = None
                storage_changed = True
        for room in self.coordinator.wiserhub.rooms.all:
            settings = self._rooms.get(str(room.id))
            if not isinstance(settings, dict):
                continue
            has_override = (
                settings.get("passive_lower_override") is not None
                or settings.get("passive_upper_override") is not None
            )
            if not has_override:
                continue
            marker = self._schedule_transition_marker(room)
            stored_marker = settings.get("passive_override_schedule_transition")
            if stored_marker is None:
                if marker is not None:
                    settings["passive_override_schedule_transition"] = marker
                    storage_changed = True
            elif marker is not None and marker != stored_marker:
                settings["passive_lower_override"] = None
                settings["passive_upper_override"] = None
                settings["passive_override_schedule_transition"] = None
                storage_changed = True
        if storage_changed:
            await self._async_save()
        for room in self.coordinator.wiserhub.rooms.all:
            room_id = str(room.id)
            if room_id not in self._sensor_boosts:
                continue
            if self.available and self.has_temperature_sensor(room.id):
                continue
            if self._sensor_boost_is_owned(room):
                await self._async_clear_sensor_boost(room)
            else:
                self._sensor_boosts.pop(room_id, None)
                await self._async_save()
        if not self.available:
            return

        for room in self.coordinator.wiserhub.rooms.all:
            if self.has_temperature_sensor(room.id):
                self._closed_limiter_rooms.discard(str(room.id))
                await self._async_update_temperature_sensor(room)
                continue
            if not self.is_enabled(room.id):
                self._closed_limiter_rooms.discard(str(room.id))
                continue
            if room.is_passive_mode and self.uses_temperature_limiter(room.id):
                current_temperature = room.current_temperature
                if current_temperature is None:
                    continue
                room_id = str(room.id)
                upper_temperature = self.upper_temperature(room.id)
                if current_temperature >= upper_temperature:
                    self._closed_limiter_rooms.add(room_id)
                elif (
                    room_id in self._closed_limiter_rooms
                    and current_temperature
                    <= upper_temperature
                    - float(self.coordinator.passive_temperature_increment)
                ):
                    self._closed_limiter_rooms.discard(room_id)
                target_temperature = (
                    FROST_PROTECTION_TEMPERATURE
                    if room_id in self._closed_limiter_rooms
                    else None
                )
                await self._async_set_external_climates(
                    room.id, target_temperature
                )
                continue
            self._closed_limiter_rooms.discard(str(room.id))
            target_temperature = room.current_target_temperature
            if target_temperature is None:
                continue
            await self._async_set_external_climates(room.id, target_temperature)

    def _external_temperature(self, room_id) -> float | None:
        """Return a fresh assigned sensor temperature converted to Celsius."""
        entity_id = self.temperature_sensor_entity_id(room_id)
        state = self.hass.states.get(entity_id) if entity_id else None
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None
        last_updated = getattr(state, "last_updated", None)
        if last_updated is not None:
            try:
                age = dt_util.utcnow() - dt_util.as_utc(last_updated)
            except (TypeError, ValueError):
                return None
            if age > timedelta(minutes=self.temperature_stale_minutes):
                return None
        try:
            temperature = float(state.state)
            unit = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
            if unit and unit != UnitOfTemperature.CELSIUS:
                temperature = TemperatureConverter.convert(
                    temperature, unit, UnitOfTemperature.CELSIUS
                )
        except (TypeError, ValueError):
            return None
        return temperature if math.isfinite(temperature) else None

    def _temperature_boost_delta(self, shortfall: float) -> float:
        """Return a valid Wiser boost increment for the measured shortfall."""
        if self.temperature_boost_mode == EXTERNAL_TEMPERATURE_BOOST_FIXED:
            boost = min(max(0.5, self.temperature_fixed_boost), 5.0)
            return math.ceil(boost * 2) / 2
        boost = shortfall * self.temperature_proportional_multiplier
        boost = min(max(0.5, boost), self.temperature_max_boost, 5.0)
        return math.ceil(boost * 2) / 2

    def _sensor_boost_is_owned(self, room) -> bool:
        """Return whether the active boost still matches one created here."""
        room_id = str(room.id)
        marker = self._sensor_boosts.get(room_id)
        if not isinstance(marker, dict):
            return False
        expected_end = marker.get("expected_end")
        if not room.is_boosted:
            try:
                expected = dt_util.parse_datetime(expected_end)
                return bool(
                    expected is not None
                    and dt_util.as_utc(expected) > dt_util.utcnow()
                )
            except (TypeError, ValueError):
                return False
        actual_end = getattr(room, "boost_end_time", None)
        if expected_end and actual_end is not None:
            try:
                expected = dt_util.parse_datetime(expected_end)
                actual = (
                    actual_end
                    if isinstance(actual_end, datetime)
                    else dt_util.parse_datetime(str(actual_end))
                )
                if expected is None or actual is None:
                    return False
                difference = dt_util.as_utc(actual) - dt_util.as_utc(expected)
                if abs(difference.total_seconds()) > 120:
                    return False
            except (TypeError, ValueError):
                return False
        return True

    async def _async_clear_sensor_boost(self, room) -> None:
        """Cancel a boost only when it is still owned by sensor feedback."""
        room_id = str(room.id)
        if not room.is_boosted:
            return
        if self._sensor_boost_is_owned(room) and not await room.cancel_boost():
            return
        if room_id in self._sensor_boosts:
            self._sensor_boosts.pop(room_id, None)
            await self._async_save()

    async def _async_update_temperature_sensor(self, room) -> None:
        """Apply external temperature feedback through owned Wiser boosts."""
        room_id = str(room.id)
        owned = self._sensor_boost_is_owned(room)
        if room_id in self._sensor_boosts and not owned:
            self._sensor_boosts.pop(room_id, None)
            await self._async_save()

        normal_auto = bool(
            room.mode == "Auto"
            and not room.is_away_mode
            and not room.is_passive_mode
            and (not room.is_override or owned)
        )
        temperature = self._external_temperature(room.id)
        target = getattr(room, "scheduled_target_temperature", None)
        try:
            target = float(target)
        except (TypeError, ValueError):
            target = None

        if not normal_auto or temperature is None or target is None:
            if owned:
                await self._async_clear_sensor_boost(room)
            return

        shortfall = target - temperature
        if shortfall <= self.temperature_tolerance:
            if owned:
                await self._async_clear_sensor_boost(room)
            return
        if room.is_boosted or room.is_override:
            return
        if owned:
            return

        delta = self._temperature_boost_delta(shortfall)
        if not await room.boost(delta, self.temperature_boost_duration):
            return
        expected_end = dt_util.utcnow() + timedelta(
            minutes=self.temperature_boost_duration
        )
        self._sensor_boosts[room_id] = {
            "expected_end": expected_end.isoformat(),
            "duration": self.temperature_boost_duration,
            "delta": delta,
        }
        await self._async_save()

    async def _async_remove_orphaned_schedules(self) -> None:
        """Remove paired values whose native Wiser schedule no longer exists."""
        schedules = getattr(self.coordinator.wiserhub, "schedules", None)
        heating_schedules = getattr(schedules, "heating_schedules", None)
        if heating_schedules is None:
            return
        valid_schedule_ids = {str(schedule.id) for schedule in heating_schedules}
        orphaned_upper_ids = set(self._upper_schedules) - valid_schedule_ids
        orphaned_lower_ids = set(self._lower_schedules) - valid_schedule_ids
        orphaned_control_ids = (
            set(self._passive_control_schedules) - valid_schedule_ids
        )
        if (
            not orphaned_upper_ids
            and not orphaned_lower_ids
            and not orphaned_control_ids
        ):
            return
        for schedule_id in orphaned_upper_ids:
            self._upper_schedules.pop(schedule_id, None)
        for schedule_id in orphaned_lower_ids:
            self._lower_schedules.pop(schedule_id, None)
        for schedule_id in orphaned_control_ids:
            self._passive_control_schedules.pop(schedule_id, None)
        await self._async_save()

    async def _async_set_external_climates(
        self, room_id, target_temperature: float | None
    ) -> None:
        """Set external climates to a target, or their maximum when open."""
        for entity_id in self.assigned_entity_ids(room_id):
            registry_entry = er.async_get(self.hass).async_get(entity_id)
            if registry_entry is not None and registry_entry.platform == DOMAIN:
                _LOGGER.warning(
                    "Ignoring Wiser climate entity %s assigned as external control",
                    entity_id,
                )
                continue
            state = self.hass.states.get(entity_id)
            if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                _LOGGER.debug("External climate entity %s is unavailable", entity_id)
                continue
            current_target = state.attributes.get(ATTR_TEMPERATURE)
            try:
                current_target = (
                    float(current_target) if current_target is not None else None
                )
            except (TypeError, ValueError):
                current_target = None

            minimum_target = state.attributes.get(ATTR_MIN_TEMP)
            try:
                minimum_target = (
                    float(minimum_target) if minimum_target is not None else None
                )
            except (TypeError, ValueError):
                minimum_target = None
            maximum_target = state.attributes.get(ATTR_MAX_TEMP)
            try:
                maximum_target = (
                    float(maximum_target) if maximum_target is not None else None
                )
            except (TypeError, ValueError):
                maximum_target = None
            target = float(
                target_temperature
                if target_temperature is not None
                else maximum_target or DEFAULT_OPEN_TEMPERATURE
            )
            target = max(
                minimum_target or FROST_PROTECTION_TEMPERATURE,
                target,
            )
            if maximum_target is not None:
                target = min(maximum_target, target)
            if current_target == target:
                continue
            try:
                await self.hass.services.async_call(
                    CLIMATE_DOMAIN,
                    SERVICE_SET_TEMPERATURE,
                    {ATTR_ENTITY_ID: entity_id, ATTR_TEMPERATURE: target},
                    blocking=True,
                )
            except HomeAssistantError as ex:
                _LOGGER.warning(
                    "Unable to set External Room Control target for %s: %s",
                    entity_id,
                    ex,
                )
