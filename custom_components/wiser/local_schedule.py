"""Home Assistant-managed schedules for Wiser features not scheduled by the hub."""

from __future__ import annotations

from copy import deepcopy
from datetime import timedelta
from time import strptime

from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import DOMAIN

LOCAL_HOT_WATER_SCHEDULE_ID = -1000
LOCAL_HOT_WATER_SCHEDULE_NAME = "OpenTherm Hot Water"
LOCAL_HOT_WATER_SCHEDULE_TYPE = "HotWater"
LOCAL_SCHEDULE_STORAGE_VERSION = 1
WEEKDAYS = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


def _schedule_preset_options(presets, minimum, maximum):
    """Return schedule-safe presets, excluding temporary boosts."""
    options = []
    seen_names = set()
    for preset in presets or []:
        if not isinstance(preset, dict) or preset.get("duration_minutes", 0):
            continue
        name = str(preset.get("name", "")).strip()
        try:
            temperature = float(preset.get("temperature"))
        except (TypeError, ValueError):
            continue
        folded_name = name.casefold()
        if (
            not name
            or folded_name in seen_names
            or not minimum <= temperature <= maximum
        ):
            continue
        seen_names.add(folded_name)
        options.append(
            {
                "name": name,
                "icon": str(preset.get("icon") or "mdi:water"),
                "temperature": temperature,
            }
        )
    return options


def _default_schedule(
    minimum, maximum=55.0, default_temperature=45.0, presets=None
):
    """Return a useful split-day schedule with the minimum between periods."""
    scheduled_temperature = min(
        maximum,
        max(minimum, default_temperature),
    )
    return {
        "Id": LOCAL_HOT_WATER_SCHEDULE_ID,
        "Name": LOCAL_HOT_WATER_SCHEDULE_NAME,
        "Type": LOCAL_HOT_WATER_SCHEDULE_TYPE,
        "SubType": LOCAL_HOT_WATER_SCHEDULE_TYPE,
        "MinSetpoint": minimum,
        "MaxSetpoint": maximum,
        "PresetOptions": _schedule_preset_options(
            presets, minimum, maximum
        ),
        "Assignments": [
            {
                "id": LOCAL_HOT_WATER_SCHEDULE_ID,
                "name": LOCAL_HOT_WATER_SCHEDULE_NAME,
            }
        ],
        "ScheduleData": [
            {
                "day": day,
                "slots": [
                    {
                        "Time": "00:00",
                        "Setpoint": f"{minimum:g}",
                    },
                    {
                        "Time": "06:00",
                        "Setpoint": f"{scheduled_temperature:g}",
                    },
                    {
                        "Time": "09:00",
                        "Setpoint": f"{minimum:g}",
                    },
                    {
                        "Time": "17:00",
                        "Setpoint": f"{scheduled_temperature:g}",
                    },
                    {
                        "Time": "22:00",
                        "Setpoint": f"{minimum:g}",
                    },
                ],
            }
            for day in WEEKDAYS
        ],
    }


def _validated_schedule(
    schedule,
    minimum,
    maximum,
    presets=None,
    *,
    replace_unknown_presets=False,
):
    """Return a normalized schedule or raise ValueError."""
    if not isinstance(schedule, dict):
        raise ValueError("Schedule must be an object")
    days = schedule.get("ScheduleData")
    if not isinstance(days, list):
        raise ValueError("ScheduleData must be a list")

    preset_options = _schedule_preset_options(presets, minimum, maximum)
    preset_names = {
        option["name"].casefold(): option["name"]
        for option in preset_options
    }
    normalized_days = []
    seen_days = set()
    for day_data in days:
        if not isinstance(day_data, dict) or day_data.get("day") not in WEEKDAYS:
            raise ValueError("Schedule contains an invalid day")
        day = day_data["day"]
        if day in seen_days:
            raise ValueError(f"Schedule contains duplicate {day} data")
        seen_days.add(day)
        slots = day_data.get("slots")
        if not isinstance(slots, list):
            raise ValueError(f"Schedule slots for {day} must be a list")
        normalized_slots = []
        seen_times = set()
        for slot in slots:
            if not isinstance(slot, dict):
                raise ValueError(f"Schedule slot for {day} must be an object")
            value = str(slot.get("Time", ""))
            try:
                parsed_time = strptime(value, "%H:%M")
            except ValueError as err:
                raise ValueError(f"Invalid schedule time {value!r}") from err
            raw_setpoint = slot.get("Setpoint")
            raw_text = str(raw_setpoint).strip()
            preset_name = preset_names.get(raw_text.casefold())
            if preset_name is not None:
                normalized_setpoint = preset_name
            else:
                try:
                    setpoint = (
                        minimum if raw_text.casefold() == "off" else float(raw_text)
                    )
                except ValueError as err:
                    if replace_unknown_presets:
                        setpoint = minimum
                    else:
                        raise ValueError(
                            f"Unknown hot-water preset {raw_text!r}"
                        ) from err
                if not minimum <= setpoint <= maximum:
                    raise ValueError(
                        f"Schedule temperature must be between {minimum:g} and "
                        f"{maximum:g} °C"
                    )
                normalized_setpoint = f"{setpoint:g}"
            canonical_time = f"{parsed_time.tm_hour:02}:{parsed_time.tm_min:02}"
            if canonical_time in seen_times:
                raise ValueError(f"Schedule contains duplicate {day} time")
            seen_times.add(canonical_time)
            normalized_slots.append(
                {
                    "Time": canonical_time,
                    "Setpoint": normalized_setpoint,
                }
            )
        normalized_days.append(
            {
                "day": day,
                "slots": sorted(normalized_slots, key=lambda slot: slot["Time"]),
            }
        )

    if not any(day["slots"] for day in normalized_days):
        raise ValueError("Schedule must contain at least one time slot")
    normalized_by_day = {day["day"]: day for day in normalized_days}
    name = str(schedule.get("Name") or LOCAL_HOT_WATER_SCHEDULE_NAME)
    return {
        "Id": LOCAL_HOT_WATER_SCHEDULE_ID,
        "Name": name,
        "Type": LOCAL_HOT_WATER_SCHEDULE_TYPE,
        "SubType": LOCAL_HOT_WATER_SCHEDULE_TYPE,
        "MinSetpoint": minimum,
        "MaxSetpoint": maximum,
        "PresetOptions": preset_options,
        "Assignments": [
            {
                "id": LOCAL_HOT_WATER_SCHEDULE_ID,
                "name": name,
            }
        ],
        "ScheduleData": [
            normalized_by_day.get(day, {"day": day, "slots": []})
            for day in WEEKDAYS
        ],
    }


def _schedule_position(schedule, now):
    """Return current setpoint and next transition for a local datetime."""
    preset_temperatures = {
        option["name"].casefold(): float(option["temperature"])
        for option in schedule.get("PresetOptions", [])
    }
    transitions = []
    days = {day["day"]: day["slots"] for day in schedule["ScheduleData"]}
    for day_index, day in enumerate(WEEKDAYS):
        for slot in days.get(day, []):
            hour, minute = (int(part) for part in slot["Time"].split(":"))
            raw_setpoint = str(slot["Setpoint"]).strip()
            temperature = preset_temperatures.get(raw_setpoint.casefold())
            if temperature is None:
                temperature = float(raw_setpoint)
            transitions.append(
                (day_index * 1440 + hour * 60 + minute, temperature)
            )
    transitions.sort()
    if not transitions:
        return None, None

    current_minute = now.weekday() * 1440 + now.hour * 60 + now.minute
    previous = [
        transition for transition in transitions if transition[0] <= current_minute
    ]
    current = previous[-1] if previous else transitions[-1]
    future = [
        transition
        for transition in transitions
        if transition[0] > current_minute
    ]
    next_transition = future[0] if future else transitions[0]
    days_ahead = (next_transition[0] - current_minute) % (7 * 1440)
    if days_ahead == 0:
        days_ahead = 7 * 1440
    next_datetime = (now + timedelta(minutes=days_ahead)).replace(
        second=0, microsecond=0
    )
    return current[1], next_datetime


class OpenThermHotWaterSchedule:
    """Persist and evaluate the integration-owned OpenTherm DHW schedule."""

    def __init__(
        self,
        hass,
        entry_id,
        minimum=35.0,
        maximum=55.0,
        default_temperature=45.0,
        presets=None,
    ):
        self._hass = hass
        self._store = Store(
            hass,
            LOCAL_SCHEDULE_STORAGE_VERSION,
            f"{DOMAIN}.{entry_id}.opentherm_hot_water_schedule",
        )
        self._default = _default_schedule(
            minimum,
            maximum,
            default_temperature,
            presets,
        )
        self._minimum = minimum
        self._maximum = maximum
        self._presets = presets or []
        self._schedule = deepcopy(self._default)
        self._listeners = set()

    async def async_load(self):
        """Load and validate saved data, retaining a safe default if corrupt."""
        saved = await self._store.async_load()
        if saved is None:
            return
        try:
            self._schedule = _validated_schedule(
                saved,
                self._minimum,
                self._maximum,
                self._presets,
                replace_unknown_presets=True,
            )
        except (TypeError, ValueError):
            self._schedule = deepcopy(self._default)

    @property
    def ws_schedule_data(self):
        """Return data in the existing Wiser schedule-card format."""
        return deepcopy(self._schedule)

    @property
    def name(self):
        return self._schedule["Name"]

    def current(self, now=None):
        """Return current setpoint and next transition."""
        return _schedule_position(self._schedule, now or dt_util.now())

    def async_add_listener(self, listener):
        """Subscribe an entity to saved schedule changes."""
        self._listeners.add(listener)
        return lambda: self._listeners.discard(listener)

    async def async_save(self, schedule):
        """Validate, persist and publish schedule changes."""
        self._schedule = _validated_schedule(
            schedule,
            self._minimum,
            self._maximum,
            self._presets,
        )
        await self._store.async_save(self._schedule)
        for listener in tuple(self._listeners):
            listener()

    async def async_set_name(self, name):
        """Rename the local schedule."""
        schedule = self.ws_schedule_data
        schedule["Name"] = name
        await self.async_save(schedule)
