"""Validate frontend definitions consistently during packaging and runtime."""

import re


REGISTRY_SCHEMA_VERSION = 1


def validate_registry(value):
    """Validate the versioned registry while accepting legacy card arrays."""
    if isinstance(value, list):
        return validate_manifest(value)
    if not isinstance(value, dict):
        raise ValueError("Invalid frontend registry document")
    if value.get("schema_version") != REGISTRY_SCHEMA_VERSION:
        raise ValueError("Unsupported frontend registry schema version")
    return validate_manifest(value.get("cards"))


def validate_manifest(value):
    """Validate names and paths before using a remotely supplied registry."""
    if not isinstance(value, list) or not 1 <= len(value) <= 100:
        raise ValueError("Frontend registry must contain between 1 and 100 cards")
    seen = {key: set() for key in ("id", "filename", "component", "panel")}
    patterns = {
        "id": r"[a-z0-9-]+",
        "filename": r"wiser-[a-z0-9-]+-(?:card|panel)\.js",
        "repository": r"[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+",
        "component": r"wiser-[a-z0-9-]+",
        "panel": r"wiser-[a-z0-9-]+-panel",
    }
    result = []
    for card in value:
        if not isinstance(card, dict):
            raise ValueError("Invalid frontend card definition")
        name = card.get("name")
        if not isinstance(name, str) or not name.strip() or len(name) > 100:
            raise ValueError("Invalid frontend card name")
        for key, pattern in patterns.items():
            item = card.get(key)
            if key == "panel" and item is None:
                continue
            if not isinstance(item, str) or not re.fullmatch(pattern, item):
                raise ValueError(f"Invalid frontend card {key}")
            if key in seen:
                if item in seen[key]:
                    raise ValueError(f"Duplicate frontend card {key}")
                seen[key].add(item)
        legacy_filenames = card.get("legacy_filenames", [])
        if not isinstance(legacy_filenames, list):
            raise ValueError("Invalid frontend card legacy filenames")
        for filename in legacy_filenames:
            if (
                not isinstance(filename, str)
                or not re.fullmatch(patterns["filename"], filename)
                or filename in seen["filename"]
            ):
                raise ValueError("Invalid or duplicate frontend legacy filename")
            seen["filename"].add(filename)
        definition = {key: card.get(key) for key in ("name", *patterns)}
        is_card = card.get("card", True)
        if type(is_card) is not bool:
            raise ValueError("Invalid frontend card flag")
        if not is_card:
            definition["card"] = False
        if legacy_filenames:
            definition["legacy_filenames"] = legacy_filenames
        result.append(definition)
    return result
