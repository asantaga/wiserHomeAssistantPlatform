"""
Constants  for Wiser Platform.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
DOMAIN = "wiser"
DATA_WISER_CONFIG = "wiser_config"
URL_BASE = "/wiser"
WISER_CARD_FILENAMES = ["wiser-schedule-card.js", "wiser-zigbee-card.js"]

VERSION = "3.2.1"
WISER_PLATFORMS = [
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
MIN_SCAN_INTERVAL = 30

# Hub
MANUFACTURER = "Drayton Wiser"
ENTITY_PREFIX = "Wiser"
ROOM = "Room"

# Notifications
NOTIFICATION_ID = "wiser_notification"
NOTIFICATION_TITLE = "Wiser Component Setup"

# Default Values
DEFAULT_BOOST_TEMP = 2
DEFAULT_BOOST_TEMP_TIME = 60
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_SETPOINT_MODE = "normal"

# Setpoint Modes
SETPOINT_MODE_BOOST = "boost"
SETPOINT_MODE_BOOST_AUTO = "boost auto mode only"

# Custom Configs
CONF_HEATING_BOOST_TEMP = "heating_boost_temp"
CONF_HEATING_BOOST_TIME = "heating_boost_time"
CONF_HW_BOOST_TIME = "hotwater_boost_time"
CONF_SETPOINT_MODE = "setpoint_mode"
CONF_MOMENTS = "moments"
CONF_LTS_SENSORS = "lts_sensors"
CONF_HOSTNAME = "hostname"
CONF_RESTORE_MANUAL_TEMP_OPTION = "restore_manual_temp_option"

# Custom Attributes
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
}

WISER_BOOST_PRESETS = {
    "Boost 30m": 30,
    "Boost 1h": 60,
    "Boost 2h": 120,
    "Boost 3h": 180,
}

WISER_SETPOINT_MODES = {
    "Normal": "normal",
    "Boost": "boost",
    "BoostAuto": "boost in auto mode only",
}

WISER_RESTORE_TEMP_DEFAULT_OPTIONS = ["Current", "Scheduled", "Minimum"]
