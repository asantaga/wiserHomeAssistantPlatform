"""Validate frontend definitions consistently during packaging and runtime."""

import re


def validate_manifest(value):
    """Validate names and paths before using a remotely supplied registry."""
    if not isinstance(value, list) or not 1 <= len(value) <= 100:
        raise ValueError("Frontend registry must contain between 1 and 100 cards")
    seen = {key: set() for key in ("id", "filename", "component", "panel")}
    patterns = {
        "id": r"[a-z0-9-]+",
        "filename": r"wiser-[a-z0-9-]+-card\.js",
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
        result.append({key: card.get(key) for key in ("name", *patterns)})
    return result


