import enum
import logging
import voluptuous as vol
from homeassistant.helpers import config_validation as cv
from homeassistant.components import websocket_api
from homeassistant.core import callback
from homeassistant.components.websocket_api import async_register_command, ActiveConnection, decorators
from wiserHeatAPIv2.schedule import WiserScheduleTypeEnum
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.components.http import HomeAssistantView
from . import const

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

    listeners = []

    @callback
    def async_handle_event_wiser_update():
        """pass data to frontend when backend changes"""
        _LOGGER.warning(msg)
        connection.send_message(
            {
                "id": msg["id"],
                "type": "event",
                "event": {  # data to pass with event
                    "event": 'wiser_updated'
                },
            }
        )

    listeners.append(
        async_dispatcher_connect(
            hass, 'wiser_update_received', async_handle_event_wiser_update
        )
    )

    def unsubscribe_listeners():
        """unsubscribe listeners when frontend connection closes"""
        while len(listeners):
            listeners.pop()()

    connection.subscriptions[msg["id"]] = unsubscribe_listeners
    connection.send_result(msg["id"])


async def async_register_websockets(hass, data):
    def get_hub_name(config_entry_id):
        try:
            api = hass.data[const.DOMAIN][config_entry_id]["data"]
            return api.wiserhub.system.name
        except:
            return None

    def get_api_for_hub(hub: str):
        if hub:
            for entry_id in hass.data[const.DOMAIN]:
                if hass.data[const.DOMAIN][entry_id]["data"].wiserhub.system.name == hub:
                    return hass.data[const.DOMAIN][entry_id]["data"]
            return None
        else:
            for entry_id in hass.data[const.DOMAIN]:
                return hass.data[const.DOMAIN][entry_id]["data"]
    
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
            vol.Required("type"): "{}/hubs".format(const.DOMAIN),
        }
    )
    @websocket_api.async_response
    async def websocket_get_hubs(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Publish schedules list data."""
        output = []
        for entry in hass.data[const.DOMAIN]:
            output.append(get_hub_name(entry))
        
        #output = output.sort()
        connection.send_result(msg["id"], output)




    # Get schedules list
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedules".format(const.DOMAIN),
            vol.Optional("hub"): str,
            vol.Optional("schedule_type"): str
        }
    )
    @websocket_api.async_response
    async def websocket_get_schedules(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Publish schedules list data."""
        output = []
        schedule_type = msg.get("schedule_type")
        if schedule_type in ['lighting','shutters']: schedule_type = 'level'
        d = get_api_for_hub(msg.get("hub"))
        if d:
            if schedule_type:
                schedule_type_enum = WiserScheduleTypeEnum[str(schedule_type).lower()]
                schedules = d.wiserhub.schedules.get_by_type(schedule_type_enum)
            else:
                schedules = d.wiserhub.schedules.all
            
            for schedule in schedules:
                output.append({"id": schedule.id, "type": (schedule.level_type if schedule.schedule_type == 'Level' else schedule.schedule_type), "name": schedule.name})

            connection.send_result(msg["id"], sorted(output, key=lambda n: n['name']))
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")   

    
    # Get schedules types for hub
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedules/types".format(const.DOMAIN),
            vol.Optional("hub"): str,
        }
    )
    @websocket_api.async_response
    async def websocket_get_schedule_types(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Publish supported schedule type list data."""
        output = ["Heating", "OnOff"]
        d = get_api_for_hub(msg.get("hub"))
        if d:
            for cap, value in d.wiserhub.system.capabilities.all.items():
                if cap == 'Light' and value == True:
                    output.append("Lighting")
                if cap == 'Shutter' and value == True:
                    output.append("Shutters")

            connection.send_result(msg["id"], output)
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")   


    #Get schedule by id
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedule/id".format(const.DOMAIN),
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
        if schedule_type in ['lighting','shutters']: schedule_type = 'level'
        schedule_id = msg.get("schedule_id")
        d = get_api_for_hub(msg.get("hub"))
        if d:
            schedule_type_enum = WiserScheduleTypeEnum[schedule_type]
            schedule = d.wiserhub.schedules.get_by_id(schedule_type_enum, schedule_id)
            if schedule:
                schedule = get_ws_schedule(d, schedule_type, schedule)
                connection.send_result(msg["id"], schedule)
            else:
                connection.send_error(msg["id"], "wiser error", f"Unable to get schedule.  Schedule with id {schedule_id} of type {schedule_type} not found")
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")    



    #Get list of rooms
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/rooms".format(const.DOMAIN),
            vol.Optional("hub"): str
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
                room_list.append({"id": room.id, "name":room.name})
            connection.send_result(msg["id"], sorted(room_list, key=lambda n: n['name']))
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")    


    # Get list of devices
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/devices".format(const.DOMAIN),
            vol.Required("device_type"): str,
            vol.Optional("hub"): str
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
            if msg["device_type"] == 'onoff':
                devices = d.wiserhub.devices.smartplugs.all
            if msg["device_type"] == 'shutters':
                devices = d.wiserhub.devices.shutters.all
            if msg["device_type"] == 'lighting':
                devices = d.wiserhub.devices.lights.all

            device_list = []
            for device in devices:
                device_list.append({"id": device.id, "name":device.name})
            connection.send_result(msg["id"], sorted(device_list, key=lambda n: n['name']))
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")   



    # Assign schedule
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedule/assign".format(const.DOMAIN),
            vol.Optional("hub"): str,
            vol.Required("schedule_type"): str,
            vol.Required("schedule_id"): int,
            vol.Required("entity_id"): str,
            vol.Optional("remove"): bool
        }
    )
    @websocket_api.async_response
    async def websocket_assign_schedule(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Assign schedule to room/device"""
        remove = msg.get("remove", False)
        schedule_type = str(msg.get("schedule_type")).lower()
        if schedule_type in ['lighting','shutters']: schedule_type = 'level'
        schedule_id = msg.get("schedule_id")
        d = get_api_for_hub(msg.get("hub"))
        if d:
            schedule_type_enum = WiserScheduleTypeEnum[schedule_type]
            schedule = d.wiserhub.schedules.get_by_id(schedule_type_enum, schedule_id)
            if schedule:
                if not remove:
                    await hass.async_add_executor_job(
                        schedule.assign_schedule, int(msg["entity_id"])
                    )
                else:
                    await hass.async_add_executor_job(
                        schedule.unassign_schedule, int(msg["entity_id"])
                    )
                await hass.async_create_task(
                    d.async_update(True)
                )
            connection.send_result(msg["id"], "success")
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")    

    
    # Create schedule
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedule/create".format(const.DOMAIN),
            vol.Optional("hub"): str,
            vol.Required("schedule_type"): str,
            vol.Required("name"):str
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
            await hass.async_add_executor_job(
                d.wiserhub.schedules.create_schedule, schedule_type_enum, name
            )
            await hass.async_create_task(
                d.async_update(True)
            )
            connection.send_result(msg["id"], "success")
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")    

    

     # Delete schedule
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedule/delete".format(const.DOMAIN),
            vol.Optional("hub"): str,
            vol.Required("schedule_type"): str,
            vol.Required("schedule_id"):int
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
                await hass.async_add_executor_job(
                    schedule.delete_schedule
                )
                await hass.async_create_task(
                    d.async_update(True)
                )
                connection.send_result(msg["id"], "success")
            else:
                connection.send_error(msg["id"], "wiser error", f"Unable to delete schedule.  Schedule with id {schedule_id} of type {schedule_type} not found")
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")


    
    # Save schedule
    @websocket_api.websocket_command(
        {
            vol.Required("type"): "{}/schedule/save".format(const.DOMAIN),
            vol.Optional("hub"): str,
            vol.Required("schedule_type"): str,
            vol.Required("schedule_id"):int,
            vol.Required("schedule"): dict
        }
    )
    @websocket_api.async_response
    async def websocket_save_schedule(
        hass, connection: ActiveConnection, msg: dict
    ) -> None:
        """Save schedule"""
        schedule_type = str(msg.get("schedule_type")).lower()
        schedule_id = msg["schedule_id"]
        d = get_api_for_hub(msg.get("hub"))
        if d:
            schedule_type_enum = WiserScheduleTypeEnum[schedule_type]
            schedule = d.wiserhub.schedules.get_by_id(schedule_type_enum, schedule_id)
            if schedule:
                await hass.async_add_executor_job(
                    schedule.delete_schedule
                )
                await hass.async_create_task(
                    d.async_update(True)
                )
                connection.send_result(msg["id"], "success")
            else:
                connection.send_error(msg["id"], "wiser error", f"Unable to delete schedule.  Schedule with id {schedule_id} of type {schedule_type} not found")
        else:
            connection.send_error(msg["id"], "wiser error", "hub not recognised")
    
    hass.components.websocket_api.async_register_command(websocket_get_hubs)
    hass.components.websocket_api.async_register_command(websocket_get_schedules)
    hass.components.websocket_api.async_register_command(websocket_get_schedule_types)
    hass.components.websocket_api.async_register_command(websocket_get_schedule_by_id)
    hass.components.websocket_api.async_register_command(websocket_get_rooms)
    hass.components.websocket_api.async_register_command(websocket_get_devices)
    hass.components.websocket_api.async_register_command(websocket_assign_schedule)
    hass.components.websocket_api.async_register_command(websocket_create_schedule)
    hass.components.websocket_api.async_register_command(websocket_delete_schedule)

    async_register_command(hass, handle_subscribe_updates)


    def get_ws_schedule(data, schedule_type, schedule):
        DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

        class settingEnum(enum.Enum):
            heating = "Temp"
            onoff = "State"
            level = "Level"


        def get_end_time(slot, slots):
            index = slots.index(slot)
            if index < len(slots) -1:
                return slots[index+1].get("Time")
            return "24:00"

        def get_previous_setting(schedule_type, day: str, schedule_data):
            days = DAYS
            i = days.index(day)
            # Reverse week starting from day before day param
            i = days.index(day)
            days = days[i:] + days[:i]
            days.reverse()

            for day in days:
                slots = schedule_data.get(day)
                if len(slots) > 0:
                    return slots[-1].get(settingEnum[schedule_type.lower()].value)

        def format_slot(data, schedule_type, day, slot, slots, schedule_data, first_slot):
            if first_slot:
                start_time = "00:00"
                end_time = slot.get('Time','24:00') 
                if end_time in ['Sunrise','Sunset']:
                    end_time = convert_special_time(data, end_time)
                setpoint = get_previous_setting(schedule_type, day, schedule_data)
                from_previous_day = True
            else:
                start_time = slot.get('Time','00:00') 
                if start_time in ['Sunrise','Sunset']:
                    start_time = convert_special_time(data, day)
                end_time = get_end_time(slot, slots)
                if end_time in ['Sunrise','Sunset']:
                    end_time = convert_special_time(data, day)
                setpoint = slot.get(settingEnum[schedule_type.lower()].value)
                from_previous_day = False
            
            return {
                    "start": start_time, 
                    "end": end_time,
                    "setpoint": setpoint,
                    "from_previous": from_previous_day
                }

        def convert_special_time(data, day: str, time: str):
            if time == "Sunrise":
                return get_sunrise(data, day)
            return get_sunset(data, day)

        def get_sunrise(data, day):
            #TODO: Add by day
            # Just get first entry for now
            s = data.wiserhub.system.sunrise_times.get(day)
            return s

        def get_sunset(data, day):
            #TODO: Add by day
            # Just get first entry for now
            s = data.wiserhub.system.sunset_times.get(day)
            return s


        def stringTimeToTime(strTime:str):
            strTime = strTime.replace(':','')
            if strTime in ['Sunrise','Sunset']:
                return strTime
            return int(strTime)

        schedule_f = schedule._convert_from_wiser_schedule(schedule.schedule_data, True)
        output = []
        for day, slots in schedule_f.items():
            if day in DAYS:
                new_slot = []
                if slots:
                    for slot in slots:
                        if slots.index(slot) == 0 and stringTimeToTime(slot.get("Time")):
                            # If schedule starts after midnight add slot from previous day
                            new_slot.append(format_slot(data, schedule.schedule_type, day, slot, slots, schedule_f, True))
                        new_slot.append(format_slot(data, schedule.schedule_type, day, slot, slots, schedule_f, False))
                else:
                    #If day has no slots add whole day slot from prev
                    new_slot.append(format_slot(data, schedule.schedule_type, day, {}, slots, schedule_f, True))

                output.append({"day": day, "slots": new_slot})

        if schedule_type == "heating":
            end_output = {
                "id": schedule.id,
                "name": schedule.name,
                "type": "Heating",
                "next": schedule.next._data,
                "attachment_ids": schedule.room_ids,
                "attachment_names": [data.wiserhub.rooms.get_by_id(room_id).name for room_id in schedule.room_ids ],
                "schedule_data": output}
        else:
            end_output = {
                "id": schedule.id,
                "name": schedule.name,
                "type": (schedule.level_type if schedule.schedule_type == 'Level' else schedule.schedule_type),
                "next": schedule.next._data,
                "attachment_ids": schedule.device_ids,
                "attachment_names": [data.wiserhub.devices.get_by_id(device_id).name for device_id in schedule.device_ids if schedule.id != 1000 ],
                "schedule_data": output}
        return end_output



