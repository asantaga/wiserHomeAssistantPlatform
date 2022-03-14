import logging
from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)

class WiserScheduleEntity(object):
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
