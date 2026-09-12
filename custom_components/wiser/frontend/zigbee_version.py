"""Read the installed Zigbee card version without executing JavaScript."""

from hashlib import sha256
from pathlib import Path
import re


_VERSION = r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?"


def zigbee_card_version(path: Path) -> str:
    """Resolve the card's banner variable, ignoring bundled library versions."""
    try:
        contents = path.read_bytes()
    except OSError:
        return "missing"
    source = contents.decode("utf-8", errors="replace")
    # Explicit build metadata is authoritative; legacy parsing remains below.
    marker = re.search(
        rf"/\*!\s*WISER-CARD-VERSION wiser-zigbee-card\s+({_VERSION})\s*\*/",
        source,
    )
    if marker:
        return marker[1]
    # New builds inline CARD_VERSION into the editor's version footer and
    # no longer emit the legacy startup banner.
    footer = re.search(
        rf'class=["\']version["\'][^`]*?common\.version["\']\)\}}:\s*'
        rf'\$\{{["\']({_VERSION})["\']\}}',
        source,
    )
    if footer:
        return footer[1]

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
