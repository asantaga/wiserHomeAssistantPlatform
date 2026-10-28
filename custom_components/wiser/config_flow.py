"""Config Flow for Wiser Rooms.

https://github.com/asantaga/wiserHomeAssistantPlatform
@msp1974

"""

import logging
from typing import Any

from aioWiserHeatAPI.exceptions import (
    WiserHubAuthenticationError,
    WiserHubConnectionError,
    WiserHubRESTError,
)
from aioWiserHeatAPI.wiserhub import WiserAPI
import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    MAJOR_VERSION,
    MINOR_VERSION,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult, section
from homeassistant.helpers import area_registry as ar, entity_registry as er
from homeassistant.helpers.selector import (
    BooleanSelector,
    EntitySelector,
    EntitySelectorConfig,
    SELECTORS,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    Selector,
    make_selector_config_schema,
    selector,
)
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .const import (
    CONF_ADDITIONAL_SENSORS,
    CONF_AUTOMATIONS_HW_AUTO_MODE,
    CONF_AUTOMATIONS_HW_BOOST_MODE,
    CONF_AUTOMATIONS_HW_CLIMATE,
    CONF_AUTOMATIONS_HW_CLIMATE_EXPERIMENTAL,
    CONF_AUTOMATIONS_HW_HEAT_MODE,
    CONF_AUTOMATIONS_HW_SENSOR_ENTITY_ID,
    CONF_AUTOMATIONS_PASSIVE,
    CONF_AUTOMATIONS_PASSIVE_TYPE,
    CONF_PASSIVE_ROOM_STRATEGIES,
    CONF_TEMPERATURE_INCREMENT,
    CONF_AUTOMATIONS_EXTERNAL_ROOM_CONTROL,
    CONF_CONTROL_STRATEGY,
    CONF_EQUIPMENT_SENSORS,
    CONF_EXTERNAL_ROOM_CONTROL_ASSIGNMENTS,
    CONF_EXTERNAL_TEMPERATURE_BOOST_DURATION,
    CONF_EXTERNAL_TEMPERATURE_BOOST_MODE,
    CONF_EXTERNAL_TEMPERATURE_FIXED_BOOST,
    CONF_EXTERNAL_TEMPERATURE_MAX_BOOST,
    CONF_EXTERNAL_TEMPERATURE_PROPORTIONAL_MULTIPLIER,
    CONF_EXTERNAL_TEMPERATURE_SENSOR_ASSIGNMENTS,
    CONF_EXTERNAL_TEMPERATURE_STALE_MINUTES,
    CONF_EXTERNAL_TEMPERATURE_TOLERANCE,
    CONF_HEATING_BOOST_TEMP,
    CONF_HEATING_BOOST_TIME,
    CONF_HOSTNAME,
    CONF_HW_BOOST_TIME,
    CONF_LEGACY_NAMING,
    CONF_OPENTHERM_HOT_WATER_CONTROL,
    CONF_OPENTHERM_HOT_WATER_MANUAL_TEMP,
    CONF_OPENTHERM_HOT_WATER_PRESETS,
    CONF_OPENTHERM_HOT_WATER_SENSOR_ENTITY_ID,
    CONF_OPENTHERM_SENSORS,
    CONF_RESTORE_MANUAL_TEMP_OPTION,
    CONF_SCHEDULE_SETPOINT_ROOMS,
    CONF_SETPOINT_MODE,
    CONF_SHOW_WISER_SIDEBAR,
    CUSTOM_DATA_STORE,
    DEFAULT_BOOST_TEMP,
    DEFAULT_BOOST_TEMP_TIME,
    DEFAULT_PASSIVE_TEMP_INCREMENT,
    DEFAULT_EXTERNAL_TEMPERATURE_BOOST_DURATION,
    DEFAULT_EXTERNAL_TEMPERATURE_FIXED_BOOST,
    DEFAULT_EXTERNAL_TEMPERATURE_MAX_BOOST,
    DEFAULT_EXTERNAL_TEMPERATURE_PROPORTIONAL_MULTIPLIER,
    DEFAULT_EXTERNAL_TEMPERATURE_STALE_MINUTES,
    DEFAULT_EXTERNAL_TEMPERATURE_TOLERANCE,
    CONTROL_STRATEGIES,
    DEFAULT_OPENTHERM_HOT_WATER_MANUAL_TEMP,
    DEFAULT_OPENTHERM_HOT_WATER_PRESET_TEMP,
    DEFAULT_SCAN_INTERVAL,
    DATA,
    DOMAIN,
    EXTERNAL_TEMPERATURE_BOOST_FIXED,
    EXTERNAL_TEMPERATURE_BOOST_PROPORTIONAL,
    WISER_RESTORE_TEMP_DEFAULT_OPTIONS,
    WISER_SETPOINT_MODES,
    HWCycleModes,
    MAX_OPENTHERM_HOT_WATER_PRESETS,
    OPENTHERM_HOT_WATER_DEFAULT_BOOSTS,
)
from .opentherm import (
    OPENTHERM_SENSOR_CATEGORIES,
    OPENTHERM_SENSOR_DEPENDENCIES,
    OPENTHERM_SENSOR_NAMES,
    detected_opentherm_sensor_keys,
    opentherm_sensor_is_enabled,
)
from .opentherm_detection import (
    opentherm_hot_water_control_is_supported,
    opentherm_hot_water_limits,
    opentherm_is_detected,
)
from .helpers import (
    active_wiser_rooms,
    room_has_climate,
    room_supports_external_temperature_feedback,
    room_supports_temperature_control,
)

_LOGGER = logging.getLogger(__name__)


def _external_room_control_duplicate_entities(assignments):
    """Return external climate entities assigned to more than one room."""
    assigned_rooms = {}
    for room_id, entity_ids in assignments.items():
        for entity_id in entity_ids:
            assigned_rooms.setdefault(entity_id, set()).add(room_id)
    return {
        entity_id
        for entity_id, room_ids in assigned_rooms.items()
        if len(room_ids) > 1
    }


def _passive_room_strategies(strategies, assignments, external_control_enabled):
    """Return valid per-room Passive Mode strategies."""
    if not external_control_enabled or not isinstance(strategies, dict):
        return {}
    return {
        str(room_id): strategy
        for room_id, strategy in strategies.items()
        if strategy in CONTROL_STRATEGIES and assignments.get(str(room_id))
    }


def _default_opentherm_hot_water_presets(minimum=35.0, maximum=55.0):
    """Return the default timed hot-water boosts from the original control."""
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


def _validate_opentherm_hot_water_presets(
    value, minimum=35.0, maximum=55.0, *, clamp_temperature=False
):
    """Validate the custom preset selector value."""
    if not isinstance(value, list):
        raise vol.Invalid("Presets must be a list")
    if len(value) > MAX_OPENTHERM_HOT_WATER_PRESETS:
        raise vol.Invalid("Too many presets")

    presets = []
    names = set()
    for item in value:
        if not isinstance(item, dict):
            raise vol.Invalid("Each preset must be an object")
        name = str(item.get("name", "")).strip()
        folded_name = name.casefold()
        if not name or folded_name in {"off", "manual", "auto", "custom"}:
            raise vol.Invalid("Preset name is empty or reserved")
        if folded_name in names:
            raise vol.Invalid("Preset names must be unique")
        try:
            temperature = float(item.get("temperature"))
            duration = int(item.get("duration_minutes", 0))
        except (TypeError, ValueError) as err:
            raise vol.Invalid(
                "Preset temperature and duration must be numbers"
            ) from err
        icon = str(item.get("icon", "")).strip()
        if clamp_temperature:
            temperature = min(max(temperature, minimum), maximum)
        if not minimum <= temperature <= maximum or not 0 <= duration <= 999:
            raise vol.Invalid("Preset temperature or duration is out of range")
        presets.append(
            {
                "name": name,
                "icon": icon,
                "temperature": temperature,
                "duration_minutes": duration,
            }
        )
        names.add(folded_name)
    return presets


def _validate_external_temperature_calculation(value):
    """Validate the live external-temperature calculation selector."""
    if not isinstance(value, dict):
        raise vol.Invalid("Boost calculation must be an object")
    mode = value.get("mode")
    if mode not in {
        EXTERNAL_TEMPERATURE_BOOST_FIXED,
        EXTERNAL_TEMPERATURE_BOOST_PROPORTIONAL,
    }:
        raise vol.Invalid("Invalid boost calculation")
    try:
        fixed_boost = float(
            value.get("fixed_boost", DEFAULT_EXTERNAL_TEMPERATURE_FIXED_BOOST)
        )
        proportional_multiplier = float(
            value.get(
                "proportional_multiplier",
                DEFAULT_EXTERNAL_TEMPERATURE_PROPORTIONAL_MULTIPLIER,
            )
        )
        maximum_boost = float(
            value.get("maximum_boost", DEFAULT_EXTERNAL_TEMPERATURE_MAX_BOOST)
        )
    except (TypeError, ValueError) as err:
        raise vol.Invalid("Boost calculation values must be numbers") from err
    if not 0.5 <= fixed_boost <= 5:
        raise vol.Invalid("Fixed boost must be between 0.5 and 5")
    if not 0.5 <= proportional_multiplier <= 5:
        raise vol.Invalid("Proportional multiplier must be between 0.5 and 5")
    if not 0.5 <= maximum_boost <= 5:
        raise vol.Invalid("Maximum boost must be between 0.5 and 5")
    return {
        "mode": mode,
        "fixed_boost": fixed_boost,
        "proportional_multiplier": proportional_multiplier,
        "maximum_boost": maximum_boost,
    }


@SELECTORS.register("opentherm_presets_v2")
class OpenThermPresetsSelector(Selector):
    """Render the preset editor supplied by the Wiser frontend module."""

    # Keep the selector name versioned. Home Assistant registers custom
    # elements once per browser session, so reusing the old name would leave a
    # previously loaded implementation in place.
    selector_type = "opentherm_presets_v2"
    CONFIG_SCHEMA = make_selector_config_schema(
        {
            vol.Optional("minimum", default=35.0): vol.Coerce(float),
            vol.Optional("maximum", default=55.0): vol.Coerce(float),
        }
    )

    def __call__(self, data):
        return _validate_opentherm_hot_water_presets(
            data,
            float(self.config.get("minimum", 35.0)),
            float(self.config.get("maximum", 55.0)),
        )


@SELECTORS.register("external_temperature_calculation_v1")
class ExternalTemperatureCalculationSelector(Selector):
    """Render a live fixed/proportional boost calculation editor."""

    selector_type = "external_temperature_calculation_v1"
    CONFIG_SCHEMA = make_selector_config_schema({})

    def __call__(self, data):
        return _validate_external_temperature_calculation(data)


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=80): int,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_input(hass: HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    wiserhub = WiserAPI(
        host=data[CONF_HOST],
        port=data[CONF_PORT],
        secret=data[CONF_PASSWORD],
        extra_config_file=hass.config.config_dir + CUSTOM_DATA_STORE,
        enable_automations=False,
    )

    await wiserhub.read_hub_data()
    wiser_id = wiserhub.system.name
    return {"title": wiser_id, "unique_id": get_unique_id(wiser_id)}


def get_unique_id(wiser_id: str):
    """Return unique id."""
    return str(f"{DOMAIN}-{wiser_id}")


def _configured_hub_entry(
    hass: HomeAssistant,
    discovered_name: str,
    host: str | None = None,
    hostname: str | None = None,
):
    """Return an existing entry matching a discovered Wiser hub."""
    discovered_folded = discovered_name.casefold()
    unique_id_prefix = f"{DOMAIN}-"
    discovered_addresses = {
        str(value).casefold().rstrip(".")
        for value in (host, hostname)
        if value
    }

    for entry in hass.config_entries.async_entries(DOMAIN):
        configured_addresses = {
            str(value).casefold().rstrip(".")
            for value in (
                entry.data.get(CONF_HOST),
                entry.data.get(CONF_HOSTNAME),
            )
            if value
        }
        if discovered_addresses & configured_addresses:
            return entry

        configured_names = {
            entry.data.get(CONF_NAME),
            entry.title,
        }
        if (
            entry.unique_id
            and entry.unique_id.startswith(unique_id_prefix)
        ):
            configured_names.add(entry.unique_id.removeprefix(unique_id_prefix))

        for configured_name in filter(None, configured_names):
            configured_name = str(configured_name)
            configured_folded = configured_name.casefold()
            if discovered_folded == configured_folded:
                return entry
            suffix_prefix = f"{configured_folded}-"
            suffix = discovered_name[len(configured_name) + 1 :]
            if discovered_folded.startswith(suffix_prefix) and suffix.isdigit():
                return entry

    return None


@config_entries.HANDLERS.register(DOMAIN)
class WiserFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """WiserFlowHandler configuration method.

    The schema version of the entries that it creates
    Home Assistant will call your migrate method if the version changes
    (this is not implemented yet)
    """

    VERSION = 1
    MINOR_VERSION = 9

    def __init__(self) -> None:
        """Initialize the wiser flow."""
        self.discovery_info = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return flow options."""
        return WiserOptionsFlowHandler()

    async def async_step_user(self, user_input=None):
        """Handle a Wiser Heat Hub config flow start.

        Manage device specific parameters.
        """
        errors = {}
        if user_input is not None:
            try:
                validated = await validate_input(self.hass, user_input)
            except WiserHubAuthenticationError:
                errors["base"] = "auth_failure"
            except WiserHubConnectionError:
                errors["base"] = "timeout_error"
            except (
                WiserHubRESTError,
                RuntimeError,
            ) as ex:
                errors["base"] = "unknown"
                _LOGGER.debug(ex)

            if "base" not in errors:
                await self.async_set_unique_id(validated["unique_id"])
                self._abort_if_unique_id_configured()

                # Add hub name to config
                user_input[CONF_NAME] = validated["title"]

                return self.async_create_entry(
                    title=validated["title"],
                    data=user_input,
                    options={
                        CONF_LEGACY_NAMING: (MAJOR_VERSION, MINOR_VERSION) < (2026, 8)
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.discovery_info or DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle zeroconf discovery."""
        if not discovery_info.name.startswith("WiserHeat"):
            return self.async_abort(reason="not_wiser_hub")
        host = discovery_info.host
        port = discovery_info.port
        zctype = discovery_info.type
        discovered_name = discovery_info.name.replace(f".{zctype}", "")
        discovered_hostname = discovery_info.hostname.replace(".local.", ".local")
        configured_entry = _configured_hub_entry(
            self.hass,
            discovered_name,
            host,
            discovered_hostname,
        )
        if configured_entry is not None:
            await self.async_set_unique_id(
                configured_entry.unique_id or get_unique_id(discovered_name)
            )
            return self.async_abort(reason="already_configured")

        name = discovered_name

        await self.async_set_unique_id(get_unique_id(name))
        self._abort_if_unique_id_configured()

        self.context.update({"title_placeholders": {"name": name}})

        self.discovery_info.update(
            {
                CONF_HOST: host,
                CONF_PORT: port,
                CONF_HOSTNAME: discovered_hostname,
                CONF_NAME: name,
            }
        )
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a confirmation flow initiated by zeroconf."""
        errors = {}
        if user_input is not None:
            try:
                validated = await validate_input(self.hass, user_input)
            except WiserHubAuthenticationError:
                _LOGGER.warning("Authentication failure connecting to Wiser Hub")
                errors["base"] = "auth_failure"
            except WiserHubConnectionError:
                _LOGGER.warning("Connection timout error connecting to Wiser Hub")
                errors["base"] = "timeout_error_discovery"
            except (
                WiserHubRESTError,
                RuntimeError,
            ) as ex:
                _LOGGER.error("Unknown error connecting to Wiser Hub")
                _LOGGER.debug(ex)
                errors["base"] = "unknown"

            if "base" not in errors:
                # Add hub name to config
                user_input[CONF_NAME] = validated["title"]
                return self.async_create_entry(
                    title=validated["title"],
                    data=user_input,
                    options={
                        CONF_LEGACY_NAMING: (MAJOR_VERSION, MINOR_VERSION) < (2026, 8)
                    },
                )

        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={
                "name": self.discovery_info[CONF_NAME],
                "hostname": self.discovery_info[CONF_HOSTNAME],
                "ip_address": self.discovery_info[CONF_HOST],
                "port": self.discovery_info[CONF_PORT],
            },
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST, default=self.discovery_info[CONF_HOST]
                    ): str,
                    vol.Optional(
                        CONF_PORT, default=self.discovery_info[CONF_PORT]
                    ): int,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )


class WiserOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for wiser hub."""

    def _opentherm(self):
        """Return the loaded entry's OpenTherm model, if available."""
        entry_data = self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id)
        if not entry_data:
            return None
        opentherm = getattr(entry_data[DATA].wiserhub.system, "opentherm", None)
        return (
            opentherm
            if opentherm_is_detected(self.config_entry, opentherm)
            else None
        )

    def _equipment_available(self):
        """Return whether the loaded entry has equipment data available."""
        entry_data = self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id)
        if not entry_data:
            return False
        devices = entry_data[DATA].wiserhub.devices

        def all_devices(collection_name):
            collection = getattr(devices, collection_name, None)
            return getattr(collection, "all", ())

        return any(
            getattr(device, "equipment", None) is not None
            for collection_name in (
                "smartplugs",
                "power_tags",
                "power_tags_c",
                "heating_actuators",
                "evse",
            )
            for device in all_devices(collection_name)
        )

    def _rooms_without_climate(self):
        """Return loaded Wiser rooms that do not create climate entities."""
        entry_data = self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id)
        if not entry_data:
            return []
        return [
            room
            for room in active_wiser_rooms(entry_data[DATA])
            if not room_has_climate(room)
        ]

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        menu_options = [
            "main_params",
            "automation_params",
            "external_room_control",
            "ui_options",
        ]
        if self._opentherm() is not None:
            menu_options.append("opentherm")
        if self._equipment_available() or self.config_entry.options.get(
            CONF_EQUIPMENT_SENSORS, False
        ):
            menu_options.append("equipment_sensors")
        return self.async_show_menu(
            step_id="init",
            menu_options=menu_options,
        )

    def _wiser_rooms(self):
        """Return Wiser rooms available to the loaded config entry."""
        entry_data = self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id)
        if not entry_data:
            return []
        return active_wiser_rooms(entry_data[DATA])

    def _external_room_control_room_fields(self):
        """Return unique form field labels mapped to Wiser room IDs."""
        rooms = sorted(
            self._wiser_rooms(),
            key=lambda room: (room.name.casefold(), room.name, str(room.id)),
        )
        name_counts = {
            room.name: sum(other.name == room.name for other in rooms)
            for room in rooms
        }
        return {
            (
                room.name
                if name_counts[room.name] == 1
                else f"{room.name} ({room.id})"
            ): str(room.id)
            for room in rooms
        }

    def _external_room_control_entities_by_room(self):
        """Return selectable external climates and temperature entities."""
        entity_registry = er.async_get(self.hass)
        area_registry = ar.async_get(self.hass)
        entries = list(entity_registry.entities.values())
        entities_by_room = {}
        for room in self._wiser_rooms():
            area = area_registry.async_get_area_by_name(room.name)
            entities_by_room[str(room.id)] = sorted(
                entry.entity_id
                for entry in entries
                if area is not None
                and entry.platform != DOMAIN
                and er.async_get_effective_area_id(self.hass, entry) == area.id
                and (
                    entry.entity_id.startswith("climate.")
                    or (
                        entry.entity_id.startswith("sensor.")
                        and getattr(
                            entry,
                            "original_device_class",
                            getattr(entry, "device_class", None),
                        )
                        == "temperature"
                    )
                )
            )
        return entities_by_room

    def _external_room_control_form_rooms(self):
        """Return temperature-controlled rooms and their external entities."""
        entities_by_room = self._external_room_control_entities_by_room()
        temperature_control_room_ids = {
            str(room.id)
            for room in self._wiser_rooms()
            if room_supports_temperature_control(room)
        }
        room_fields = {
            field_name: room_id
            for field_name, room_id in self._external_room_control_room_fields().items()
            if room_id in temperature_control_room_ids
        }
        return room_fields, entities_by_room

    def _external_temperature_sensor_room_ids(self):
        """Return TRV rooms without a native Wiser temperature sensor."""
        return {
            str(room.id)
            for room in self._wiser_rooms()
            if room_supports_external_temperature_feedback(room)
        }

    def _save_external_room_control_options(self, external_options):
        """Save External Room Control while keeping Passive strategies valid."""
        assignments = external_options.get(
            CONF_EXTERNAL_ROOM_CONTROL_ASSIGNMENTS, {}
        )
        sensor_assignments = external_options.get(
            CONF_EXTERNAL_TEMPERATURE_SENSOR_ASSIGNMENTS, {}
        )
        external_options[CONF_AUTOMATIONS_EXTERNAL_ROOM_CONTROL] = bool(
            assignments or sensor_assignments
        )
        options = dict(self.config_entry.options)
        options[CONF_AUTOMATIONS_EXTERNAL_ROOM_CONTROL] = external_options
        saved_passive_options = options.get(CONF_AUTOMATIONS_PASSIVE, {})
        passive_options = (
            dict(saved_passive_options)
            if isinstance(saved_passive_options, dict)
            else {}
        )
        passive_options.pop(CONF_AUTOMATIONS_PASSIVE_TYPE, None)
        passive_options.pop(CONF_CONTROL_STRATEGY, None)
        passive_options[CONF_PASSIVE_ROOM_STRATEGIES] = _passive_room_strategies(
            passive_options.get(CONF_PASSIVE_ROOM_STRATEGIES, {}),
            assignments,
            bool(assignments),
        )
        options[CONF_AUTOMATIONS_PASSIVE] = passive_options
        return self.async_create_entry(data=options)

    async def async_step_external_room_control(self, user_input=None):
        """Choose the External Room Control configuration to edit."""
        return self.async_show_menu(
            step_id="external_room_control",
            menu_options=[
                "external_climate_devices",
                "external_temperature_sensors",
            ],
        )

    async def async_step_external_climate_devices(self, user_input=None):
        """Assign external climate devices to Wiser rooms."""
        room_fields, entities_by_room = self._external_room_control_form_rooms()
        external_options = dict(
            self.config_entry.options.get(
                CONF_AUTOMATIONS_EXTERNAL_ROOM_CONTROL, {}
            )
        )
        assignments = {
            str(room_id): list(entity_ids)
            for room_id, entity_ids in external_options.get(
                CONF_EXTERNAL_ROOM_CONTROL_ASSIGNMENTS, {}
            ).items()
        }
        sensor_assignments = dict(
            external_options.get(
                CONF_EXTERNAL_TEMPERATURE_SENSOR_ASSIGNMENTS, {}
            )
        )
        saved_boost_mode = external_options.get(
            CONF_EXTERNAL_TEMPERATURE_BOOST_MODE,
            EXTERNAL_TEMPERATURE_BOOST_PROPORTIONAL,
        )
        errors = {}
        if user_input is not None:
            registry = er.async_get(self.hass)
            submitted_assignments = {}
            for field_name, room_id in room_fields.items():
                entity_ids = list(user_input.get(field_name, []))
                if any(
                    (entry := registry.async_get(entity_id)) is not None
                    and entry.platform == DOMAIN
                    for entity_id in entity_ids
                ):
                    errors["base"] = "external_climate_must_not_be_wiser"
                if entity_ids:
                    submitted_assignments[room_id] = entity_ids
            if _external_room_control_duplicate_entities(submitted_assignments):
                errors["base"] = "external_climate_duplicate_assignment"
            if not errors:
                for room_id in submitted_assignments:
                    sensor_assignments.pop(room_id, None)
                external_options[CONF_EXTERNAL_ROOM_CONTROL_ASSIGNMENTS] = (
                    submitted_assignments
                )
                external_options[CONF_EXTERNAL_TEMPERATURE_SENSOR_ASSIGNMENTS] = (
                    sensor_assignments
                )
                return self._save_external_room_control_options(external_options)

        data_schema = {}
        for field_name, room_id in room_fields.items():
            climate_entities = [
                entity_id
                for entity_id in entities_by_room.get(room_id, [])
                if entity_id.startswith("climate.")
            ]
            data_schema[
                vol.Optional(field_name, default=assignments.get(room_id, []))
            ] = EntitySelector(
                EntitySelectorConfig(
                    domain="climate",
                    multiple=True,
                    include_entities=climate_entities,
                )
            )
        return self.async_show_form(
            step_id="external_climate_devices",
            errors=errors,
            data_schema=vol.Schema(data_schema),
        )

    async def async_step_external_temperature_sensors(self, user_input=None):
        """Assign external temperature sensors and configure feedback."""
        room_fields, entities_by_room = self._external_room_control_form_rooms()
        eligible_room_ids = self._external_temperature_sensor_room_ids()
        room_fields = {
            field_name: room_id
            for field_name, room_id in room_fields.items()
            if room_id in eligible_room_ids
        }
        if not room_fields:
            return self.async_abort(reason="no_external_temperature_rooms")
        external_options = dict(
            self.config_entry.options.get(
                CONF_AUTOMATIONS_EXTERNAL_ROOM_CONTROL, {}
            )
        )
        assignments = {
            str(room_id): list(entity_ids)
            for room_id, entity_ids in external_options.get(
                CONF_EXTERNAL_ROOM_CONTROL_ASSIGNMENTS, {}
            ).items()
        }
        sensor_assignments = dict(
            external_options.get(
                CONF_EXTERNAL_TEMPERATURE_SENSOR_ASSIGNMENTS, {}
            )
        )
        errors = {}
        if user_input is not None:
            registry = er.async_get(self.hass)
            submitted_sensors = {}
            submitted_options = dict(user_input)
            calculation = submitted_options.pop(
                CONF_EXTERNAL_TEMPERATURE_BOOST_MODE
            )
            submitted_options[CONF_EXTERNAL_TEMPERATURE_BOOST_MODE] = (
                calculation["mode"]
            )
            submitted_options[CONF_EXTERNAL_TEMPERATURE_FIXED_BOOST] = (
                calculation["fixed_boost"]
            )
            submitted_options[
                CONF_EXTERNAL_TEMPERATURE_PROPORTIONAL_MULTIPLIER
            ] = calculation["proportional_multiplier"]
            submitted_options[CONF_EXTERNAL_TEMPERATURE_MAX_BOOST] = (
                calculation["maximum_boost"]
            )
            for field_name, room_id in room_fields.items():
                entity_id = submitted_options.pop(field_name, None)
                if not entity_id:
                    continue
                entry = registry.async_get(entity_id)
                if entry is not None and entry.platform == DOMAIN:
                    errors["base"] = "external_sensor_must_not_be_wiser"
                submitted_sensors[room_id] = entity_id
            if len(set(submitted_sensors.values())) != len(submitted_sensors):
                errors["base"] = "external_sensor_duplicate_assignment"
            if not errors:
                for room_id in submitted_sensors:
                    assignments.pop(room_id, None)
                external_options.update(submitted_options)
                external_options[CONF_EXTERNAL_ROOM_CONTROL_ASSIGNMENTS] = assignments
                external_options[CONF_EXTERNAL_TEMPERATURE_SENSOR_ASSIGNMENTS] = (
                    submitted_sensors
                )
                return self._save_external_room_control_options(external_options)

        data_schema = {}
        for field_name, room_id in room_fields.items():
            temperature_entities = [
                entity_id
                for entity_id in entities_by_room.get(room_id, [])
                if not entity_id.startswith("climate.")
            ]
            data_schema[
                vol.Optional(
                    field_name,
                    default=sensor_assignments.get(room_id),
                )
            ] = EntitySelector(
                EntitySelectorConfig(
                    domain="sensor",
                    device_class="temperature",
                    multiple=False,
                    include_entities=temperature_entities,
                )
            )
        data_schema.update(
            self._external_temperature_common_schema(external_options)
        )
        return self.async_show_form(
            step_id="external_temperature_sensors",
            errors=errors,
            data_schema=vol.Schema(data_schema),
        )

    async def async_step_opentherm(self, user_input=None):
        """Choose an OpenTherm feature to configure."""
        if self._opentherm() is None:
            return self.async_abort(reason="opentherm_not_available")
        menu_options = ["opentherm_sensors"]
        if opentherm_hot_water_control_is_supported(
            self.config_entry, self._opentherm()
        ):
            menu_options.insert(0, "opentherm_hot_water_control")
        return self.async_show_menu(
            step_id="opentherm",
            menu_options=menu_options,
        )

    async def async_step_opentherm_hot_water_control(self, user_input=None):
        """Configure Home Assistant control of the OpenTherm DHW setpoint."""
        opentherm = self._opentherm()
        if opentherm is None or not opentherm_hot_water_control_is_supported(
            self.config_entry, opentherm
        ):
            return self.async_abort(reason="opentherm_not_available")
        minimum, maximum = opentherm_hot_water_limits(opentherm)
        try:
            manual_default = float(
                self.config_entry.options.get(
                    CONF_OPENTHERM_HOT_WATER_MANUAL_TEMP,
                    DEFAULT_OPENTHERM_HOT_WATER_MANUAL_TEMP,
                )
            )
        except (TypeError, ValueError):
            manual_default = DEFAULT_OPENTHERM_HOT_WATER_MANUAL_TEMP
        manual_default = min(max(manual_default, minimum), maximum)
        try:
            preset_default = _validate_opentherm_hot_water_presets(
                self.config_entry.options.get(
                    CONF_OPENTHERM_HOT_WATER_PRESETS,
                    _default_opentherm_hot_water_presets(minimum, maximum),
                ),
                minimum,
                maximum,
                clamp_temperature=True,
            )
        except vol.Invalid:
            preset_default = _default_opentherm_hot_water_presets(
                minimum, maximum
            )
        errors = {}
        if user_input is not None:
            try:
                user_input[CONF_OPENTHERM_HOT_WATER_PRESETS] = (
                    _validate_opentherm_hot_water_presets(
                        user_input.get(CONF_OPENTHERM_HOT_WATER_PRESETS, []),
                        minimum,
                        maximum,
                    )
                )
            except vol.Invalid:
                errors["base"] = "invalid_hot_water_presets"
            else:
                options = self.config_entry.options | user_input
                if not user_input.get(
                    CONF_OPENTHERM_HOT_WATER_SENSOR_ENTITY_ID
                ):
                    options.pop(
                        CONF_OPENTHERM_HOT_WATER_SENSOR_ENTITY_ID, None
                    )
                # Remove the prototype option now that Off follows the minimum
                # domestic-hot-water temperature reported by OpenTherm.
                options.pop("opentherm_hot_water_off_temperature", None)
                return self.async_create_entry(data=options)
        return self.async_show_form(
            step_id="opentherm_hot_water_control",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_OPENTHERM_HOT_WATER_CONTROL,
                        default=self.config_entry.options.get(
                            CONF_OPENTHERM_HOT_WATER_CONTROL, False
                        ),
                    ): BooleanSelector(),
                    vol.Optional(
                        CONF_OPENTHERM_HOT_WATER_MANUAL_TEMP,
                        default=manual_default,
                    ): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=minimum, max=maximum),
                    ),
                    vol.Optional(
                        CONF_OPENTHERM_HOT_WATER_SENSOR_ENTITY_ID,
                        description={
                            "suggested_value": self.config_entry.options.get(
                                CONF_OPENTHERM_HOT_WATER_SENSOR_ENTITY_ID
                            )
                        },
                    ): EntitySelector(
                        EntitySelectorConfig(
                            domain="sensor",
                            device_class="temperature",
                            multiple=False,
                        )
                    ),
                    vol.Optional(
                        CONF_OPENTHERM_HOT_WATER_PRESETS,
                        default=preset_default,
                    ): OpenThermPresetsSelector(
                        {"minimum": minimum, "maximum": maximum}
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_equipment_sensors(self, user_input=None):
        """Configure detailed equipment data sensors."""
        if not self._equipment_available() and not self.config_entry.options.get(
            CONF_EQUIPMENT_SENSORS, False
        ):
            return self.async_abort(reason="equipment_not_available")
        if user_input is not None:
            return self.async_create_entry(
                data=self.config_entry.options | user_input
            )
        return self.async_show_form(
            step_id="equipment_sensors",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_EQUIPMENT_SENSORS,
                        default=self.config_entry.options.get(
                            CONF_EQUIPMENT_SENSORS, False
                        ),
                    ): BooleanSelector(),
                }
            ),
        )

    async def async_step_ui_options(self, user_input=None):
        """Configure Wiser UI options, including legacy naming and sidebar panels."""
        if user_input is not None:
            return self.async_create_entry(
                data=self.config_entry.options | user_input
            )

        return self.async_show_form(
            step_id="ui_options",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_LEGACY_NAMING,
                        default=self.config_entry.options.get(
                            CONF_LEGACY_NAMING, True
                        ),
                    ): BooleanSelector(),
                    vol.Optional(
                        CONF_SHOW_WISER_SIDEBAR,
                        default=self.config_entry.options.get(
                            CONF_SHOW_WISER_SIDEBAR,
                            True,
                        ),
                    ): BooleanSelector(),
                }
            ),
        )

    async def async_step_opentherm_sensors(self, user_input=None):
        """Choose an OpenTherm sensor category."""
        opentherm = self._opentherm()
        if opentherm is None:
            return self.async_abort(reason="opentherm_not_available")

        detected_keys = set(detected_opentherm_sensor_keys(opentherm))
        menu_options = [
            category
            for category, keys in OPENTHERM_SENSOR_CATEGORIES.items()
            if detected_keys.intersection(keys)
        ]
        return self.async_show_menu(
            step_id="opentherm_sensors",
            menu_options=menu_options,
        )

    def _opentherm_sensor_form(self, step_id, user_input):
        """Build and save a category of OpenTherm sensor toggles."""
        opentherm = self._opentherm()
        if opentherm is None:
            return self.async_abort(reason="opentherm_not_available")

        detected_keys = detected_opentherm_sensor_keys(opentherm)
        category_keys = set(OPENTHERM_SENSOR_CATEGORIES[step_id])
        if user_input is not None:
            existing = self.config_entry.options.get(CONF_OPENTHERM_SENSORS)
            configured = {
                key: opentherm_sensor_is_enabled(existing, key)
                for key in OPENTHERM_SENSOR_NAMES
            }
            configured.update(user_input)
            # Derived readings automatically enable their source entities, so
            # selecting one always produces a usable entity.
            for derived_key, dependencies in OPENTHERM_SENSOR_DEPENDENCIES.items():
                if configured.get(derived_key):
                    configured.update(dict.fromkeys(dependencies, True))
            options = self.config_entry.options | {
                CONF_OPENTHERM_SENSORS: configured
            }
            return self.async_create_entry(data=options)

        configured = self.config_entry.options.get(CONF_OPENTHERM_SENSORS)
        sorted_keys = sorted(
            category_keys.intersection(detected_keys),
            key=OPENTHERM_SENSOR_NAMES.__getitem__,
        )
        data_schema = {
            vol.Optional(
                key,
                default=opentherm_sensor_is_enabled(configured, key),
            ): BooleanSelector()
            for key in sorted_keys
        }
        return self.async_show_form(
            step_id=step_id,
            data_schema=vol.Schema(data_schema),
        )

    async def async_step_opentherm_readings(self, user_input=None):
        """Configure OpenTherm reading sensors."""
        return self._opentherm_sensor_form("opentherm_readings", user_input)

    async def async_step_opentherm_central_heating(self, user_input=None):
        """Configure OpenTherm central-heating sensors."""
        return self._opentherm_sensor_form(
            "opentherm_central_heating", user_input
        )

    async def async_step_opentherm_hot_water(self, user_input=None):
        """Configure OpenTherm hot-water sensors."""
        return self._opentherm_sensor_form("opentherm_hot_water", user_input)

    async def async_step_opentherm_status(self, user_input=None):
        """Configure OpenTherm status sensors."""
        return self._opentherm_sensor_form("opentherm_status", user_input)

    async def async_step_main_params(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            if user_input[CONF_HOST]:
                data = {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                    CONF_PASSWORD: self.config_entry.data[CONF_PASSWORD],
                    CONF_NAME: self.config_entry.data[CONF_NAME],
                }
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=data
                )
            options = self.config_entry.options | user_input
            options.pop(CONF_HOST)
            options.pop(CONF_PORT)
            return self.async_create_entry(data=options)

        data_schema = {
            vol.Required(CONF_HOST, default=self.config_entry.data[CONF_HOST]): str,
            vol.Optional(
                CONF_PORT, default=self.config_entry.data.get(CONF_PORT, 80)
            ): int,
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                ),
            ): int,
            vol.Optional(
                CONF_HEATING_BOOST_TEMP,
                default=self.config_entry.options.get(
                    CONF_HEATING_BOOST_TEMP, DEFAULT_BOOST_TEMP
                ),
            ): int,
            vol.Optional(
                CONF_HEATING_BOOST_TIME,
                default=self.config_entry.options.get(
                    CONF_HEATING_BOOST_TIME, DEFAULT_BOOST_TEMP_TIME
                ),
            ): int,
            vol.Optional(
                CONF_HW_BOOST_TIME,
                default=self.config_entry.options.get(
                    CONF_HW_BOOST_TIME, DEFAULT_BOOST_TEMP_TIME
                ),
            ): int,
            vol.Optional(
                CONF_SETPOINT_MODE,
                default=self.config_entry.options.get(
                    CONF_SETPOINT_MODE, list(WISER_SETPOINT_MODES.values())[0]
                ),
            ): selector(
                {
                    "select": {
                        "options": list(WISER_SETPOINT_MODES.values()),
                        "mode": SelectSelectorMode.DROPDOWN,
                    }
                }
            ),
            vol.Optional(
                CONF_RESTORE_MANUAL_TEMP_OPTION,
                default=self.config_entry.options.get(
                    CONF_RESTORE_MANUAL_TEMP_OPTION,
                    WISER_RESTORE_TEMP_DEFAULT_OPTIONS[0],
                ),
            ): selector(
                {
                    "select": {
                        "options": WISER_RESTORE_TEMP_DEFAULT_OPTIONS,
                        "mode": SelectSelectorMode.DROPDOWN,
                    }
                }
            ),
        }
        return self.async_show_form(
            step_id="main_params", data_schema=vol.Schema(data_schema)
        )

    def _external_temperature_common_schema(self, external_options):
        """Return common settings for external temperature feedback."""
        return {
            vol.Optional(
                CONF_EXTERNAL_TEMPERATURE_TOLERANCE,
                default=external_options.get(
                    CONF_EXTERNAL_TEMPERATURE_TOLERANCE,
                    DEFAULT_EXTERNAL_TEMPERATURE_TOLERANCE,
                ),
            ): selector(
                {
                    "number": {
                        "min": 0,
                        "max": 5,
                        "step": 0.1,
                        "unit_of_measurement": UnitOfTemperature.CELSIUS,
                        "mode": "box",
                    }
                }
            ),
            vol.Optional(
                CONF_EXTERNAL_TEMPERATURE_BOOST_DURATION,
                default=external_options.get(
                    CONF_EXTERNAL_TEMPERATURE_BOOST_DURATION,
                    DEFAULT_EXTERNAL_TEMPERATURE_BOOST_DURATION,
                ),
            ): selector(
                {
                    "number": {
                        "min": 10,
                        "max": 180,
                        "step": 5,
                        "unit_of_measurement": "min",
                        "mode": "box",
                    }
                }
            ),
            vol.Required(
                CONF_EXTERNAL_TEMPERATURE_BOOST_MODE,
                default={
                    "mode": external_options.get(
                        CONF_EXTERNAL_TEMPERATURE_BOOST_MODE,
                        EXTERNAL_TEMPERATURE_BOOST_PROPORTIONAL,
                    ),
                    "fixed_boost": external_options.get(
                        CONF_EXTERNAL_TEMPERATURE_FIXED_BOOST,
                        DEFAULT_EXTERNAL_TEMPERATURE_FIXED_BOOST,
                    ),
                    "proportional_multiplier": external_options.get(
                        CONF_EXTERNAL_TEMPERATURE_PROPORTIONAL_MULTIPLIER,
                        DEFAULT_EXTERNAL_TEMPERATURE_PROPORTIONAL_MULTIPLIER,
                    ),
                    "maximum_boost": external_options.get(
                        CONF_EXTERNAL_TEMPERATURE_MAX_BOOST,
                        DEFAULT_EXTERNAL_TEMPERATURE_MAX_BOOST,
                    ),
                },
            ): ExternalTemperatureCalculationSelector({}),
            vol.Optional(
                CONF_EXTERNAL_TEMPERATURE_STALE_MINUTES,
                default=external_options.get(
                    CONF_EXTERNAL_TEMPERATURE_STALE_MINUTES,
                    DEFAULT_EXTERNAL_TEMPERATURE_STALE_MINUTES,
                ),
            ): selector(
                {
                    "number": {
                        "min": 5,
                        "max": 180,
                        "step": 5,
                        "unit_of_measurement": "min",
                        "mode": "box",
                    }
                }
            ),
        }

    async def async_step_automation_params(self, user_input=None):
        """Automation options."""
        saved_external_options = dict(
            self.config_entry.options.get(CONF_AUTOMATIONS_EXTERNAL_ROOM_CONTROL, {})
        )
        saved_assignments = {
            str(room_id): list(entity_ids)
            for room_id, entity_ids in saved_external_options.get(
                CONF_EXTERNAL_ROOM_CONTROL_ASSIGNMENTS, {}
            ).items()
        }
        saved_passive_options = self.config_entry.options.get(
            CONF_AUTOMATIONS_PASSIVE, {}
        )
        if not isinstance(saved_passive_options, dict):
            saved_passive_options = {}
        saved_passive_options = dict(saved_passive_options)
        saved_room_strategies = _passive_room_strategies(
            saved_passive_options.get(CONF_PASSIVE_ROOM_STRATEGIES, {}),
            saved_assignments,
            bool(saved_assignments),
        )
        if user_input is not None and CONF_AUTOMATIONS_PASSIVE in user_input:
            user_input = dict(user_input)
            submitted_passive = dict(user_input[CONF_AUTOMATIONS_PASSIVE])
            submitted_passive.pop(CONF_AUTOMATIONS_PASSIVE_TYPE, None)
            submitted_passive.pop(CONF_CONTROL_STRATEGY, None)
            submitted_passive[CONF_PASSIVE_ROOM_STRATEGIES] = (
                _passive_room_strategies(
                    saved_room_strategies,
                    saved_assignments,
                    bool(saved_assignments),
                )
            )
            user_input[CONF_AUTOMATIONS_PASSIVE] = submitted_passive
        if user_input is not None:
            return self.async_create_entry(
                data=self.config_entry.options | user_input
            )

        errors = {}
        options = self.config_entry.options
        additional_sensor_options = options.get(CONF_ADDITIONAL_SENSORS, {})
        if not isinstance(additional_sensor_options, dict):
            additional_sensor_options = {}

        passive_options = dict(saved_passive_options)
        if user_input is not None:
            passive_options = dict(
                user_input.get(CONF_AUTOMATIONS_PASSIVE, passive_options)
            )
        passive_enabled = passive_options.get(CONF_AUTOMATIONS_PASSIVE, False)
        passive_section_schema = {
            vol.Optional(
                CONF_AUTOMATIONS_PASSIVE,
                default=passive_enabled,
            ): bool,
        }
        passive_section_schema[
            vol.Optional(
                CONF_TEMPERATURE_INCREMENT,
                default=passive_options.get(
                    CONF_TEMPERATURE_INCREMENT,
                    DEFAULT_PASSIVE_TEMP_INCREMENT,
                ),
            )
        ] = selector(
            {
                "number": {
                    "min": 0.5,
                    "max": 20,
                    "step": 0.5,
                    "unit_of_measurement": UnitOfTemperature.CELSIUS,
                    "mode": "box",
                }
            }
        )
        data_schema = {
            vol.Required(CONF_AUTOMATIONS_PASSIVE): section(
                vol.Schema(passive_section_schema),
                {"collapsed": True},
            ),
            vol.Required(CONF_AUTOMATIONS_HW_CLIMATE): section(
                vol.Schema(
                    {
                        vol.Optional(
                            CONF_AUTOMATIONS_HW_CLIMATE,
                            default=options.get(CONF_AUTOMATIONS_HW_CLIMATE, {}).get(
                                CONF_AUTOMATIONS_HW_CLIMATE, False
                            ),
                        ): bool,
                        vol.Optional(
                            CONF_AUTOMATIONS_HW_CLIMATE_EXPERIMENTAL,
                            default=options.get(CONF_AUTOMATIONS_HW_CLIMATE, {}).get(
                                CONF_AUTOMATIONS_HW_CLIMATE_EXPERIMENTAL, False
                            ),
                        ): bool,
                        vol.Optional(
                            CONF_AUTOMATIONS_HW_SENSOR_ENTITY_ID,
                            default=options.get(CONF_AUTOMATIONS_HW_CLIMATE, {}).get(
                                CONF_AUTOMATIONS_HW_SENSOR_ENTITY_ID, "sensor.no_sensor"
                            ),
                        ): EntitySelector(
                            EntitySelectorConfig(
                                domain=["sensor", "number", "input_number"],
                                device_class="temperature",
                                multiple=False,
                            )
                        ),
                        vol.Optional(
                            CONF_AUTOMATIONS_HW_AUTO_MODE,
                            default=options.get(CONF_AUTOMATIONS_HW_CLIMATE, {}).get(
                                CONF_AUTOMATIONS_HW_AUTO_MODE,
                                HWCycleModes.CONTINUOUS,
                            ),
                        ): selector(
                            {
                                "select": {
                                    "options": list(HWCycleModes),
                                    "mode": SelectSelectorMode.DROPDOWN,
                                }
                            }
                        ),
                        vol.Optional(
                            CONF_AUTOMATIONS_HW_HEAT_MODE,
                            default=options.get(CONF_AUTOMATIONS_HW_CLIMATE, {}).get(
                                CONF_AUTOMATIONS_HW_HEAT_MODE,
                                HWCycleModes.CONTINUOUS,
                            ),
                        ): selector(
                            {
                                "select": {
                                    "options": list(HWCycleModes),
                                    "mode": SelectSelectorMode.DROPDOWN,
                                }
                            }
                        ),
                        vol.Optional(
                            CONF_AUTOMATIONS_HW_BOOST_MODE,
                            default=options.get(CONF_AUTOMATIONS_HW_CLIMATE, {}).get(
                                CONF_AUTOMATIONS_HW_BOOST_MODE,
                                HWCycleModes.CONTINUOUS,
                            ),
                        ): selector(
                            {
                                "select": {
                                    "options": list(HWCycleModes),
                                    "mode": SelectSelectorMode.DROPDOWN,
                                }
                            }
                        ),
                    }
                ),
                {"collapsed": True},
            ),
            vol.Required(CONF_ADDITIONAL_SENSORS): section(
                vol.Schema(
                    {
                        vol.Optional(
                            CONF_SCHEDULE_SETPOINT_ROOMS,
                            default=[
                                str(room_id)
                                for room_id in additional_sensor_options.get(
                                    CONF_SCHEDULE_SETPOINT_ROOMS, []
                                )
                            ],
                        ): selector(
                            {
                                "select": {
                                    "options": [
                                        {"value": str(room.id), "label": room.name}
                                        for room in self._rooms_without_climate()
                                    ],
                                    "multiple": True,
                                    "mode": SelectSelectorMode.DROPDOWN,
                                }
                            }
                        ),
                    }
                ),
                {"collapsed": True},
            ),
        }
        return self.async_show_form(
            step_id="automation_params",
            errors=errors,
            data_schema=vol.Schema(data_schema),
        )

class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""


class UnknownError(exceptions.HomeAssistantError):
    """Error to indicate there is an unknown error."""
