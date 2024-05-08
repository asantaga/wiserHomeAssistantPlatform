"""Handles schedule entities."""

import logging

from aioWiserHeatAPI.const import WiserScheduleTypeEnum
from aioWiserHeatAPI.wiserhub import WiserScheduleError

from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)


class WiserScheduleEntity:
    """Class to manage entity with schedule."""

    @property
    def data(self):
        """Return data."""
        return self._data

    # @property
    # def schedule(self):
    #    return self._schedule

    @property
    def device(self):
        """Return device."""
        return self._device if hasattr(self, "_device") else None

    def get_schedule_type(self, expand_level: bool = False):
        """Get scheudle type for entity."""
        schedule_type = WiserScheduleTypeEnum.heating
        if hasattr(self, "_device_id"):
            if self.data.wiserhub.devices.get_by_id(self._device_id).product_type in [
                "SmartPlug"
            ]:
                schedule_type = WiserScheduleTypeEnum.onoff
            elif expand_level:
                if (
                    self.data.wiserhub.devices.get_by_id(self._device_id).product_type
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
        """Get device schedule."""
        try:
            if self.schedule:
                _LOGGER.debug(
                    "Saving %s schedule to file %s", self.schedule.name, filename
                )
                await self.schedule.save_schedule_to_yaml_file(filename)
            else:
                _LOGGER.error("No schedule exists for %s", self.name)
        except Exception as ex:
            raise HomeAssistantError(
                f"Error saving {self.schedule.name} schedule to file {filename}. {ex}"
            ) from ex

    @callback
    async def set_schedule(self, filename: str) -> None:
        """Set schedule."""
        try:
            if self.schedule:
                _LOGGER.debug(
                    "Setting %s schedule from file %s", self.schedule.name, filename
                )
                await self.schedule.set_schedule_from_yaml_file(filename)
                await self.data.async_refresh()
        except WiserScheduleError as ex:
            raise HomeAssistantError(ex) from ex
        except Exception as ex:
            raise HomeAssistantError(
                f"Error setting {self.schedule.name} schedule from file {filename}. {ex}"
            ) from ex

    @callback
    async def set_schedule_from_data(self, schedule: str) -> None:
        """Set schedule from yaml data."""
        try:
            if self.schedule:
                _LOGGER.debug(
                    "Setting %s schedule from schedule data.\n %s",
                    self.schedule.name,
                    schedule,
                )
                await self.schedule.set_schedule_from_yaml_data(schedule)
                await self.data.async_refresh()
        except WiserScheduleError as ex:
            raise HomeAssistantError(ex) from ex
        except Exception as ex:
            raise HomeAssistantError(
                f"Error setting {self.schedule.name} schedule from data.\n{schedule}. {ex}"
            ) from ex

    @callback
    async def assign_schedule_to_another_entity(self, to_entity) -> None:
        """Assign schedule to another device."""
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
                            "Assigning %s schedule to %s", entity_name, to_entity_name
                        )
                        await self.schedule.assign_schedule(to_id)
                        await self.data.async_refresh()
                    except Exception as ex:  # pylint: disable=broad-exception-caught
                        _LOGGER.error(
                            "Unknown error assigning %s schedule to %s. %s",
                            entity_name,
                            to_entity_name,
                            ex,
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
                "Error assigning schedule. %s has no schedule assigned",
                schedule_entity_name,
            )

    @callback
    async def assign_schedule_by_id_or_name(
        self, schedule_id: int | None, schedule_name: str | None
    ) -> None:
        """Assign a schedule by schedule id or schedule name."""
        try:
            to_id = None
            schedule_type = self.get_schedule_type()
            schedule_identifier = (
                "id " + str(schedule_id) if schedule_id else "name " + schedule_name
            )
            if hasattr(self, "room"):
                to_id = self.room.id
                room_name = self.room.name
                _LOGGER.debug(
                    "Assigning %s schedule with %s to room %s",
                    schedule_type.value,
                    schedule_identifier,
                    room_name,
                )
            else:
                to_id = self.device.device_type_id
                device_name = self.device.name
                _LOGGER.info(
                    "Assigning %s schedule with %s to device %s",
                    schedule_type.value,
                    schedule_identifier,
                    device_name,
                )

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
                    "Error assigning schedule to %s. %s schedule with %s does not exist",
                    self.name,
                    schedule_type.value,
                    schedule_identifier,
                )
        except Exception as ex:  # pylint: disable=broad-exception-caught
            _LOGGER.error(
                "Error assigning schedule with id %s to %s. %s",
                schedule_id,
                self.name,
                ex,
            )

    @callback
    async def create_schedule(self) -> None:
        """Create a new schedule."""
        to_id = []
        try:
            schedule_type = self.get_schedule_type(True)
            name = self.name
            if hasattr(self, "room"):
                to_id.append(self.room.id)
                name = self.room.name
                _LOGGER.debug(
                    "Creating %s schedule with name %s and assigning to room %s",
                    schedule_type.value,
                    name,
                    name,
                )
            else:
                to_id.append(self.device.id)
                name = self.device.name
                _LOGGER.debug(
                    "Creating %s schedule with name %s and assigning to device %s",
                    schedule_type.value,
                    name,
                    name,
                )

            await self.data.wiserhub.schedules.create_schedule(
                schedule_type,
                name,
                to_id,
            )
            await self.data.async_refresh()

        except Exception as ex:  # pylint: disable=broad-exception-caught
            _LOGGER.error("Error assigning schedule to %s. %s", name, ex)

    @callback
    async def copy_schedule(self, to_entity) -> None:
        """Copy schedule to another schedule."""
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
                                "Copying schedule from %s to %s",
                                self.name,
                                to_entity.name,
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
                                    "Unknown error copying schedule from %s to %s. %s",
                                    self.name,
                                    to_entity.name,
                                    ex,
                                )
                        else:
                            _LOGGER.error(
                                "Error copying schedule %s of type %s to %s of type %s.  You cannot copy schedules of different types",
                                self.name,
                                self._schedule.schedule_type
                                + (" - " + self._schedule.schedule_level_type)
                                if hasattr(self._schedule, "schedule_level_type")
                                else "",
                                to_entity.name,
                                to_entity.schedule.schedule_type
                                + (" - " + to_entity.schedule.schedule_level_type)
                                if hasattr(to_entity.schedule, "schedule_level_type")
                                else "",
                            )
                    else:
                        _LOGGER.error(
                            "Error copying schedule. %s has no assigned schedule to copy to",
                            to_entity.name,
                        )
                else:
                    _LOGGER.error(
                        "Cannot copy schedule to entity %s. Please see wiki for entities to choose",
                        to_entity.name,
                    )
            else:
                _LOGGER.error("You cannot copy schedules across different Wiser Hubs")
        else:
            _LOGGER.error(
                "Error copying schedule. %s has no schedule assigned to copy", self.name
            )

    @callback
    async def async_advance_schedule(self) -> None:
        """Advance to next schedule setting for room."""
        _LOGGER.debug("Advancing room schedule for %s", self.room.name)
        await self.room.schedule_advance()
        await self._data.async_refresh()
