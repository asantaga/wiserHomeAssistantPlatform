"""Shared Home Assistant entity behaviour for Wiser."""

from .const import DOMAIN
from .helpers import get_hub_entity_object_id


class WiserEntityMixin:
    """Apply stable object IDs to entities attached to the physical HeatHub."""

    @property
    def suggested_object_id(self):
        """Suggest a MAC-derived object ID for newly registered hub entities."""
        device_info = self.device_info
        hub_identifier = (DOMAIN, self._data.wiserhub.system.name)

        if device_info and hub_identifier in device_info.get("identifiers", set()):
            return get_hub_entity_object_id(self._data, self.name)

        return super().suggested_object_id
