"""External Passive Mode control for Home Assistant climate entities."""

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
    CONF_AUTOMATIONS_EXTERNAL_PASSIVE,
    CONF_EXTERNAL_PASSIVE_ASSIGNMENTS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

SERVICE_SET_TEMPERATURE = "set_temperature"
ATTR_MAX_TEMP = "max_temp"
STORAGE_VERSION = 1
DEFAULT_LOWER_TEMPERATURE = 14.0
DEFAULT_UPPER_TEMPERATURE = 18.0
DEFAULT_OPEN_TEMPERATURE = 25.0
FROST_PROTECTION_TEMPERATURE = 5.0
MAX_SCHEDULE_TEMPERATURE = 30.0
WEEKDAYS = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


class ExternalPassiveController:
    """Persist External Passive settings and control assigned climate entities."""

    def __init__(self, hass, config_entry, coordinator) -> None:
        """Initialise the controller from config-entry options."""
        self.hass = hass
        self.coordinator = coordinator
        options = config_entry.options.get(CONF_AUTOMATIONS_EXTERNAL_PASSIVE, {})
        self.available = options.get(CONF_AUTOMATIONS_EXTERNAL_PASSIVE, False)
        configured_assignments = {
            str(room_id): list(entity_ids)
            for room_id, entity_ids in options.get(
                CONF_EXTERNAL_PASSIVE_ASSIGNMENTS, {}
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
                "Ignoring external TRVs assigned to multiple Wiser rooms: %s",
                ", ".join(sorted(duplicate_entities)),
            )
        self._store = Store(
            hass,
            STORAGE_VERSION,
            f"{DOMAIN}.external_passive.{config_entry.entry_id}",
        )
        self._rooms: dict[str, dict] = {}
        self._upper_schedules: dict[str, dict] = {}

    async def async_load(self) -> None:
        """Load per-room enablement, limits, and remembered valve targets."""
        stored = await self._store.async_load() or {}
        rooms = stored.get("rooms", {})
        self._rooms = rooms if isinstance(rooms, dict) else {}
        upper_schedules = stored.get("upper_schedules", {})
        self._upper_schedules = (
            upper_schedules if isinstance(upper_schedules, dict) else {}
        )
        storage_changed = False
        for room_id in list(self._rooms):
            before = self._rooms[room_id]
            before = dict(before) if isinstance(before, dict) else None
            settings = self._settings(room_id)
            assigned_entities = set(self.assigned_entity_ids(room_id))
            open_targets = settings["open_targets"]
            retained_targets = {
                entity_id: target
                for entity_id, target in open_targets.items()
                if entity_id in assigned_entities
            }
            if retained_targets != open_targets:
                settings["open_targets"] = retained_targets
            if before != settings:
                storage_changed = True
        if storage_changed:
            await self._async_save()

    async def _async_save(self) -> None:
        """Persist per-room settings."""
        await self._store.async_save(
            {
                "rooms": self._rooms,
                "upper_schedules": self._upper_schedules,
            }
        )

    def _settings(self, room_id) -> dict:
        """Return settings for a room, creating defaults when needed."""
        room_id = str(room_id)
        settings = self._rooms.get(room_id)
        if not isinstance(settings, dict):
            settings = {}
            self._rooms[room_id] = settings
        settings.setdefault("enabled", False)
        settings.setdefault("lower", DEFAULT_LOWER_TEMPERATURE)
        settings.setdefault("upper", DEFAULT_UPPER_TEMPERATURE)
        settings.setdefault("upper_override", None)
        if not isinstance(settings.get("open_targets"), dict):
            settings["open_targets"] = {}
        return settings

    def assigned_entity_ids(self, room_id) -> list[str]:
        """Return climate entities assigned to a Wiser room."""
        return self.assignments.get(str(room_id), [])

    def has_assignment(self, room_id) -> bool:
        """Return whether a room has at least one external climate entity."""
        return bool(self.assigned_entity_ids(room_id))

    def is_enabled(self, room_id) -> bool:
        """Return whether External Passive Mode is enabled for a room."""
        return bool(
            self.available
            and self.has_assignment(room_id)
            and self._settings(room_id).get("enabled", False)
        )

    def is_active(self, room) -> bool:
        """Return whether External Passive Mode is currently active."""
        return bool(
            self.is_enabled(room.id)
            and str(room.mode).casefold() != "off"
            and not room.is_boosted
            and not room.is_away_mode
        )

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

    def lower_temperature(self, room_id) -> float:
        """Return the hub-scheduled or overridden room demand threshold."""
        settings = self._settings(room_id)
        room = self._room(room_id)
        lower_temperature = float(settings["lower"])
        if room is not None:
            if str(room.mode).casefold() == "auto" and not room.is_override:
                lower_temperature = room.scheduled_target_temperature
            else:
                lower_temperature = room.current_target_temperature
        return min(float(lower_temperature), self.upper_temperature(room_id))

    def upper_temperature(self, room_id) -> float:
        """Return the overridden or currently scheduled valve-closing limit."""
        settings = self._settings(room_id)
        if settings.get("upper_override") is not None:
            return float(settings["upper_override"])
        room = self._room(room_id)
        scheduled = self._scheduled_upper_temperature(room) if room else None
        return float(scheduled if scheduled is not None else settings["upper"])

    def _schedule_room_ids(self, schedule) -> set[str]:
        """Return enabled External Passive rooms assigned to a schedule."""
        return {
            str(room_id)
            for room_id in schedule.assignment_ids
            if self.is_enabled(room_id)
        }

    def schedule_uses_upper_limits(self, schedule) -> bool:
        """Return whether a heating schedule needs External Passive upper values."""
        return bool(
            self.available
            and str(schedule.schedule_type).casefold() == "heating"
            and self._schedule_room_ids(schedule)
        )

    def schedule_data(self, schedule) -> dict:
        """Add locally stored upper limits to a native Wiser heating schedule."""
        data = deepcopy(schedule.ws_schedule_data)
        if not self.schedule_uses_upper_limits(schedule):
            return data

        room_ids = self._schedule_room_ids(schedule)
        default_upper = max(
            float(self._settings(room_id)["upper"])
            for room_id in room_ids
        )
        saved = self._upper_schedules.get(str(schedule.id), {})
        data["ExternalPassiveRange"] = True
        data["MinUpperSetpoint"] = FROST_PROTECTION_TEMPERATURE
        data["MaxUpperSetpoint"] = MAX_SCHEDULE_TEMPERATURE
        for day in data.get("ScheduleData", []):
            saved_day = saved.get(day.get("day"), {})
            for slot in day.get("slots") or []:
                lower = self._numeric_setpoint(slot.get("Setpoint"))
                minimum_upper = max(
                    FROST_PROTECTION_TEMPERATURE,
                    lower if lower is not None else FROST_PROTECTION_TEMPERATURE,
                )
                slot["UpperSetpoint"] = float(
                    max(
                        minimum_upper,
                        saved_day.get(slot.get("Time"), default_upper),
                    )
                )
        return data

    @staticmethod
    def _numeric_setpoint(value):
        """Return a numeric setpoint, treating the Wiser Off value as absent."""
        try:
            temperature = float(value)
        except (TypeError, ValueError):
            return None
        return None if temperature < FROST_PROTECTION_TEMPERATURE else temperature

    def validated_upper_schedule(self, _schedule_id, schedule_data) -> dict:
        """Validate and normalize upper values from the combined editor payload."""
        normalized = {}
        for day in schedule_data.get("ScheduleData", []):
            day_name = day.get("day")
            if day_name not in WEEKDAYS or not isinstance(day.get("slots"), list):
                raise ValueError("External Passive schedule contains an invalid day")
            normalized_day = {}
            for slot in day["slots"]:
                time_value = str(slot.get("Time", ""))
                try:
                    upper = float(slot.get("UpperSetpoint"))
                except (TypeError, ValueError) as err:
                    raise ValueError(
                        "Missing External Passive upper temperature for "
                        f"{day_name} {time_value}"
                    ) from err
                lower = self._numeric_setpoint(slot.get("Setpoint"))
                if not (
                    FROST_PROTECTION_TEMPERATURE
                    <= upper
                    <= MAX_SCHEDULE_TEMPERATURE
                ):
                    raise ValueError(
                        "External Passive upper temperatures must be between "
                        f"{FROST_PROTECTION_TEMPERATURE:g} and "
                        f"{MAX_SCHEDULE_TEMPERATURE:g} °C"
                    )
                if lower is not None and upper < lower:
                    raise ValueError(
                        "Upper temperature must not be below the lower temperature "
                        f"at {day_name} {time_value}"
                    )
                normalized_day[time_value] = upper
            normalized[day_name] = normalized_day
        if not any(normalized.values()):
            raise ValueError("External Passive schedule must contain a time slot")
        return normalized

    async def async_save_upper_schedule(self, schedule_id, upper_schedule) -> None:
        """Persist a previously validated upper schedule."""
        self._upper_schedules[str(schedule_id)] = upper_schedule
        await self._async_save()

    async def async_copy_upper_schedule(self, schedule_id, to_schedule_id) -> None:
        """Copy paired upper values with an existing native schedule copy."""
        source = self._upper_schedules.get(str(schedule_id))
        if source is None:
            return
        self._upper_schedules[str(to_schedule_id)] = deepcopy(source)
        await self._async_save()

    async def async_delete_upper_schedule(self, schedule_id) -> None:
        """Remove local upper values after the hub schedule is deleted."""
        if self._upper_schedules.pop(str(schedule_id), None) is not None:
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

    def _scheduled_upper_temperature(
        self, room, now: datetime | None = None, *, next_period: bool = False
    ):
        """Evaluate the upper value paired with the current or next hub slot."""
        schedule = getattr(room, "schedule", None)
        if schedule is None:
            return None
        saved = self._upper_schedules.get(str(schedule.id))
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

    async def async_set_enabled(self, room_id, enabled: bool) -> None:
        """Enable or disable External Passive Mode for a room."""
        settings = self._settings(room_id)
        was_enabled = bool(settings["enabled"])
        settings["enabled"] = enabled
        if not enabled:
            settings["upper_override"] = None
        await self._async_save()
        if was_enabled and not enabled:
            room = self._room(room_id)
            if room is not None:
                await room.cancel_overrides()

    async def async_set_lower_temperature(self, room_id, temperature: float) -> None:
        """Use the hub's normal target override for the demand threshold."""
        lower_temperature = min(
            float(temperature), self.upper_temperature(room_id)
        )
        if room := self._room(room_id):
            await room.set_target_temperature(lower_temperature)
            return
        self._settings(room_id)["lower"] = lower_temperature
        await self._async_save()

    async def async_set_upper_temperature(self, room_id, temperature: float) -> None:
        """Set a temporary upper override paired with the native room override."""
        settings = self._settings(room_id)
        settings["upper_override"] = max(
            float(temperature), self.lower_temperature(room_id)
        )
        room = self._room(room_id)
        if room is not None and not room.is_override:
            await room.set_target_temperature(room.current_target_temperature)
        await self._async_save()

    async def async_cancel_upper_override(self, room_id) -> None:
        """Return the upper threshold to its current local schedule slot."""
        settings = self._settings(room_id)
        if settings.get("upper_override") is None:
            return
        settings["upper_override"] = None
        await self._async_save()

    async def async_advance_upper_schedule(self, room_id) -> None:
        """Pair Wiser's Advance Schedule override with the next upper slot."""
        room = self._room(room_id)
        upper = (
            self._scheduled_upper_temperature(room, next_period=True)
            if room is not None
            else None
        )
        if upper is None:
            return
        self._settings(room_id)["upper_override"] = upper
        await self._async_save()

    async def async_update(self) -> None:
        """Apply room demand and external-valve limits after fresh hub data."""
        await self._async_remove_orphaned_upper_schedules()
        if not self.available:
            return

        for room in self.coordinator.wiserhub.rooms.all:
            if not self.is_enabled(room.id):
                continue

            if room.is_boosted:
                await self._async_set_external_valves(room.id, closed=False)
                continue

            if not self.is_active(room):
                continue

            current_temperature = room.current_temperature
            if current_temperature is None:
                continue

            settings = self._settings(room.id)
            if settings.get("upper_override") is not None and not room.is_override:
                settings["upper_override"] = None
                await self._async_save()

            upper_temperature = self.upper_temperature(room.id)
            if current_temperature >= upper_temperature:
                await self._async_set_external_valves(room.id, closed=True)
            else:
                await self._async_set_external_valves(room.id, closed=False)

    async def _async_remove_orphaned_upper_schedules(self) -> None:
        """Remove upper schedules whose native Wiser schedule no longer exists."""
        schedules = getattr(self.coordinator.wiserhub, "schedules", None)
        heating_schedules = getattr(schedules, "heating_schedules", None)
        if heating_schedules is None:
            return
        valid_schedule_ids = {str(schedule.id) for schedule in heating_schedules}
        orphaned_schedule_ids = set(self._upper_schedules) - valid_schedule_ids
        if not orphaned_schedule_ids:
            return
        for schedule_id in orphaned_schedule_ids:
            self._upper_schedules.pop(schedule_id, None)
        await self._async_save()

    async def _async_set_external_valves(self, room_id, *, closed: bool) -> None:
        """Close external TRVs or restore their remembered open targets."""
        settings = self._settings(room_id)
        open_targets = settings["open_targets"]
        storage_changed = False
        for entity_id in self.assigned_entity_ids(room_id):
            registry_entry = er.async_get(self.hass).async_get(entity_id)
            if registry_entry is not None and registry_entry.platform == DOMAIN:
                _LOGGER.warning(
                    "Ignoring Wiser climate entity %s assigned as an external TRV",
                    entity_id,
                )
                continue
            state = self.hass.states.get(entity_id)
            if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                _LOGGER.debug("External passive TRV %s is unavailable", entity_id)
                continue
            current_target = state.attributes.get(ATTR_TEMPERATURE)
            try:
                current_target = (
                    float(current_target) if current_target is not None else None
                )
            except (TypeError, ValueError):
                current_target = None

            maximum_target = state.attributes.get(ATTR_MAX_TEMP)
            try:
                maximum_target = (
                    float(maximum_target) if maximum_target is not None else None
                )
            except (TypeError, ValueError):
                maximum_target = None
            if (
                maximum_target is not None
                and maximum_target <= FROST_PROTECTION_TEMPERATURE
            ):
                maximum_target = None

            if (
                current_target is not None
                and current_target != FROST_PROTECTION_TEMPERATURE
            ):
                if open_targets.get(entity_id) != current_target:
                    open_targets[entity_id] = current_target
                    storage_changed = True

            target = (
                FROST_PROTECTION_TEMPERATURE
                if closed
                else float(
                    maximum_target
                    or open_targets.get(entity_id, DEFAULT_OPEN_TEMPERATURE)
                )
            )
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
                    "Unable to set External Passive target for %s: %s",
                    entity_id,
                    ex,
                )
        if storage_changed:
            await self._async_save()
