"""Device registry helpers for the Wiser integration."""


def assign_device_area_if_unset(
    device_registry, area_registry, device, suggested_area
):
    """Assign a device to its Wiser room without overriding a user area."""
    if device is None or device.area_id is not None or not suggested_area:
        return device

    area = area_registry.async_get_or_create(suggested_area)
    return device_registry.async_update_device(device.id, area_id=area.id)


def move_devices_from_managed_area(
    device_registry,
    area_registry,
    devices,
    previous_area_name,
    new_area_name,
):
    """Move Wiser devices that remain in their previous managed area."""
    if not previous_area_name or previous_area_name == new_area_name:
        return 0

    previous_area = area_registry.async_get_area_by_name(previous_area_name)
    if previous_area is None:
        return 0

    new_area = area_registry.async_get_or_create(new_area_name)
    moved = 0
    for device in {device.id: device for device in devices if device}.values():
        if device.area_id != previous_area.id:
            continue
        device_registry.async_update_device(device.id, area_id=new_area.id)
        moved += 1
    return moved


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


def migrate_physical_device(
    device_registry,
    entity_registry,
    config_entry_id,
    identifier,
    candidates,
    name,
    via_device=None,
    **device_info,
):
    """Give a physical device a stable ID and merge duplicate registry rows."""
    get_by_identifier = getattr(
        device_registry, "async_get_device_by_identifier", None
    )
    stable_device = (
        get_by_identifier(identifier, config_entry_id)
        if get_by_identifier
        else device_registry.async_get_device(identifiers={identifier})
    )

    candidates = list({device.id: device for device in candidates}.values())
    if stable_device is not None and all(
        device.id != stable_device.id for device in candidates
    ):
        candidates.append(stable_device)
    if candidates:
        canonical = min(
            candidates,
            key=lambda device: (
                getattr(device, "created_at", None) is None,
                getattr(device, "created_at", None),
                device.id,
            ),
        )
    else:
        canonical = None

    if canonical is None:
        create_info = {
            key: value
            for key, value in device_info.items()
            if key != "via_device_id"
        }
        if via_device is not None:
            create_info["via_device"] = via_device
        return device_registry.async_get_or_create(
            config_entry_id=config_entry_id,
            identifiers={identifier},
            name=name,
            **create_info,
        )

    for duplicate in candidates:
        if duplicate.id == canonical.id:
            continue
        for entity in list(entity_registry.entities.values()):
            if entity.device_id == duplicate.id:
                entity_registry.async_update_entity(
                    entity.entity_id, device_id=canonical.id
                )
        device_registry.async_remove_device(duplicate.id)
    return device_registry.async_update_device(
        canonical.id,
        new_identifiers={identifier},
        name=name,
        **device_info,
    )


def migrate_entity_unique_id_duplicates(
    entity_registry,
    entries,
    new_unique_id,
):
    """Keep the oldest entity while replacing duplicate historical IDs."""
    entries = list({entry.entity_id: entry for entry in entries}.values())
    if not entries:
        return None

    existing_entity_id = entity_registry.async_get_entity_id(
        entries[0].domain, entries[0].platform, new_unique_id
    )
    existing = (
        entity_registry.async_get(existing_entity_id)
        if existing_entity_id is not None
        else None
    )
    if existing is not None and all(
        entry.entity_id != existing.entity_id for entry in entries
    ):
        entries.append(existing)
    canonical = min(
        entries,
        key=lambda entry: (
            getattr(entry, "created_at", None) is None,
            getattr(entry, "created_at", None),
            entry.entity_id,
        ),
    )
    for duplicate in entries:
        if duplicate.entity_id != canonical.entity_id:
            entity_registry.async_remove(duplicate.entity_id)
    if canonical.unique_id != new_unique_id:
        entity_registry.async_update_entity(
            canonical.entity_id, new_unique_id=new_unique_id
        )
    return canonical


def migrate_room_entities(
    entity_registry,
    room_device_id,
    unique_id_for_type,
):
    """Migrate room-name-derived entities and remove their duplicates."""
    groups = {}
    for entry in list(entity_registry.entities.values()):
        if entry.device_id != room_device_id or entry.platform != "wiser":
            continue

        entity_type = None
        translation_key = getattr(entry, "translation_key", None)
        if entry.domain == "climate":
            entity_type = "climate"
        elif entry.domain == "switch" and translation_key:
            entity_type = f"switch_{translation_key}"
        elif entry.domain == "sensor":
            if translation_key == "heating_demand":
                entity_type = "heating_demand"
            elif translation_key == "target_temperature":
                entity_type = "current_target_temp"
            elif (
                translation_key is None
                and "temperature"
                in {
                    str(getattr(entry, "device_class", None)),
                    str(getattr(entry, "original_device_class", None)),
                }
            ):
                entity_type = "current_temp"

        if entity_type is not None:
            groups.setdefault(entity_type, []).append(entry)

    for entity_type, entries in groups.items():
        migrate_entity_unique_id_duplicates(
            entity_registry,
            entries,
            unique_id_for_type(entity_type),
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
    via_device=None,
):
    """Migrate or create a Wiser room device with its stable identifier."""
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
        updates = {"new_identifiers": {identifier}, "name": name}
        if (
            room_device.area_id is None
            and legacy_device is not None
            and legacy_device.area_id is not None
        ):
            updates["area_id"] = legacy_device.area_id
        room_device = device_registry.async_update_device(room_device.id, **updates)
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

    create_info = {}
    if via_device is not None:
        create_info["via_device"] = via_device
    return device_registry.async_get_or_create(
        config_entry_id=config_entry_id,
        identifiers={identifier},
        name=name,
        **create_info,
    )


def remove_room_devices(
    device_registry,
    entity_registry,
    config_entry_id,
    identifiers,
):
    """Remove deleted logical room devices and their registry entities."""
    get_by_identifier = getattr(
        device_registry, "async_get_device_by_identifier", None
    )
    removed_device_ids = set()

    for identifier in identifiers:
        device = (
            get_by_identifier(identifier, config_entry_id)
            if get_by_identifier
            else device_registry.async_get_device(identifiers={identifier})
        )
        if device is None or device.id in removed_device_ids:
            continue

        for entity in list(entity_registry.entities.values()):
            if entity.device_id == device.id:
                entity_registry.async_remove(entity.entity_id)

        device_registry.async_remove_device(device.id)
        removed_device_ids.add(device.id)

    return len(removed_device_ids)
