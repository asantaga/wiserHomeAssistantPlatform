import logging
import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import callback
from homeassistant.components.websocket_api import (
    async_register_command,
    ActiveConnection,
)
from aioWiserHeatAPI.schedule import WiserScheduleTypeEnum
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DATA, DOMAIN

_LOGGER = logging.getLogger(__name__)


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
    def get_hub_name(config_entry_id):
        try:
            api = hass.data[DOMAIN][config_entry_id][DATA]
            return api.wiserhub.system.name
        except:
            return None

    def get_api_for_hub(hub: str):
        if hub:
            for entry_id in hass.data[DOMAIN]:
                if hass.data[DOMAIN][entry_id][DATA].wiserhub.system.name == hub:
                    return hass.data[DOMAIN][entry_id][DATA]
            return None
        else:
            for entry_id in hass.data[DOMAIN]:
                return hass.data[DOMAIN][entry_id][DATA]

    def get_entity_from_entity_id(entity: str):
        """Get wiser entity from entity_id"""
        domain = entity.split(".", 1)[0]
        entity_comp = hass.data.get("entity_components", {}).get(domain)
        if entity_comp:
            return entity_comp.get_entity(entity)
        return None

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
            rooms = d.wiserhub.rooms.all
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
            nodes = []
            edges = []

            # Add controller
            nodes.append(
                {
                    "id": 0,
                    "label": f"Wiser Hub",
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

    hass.components.websocket_api.async_register_command(websocket_get_hubs)
    hass.components.websocket_api.async_register_command(websocket_get_suntimes)
    hass.components.websocket_api.async_register_command(websocket_get_schedules)
    hass.components.websocket_api.async_register_command(websocket_get_schedule_types)
    hass.components.websocket_api.async_register_command(websocket_get_schedule_by_id)
    hass.components.websocket_api.async_register_command(websocket_get_rooms)
    hass.components.websocket_api.async_register_command(websocket_get_devices)
    hass.components.websocket_api.async_register_command(websocket_assign_schedule)
    hass.components.websocket_api.async_register_command(websocket_create_schedule)
    hass.components.websocket_api.async_register_command(websocket_rename_schedule)
    hass.components.websocket_api.async_register_command(websocket_delete_schedule)
    hass.components.websocket_api.async_register_command(websocket_save_schedule)
    hass.components.websocket_api.async_register_command(websocket_copy_schedule)
    hass.components.websocket_api.async_register_command(websocket_get_zigbee_data)

    async_register_command(hass, handle_subscribe_updates)
