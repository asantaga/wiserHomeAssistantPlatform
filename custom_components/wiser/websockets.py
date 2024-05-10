"""Websockets to support custom Wiser cards."""

import logging

from aioWiserHeatAPI.schedule import WiserScheduleTypeEnum
import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.websocket_api import (
    ActiveConnection,
    async_register_command,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DATA, DOMAIN
from .coordinator import WiserUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


def get_hub_name(hass: HomeAssistant, config_entry_id: str) -> str | None:
    """Return name of hub for config entry."""
    try:
        api: WiserUpdateCoordinator = hass.data[DOMAIN][config_entry_id][DATA]
        return api.wiserhub.system.name  # noqa: TRY300
    except:  # noqa: E722
        return None


def get_api_for_hub(hass: HomeAssistant, hub: str) -> WiserUpdateCoordinator | None:
    """Get the api for the hub by name."""
    if hub:
        for entry_id in hass.data[DOMAIN]:
            if hass.data[DOMAIN][entry_id][DATA].wiserhub.system.name == hub:
                return hass.data[DOMAIN][entry_id][DATA]
        return None

    for entry_id in hass.data[DOMAIN]:
        return hass.data[DOMAIN][entry_id][DATA]


# Websocket command to send updates to frontend
@callback
@websocket_api.websocket_command(
    {
        vol.Required("type"): "wiser_updated",
    }
)
@websocket_api.async_response
async def handle_subscribe_updates(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
):
    """Subscribe listeners when frontend connection is opened."""

    @callback
    async def handle_event_wiser_update(hub: str):
        """Pass data to frontend when backend changes."""
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
        """Unsubscribe listeners when frontend connection closes."""
        remove_listener()

    connection.subscriptions[msg["id"]] = unsubscribe_listeners
    connection.send_result(msg["id"])


# Websocket command to get list of hubs
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/hubs",
    }
)
@websocket_api.async_response
async def websocket_get_hubs(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Publish schedules list data."""
    output = [get_hub_name(hass, entry) for entry in hass.data[DOMAIN]]
    connection.send_result(msg["id"], sorted(output))


# Get sunrise and sunset times
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/suntimes",
        vol.Optional("hub"): str,
    }
)
@websocket_api.async_response
async def websocket_get_suntimes(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Publish schedules list data."""
    d = get_api_for_hub(hass, msg.get("hub"))
    if d:
        sunrises = [
            {"day": day, "time": time}
            for day, time in d.wiserhub.system.sunrise_times.items()
        ]
        sunsets = [
            {"day": day, "time": time}
            for day, time in d.wiserhub.system.sunset_times.items()
        ]
        connection.send_result(msg["id"], {"Sunrises": sunrises, "Sunsets": sunsets})
    else:
        connection.send_error(msg["id"], "wiser error", "hub not recognised")


# Get schedules list
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/schedules",
        vol.Optional("hub"): str,
        vol.Optional("schedule_type"): str,
    }
)
@websocket_api.async_response
async def websocket_get_schedules(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Publish schedules list data."""
    output = []
    schedule_type = msg.get("schedule_type", "")
    d = get_api_for_hub(hass, msg.get("hub"))
    if d:
        schedules = d.wiserhub.schedules.all
        output.extend(
            [
                {
                    "Id": schedule.id,
                    "Type": schedule.schedule_type,
                    "Name": schedule.name,
                    "Assignments": len(schedule.assignment_ids),
                }
                for schedule in schedules
                if schedule.schedule_type == schedule_type or not schedule_type
            ]
        )

        connection.send_result(msg["id"], sorted(output, key=lambda n: n["Name"]))
    else:
        connection.send_error(msg["id"], "wiser error", "hub not recognised")


# Get schedules types for hub
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/schedules/types",
        vol.Optional("hub"): str,
    }
)
@websocket_api.async_response
async def websocket_get_schedule_types(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Publish supported schedule type list data."""
    output = ["Heating"]
    d = get_api_for_hub(hass, msg.get("hub"))
    if d:
        for cap, value in d.wiserhub.system.capabilities.all.items():
            if cap == "SmartPlug" and value is True:
                output.append("OnOff")
            if cap == "Light" and value is True:
                output.append("Lighting")
            if cap == "Shutter" and value is True:
                output.append("Shutters")

        connection.send_result(msg["id"], output)
    else:
        connection.send_error(msg["id"], "wiser error", "hub not recognised")


# Get schedule by id
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/schedule/id",
        vol.Optional("hub"): str,
        vol.Required("schedule_type"): str,
        vol.Required("schedule_id"): vol.Coerce(int),
    }
)
@websocket_api.async_response
async def websocket_get_schedule_by_id(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Publish schedule data."""
    schedule_type = str(msg.get("schedule_type")).lower()
    schedule_id = msg.get("schedule_id")
    d = get_api_for_hub(hass, msg.get("hub"))
    if d:
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
        vol.Required("type"): f"{DOMAIN}/rooms",
        vol.Optional("hub"): str,
    }
)
@websocket_api.async_response
async def websocket_get_rooms(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Publish room list."""
    d = get_api_for_hub(hass, msg.get("hub"))
    if d:
        rooms = d.wiserhub.rooms.all
        room_list = []
        room_list.extend([{"Id": room.id, "Name": room.name} for room in rooms])

        connection.send_result(msg["id"], sorted(room_list, key=lambda n: n["Name"]))
    else:
        connection.send_error(msg["id"], "wiser error", "hub not recognised")


# Get list of devices
@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/devices",
        vol.Required("device_type"): str,
        vol.Optional("hub"): str,
    }
)
@websocket_api.async_response
async def websocket_get_devices(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Publish device list."""
    d = get_api_for_hub(hass, msg.get("hub"))
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
            device_list.extend(
                [
                    {"Id": device.device_type_id, "Name": device.name}
                    for device in devices
                ]
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
        vol.Required("type"): f"{DOMAIN}/schedule/assign",
        vol.Optional("hub"): str,
        vol.Required("schedule_type"): str,
        vol.Required("schedule_id"): int,
        vol.Required("entity_id"): str,
        vol.Optional("remove"): bool,
    }
)
@websocket_api.async_response
async def websocket_assign_schedule(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Assign schedule to room/device."""
    remove = msg.get("remove", False)
    schedule_type = str(msg.get("schedule_type")).lower()
    if schedule_type in ["lighting", "shutters"]:
        schedule_type = "level"
    schedule_id = msg.get("schedule_id")
    d = get_api_for_hub(hass, msg.get("hub"))
    if d:
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
        vol.Required("type"): f"{DOMAIN}/schedule/create",
        vol.Optional("hub"): str,
        vol.Required("schedule_type"): str,
        vol.Required("name"): str,
    }
)
@websocket_api.async_response
async def websocket_create_schedule(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Create default schedule."""
    schedule_type = str(msg.get("schedule_type")).lower()
    name = msg["name"]
    d = get_api_for_hub(hass, msg.get("hub"))
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
        vol.Required("type"): f"{DOMAIN}/schedule/rename",
        vol.Optional("hub"): str,
        vol.Required("schedule_type"): str,
        vol.Required("schedule_id"): int,
        vol.Required("schedule_name"): str,
    }
)
@websocket_api.async_response
async def websocket_rename_schedule(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Rename schedule."""
    schedule_type = str(msg.get("schedule_type")).lower()
    schedule_id = msg.get("schedule_id")
    name = msg["schedule_name"]
    d = get_api_for_hub(hass, msg.get("hub"))
    if d:
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
        vol.Required("type"): f"{DOMAIN}/schedule/delete",
        vol.Optional("hub"): str,
        vol.Required("schedule_type"): str,
        vol.Required("schedule_id"): int,
    }
)
@websocket_api.async_response
async def websocket_delete_schedule(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Create default schedule."""
    schedule_type = str(msg.get("schedule_type")).lower()
    schedule_id = msg["schedule_id"]
    d = get_api_for_hub(hass, msg.get("hub"))
    if d:
        schedule_type_enum = WiserScheduleTypeEnum[schedule_type]
        schedule = d.wiserhub.schedules.get_by_id(schedule_type_enum, schedule_id)
        if schedule:
            await schedule.delete_schedule()
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
        vol.Required("type"): f"{DOMAIN}/schedule/save",
        vol.Optional("hub"): str,
        vol.Required("schedule_type"): str,
        vol.Required("schedule_id"): int,
        vol.Required("schedule"): dict,
    }
)
@websocket_api.async_response
async def websocket_save_schedule(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Save schedule."""
    schedule_type = str(msg.get("schedule_type")).lower()
    schedule_id = msg["schedule_id"]
    new_schedule = msg["schedule"]
    d = get_api_for_hub(hass, msg.get("hub"))
    if d:
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
        vol.Required("type"): f"{DOMAIN}/schedule/copy",
        vol.Optional("hub"): str,
        vol.Required("schedule_type"): str,
        vol.Required("schedule_id"): int,
        vol.Required("to_schedule_id"): int,
    }
)
@websocket_api.async_response
async def websocket_copy_schedule(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Copy schedule to another schedule."""
    schedule_type = str(msg.get("schedule_type")).lower()
    schedule_id = msg["schedule_id"]
    to_schedule_id = msg["to_schedule_id"]
    d = get_api_for_hub(hass, msg.get("hub"))
    if d:
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
        vol.Required("type"): f"{DOMAIN}/zigbee",
        vol.Optional("hub"): str,
    }
)
@websocket_api.async_response
async def websocket_get_zigbee_data(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict
) -> None:
    """Publish devices zigbee data."""
    d = get_api_for_hub(hass, msg.get("hub"))
    if d:
        nodes = []
        edges = []

        # Add controller
        nodes.append(
            {
                "id": 0,
                "label": "Wiser Hub",
                "group": "Controller",
            }
        )

        for device in d.wiserhub.devices.all:
            room = d.wiserhub.rooms.get_by_device_id(device.id)
            nodes.append(
                {
                    "id": device.node_id,
                    "label": f"{device.name}\n({room.name if room else 'No Room'})",
                    "group": device.product_type,
                }
            )

            if device.product_type in ["SmartPlug", "HeatingActuator"]:
                lqi = device.signal.displayed_signal_strength
            else:
                lqi = f"{device.signal.displayed_signal_strength} ({device.signal.controller_signal_strength}%)"

            edge = {
                "id": f"{device.node_id}-{device.parent_node_id}",
                "from": device.node_id,
                "to": device.parent_node_id,
                "label": lqi,
            }
            if lqi == "NoSignal":
                edge["color"] = "#db4437"

            edges.append(edge)

        connection.send_result(msg["id"], {"nodes": nodes, "edges": edges})
    else:
        connection.send_error(msg["id"], "wiser error", "hub not recognised")


async def async_register_websockets(hass: HomeAssistant, data: WiserUpdateCoordinator):  # noqa: C901
    """Register custom websockets."""

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

    async_register_command(hass, handle_subscribe_updates)
