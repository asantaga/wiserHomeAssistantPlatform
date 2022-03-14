"""
Constants  for Wiser Platform.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
DOMAIN = "wiser"
DATA_WISER_CONFIG = "wiser_config"

VERSION = "3.0.23"
WISER_PLATFORMS = ["climate", "sensor", "switch", "select", "button", "number"]
DATA = "data"
UPDATE_TRACK = "update_track"
UPDATE_LISTENER = "update_listener"

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

# Custom Attributes
ATTR_TIME_PERIOD = "time_period"

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
    "SERVICE_COPY_HEATING_SCHEDULE": "copy_heating_schedule",
    "SERVICE_COPY_ONOFF_SCHEDULE": "copy_onoff_schedule",
    "SERVICE_COPY_SCHEDULE": "copy_schedule",
    "SERVICE_GET_SCHEDULE": "get_schedule",
    "SERVICE_SET_SCHEDULE": "set_schedule",
    "SERVICE_GET_HEATING_SCHEDULE": "get_heating_schedule",
    "SERVICE_GET_ONOFF_SCHEDULE": "get_onoff_schedule",
    "SERVICE_SET_HEATING_SCHEDULE": "set_heating_schedule",
    "SERVICE_SET_ONOFF_SCHEDULE": "set_onoff_schedule",
    "SERVICE_SET_SMARTPLUG_MODE": "set_smartplug_mode",
    "SERVICE_SET_HOTWATER_MODE": "set_hotwater_mode",  
}

WISER_BOOST_PRESETS = {
    "Boost 30m": 30,
    "Boost 1h": 60,
    "Boost 2h": 120,
    "Boost 3h": 180
}
