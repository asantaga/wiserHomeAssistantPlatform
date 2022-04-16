import logging
from homeassistant.core import callback

from wiserHeatAPIv2.schedule import WiserScheduleTypeEnum

_LOGGER = logging.getLogger(__name__)

class WiserScheduleEntity(object):
    def get_schedule_type(self, expand_level: bool = False):
        """Get scheudle type for entity"""
        schedule_type = WiserScheduleTypeEnum.heating
        if hasattr(self, "_device_id"):
            if self._data.wiserhub.devices.get_by_id(self._device_id).product_type in ['SmartPlug','OnOffLight']:
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
    def copy_schedule(self, to_schedule_id: int, to_entity_name: str)-> None:
        try:
            if self._schedule:
                _LOGGER.info(f"Copying schedule from {self._schedule.name} to {to_entity_name}")
                self.hass.async_add_executor_job(
                        self._schedule.copy_schedule, to_schedule_id
                    )
                self.hass.async_create_task(
                    self.async_force_update()
                )
        except:
            _LOGGER.error(f"Error copying schedule from {self._schedule.name} to {to_entity_name}")

    @callback
    async def async_advance_schedule(self) -> None:
        """Advance to next schedule setting for room"""
        _LOGGER.info(f"Advancing room schedule for  {self._room.name}")
        await self.hass.async_add_executor_job(
            self._room.schedule_advance
        )
        await self.async_force_update()
