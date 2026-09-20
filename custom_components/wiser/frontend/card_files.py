"""Persistent, verified card overrides outside the integration installation."""

from hashlib import sha256
import json
from pathlib import Path
import tempfile

from awesomeversion import AwesomeVersion
from awesomeversion.exceptions import AwesomeVersionException

from ..const import URL_BASE

CARD_CACHE = ".storage/wiser_cards"
CARD_CACHE_URL = f"{URL_BASE}/cards"


def newer_version(candidate, installed):
    """Compare semantic release versions without offering downgrades."""
    try:
        return AwesomeVersion(candidate) > AwesomeVersion(installed)
    except (AwesomeVersionException, ValueError, TypeError):
        return False


def resolve_card(config_dir, filename, version_reader):
    """Prefer a verified downloaded card only while newer than the bundled card."""
    bundled = Path(__file__).parent / filename
    version = version_reader(bundled)
    fallback = (bundled, f"{URL_BASE}/{filename}?v={version}", version)
    directory = Path(config_dir) / CARD_CACHE
    try:
        record = json.loads((directory / f"{filename}.json").read_text())
        cached = directory / record["file"]
        # Metadata must not redirect static serving outside the card cache.
        digest = record["digest"]
        expected = f"{Path(filename).stem}-{digest}.js"
        if record["file"] != expected or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return fallback
        if not newer_version(record["version"], version):
            return fallback
        if sha256(cached.read_bytes()).hexdigest() != digest:
            return fallback
        return cached, f"{CARD_CACHE_URL}/{cached.name}?v={record['version']}", record["version"]
    except (OSError, ValueError, KeyError, TypeError):
        return fallback


def store_card(config_dir, filename, version, contents):
    """Write immutable assets, then atomically switch the active metadata."""
    directory = Path(config_dir) / CARD_CACHE
    directory.mkdir(parents=True, exist_ok=True)
    digest = sha256(contents).hexdigest()
    asset_name = f"{Path(filename).stem}-{digest}.js"
    _atomic_write(directory / asset_name, contents)
    metadata = {"file": asset_name, "version": version, "digest": digest}
    _atomic_write(directory / f"{filename}.json", json.dumps(metadata).encode())


def _atomic_write(path, contents):
    """Keep the previous working file intact if a write fails."""
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(contents)
            stream.flush()
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
