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
            # Home Assistant builds default entity IDs from area + effective
            # device name + suggested object ID. Use the registry name here so
            # a user override is handled differently from our default hub name.
            device_entry = getattr(self, "device_entry", None)
            device_name = None
            if device_entry is not None:
                device_name = device_entry.name_by_user or device_entry.name
            return get_hub_entity_object_id(self._data, self.name, device_name)

        return super().suggested_object_id
