"""Device registry helpers for the Wiser integration."""


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
