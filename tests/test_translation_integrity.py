"""Validate JSON catalogue keys without silently accepting shadowed entries."""

import json
from pathlib import Path
import unittest


COMPONENT_PATH = Path(__file__).parents[1] / "custom_components/wiser"


class TranslationCatalogueIntegrityTest(unittest.TestCase):
    def test_translation_catalogues_have_no_duplicate_keys(self):
        def unique_object(pairs):
            result = {}
            for key, value in pairs:
                self.assertNotIn(key, result, f"Duplicate catalogue key: {key}")
                result[key] = value
            return result

        paths = [COMPONENT_PATH / "strings.json", COMPONENT_PATH / "icons.json"]
        paths.extend(sorted((COMPONENT_PATH / "translations").glob("*.json")))
        for path in paths:
            with self.subTest(path=path.name):
                json.loads(
                    path.read_text(encoding="utf-8"), object_pairs_hook=unique_object
                )
