import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "wiser"
DATA_WISER_CONFIG = "wiser_config"
VERSION = "1.3.1"
WISER_PLATFORMS = ["climate", "sensor", "switch"]

#Battery
BATTERY_FULL = 31
MIN_BATTERY_LEVEL = 21

#Hub
HUBNAME = "Wiser Heat Hub"
MANUFACTURER = "Drayton WIser"
ROOM = "Room"

#Notifications
NOTIFICATION_ID = "wiser_notification"
NOTIFICATION_TITLE = "Wiser Component Setup"

#Default Values
DEFAULT_BOOST_TEMP = 2
DEFAULT_BOOST_TEMP_TIME = 60

#Custom Configs
CONF_BOOST_TEMP = "boost_temp"
CONF_BOOST_TEMP_TIME = "boost_time"


WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]
WEEKENDS = ["saturday", "sunday"]
SPECIALDAYS = ["weekdays", "weekends"]

WISER_SWITCHES = {
    "Valve Protection": "ValveProtectionEnabled",
    "Eco Mode": "EcoModeEnabled",
    "Away Mode Affects Hot Water": "AwayModeAffectsHotWater",
    "Comfort Mode": "ComfortModeEnabled",
    "Away Mode": "OverrideType",
}

SIGNAL_STRENGTH_ICONS = {
    "NoSignal": "mdi:wifi-strength-alert-outline",
    "Poor": "mdi:wifi-strength-1",
    "Medium": "mdi:wifi-strength-2",
    "Good": "mdi:wifi-strength-3",
    "VeryGood": "mdi:wifi-strength-4",
}
