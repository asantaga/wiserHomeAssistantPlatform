"""Entity registry migrations for Wiser."""

from __future__ import annotations

from uuid import UUID

from homeassistant.helpers import entity_registry as er

from .const import CARD_MANIFEST, DOMAIN
from .helpers import get_uuid_unique_id


def _is_uuid(value: object) -> bool:
    """Return whether a value is already a UUID unique ID."""
    try:
        UUID(value)
    except (TypeError, ValueError, AttributeError):
        return False
    return True


def migrate_entity_unique_ids(hass, config_entry_id: str) -> int:
    """Migrate Wiser registry entries to deterministic UUIDv5 unique IDs.

    Every target is validated before any registry entry is changed, preventing
    a partially applied migration when a collision exists.
    """
    registry = er.async_get(hass)
    migrations: list[tuple[str, str]] = []
    target_entity_ids: dict[tuple[str, str], str] = {}

    for entry in er.async_entries_for_config_entry(registry, config_entry_id):
        # Card update entities are shared across hubs and deliberately use
        # stable, human-readable unique IDs. Converting them prevents the
        # update coordinator from finding the existing registry records and
        # creates a duplicate set on the next platform setup.
        if (
            entry.platform != DOMAIN
            or entry.domain == "update"
            or _is_uuid(entry.unique_id)
        ):
            continue

        if not isinstance(entry.unique_id, str):
            raise ValueError(
                f"Wiser entity {entry.entity_id} has no valid unique ID"
            )

        new_unique_id = get_uuid_unique_id(entry.unique_id)
        target_key = (entry.domain, new_unique_id)
        previous_entity_id = target_entity_ids.get(target_key)
        if previous_entity_id is not None and previous_entity_id != entry.entity_id:
            raise ValueError(
                f"Wiser unique ID migration collision between "
                f"{previous_entity_id} and {entry.entity_id}"
            )

        existing_entity_id = registry.async_get_entity_id(
            entry.domain, DOMAIN, new_unique_id
        )
        if existing_entity_id is not None and existing_entity_id != entry.entity_id:
            raise ValueError(
                f"Wiser unique ID {new_unique_id} is already used by "
                f"{existing_entity_id}"
            )

        target_entity_ids[target_key] = entry.entity_id
        migrations.append((entry.entity_id, new_unique_id))

    for entity_id, new_unique_id in migrations:
        registry.async_update_entity(entity_id, new_unique_id=new_unique_id)

    return len(migrations)


def repair_card_update_unique_ids(hass, config_entry_id: str) -> int:
    """Restore card-update IDs converted by the catch-all v4 migration.

    Preserve the older registry record (which was converted to UUIDv5 in
    place) and remove the replacement subsequently created at the stable ID.
    """
    registry = er.async_get(hass)
    entries = [
        entry
        for entry in er.async_entries_for_config_entry(registry, config_entry_id)
        if entry.platform == DOMAIN and entry.domain == "update"
    ]
    repaired = 0

    for card in CARD_MANIFEST:
        stable_unique_id = f"wiser_{card['id']}_card_update"
        migrated_unique_id = get_uuid_unique_id(stable_unique_id)
        historical = next(
            (
                entry
                for entry in entries
                if entry.unique_id == migrated_unique_id
            ),
            None,
        )
        if historical is None:
            continue

        replacement = next(
            (
                entry
                for entry in entries
                if entry.unique_id == stable_unique_id
            ),
            None,
        )
        if replacement is not None:
            registry.async_remove(replacement.entity_id)
            entries.remove(replacement)

        registry.async_update_entity(
            historical.entity_id, new_unique_id=stable_unique_id
        )
        repaired += 1

    return repaired
