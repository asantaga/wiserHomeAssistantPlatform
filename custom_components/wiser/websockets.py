import logging
import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import callback
from homeassistant.components.websocket_api import (
    async_register_command,
    ActiveConnection,
)
from aioWiserHeatAPI.exceptions import WiserScheduleError
from aioWiserHeatAPI.schedule import WiserScheduleTypeEnum
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DATA, DOMAIN, OPENTHERM_HOT_WATER_SCHEDULE
from .local_schedule import (
    LOCAL_HOT_WATER_SCHEDULE_ID,
    LOCAL_HOT_WATER_SCHEDULE_TYPE,
)
from .frontend.wiser_sidebar import (
    save_panel_config,
    save_wiser_panel_tabs,
)
from .helpers import active_wiser_rooms
from .zigbee import build_zigbee_network_data

_LOGGER = logging.getLogger(__name__)

POWER_NOTIFICATION_TYPES = {
    "under": "under_power_notification",
    "over": "over_power_notification",
}


def build_power_notification_data(wiserhub):
    """Return equipment power notifications in a frontend-friendly format."""
    output = []
    equipment_collection = getattr(wiserhub.devices, "equipments", None)
    for equipment in getattr(equipment_collection, "all", []):
        notifications = {}
        for notification_type, attribute in POWER_NOTIFICATION_TYPES.items():
            notification = getattr(equipment, attribute, None)
            notifications[notification_type] = (
                {
                    "period_mins": notification.period_mins,
                    "limit": notification.limit,
                    "enabled": notification.enabled,
                }
                if notification is not None
                else None
            )
        output.append(
            {
                "equipment_id": equipment.id,
                "device_id": equipment.device_id,
                "device_type": equipment.device_type,
                "name": equipment.equipment_name,
                "family": equipment.equipment_family,
                "monitored": equipment.monitored,
                "smart_supported": equipment.smart_supported,
                "notifications": notifications,
            }
        )
    return output


def build_native_notification_data(wiserhub):
    """Return all locally exposed native Wiser notification settings."""
    devices = wiserhub.devices
    smoke_alarms = []
    smoke_collection = getattr(devices, "smokealarms", None)
    for alarm in getattr(smoke_collection, "all", []):
        if not getattr(alarm, "notification_supported", False):
            continue
        smoke_alarms.append(
            {
                "device_id": alarm.id,
                "name": alarm.name,
                "device_type": alarm.device_type,
                "enabled": alarm.notification_enabled,
                "supervision_notify": alarm.supervision_notify,
                "restore_notify": alarm.restore_notify,
            }
        )

    sensors = []
    sensor_collection = getattr(devices, "binary_sensor", None)
    for sensor in getattr(sensor_collection, "all", []):
        enabled = getattr(sensor, "enable_notification", None)
        if enabled is None:
            continue
        sensors.append(
            {
                "device_id": sensor.id,
                "name": sensor.name,
                "device_type": sensor.device_type,
                "sensor_type": sensor.type,
                "enabled": enabled,
            }
        )

    raw_data = getattr(wiserhub, "raw_hub_data", {}) or {}
    domain = raw_data.get("Domain", {}) if isinstance(raw_data, dict) else {}
    automation_data = domain.get("Automation", []) if isinstance(domain, dict) else []
    automation_collection = getattr(wiserhub, "automations", None)
    automations = [
        {
            "automation_id": automation.get("id"),
            "name": automation.get("Name"),
            "enabled": automation.get("Enabled", False),
            "writable": callable(
                getattr(
                    automation_collection.get_by_id(automation.get("id"))
                    if automation_collection
                    else None,
                    "set_enabled",
                    None,
                )
            ),
        }
        for automation in automation_data
        if isinstance(automation, dict) and "Enabled" in automation
    ]

    return {
        "equipment": build_power_notification_data(wiserhub),
        "smoke_alarms": smoke_alarms,
        "sensors": sensors,
        "automations": automations,
    }


@callback
@websocket_api.websocket_command(
    {
        vol.Required("type"): "wiser_updated",
    }
)
@websocket_api.async_response
async def handle_subscribe_updates(hass, connection, msg):
    """subscribe listeners when frontend connection is opened"""

    @callback
    async def handle_event_wiser_update(hub: str):
        """pass data to frontend when backend changes"""
        connection.send_message(
            {
                "id": msg["id"],
                "type": "event",
                "event": {
                    "event": "wiser_updated",
                    "hub": hub,
                },  # data to pass with event
            }
        )

    remove_listener = async_dispatcher_connect(
        hass, "wiser_update_received", handle_event_wiser_update
    )

    def unsubscribe_listeners():
        """unsubscribe listeners when frontend connection closes"""
        remove_listener()

    connection.subscriptions[msg["id"]] = unsubscribe_listeners
    connection.send_result(msg["id"])


async def async_register_websockets(hass, data):
    def get_entry_for_hub(hub: str):
        """Return the integration runtime data for the requested hub."""
        for entry_id, entry_data in hass.data[DOMAIN].items():
            if not hub or entry_data[DATA].wiserhub.system.name == hub:
                return entry_data
        return None

    def get_hub_name(config_entry_id):
        try:
            api = hass.data[DOMAIN][config_entry_id][DATA]
            return api.wiserhub.system.name
        except:
            return None

    def get_api_for_hub(hub: str):
        entry_data = get_entry_for_hub(hub)
        return entry_data[DATA] if entry_data else None

    def get_local_hot_water_schedule(hub: str):
        """Return this hub's integration-owned hot-water schedule, if enabled."""
        entry_data = get_entry_for_hub(hub)
        return entry_data.get(OPENTHERM_HOT_WATER_SCHEDULE) if entry_data else None

    def get_entity_from_entity_id(entity: str):
        """Get wiser entity from entity_id"""
        domain = entity.split(".", 1)[0]
        entity_comp = hass.data.get("entity_components", {}).get(domain)
        if entity_comp:
            return entity_comp.get_entity(entity)
        return None

    @callback
    @websocket_api.websocket_command({
        vol.Required("type"): "wiser/panel/configure",
        vol.Required("panel_id"): str,
        vol.Required("configs"): {str: dict},
    })
    @websocket_api.require_admin
    def websocket_configure_panel(hass, connection, msg):
        """Save settings for any panel supplied by the frontend registry."""
        try:
            save_panel_config(hass, msg["panel_id"], msg["configs"])
        except ValueError as err:
            connection.send_error(msg["id"], "invalid_config", str(err))
            return
        connection.send_result(msg["id"])

    @callback
    @websocket_api.websocket_command({
        vol.Required("type"): "wiser/panel/configure_tabs",
        vol.Required("tabs"): [
            {
                vol.Required("id"): str,
                vol.Required("title"): str,
            }
        ],
    })
    @websocket_api.require_admin
    def websocket_configure_wiser_panel_tabs(hass, connection, msg):
        """Save the unified Wiser panel tab order and custom titles."""
        try:
            save_wiser_panel_tabs(hass, msg["tabs"])
        except ValueError as err:
            connection.send_error(msg["id"], "invalid_config", str(err))
            return
        connection.send_result(msg["id"])

    # Get Hubs
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/hubs".format(DOMAIN),
        }
    )
    @websocket_api.async_response
    async def websocket_get_hubs(hass, connection: ActiveConnection, msg: dict) -> None:
        """Publish schedules list data."""
        output = []
        for entry in hass.data[DOMAIN]:
            output.append(get_hub_name(entry))

        # output = output.sort()
        connection.send_result(msg["id"], output)

    # Get sunrise and sunset times
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/suntimes".format(DOMAIN),
            vol.Optional("hub"): str,
        }
    )
    @websocket_api.async_response
    async def websocket_get_suntimes(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Publish schedules list data."""
        d = get_api_for_hub(msg.get("hub"))
        if d:
            sunrises = []
            for key, value in d.wiserhub.system.sunrise_times.items():
                sunrises.append({"day": key, "time": value})
            sunsets = []
            for key, value in d.wiserhub.system.sunset_times.items():
                sunsets.append({"day": key, "time": value})

            output = {"Sunrises": sunrises, "Sunsets": sunsets}
            connection.send_result(msg["id"], output)
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")

    # Get schedules list
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedules".format(DOMAIN),
            vol.Optional("hub"): str,
            vol.Optional("schedule_type"): str,
        }
    )
    @websocket_api.async_response
    async def websocket_get_schedules(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Publish schedules list data."""
        output = []
        schedule_type = msg.get("schedule_type", "")
        d = get_api_for_hub(msg.get("hub"))
        if d:
            schedules = d.wiserhub.schedules.all
            for schedule in schedules:
                if schedule.schedule_type == schedule_type or not schedule_type:
                    output.append(
                        {
                            "Id": schedule.id,
                            "Type": schedule.schedule_type,
                            "Name": schedule.name,
                            "Assignments": len(schedule.assignment_ids),
                        }
                    )

            local_schedule = get_local_hot_water_schedule(msg.get("hub"))
            if local_schedule and (
                not schedule_type
                or schedule_type.lower()
                == LOCAL_HOT_WATER_SCHEDULE_TYPE.lower()
            ):
                output.append(
                    {
                        "Id": LOCAL_HOT_WATER_SCHEDULE_ID,
                        "Type": LOCAL_HOT_WATER_SCHEDULE_TYPE,
                        "Name": local_schedule.name,
                        "Assignments": 1,
                    }
                )

            connection.send_result(msg["id"], sorted(output, key=lambda n: n["Name"]))
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")

    # Get schedules types for hub
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedules/types".format(DOMAIN),
            vol.Optional("hub"): str,
        }
    )
    @websocket_api.async_response
    async def websocket_get_schedule_types(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Publish supported schedule type list data."""
        output = ["Heating"]
        d = get_api_for_hub(msg.get("hub"))
        if d:
            for cap, value in d.wiserhub.system.capabilities.all.items():
                if cap == "SmartPlug" and value == True:
                    output.append("OnOff")
                if cap == "Light" and value == True:
                    output.append("Lighting")
                if cap == "Shutter" and value == True:
                    output.append("Shutters")

            connection.send_result(msg["id"], output)
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")

    # Get schedule by id
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedule/id".format(DOMAIN),
            vol.Optional("hub"): str,
            vol.Required("schedule_type"): str,
            vol.Required("schedule_id"): vol.Coerce(int),
        }
    )
    @websocket_api.async_response
    async def websocket_get_schedule_by_id(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Publish schedule data."""
        schedule_type = str(msg.get("schedule_type")).lower()
        schedule_id = msg.get("schedule_id")
        d = get_api_for_hub(msg.get("hub"))
        if d:
            local_schedule = get_local_hot_water_schedule(msg.get("hub"))
            if (
                schedule_id == LOCAL_HOT_WATER_SCHEDULE_ID
                and schedule_type == LOCAL_HOT_WATER_SCHEDULE_TYPE.lower()
                and local_schedule
            ):
                connection.send_result(
                    msg["id"], local_schedule.ws_schedule_data
                )
                return
            schedule_type_enum = WiserScheduleTypeEnum[schedule_type]
            schedule = d.wiserhub.schedules.get_by_id(schedule_type_enum, schedule_id)
            if schedule:
                schedule = schedule.ws_schedule_data
                connection.send_result(msg["id"], schedule)
            else:
                connection.send_error(
                    msg["id"],
                    "wiser error",
                    f"Unable to get schedule.  Schedule with id {schedule_id} of type {schedule_type} not found",
                )
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")

    # Get list of rooms
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/rooms".format(DOMAIN),
            vol.Optional("hub"): str,
        }
    )
    @websocket_api.async_response
    async def websocket_get_rooms(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Publish room list"""
        d = get_api_for_hub(msg.get("hub"))
        if d:
            rooms = active_wiser_rooms(d)
            room_list = []
            for room in rooms:
                room_list.append({"Id": room.id, "Name": room.name})
            connection.send_result(
                msg["id"], sorted(room_list, key=lambda n: n["Name"])
            )
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")

    # Get list of devices
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/devices".format(DOMAIN),
            vol.Required("device_type"): str,
            vol.Optional("hub"): str,
        }
    )
    @websocket_api.async_response
    async def websocket_get_devices(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Publish device list"""
        d = get_api_for_hub(msg.get("hub"))
        devices = None
        if d:
            if msg["device_type"].lower() == "onoff":
                devices = d.wiserhub.devices.smartplugs.all
            if msg["device_type"].lower() == "shutters":
                devices = d.wiserhub.devices.shutters.all
            if msg["device_type"].lower() == "lighting":
                devices = d.wiserhub.devices.lights.all

            device_list = []
            if devices:
                for device in devices:
                    device_list.append(
                        {"Id": device.device_type_id, "Name": device.name}
                    )
                connection.send_result(
                    msg["id"], sorted(device_list, key=lambda n: n["Name"])
                )
            else:
                connection.send_result(msg["id"], [])
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")

    # Assign schedule
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedule/assign".format(DOMAIN),
            vol.Optional("hub"): str,
            vol.Required("schedule_type"): str,
            vol.Required("schedule_id"): int,
            vol.Required("entity_id"): str,
            vol.Optional("remove"): bool,
        }
    )
    @websocket_api.async_response
    async def websocket_assign_schedule(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Assign schedule to room/device"""
        remove = msg.get("remove", False)
        schedule_type = str(msg.get("schedule_type")).lower()
        if schedule_type in ["lighting", "shutters"]:
            schedule_type = "level"
        schedule_id = msg.get("schedule_id")
        d = get_api_for_hub(msg.get("hub"))
        if d:
            if schedule_id == LOCAL_HOT_WATER_SCHEDULE_ID:
                connection.send_error(
                    msg["id"],
                    "wiser error",
                    "The integration-owned OpenTherm hot-water schedule cannot be assigned",
                )
                return
            schedule_type_enum = WiserScheduleTypeEnum[schedule_type]
            schedule = d.wiserhub.schedules.get_by_id(schedule_type_enum, schedule_id)
            if schedule:
                if not remove:
                    await schedule.assign_schedule(int(msg["entity_id"]))
                else:
                    await schedule.unassign_schedule(int(msg["entity_id"]))
                await d.async_refresh()
            connection.send_result(msg["id"], "success")
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")

    # Create schedule
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedule/create".format(DOMAIN),
            vol.Optional("hub"): str,
            vol.Required("schedule_type"): str,
            vol.Required("name"): str,
        }
    )
    @websocket_api.async_response
    async def websocket_create_schedule(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Create default schedule"""
        schedule_type = str(msg.get("schedule_type")).lower()
        name = msg["name"]
        d = get_api_for_hub(msg.get("hub"))
        if d:
            schedule_type_enum = WiserScheduleTypeEnum[schedule_type]
            await d.wiserhub.schedules.create_schedule(schedule_type_enum, name)
            await d.async_refresh()
            connection.send_result(msg["id"], "success")
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")

    # Rename schedule
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedule/rename".format(DOMAIN),
            vol.Optional("hub"): str,
            vol.Required("schedule_type"): str,
            vol.Required("schedule_id"): int,
            vol.Required("schedule_name"): str,
        }
    )
    @websocket_api.async_response
    async def websocket_rename_schedule(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        schedule_type = str(msg.get("schedule_type")).lower()
        schedule_id = msg.get("schedule_id")
        name = msg["schedule_name"]
        d = get_api_for_hub(msg.get("hub"))
        if d:
            local_schedule = get_local_hot_water_schedule(msg.get("hub"))
            if schedule_id == LOCAL_HOT_WATER_SCHEDULE_ID and local_schedule:
                await local_schedule.async_set_name(name)
                connection.send_result(msg["id"], "success")
                return
            schedule_type_enum = WiserScheduleTypeEnum[schedule_type]
            schedule = d.wiserhub.schedules.get_by_id(schedule_type_enum, schedule_id)
            if schedule:
                await schedule.set_name(name)
                await d.async_refresh()
                connection.send_result(msg["id"], "success")
            else:
                connection.send_error(
                    msg["id"],
                    "wiser error",
                    f"Unable to rename schedule.  Schedule with id {schedule_id} of type {schedule_type} not found",
                )
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")

    # Delete schedule
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedule/delete".format(DOMAIN),
            vol.Optional("hub"): str,
            vol.Required("schedule_type"): str,
            vol.Required("schedule_id"): int,
        }
    )
    @websocket_api.async_response
    async def websocket_delete_schedule(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Create default schedule"""
        schedule_type = str(msg.get("schedule_type")).lower()
        schedule_id = msg["schedule_id"]
        d = get_api_for_hub(msg.get("hub"))
        if d:
            if schedule_id == LOCAL_HOT_WATER_SCHEDULE_ID:
                connection.send_error(
                    msg["id"],
                    "wiser error",
                    "The integration-owned OpenTherm hot-water schedule cannot be deleted",
                )
                return
            schedule_type_enum = WiserScheduleTypeEnum[schedule_type]
            schedule = d.wiserhub.schedules.get_by_id(schedule_type_enum, schedule_id)
            if schedule:
                try:
                    await schedule.delete_schedule()
                except WiserScheduleError as ex:
                    await d.async_refresh()
                    if d.wiserhub.schedules.get_by_id(schedule_type_enum, schedule_id):
                        connection.send_error(
                            msg["id"],
                            "wiser error",
                            f"Unable to delete schedule. {ex}",
                        )
                        return
                    _LOGGER.warning(
                        "Schedule %s/%s was deleted despite a hub response error: %s",
                        schedule_type,
                        schedule_id,
                        ex,
                    )
                else:
                    await d.async_refresh()
                connection.send_result(msg["id"], "success")
            else:
                connection.send_error(
                    msg["id"],
                    "wiser error",
                    f"Unable to delete schedule.  Schedule with id {schedule_id} of type {schedule_type} not found",
                )
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")

    # Save schedule
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedule/save".format(DOMAIN),
            vol.Optional("hub"): str,
            vol.Required("schedule_type"): str,
            vol.Required("schedule_id"): int,
            vol.Required("schedule"): dict,
        }
    )
    @websocket_api.async_response
    async def websocket_save_schedule(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Save schedule"""
        schedule_type = str(msg.get("schedule_type")).lower()
        schedule_id = msg["schedule_id"]
        new_schedule = msg["schedule"]
        d = get_api_for_hub(msg.get("hub"))
        if d:
            local_schedule = get_local_hot_water_schedule(msg.get("hub"))
            if schedule_id == LOCAL_HOT_WATER_SCHEDULE_ID and local_schedule:
                try:
                    await local_schedule.async_save(new_schedule)
                except (TypeError, ValueError) as err:
                    connection.send_error(
                        msg["id"], "invalid_schedule", str(err)
                    )
                    return
                connection.send_result(msg["id"], "success")
                return
            schedule_type_enum = WiserScheduleTypeEnum[schedule_type]
            schedule = d.wiserhub.schedules.get_by_id(schedule_type_enum, schedule_id)
            if schedule:
                await schedule.set_schedule_from_ws_data(new_schedule)
                await d.async_refresh()
                connection.send_result(msg["id"], "success")
            else:
                connection.send_error(
                    msg["id"],
                    "wiser error",
                    f"Unable to delete schedule.  Schedule with id {schedule_id} of type {schedule_type} not found",
                )
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")

    # Copy schedule
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedule/copy".format(DOMAIN),
            vol.Optional("hub"): str,
            vol.Required("schedule_type"): str,
            vol.Required("schedule_id"): int,
            vol.Required("to_schedule_id"): int,
        }
    )
    @websocket_api.async_response
    async def websocket_copy_schedule(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        schedule_type = str(msg.get("schedule_type")).lower()
        schedule_id = msg["schedule_id"]
        to_schedule_id = msg["to_schedule_id"]
        d = get_api_for_hub(msg.get("hub"))
        if d:
            if LOCAL_HOT_WATER_SCHEDULE_ID in (schedule_id, to_schedule_id):
                connection.send_error(
                    msg["id"],
                    "wiser error",
                    "The integration-owned OpenTherm hot-water schedule cannot be copied",
                )
                return
            schedule_type_enum = WiserScheduleTypeEnum[schedule_type]
            schedule = d.wiserhub.schedules.get_by_id(schedule_type_enum, schedule_id)
            if schedule:
                await schedule.copy_schedule(to_schedule_id)
                await d.async_refresh()
                connection.send_result(msg["id"], "success")
            else:
                connection.send_error(
                    msg["id"],
                    "wiser error",
                    f"Unable to copy schedule.  Schedule with id {schedule_id} of type {schedule_type} not found",
                )
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")

    # Get zigbee data
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/zigbee".format(DOMAIN),
            vol.Optional("hub"): str,
        }
    )
    @websocket_api.async_response
    async def websocket_get_zigbee_data(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Publish devices zigbee data."""
        d = get_api_for_hub(msg.get("hub"))
        if d:
            connection.send_result(
                msg["id"], build_zigbee_network_data(d.wiserhub)
            )
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/power_notifications".format(DOMAIN),
            vol.Optional("hub"): str,
        }
    )
    @websocket_api.async_response
    async def websocket_get_power_notifications(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Publish native equipment power notification data."""
        d = get_api_for_hub(msg.get("hub"))
        if d:
            connection.send_result(
                msg["id"], build_power_notification_data(d.wiserhub)
            )
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/notifications".format(DOMAIN),
            vol.Optional("hub"): str,
        }
    )
    @websocket_api.async_response
    async def websocket_get_notifications(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Publish all locally exposed native Wiser notifications."""
        d = get_api_for_hub(msg.get("hub"))
        if d:
            connection.send_result(
                msg["id"], build_native_notification_data(d.wiserhub)
            )
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/device_notification/set".format(DOMAIN),
            vol.Optional("hub"): str,
            vol.Required("category"): vol.In(["smoke_alarm", "sensor"]),
            vol.Required("device_id"): int,
            vol.Required("enabled"): bool,
        }
    )
    @websocket_api.require_admin
    @websocket_api.async_response
    async def websocket_set_device_notification(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Enable or disable notifications for a supported Wiser device."""
        d = get_api_for_hub(msg.get("hub"))
        if not d:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")
            return
        collection_name = (
            "smokealarms" if msg["category"] == "smoke_alarm" else "binary_sensor"
        )
        collection = getattr(d.wiserhub.devices, collection_name, None)
        device = collection.get_by_id(msg["device_id"]) if collection else None
        setter = getattr(device, "set_notification_enabled", None)
        if setter is None:
            connection.send_error(
                msg["id"], "not_found", "notification-capable device not recognised"
            )
            return
        await setter(msg["enabled"])
        await d.async_refresh()
        connection.send_result(
            msg["id"], build_native_notification_data(d.wiserhub)
        )

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/automation/set_enabled".format(DOMAIN),
            vol.Optional("hub"): str,
            vol.Required("automation_id"): int,
            vol.Required("enabled"): bool,
        }
    )
    @websocket_api.require_admin
    @websocket_api.async_response
    async def websocket_set_automation_enabled(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Enable or disable a Wiser automation."""
        d = get_api_for_hub(msg.get("hub"))
        if not d:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")
            return
        collection = getattr(d.wiserhub, "automations", None)
        automation = collection.get_by_id(msg["automation_id"]) if collection else None
        setter = getattr(automation, "set_enabled", None)
        if setter is None:
            connection.send_error(
                msg["id"], "not_found", "automation not recognised"
            )
            return
        await setter(msg["enabled"])
        await d.async_refresh()
        connection.send_result(
            msg["id"], build_native_notification_data(d.wiserhub)
        )

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/power_notification/set".format(DOMAIN),
            vol.Optional("hub"): str,
            vol.Required("equipment_id"): int,
            vol.Required("notification_type"): vol.In(
                list(POWER_NOTIFICATION_TYPES)
            ),
            vol.Required("period_mins"): vol.All(int, vol.Range(min=0)),
            vol.Required("limit"): vol.All(int, vol.Range(min=0)),
            vol.Required("enabled"): bool,
        }
    )
    @websocket_api.require_admin
    @websocket_api.async_response
    async def websocket_set_power_notification(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Create or update a native equipment power notification."""
        d = get_api_for_hub(msg.get("hub"))
        if not d:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")
            return
        equipment = d.wiserhub.devices.equipments.get_by_id(msg["equipment_id"])
        if equipment is None:
            connection.send_error(
                msg["id"], "not_found", "equipment not recognised"
            )
            return
        setter = getattr(
            equipment,
            f"set_{msg['notification_type']}_power_notification",
        )
        await setter(msg["period_mins"], msg["limit"], msg["enabled"])
        await d.async_refresh()
        connection.send_result(
            msg["id"], build_power_notification_data(d.wiserhub)
        )

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/power_notification/delete".format(DOMAIN),
            vol.Optional("hub"): str,
            vol.Required("equipment_id"): int,
            vol.Required("notification_type"): vol.In(
                list(POWER_NOTIFICATION_TYPES)
            ),
        }
    )
    @websocket_api.require_admin
    @websocket_api.async_response
    async def websocket_delete_power_notification(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Delete a native equipment power notification."""
        d = get_api_for_hub(msg.get("hub"))
        if not d:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")
            return
        equipment = d.wiserhub.devices.equipments.get_by_id(msg["equipment_id"])
        if equipment is None:
            connection.send_error(
                msg["id"], "not_found", "equipment not recognised"
            )
            return
        deleter = getattr(
            equipment,
            f"delete_{msg['notification_type']}_power_notification",
        )
        await deleter()
        await d.async_refresh()
        connection.send_result(
            msg["id"], build_power_notification_data(d.wiserhub)
        )

    async_register_command(hass, websocket_configure_panel)
    async_register_command(hass, websocket_configure_wiser_panel_tabs)
    async_register_command(hass, websocket_get_hubs)
    async_register_command(hass, websocket_get_suntimes)
    async_register_command(hass, websocket_get_schedules)
    async_register_command(hass, websocket_get_schedule_types)
    async_register_command(hass, websocket_get_schedule_by_id)
    async_register_command(hass, websocket_get_rooms)
    async_register_command(hass, websocket_get_devices)
    async_register_command(hass, websocket_assign_schedule)
    async_register_command(hass, websocket_create_schedule)
    async_register_command(hass, websocket_rename_schedule)
    async_register_command(hass, websocket_delete_schedule)
    async_register_command(hass, websocket_save_schedule)
    async_register_command(hass, websocket_copy_schedule)
    async_register_command(hass, websocket_get_zigbee_data)
    async_register_command(hass, websocket_get_power_notifications)
    async_register_command(hass, websocket_get_notifications)
    async_register_command(hass, websocket_set_device_notification)
    async_register_command(hass, websocket_set_automation_enabled)
    async_register_command(hass, websocket_set_power_notification)
    async_register_command(hass, websocket_delete_power_notification)

    async_register_command(hass, handle_subscribe_updates)
