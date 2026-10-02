"""Load frontend definitions maintained inside the integration."""

import json
import logging
from pathlib import Path

from ..const import CARD_MANIFEST
from .manifest import validate_registry

_LOGGER = logging.getLogger(__name__)
REGISTRY_DATA = "wiser_frontend_registry"
REGISTRY_PATH = Path(__file__).parent / "cards.json"


def get_manifest(hass):
    """Return the last valid local frontend registry."""
    return hass.data.get(REGISTRY_DATA, CARD_MANIFEST)


def _load_registry():
    """Read and validate the local registry."""
    return validate_registry(json.loads(REGISTRY_PATH.read_text("utf-8")))


async def async_load_registry(hass):
    """Reload local definitions so a manual update check sees file edits."""
    try:
        manifest = await hass.async_add_executor_job(_load_registry)
    except (OSError, ValueError, TypeError, KeyError) as error:
        _LOGGER.warning("Unable to load Wiser frontend registry: %s", error)
        return get_manifest(hass)
    hass.data[REGISTRY_DATA] = manifest
    return manifest
