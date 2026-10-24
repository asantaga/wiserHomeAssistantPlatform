"""External Room Control and Passive Mode schedule support."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import logging

from homeassistant.components.climate import DOMAIN as CLIMATE_DOMAIN
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    CONF_AUTOMATIONS_EXTERNAL_ROOM_CONTROL,
    CONF_EXTERNAL_ROOM_CONTROL_ASSIGNMENTS,
    CONTROL_STRATEGY_TEMPERATURE_LIMITER,
    DOMAIN,
)

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
        self.available = options.get(CONF_AUTOMATIONS_EXTERNAL_ROOM_CONTROL, False)
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
        self._native_passive_migrated = False
        self._closed_limiter_rooms: set[str] = set()

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
        self._native_passive_migrated = bool(
            stored.get("native_passive_migrated", False)
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
                "native_passive_migrated": self._native_passive_migrated,
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
        schedule_id = str(schedule.id)
        return {
            str(room.id)
            for room in self.coordinator.wiserhub.rooms.all
            if str(room.id) in assigned_ids
            or (
                getattr(room, "schedule", None) is not None
                and str(room.schedule.id) == schedule_id
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
        uses_external_range = self.schedule_uses_external_range(schedule)
        uses_native_range = (
            not uses_external_range and self.schedule_uses_native_range(schedule)
        )
        if not uses_external_range and not uses_native_range:
            return data

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
            return data

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
        return data

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

    async def async_copy_upper_schedule(self, schedule_id, to_schedule_id) -> None:
        """Copy paired external cutoffs with a Wiser schedule copy."""
        source = self._upper_schedules.get(str(schedule_id))
        if source is None:
            return
        self._upper_schedules[str(to_schedule_id)] = deepcopy(source)
        await self._async_save()

    async def async_copy_lower_schedule(self, schedule_id, to_schedule_id) -> None:
        """Copy paired native lower values with a Wiser schedule copy."""
        source = self._lower_schedules.get(str(schedule_id))
        if source is None:
            return
        self._lower_schedules[str(to_schedule_id)] = deepcopy(source)
        await self._async_save()

    async def async_delete_upper_schedule(self, schedule_id) -> None:
        """Remove local external cutoffs after the hub schedule is deleted."""
        if self._upper_schedules.pop(str(schedule_id), None) is not None:
            await self._async_save()

    async def async_delete_lower_schedule(self, schedule_id) -> None:
        """Remove local native lower values after the hub schedule is deleted."""
        if self._lower_schedules.pop(str(schedule_id), None) is not None:
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

    def _scheduled_temperature(
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
            return float((future[0] if future else transitions[0])[1])
        previous = [item for item in transitions if item[0] <= current_minute]
        return float((previous[-1] if previous else transitions[-1])[1])

    def passive_lower_temperature(self, room, now: datetime | None = None):
        """Return the scheduled lower limit for either Passive range type."""
        schedule = getattr(room, "schedule", None)
        if schedule is None:
            return None
        override = self._settings(room.id).get("passive_lower_override")
        if override is not None and room.is_override:
            return min(float(override), float(room.passive_mode_upper_temp))
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
        """Mirror each Wiser room target to its assigned external climates."""
        await self._async_remove_orphaned_schedules()
        storage_changed = False
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
        if not self.available:
            return

        for room in self.coordinator.wiserhub.rooms.all:
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

    async def _async_remove_orphaned_schedules(self) -> None:
        """Remove paired values whose native Wiser schedule no longer exists."""
        schedules = getattr(self.coordinator.wiserhub, "schedules", None)
        heating_schedules = getattr(schedules, "heating_schedules", None)
        if heating_schedules is None:
            return
        valid_schedule_ids = {str(schedule.id) for schedule in heating_schedules}
        orphaned_upper_ids = set(self._upper_schedules) - valid_schedule_ids
        orphaned_lower_ids = set(self._lower_schedules) - valid_schedule_ids
        if not orphaned_upper_ids and not orphaned_lower_ids:
            return
        for schedule_id in orphaned_upper_ids:
            self._upper_schedules.pop(schedule_id, None)
        for schedule_id in orphaned_lower_ids:
            self._lower_schedules.pop(schedule_id, None)
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
