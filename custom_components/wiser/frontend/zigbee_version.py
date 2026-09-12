"""Read the installed Zigbee card version without executing JavaScript."""

from hashlib import sha256
from pathlib import Path
import re


_VERSION = r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?"


def zigbee_card_version(path: Path, fallback: str) -> str:
    """Resolve the card's banner variable, ignoring bundled library versions."""
    try:
        contents = path.read_bytes()
    except OSError:
        return fallback
    source = contents.decode("utf-8", errors="replace")
    banner = re.search(
        r'WISER-ZIGBEE(?:-NETWORK)?-CARD[^`]*?common\.version[\"\']\)\}\s*\$\{([\w$]+)\}',
        source,
    )
    if banner:
        assignment = re.search(
            rf'(?<![\w$]){re.escape(banner[1])}\s*=\s*[\"\']({_VERSION})[\"\']',
            source,
        )
        if assignment:
            return assignment[1]
    # Still refresh caches for unfamiliar builds rather than advertise a stale
    # version from const.py. This is a content identifier, not a release number.
    return f"sha256-{sha256(contents).hexdigest()[:16]}"
