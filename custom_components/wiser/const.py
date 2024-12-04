"""
Constants  for Wiser Platform.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""

from enum import StrEnum


VERSION = "3.4.14"
DOMAIN = "wiser"
DATA_WISER_CONFIG = "wiser_config"
URL_BASE = "/wiser"

WISER_CARDS = [
    {
        "name": "Wiser Schedule Card",
        "filename": "wiser-schedule-card.js",
        "version": "1.3.3",
    },
    {
        "name": "Wiser Zigbee Card",
        "filename": "wiser-zigbee-card.js",
        "version": "2.1.2",
    },
]

WISER_PLATFORMS = [
    "binary_sensor",
    "climate",
    "sensor",
    "switch",
    "select",
    "button",
    "number",
    "light",
    "cover",
]
DATA = "data"
UPDATE_TRACK = "update_track"
UPDATE_LISTENER = "update_listener"
MIN_SCAN_INTERVAL = 10
CUSTOM_DATA_STORE = "/.storage/wiser_custom_data"

# Hub
MANUFACTURER = "Drayton Wiser"
MANUFACTURER_SCHNEIDER = "Schneider Electric"
ENTITY_PREFIX = "Wiser"
ROOM = "Room"
HOT_WATER = "Hot Water"

# Notifications
NOTIFICATION_ID = "wiser_notification"
NOTIFICATION_TITLE = "Wiser Component Setup"


class HWCycleModes(StrEnum):
    """HW cycle modes for HW climate automation."""

    CONTINUOUS = "Continuous"
    ONCE = "Once"


# Default Values
DEFAULT_BOOST_TEMP = 2
DEFAULT_BOOST_TEMP_TIME = 60
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_SETPOINT_MODE = "normal"
DEFAULT_PASSIVE_TEMP_INCREMENT = 0.5
DEFAULT_HW_AUTO_MODE = HWCycleModes.CONTINUOUS
DEFAULT_HW_HEAT_MODE = HWCycleModes.CONTINUOUS
DEFAULT_HW_BOOST_MODE = HWCycleModes.CONTINUOUS
HW_CLIMATE_MIN_TEMP = 40
HW_CLIMATE_MAX_TEMP = 80

# Setpoint Modes
SETPOINT_MODE_BOOST = "boost"
SETPOINT_MODE_BOOST_AUTO = "boost auto mode only"

# Custom Configs
CONF_AUTOMATIONS_PASSIVE = "automations_passive_mode"
CONF_AUTOMATIONS_PASSIVE_TEMP_INCREMENT = "passive_mode_temperature_increments"
CONF_HEATING_BOOST_TEMP = "heating_boost_temp"
CONF_HEATING_BOOST_TIME = "heating_boost_time"
CONF_HW_BOOST_TIME = "hotwater_boost_time"
CONF_SETPOINT_MODE = "setpoint_mode"
CONF_HOSTNAME = "hostname"
CONF_RESTORE_MANUAL_TEMP_OPTION = "restore_manual_temp_option"
CONF_AUTOMATIONS_HW_CLIMATE = "automations_hw_climate"
CONF_AUTOMATIONS_HW_AUTO_MODE = "hotwater_auto_mode"
CONF_AUTOMATIONS_HW_CLIMATE = "hotwater_climate"
CONF_AUTOMATIONS_HW_HEAT_MODE = "hotwater_heat_mode"
CONF_AUTOMATIONS_HW_BOOST_MODE = "hotwater_boost_mode"
CONF_AUTOMATIONS_HW_SENSOR_ENTITY_ID = "hotwater_sensor_entity_id"
CONF_DEPRECATED_HW_TARGET_TEMP = "hotwater_target_temperature"

# Custom Attributes
ATTR_OPENTHERM_ENDPOINT = "endpoint"
ATTR_OPENTHERM_PARAM = "parameter"
ATTR_OPENTHERM_PARAM_VALUE = "parameter_value"
ATTR_HUB = "hub"
ATTR_TIME_PERIOD = "time_period"
ATTR_FILENAME = "filename"
ATTR_TO_ENTITY_ID = "to_entity_id"
ATTR_SCHEDULE_ID = "schedule_id"
ATTR_SCHEDULE_NAME = "schedule_name"
ATTR_SCHEDULE = "schedule"


# Signal icons
SIGNAL_STRENGTH_ICONS = {
    "Online": "mdi:wifi-strength-4",
    "NoSignal": "mdi:wifi-strength-alert-outline",
    "Poor": "mdi:wifi-strength-1",
    "Medium": "mdi:wifi-strength-2",
    "Good": "mdi:wifi-strength-3",
    "VeryGood": "mdi:wifi-strength-4",
}

WISER_SERVICES = {
    "SERVICE_BOOST_HEATING": "boost_heating",
    "SERVICE_BOOST_HOTWATER": "boost_hotwater",
    "SERVICE_ASSIGN_SCHEDULE": "assign_schedule",
    "SERVICE_COPY_SCHEDULE": "copy_schedule",
    "SERVICE_GET_SCHEDULE": "get_schedule",
    "SERVICE_SET_SCHEDULE": "set_schedule",
    "SERVICE_SET_SCHEDULE_FROM_DATA": "set_schedule_from_string",
    "SERVICE_SET_DEVICE_MODE": "set_device_mode",
    "SERVICE_SEND_OPENTHERM_COMMAND": "set_opentherm_parameter",
}

WISER_BOOST_PRESETS = {
    "Boost 30m": 30,
    "Boost 1h": 60,
    "Boost 2h": 120,
    "Boost 3h": 180,
}

WISER_SETPOINT_MODES = {
    "Normal": "Normal",
    "Boost": "Boost",
    "BoostAuto": "Boost in auto mode only",
}

WISER_RESTORE_TEMP_DEFAULT_OPTIONS = ["Current", "Scheduled", "Minimum"]
