import logging
import enum
import json
from homeassistant.core import callback

from wiserHeatAPIv2.schedule import WiserScheduleTypeEnum

_LOGGER = logging.getLogger(__name__)

class WiserScheduleEntity(object):

    def get_schedule_type(self, expand_level: bool = False):
        """Get scheudle type for entity"""
        schedule_type = WiserScheduleTypeEnum.heating
        if hasattr(self, "_device_id"):
            if self._data.wiserhub.devices.get_by_id(self._device_id).product_type in ['SmartPlug']:
                schedule_type = WiserScheduleTypeEnum.onoff
            else:
                if expand_level:
                    if self._data.wiserhub.devices.get_by_id(self._device_id).product_type == "Shutter":
                        schedule_type = WiserScheduleTypeEnum.shutters
                    else:
                        schedule_type = WiserScheduleTypeEnum.lighting
                else:
                    schedule_type = WiserScheduleTypeEnum.level
        return schedule_type

    @callback
    def get_schedule(self, filename: str) -> None:
        try:
            if self._schedule:
                _LOGGER.info(f"Saving {self._schedule.name} schedule to file {filename}")
                self.hass.async_add_executor_job(
                    self._schedule.save_schedule_to_yaml_file, filename
                )
            else:
                _LOGGER.error(f"No schedule exists for {self.name}")
        except Exception as ex:
            _LOGGER.error(f"Error saving {self._schedule.name} schedule to file {filename}. {ex}")

    @callback
    def set_schedule(self, filename: str) -> None:
        try:
            if self._schedule:
                _LOGGER.info(f"Setting {self._schedule.name} schedule from file {filename}")
                self.hass.async_add_executor_job(
                    self._schedule.set_schedule_from_yaml_file, filename
                )
                self.hass.async_create_task(
                    self.async_force_update()
                )
        except:
            _LOGGER.error(f"Error setting {self._schedule.name} schedule from file {filename}")

    @callback 
    def assign_schedule_to_another_entity(self, to_entity)-> None:
        if self._schedule:
            # Check they are on the same wiser hub
            if self._data.wiserhub.system.name == to_entity._data.wiserhub.system.name:
                # Check they are of the same schedule type
                if (
                    (hasattr(self, "_room_id") and hasattr(to_entity, "_room_id")) 
                    or 
                    (hasattr(self, "_device_id") and hasattr(to_entity, "_device_id"))
                ):
                    try:
                        if hasattr(self, "_room_id"):
                            to_entity_name = to_entity._room.name
                            entity_name = self._room.name
                            to_id = to_entity._room_id
                        else:
                            to_entity_name = to_entity._data.wiserhub.devices.get_by_id(to_entity._device_id).name
                            entity_name = self._data.wiserhub.devices.get_by_id(self._device_id).name
                            to_id = to_entity._device_id

                        _LOGGER.info(f"Assigning {entity_name} schedule to {to_entity_name}")
                        self.hass.async_add_executor_job(
                            self._schedule.assign_schedule, to_id
                        )
                        self.hass.async_create_task(
                            self.async_force_update()
                        )
                    except Exception as ex:
                        _LOGGER.error(f"Unknown error assigning {entity_name} schedule to {to_entity_name}. {ex}")
                else:
                    _LOGGER.error(f"Error assigning schedule.  You must assign schedules of the same type")
            else:
                _LOGGER.error("Error assigning schedule. You cannot assign schedules across different Wiser Hubs.  Download form one and upload to the other instead")
        else:
            _LOGGER.error(f"Error assigning schedule. {self._room.name if hasattr(self, '_room_id') else self._data.wiserhub.devices.get_by_id(self._device_id).name} has no schedule assigned")
                

    @callback 
    def assign_schedule_by_id(self, schedule_id: int)-> None:
        try:
            to_id = []
            schedule_type = self.get_schedule_type()
            if hasattr(self, "_room_id"):
                to_id.append(self._room_id)
                _LOGGER.info(f"Assigning {schedule_type.value} schedule with id {schedule_id} to room {self._data.wiserhub.rooms.get_by_id(self._room_id).name}")
            else:
                to_id.append(self._device_id)
                _LOGGER.info(f"Assigning {schedule_type.value} schedule with id {schedule_id} to device {self._data.wiserhub.devices.get_by_id(self._device_id).name}")

            schedule = self._data.wiserhub.schedules.get_by_id(schedule_type, schedule_id)
            if schedule:
                self.hass.async_add_executor_job(
                    schedule.assign_schedule, to_id
                )
                self.hass.async_create_task(
                    self.async_force_update()
                )
            else:
                _LOGGER.error(f"Error assigning schedule to {self.name}. {schedule_type.value} schedule with id {schedule_id} does not exist")
        except Exception as ex:
            _LOGGER.error(f"Error assigning schedule with id {schedule_id} to {self.name}. {ex}")

    @callback
    def create_schedule(self) -> None:
        to_id = []
        try:
            schedule_type = self.get_schedule_type(True)
            name = self.name
            if hasattr(self, "_room_id"):
                to_id.append(self._room_id)
                name = self._room.name
                _LOGGER.info(f"Creating {schedule_type.value} schedule with name {name} and assigning to room {self._room.name}")
            else:
                to_id.append(self._device_id)
                name = self._data.wiserhub.devices.get_by_id(self._device_id).name
                _LOGGER.info(f"Creating {schedule_type.value} schedule with name {name} and assigning to device {self._data.wiserhub.devices.get_by_id(self._device_id).name}")

            self.hass.async_add_executor_job(
                self._data.wiserhub.schedules.create_schedule, schedule_type, name, to_id
            )
            self.hass.async_create_task(
                self.async_force_update()
            )

        except Exception as ex:
            _LOGGER.error(f"Error assigning schedule to {name}. {ex}")


    @callback
    def copy_schedule(self, to_entity)-> None:
        # Check if from_entity has an assigned schedule
        if self._schedule:
            # Check on same hub
            if self._data.wiserhub.system.name == to_entity._data.wiserhub.system.name:
                # Check to entity is a schedule entity
                if hasattr(to_entity, "_schedule"):
                    # Check to entity has a schedule assigned
                    if to_entity._schedule:
                        # Check schedules are of the same type
                        if (
                            (self._schedule.schedule_type == to_entity._schedule.schedule_type)
                            and
                            (getattr(self._schedule,"schedule_level_type", None) == getattr(to_entity._schedule,"schedule_level_type", None))
                        ):
                            _LOGGER.info(f"Copying schedule from {self.name} to {to_entity.name}")
                            try:
                                if self._schedule:
                                    self.hass.async_add_executor_job(
                                            self._schedule.copy_schedule, to_entity._schedule.id
                                        )
                                    self.hass.async_create_task(
                                        self.async_force_update()
                                    )
                            except Exception as ex:
                                _LOGGER.error(f"Unknown error copying schedule from {self.name} to {to_entity.name}: {ex}")
                        else:
                            _LOGGER.error(
                                f"Error copying schedule.  You cannot copy schedules of different types. "
                                + f"{self.name} is type {self._schedule.schedule_type}"
                                + f"{' - ' + self._schedule.schedule_level_type if hasattr(self._schedule,'schedule_level_type') else ''}"
                                + f" and {to_entity.name} is type {to_entity._schedule.schedule_type}"
                                + f"{' - ' + to_entity._schedule.schedule_level_type if hasattr(to_entity._schedule,'schedule_level_type') else ''}"
                            )
                    else:
                        _LOGGER.error(f"Error copying schedule. {to_entity.name} has no assigned schedule to copy to")
                else:
                    _LOGGER.error(f"Cannot copy schedule to entity {to_entity.name}. Please see integration instructions for entities to choose")
            else:
                _LOGGER.error("You cannot copy schedules across different Wiser Hubs.  Download form one and upload to the other instead")
        else:
            _LOGGER.error(f"Error copying schedule. {self.name} has no schedule assigned to copy")
        
    @callback
    async def async_advance_schedule(self) -> None:
        """Advance to next schedule setting for room"""
        _LOGGER.info(f"Advancing room schedule for  {self._room.name}")
        await self.hass.async_add_executor_job(
            self._room.schedule_advance
        )
        await self.async_force_update()


    def get_ws_schedule(self):
        days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

        class settingEnum(enum.Enum):
            heating = "Temp"
            onoff = "State"
            level = "Level"


        def get_end_time(slot, slots):
            index = slots.index(slot)
            if index < len(slots) -1:
                return slots[index+1].get("Time")
            return "24:00"

        def get_setting(start_time: str, slots, settings):

            index = slots.index(start_time)
            return settings[index]

        def get_previous_day(day: str):
            index = days.index(day)
            if index == 0:
                return days[len(days)-1]
            if index == len(days)-1:
                return days[0]
            return days[index - 1]

        def get_prev_day_last_setting(schedule_type, day: str, schedule_data):
            slots = schedule_data.get(get_previous_day(day))
            return slots[-1].get(settingEnum[schedule_type.lower()].value)

        def format_slot(schedule_type, day, slot, slots, schedule_data, first_slot):
            if first_slot:
                start_time = "00:00"
                end_time = slot.get('Time')
                setpoint = get_prev_day_last_setting(schedule_type, day, schedule_data)
                from_previous_day = True
            else:
                start_time = slot.get("Time")
                end_time = get_end_time(slot, slots)
                setpoint = slot.get(settingEnum[schedule_type.lower()].value)
                from_previous_day = False
            
            return {
                    "start": start_time, 
                    "end": end_time,
                    "setpoint": setpoint,
                    "from_previous": from_previous_day
                }

        def stringTimeToTime(strTime:str) -> int:
            return int(strTime.replace(':',''))

        #schedule = self._data.wiserhub.schedules.get_by_id(WiserScheduleTypeEnum[self._schedule.schedule_type.lower()], self._schedule.id)
        schedule = self._schedule
        schedule_f = schedule._convert_from_wiser_schedule(schedule.schedule_data)
        output = []
        for day, slots in schedule_f.items():
            if day in days:
                # print(f"Day - {day}, Prev - {get_previous_day(day)}")
                new_slot = []
                for slot in slots:
                    if slots.index(slot) == 0 and stringTimeToTime(slot.get("Time")) > 0:
                        # If schedule starts after midnight add slot from previous day
                        new_slot.append(format_slot(self._schedule.schedule_type, day, slot, slots, schedule_f, True))
                    new_slot.append(format_slot(self._schedule.schedule_type, day, slot, slots, schedule_f, False))

                output.append({"day": day, "slots": new_slot})


        end_output = {
            "id": schedule.id,
            "name": schedule.name,
            "type": "Heating",
            "next": schedule.next._data,
            "rooms_ids": schedule.room_ids,
            "room_names": [self._data.wiserhub.rooms.get_by_id(room_id).name for room_id in schedule.room_ids ],
            "schedule_data": output}
        return end_output

