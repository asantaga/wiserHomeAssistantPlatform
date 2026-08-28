"""Device registry helpers for the Wiser integration."""


def register_room_assigned_device(
    device_registry,
    config_entry_id,
    identifier,
    parent_device_id,
    suggested_area,
    **device_info,
):
    """Register a physical device in its Wiser room on first creation."""
    return device_registry.async_get_or_create(
        config_entry_id=config_entry_id,
        identifiers={identifier},
        suggested_area=suggested_area,
        via_device_id=parent_device_id,
        **device_info,
    )


def register_hub_device(
    device_registry,
    config_entry_id,
    identifier,
    legacy_identifier,
    connection,
    **device_info,
):
    """Register one HeatHub device, migrating the legacy Controller device."""
    get_by_identifier = getattr(
        device_registry, "async_get_device_by_identifier", None
    )

    if get_by_identifier:
        hub_device = get_by_identifier(identifier, config_entry_id)
        legacy_device = get_by_identifier(legacy_identifier, config_entry_id)
    else:
        hub_device = device_registry.async_get_device(identifiers={identifier})
        legacy_device = device_registry.async_get_device(
            identifiers={legacy_identifier}
        )

    if hub_device:
        return device_registry.async_update_device(
            hub_device.id,
            new_connections={connection},
            new_identifiers={identifier},
            via_device_id=None,
            **device_info,
        )

    if legacy_device:
        return device_registry.async_update_device(
            legacy_device.id,
            new_connections={connection},
            new_identifiers={identifier},
            via_device_id=None,
            **device_info,
        )

    return device_registry.async_get_or_create(
        config_entry_id=config_entry_id,
        connections={connection},
        identifiers={identifier},
        **device_info,
    )


def merge_legacy_hub_device(
    device_registry,
    entity_registry,
    config_entry_id,
    identifier,
    legacy_identifier,
):
    """Move legacy Controller entities to the HeatHub and remove the duplicate."""
    get_by_identifier = getattr(
        device_registry, "async_get_device_by_identifier", None
    )
    if get_by_identifier:
        hub_device = get_by_identifier(identifier, config_entry_id)
        legacy_device = get_by_identifier(legacy_identifier, config_entry_id)
    else:
        hub_device = device_registry.async_get_device(identifiers={identifier})
        legacy_device = device_registry.async_get_device(
            identifiers={legacy_identifier}
        )

    if hub_device is None or legacy_device is None:
        return False

    for entity in list(entity_registry.entities.values()):
        if entity.device_id == legacy_device.id:
            entity_registry.async_update_entity(
                entity.entity_id, device_id=hub_device.id
            )

    device_registry.async_remove_device(legacy_device.id)
    return True


def migrate_room_device(
    device_registry,
    entity_registry,
    config_entry_id,
    identifier,
    legacy_identifier,
    name,
):
    """Migrate a name-derived Wiser room device to its stable identifier."""
    get_by_identifier = getattr(
        device_registry, "async_get_device_by_identifier", None
    )
    if get_by_identifier:
        room_device = get_by_identifier(identifier, config_entry_id)
        legacy_device = get_by_identifier(legacy_identifier, config_entry_id)
    else:
        room_device = device_registry.async_get_device(identifiers={identifier})
        legacy_device = device_registry.async_get_device(
            identifiers={legacy_identifier}
        )

    if room_device is not None:
        device_registry.async_update_device(
            room_device.id, new_identifiers={identifier}, name=name
        )
        if legacy_device is not None and legacy_device.id != room_device.id:
            for entity in list(entity_registry.entities.values()):
                if entity.device_id == legacy_device.id:
                    entity_registry.async_update_entity(
                        entity.entity_id, device_id=room_device.id
                    )
            device_registry.async_remove_device(legacy_device.id)
        return room_device

    if legacy_device is not None:
        return device_registry.async_update_device(
            legacy_device.id,
            new_identifiers={identifier},
            name=name,
        )

    return None
