"""Verify shared artwork naming, aliases, provenance, and old URL retention."""

from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "prepare_device_images", ROOT / "scripts/prepare-device-images.py"
)
ARTWORK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ARTWORK)


class PrepareDeviceImagesTest(unittest.TestCase):
    def test_catalogue_deduplicates_aliases_and_preserves_provenance(self):
        sources = {
            "OnOffLight": {"file": "power.png", "source": "https://example.com/power"},
            "LoadControl": {"file": "power.png", "source": "https://example.com/power"},
        }
        existing = json.loads((ARTWORK.IMAGES / "manifest.json").read_text())
        png = (ARTWORK.IMAGES.parent / existing["OnOffLight"].removeprefix("/wiser/")).read_bytes()
        with TemporaryDirectory() as directory:
            output = Path(directory)
            urls = ARTWORK.write_catalogue(output, sources, {"power.png": png})
            self.assertEqual(urls["OnOffLight"], urls["LoadControl"])
            filename = f"power-{sha256(png).hexdigest()[:12]}.png"
            self.assertEqual(urls["OnOffLight"], f"/wiser/images/devices/{filename}")
            self.assertEqual((output / "devices" / filename).read_bytes(), png)
            self.assertEqual(len(list((output / "devices").iterdir())), 1)
            self.assertEqual(json.loads((output / "SOURCES.json").read_text()), sources)
            self.assertEqual(json.loads((output / "manifest.json").read_text()), urls)
            # A new image URL must not break an older independently released card.
            replacement = (ARTWORK.IMAGES.parent / existing["RoomStat"].removeprefix("/wiser/")).read_bytes()
            updated = ARTWORK.write_catalogue(output, sources, {"power.png": replacement})
            self.assertNotEqual(updated["OnOffLight"], urls["OnOffLight"])
            self.assertTrue((output / "devices" / filename).exists())
            self.assertEqual(len(list((output / "devices").iterdir())), 2)

    def test_every_catalogue_source_has_preparation_input(self):
        sources = json.loads((ARTWORK.IMAGES / "SOURCES.json").read_text())
        self.assertEqual(
            {Path(entry["file"]).stem for entry in sources.values()},
            set(ARTWORK.SOURCE_FILES),
        )
