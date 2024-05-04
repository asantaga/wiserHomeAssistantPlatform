import logging
from typing import Union

from aioWiserHeatAPI.const import WiserScheduleTypeEnum
from aioWiserHeatAPI.wiserhub import WiserScheduleError

from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)


class WiserScheduleEntity:
    @property
    def data(self):
        return self._data

    @property
    def schedule(self):
        return self._schedule

    @property
    def device(self):
        return self._device if hasattr(self, "_device") else None

    def get_schedule_type(self, expand_level: bool = False):
        """Get scheudle type for entity"""
        schedule_type = WiserScheduleTypeEnum.heating
        if hasattr(self, "_device_id"):
            if self.data.wiserhub.devices.get_by_id(self._device_id).product_type in [
                "SmartPlug"
            ]:
                schedule_type = WiserScheduleTypeEnum.onoff
            else:
                if expand_level:
                    if (
                        self.data.wiserhub.devices.get_by_id(
                            self._device_id
                        ).product_type
                        == "Shutter"
                    ):
                        schedule_type = WiserScheduleTypeEnum.shutters
                    else:
                        schedule_type = WiserScheduleTypeEnum.lighting
                else:
                    schedule_type = WiserScheduleTypeEnum.level
        return schedule_type

    @callback
    async def get_schedule(self, filename: str) -> None:
        try:
            if self.schedule:
                _LOGGER.debug(
                    f"Saving {self.schedule.name} schedule to file {filename}"
                )
                await self.schedule.save_schedule_to_yaml_file(filename)
            else:
                _LOGGER.error(f"No schedule exists for {self.name}")
        except Exception as ex:
            raise HomeAssistantError(
                f"Error saving {self.schedule.name} schedule to file {filename}. {ex}"
            )

    @callback
    async def set_schedule(self, filename: str) -> None:
        try:
            if self.schedule:
                _LOGGER.debug(
                    f"Setting {self.schedule.name} schedule from file {filename}"
                )
                await self.schedule.set_schedule_from_yaml_file(filename)
                await self.data.async_refresh()
        except WiserScheduleError as ex:
            raise HomeAssistantError(ex)
        except Exception as ex:
            raise HomeAssistantError(
                f"Error setting {self.schedule.name} schedule from file {filename}. {ex}"
            )

    @callback
    async def set_schedule_from_data(self, schedule: str) -> None:
        try:
            if self.schedule:
                _LOGGER.debug(
                    f"Setting {self.schedule.name} schedule from schedule data.\n{schedule}"
                )
                await self.schedule.set_schedule_from_yaml_data(schedule)
                await self.data.async_refresh()
        except WiserScheduleError as ex:
            raise HomeAssistantError(ex)
        except Exception as ex:
            raise HomeAssistantError(
                f"Error setting {self.schedule.name} schedule from data.\n{schedule}. {ex}"
            )

    @callback
    async def assign_schedule_to_another_entity(self, to_entity) -> None:
        if self.schedule:
            # Check they are on the same wiser hub
            if self.data.wiserhub.system.name == to_entity.data.wiserhub.system.name:
                # Check they are of the same schedule type
                if self.get_schedule_type() == to_entity.get_schedule_type():
                    try:
                        if hasattr(self, "room"):
                            to_entity_name = to_entity.room.name
                            entity_name = self.room.name
                            to_id = to_entity.room.id
                        else:
                            to_entity_name = to_entity.data.wiserhub.devices.get_by_id(
                                to_entity.device.id
                            ).name
                            entity_name = self.data.wiserhub.devices.get_by_id(
                                self.device.id
                            ).name
                            to_id = to_entity.device.device_type_id

                        _LOGGER.info(
                            f"Assigning {entity_name} schedule to {to_entity_name}"
                        )
                        await self.schedule.assign_schedule(to_id)
                        await self.data.async_refresh()
                    except Exception as ex:  # pylint: disable=broad-exception-caught
                        _LOGGER.error(
                            f"Unknown error assigning {entity_name} schedule to {to_entity_name}. {ex}"
                        )
                else:
                    _LOGGER.error(
                        "Error assigning schedule.  You must assign schedules of the same type"
                    )
            else:
                _LOGGER.error(
                    "Error assigning schedule. You cannot assign schedules across different Wiser Hubs"
                )
        else:
            schedule_entity_name = (
                self.room.name if hasattr(self, "room") else self.device.name
            )
            _LOGGER.error(
                f"Error assigning schedule. {schedule_entity_name} has no schedule assigned"
            )

    @callback
    async def assign_schedule_by_id_or_name(
        self, schedule_id: Union[int, None], schedule_name: Union[str, None]
    ) -> None:
        try:
            to_id = None
            schedule_type = self.get_schedule_type()
            schedule_identifier = (
                "id " + str(schedule_id)
                if schedule_id is not None
                else "name " + schedule_name
            )

            if schedule_id == 0:
                if hasattr(self, "room"):
                    if self.schedule:
                        _LOGGER.debug(
                            f"Unassigning {schedule_type.value} schedule with id {self.schedule.id} from room {self.room.name}"
                        )
                        await self.schedule.unassign_schedule(self.room.id)
                    else:
                        _LOGGER.warning(
                            f"Unable to unassign schedule from {self.room.name} as no schedule is assigned"
                        )
                else:
                    if self.schedule:
                        _LOGGER.debug(
                            f"Unassigning {schedule_type.value} schedule with id {self.schedule.id} from room {self.device.name}"
                        )
                        await self.schedule.unassign_schedule(
                            self.device.device_type_id
                        )
                        await self.data.async_refresh()
                    else:
                        _LOGGER.warning(
                            f"Unable to unassign schedule from {self.device.name} as no schedule is assigned"
                        )
            else:
                if hasattr(self, "room"):
                    to_id = self.room.id
                    room_name = self.room.name
                    _LOGGER.debug(
                        f"Assigning {schedule_type.value} schedule with {schedule_identifier} to room {room_name}"
                    )
                else:
                    to_id = self.device.device_type_id
                    device_name = self.device.name
                    _LOGGER.info(
                        f"Assigning {schedule_type.value} schedule with {schedule_identifier} to device {device_name}"
                    )

                schedule = None
                if schedule_name:
                    schedule = self.data.wiserhub.schedules.get_by_name(
                        schedule_type, schedule_name
                    )
                elif schedule_id:
                    schedule = self.data.wiserhub.schedules.get_by_id(
                        schedule_type, schedule_id
                    )

                if schedule:
                    await schedule.assign_schedule(to_id)
                    await self.data.async_refresh()
                else:
                    _LOGGER.error(
                        f"Error assigning schedule to {self.name}. {schedule_type.value} schedule with {schedule_identifier} does not exist"  # noqa: E501
                    )
        except Exception as ex:  # pylint: disable=broad-exception-caught
            _LOGGER.error(
                f"Error assigning schedule with id {schedule_id} to {self.name}. {ex}"
            )

    @callback
    async def create_schedule(self) -> None:
        to_id = []
        try:
            schedule_type = self.get_schedule_type(True)
            name = self.name
            if hasattr(self, "room"):
                to_id.append(self.room.id)
                name = self.room.name
                _LOGGER.debug(
                    f"Creating {schedule_type.value} schedule with name {name} and assigning to room {name}"
                )
            else:
                to_id.append(self.device.id)
                name = self.device.name
                _LOGGER.debug(
                    f"Creating {schedule_type.value} schedule with name {name} and assigning to device {name}"
                )

            await self.data.wiserhub.schedules.create_schedule(
                schedule_type,
                name,
                to_id,
            )
            await self.data.async_refresh()

        except Exception as ex:  # pylint: disable=broad-exception-caught
            _LOGGER.error(f"Error assigning schedule to {name}. {ex}")

    @callback
    async def copy_schedule(self, to_entity) -> None:
        # Check if from_entity has an assigned schedule
        if self.schedule:
            # Check they are on the same wiser hub
            if self.data.wiserhub.system.name == to_entity.data.wiserhub.system.name:
                # Check to entity is a schedule entity
                if hasattr(to_entity, "schedule"):
                    # Check to entity has a schedule assigned
                    if to_entity.schedule:
                        # Check they are of the same schedule type
                        if self.get_schedule_type() == to_entity.get_schedule_type():
                            _LOGGER.debug(
                                f"Copying schedule from {self.name} to {to_entity.name}"
                            )
                            try:
                                await self.schedule.copy_schedule(
                                    to_entity.schedule.id,
                                )
                                await self.data.async_refresh()
                            except (
                                Exception  # pylint: disable=broad-exception-caught
                            ) as ex:
                                _LOGGER.error(
                                    f"Unknown error copying schedule from {self.name} to {to_entity.name}: {ex}"
                                )
                        else:
                            _LOGGER.error(
                                "Error copying schedule.  You cannot copy schedules of different types. "
                                + f"{self.name} is type {self._schedule.schedule_type}"
                                + f"{' - ' + self._schedule.schedule_level_type if hasattr(self._schedule,'schedule_level_type') else ''}"  # noqa: E501
                                + f" and {to_entity.name} is type {to_entity.schedule.schedule_type}"
                                + f"{' - ' + to_entity.schedule.schedule_level_type if hasattr(to_entity.schedule,'schedule_level_type') else ''}"  # noqa: E501
                            )
                    else:
                        _LOGGER.error(
                            f"Error copying schedule. {to_entity.name} has no assigned schedule to copy to"
                        )
                else:
                    _LOGGER.error(
                        f"Cannot copy schedule to entity {to_entity.name}. Please see wiki for entities to choose"
                    )
            else:
                _LOGGER.error("You cannot copy schedules across different Wiser Hubs")
        else:
            _LOGGER.error(
                f"Error copying schedule. {self.name} has no schedule assigned to copy"
            )

    @callback
    async def async_advance_schedule(self) -> None:
        """Advance to next schedule setting for room"""
        _LOGGER.debug(f"Advancing room schedule for  {self.room.name}")
        await self.room.schedule_advance()
        await self._data.async_refresh()
