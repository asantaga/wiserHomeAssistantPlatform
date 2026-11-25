"""Validate all Wiser translation catalogues and their runtime keys."""

import ast
import json
from pathlib import Path
from string import Formatter
import unittest


COMPONENT_PATH = Path(__file__).parents[1] / "custom_components/wiser"
CATALOGUES = (
    COMPONENT_PATH / "strings.json",
    *sorted((COMPONENT_PATH / "translations").glob("*.json")),
)


def catalogue_leaves(value, prefix=()):
    """Return every leaf value with its full catalogue path."""
    if isinstance(value, dict):
        return {
            path: leaf
            for key, child in value.items()
            for path, leaf in catalogue_leaves(child, (*prefix, key)).items()
        }
    return {prefix: value}


class TranslationIntegrityTest(unittest.TestCase):
    """Cover all languages, including source text used by future translations."""

    def test_catalogues_have_no_duplicate_keys(self):
        def unique_object(pairs):
            result = {}
            for key, value in pairs:
                self.assertNotIn(key, result, f"Duplicate catalogue key: {key}")
                result[key] = value
            return result

        for path in (*CATALOGUES, COMPONENT_PATH / "icons.json"):
            with self.subTest(path=path.name):
                json.loads(path.read_text(), object_pairs_hook=unique_object)

    def test_every_language_has_the_complete_source_schema(self):
        reference = catalogue_leaves(json.loads(CATALOGUES[0].read_text()))
        for path in CATALOGUES[1:]:
            with self.subTest(path=path.name):
                translated = catalogue_leaves(json.loads(path.read_text()))
                self.assertEqual(set(translated), set(reference))
                for key, value in translated.items():
                    self.assertIsInstance(value, type(reference[key]), ".".join(key))

    def test_text_and_placeholders_are_valid_in_every_catalogue(self):
        reference = catalogue_leaves(json.loads(CATALOGUES[0].read_text()))
        formatter = Formatter()
        for path in CATALOGUES:
            for key, value in catalogue_leaves(json.loads(path.read_text())).items():
                if not isinstance(value, str):
                    continue
                with self.subTest(path=path.name, key=".".join(key)):
                    self.assertTrue(value.strip())
                    self.assertNotIn("[%key:", value)
                    placeholders = {
                        field for _, field, _, _ in formatter.parse(value) if field
                    }
                    expected = {
                        field for _, field, _, _ in formatter.parse(reference[key])
                        if field
                    }
                    self.assertEqual(placeholders, expected)

    def test_source_text_agrees_with_english_runtime_catalogue(self):
        source = json.loads(CATALOGUES[0].read_text())
        english = json.loads((COMPONENT_PATH / "translations/en.json").read_text())
        self.assertEqual(source, english)

    def test_external_control_and_climate_ui_text_is_localised(self):
        source = catalogue_leaves(json.loads(CATALOGUES[0].read_text()))
        keys = {
            key for key in source
            if any(part.startswith("external_") for part in key)
            or key[-1] in ("no_external_temperature_rooms", "wiser_climate_controls")
        }
        for path in CATALOGUES[1:]:
            if path.stem in ("en", "en-GB"):
                continue
            translated = catalogue_leaves(json.loads(path.read_text()))
            for key in keys:
                with self.subTest(path=path.name, key=".".join(key)):
                    self.assertNotEqual(translated[key], source[key])

    def test_static_entity_translation_keys_exist(self):
        entities = json.loads(CATALOGUES[0].read_text())["entity"]
        for path in COMPONENT_PATH.glob("*.py"):
            if path.stem not in entities:
                continue
            for node in ast.walk(ast.parse(path.read_text())):
                keys = []
                if isinstance(node, ast.keyword) and node.arg == "translation_key":
                    if isinstance(node.value, ast.Constant):
                        keys = [node.value.value]
                elif isinstance(node, ast.Assign) and any(
                    (isinstance(target, ast.Attribute)
                     and target.attr == "_attr_translation_key")
                    or (isinstance(target, ast.Name)
                        and target.id == "_attr_translation_key")
                    for target in node.targets
                ):
                    if isinstance(node.value, ast.Constant):
                        keys = [node.value.value]
                    elif (
                        isinstance(node.value, ast.Call)
                        and isinstance(node.value.func, ast.Attribute)
                        and isinstance(node.value.func.value, ast.Dict)
                    ):
                        keys = [
                            value.value for value in node.value.func.value.values
                            if isinstance(value, ast.Constant)
                        ]
                for key in keys:
                    if isinstance(key, str):
                        with self.subTest(path=path.name, line=node.lineno, key=key):
                            self.assertIn(key, entities[path.stem])

    def test_flow_errors_and_aborts_use_the_correct_translation_section(self):
        source = json.loads(CATALOGUES[0].read_text())
        tree = ast.parse((COMPONENT_PATH / "config_flow.py").read_text())
        for flow in (node for node in tree.body if isinstance(node, ast.ClassDef)):
            section = next((
                {"ConfigFlow": "config", "OptionsFlow": "options"}[base.attr]
                for base in flow.bases
                if isinstance(base, ast.Attribute)
                and base.attr in ("ConfigFlow", "OptionsFlow")
            ), None)
            if section is None:
                continue
            for node in ast.walk(flow):
                if (
                    isinstance(node, ast.Assign)
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                    and any(
                        isinstance(target, ast.Subscript)
                        and isinstance(target.value, ast.Name)
                        and target.value.id == "errors"
                        for target in node.targets
                    )
                ):
                    with self.subTest(flow=section, line=node.lineno):
                        self.assertIn(node.value.value, source[section]["error"])
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "async_abort"
                ):
                    for keyword in node.keywords:
                        if keyword.arg == "reason" and isinstance(keyword.value, ast.Constant):
                            with self.subTest(flow=section, line=node.lineno):
                                self.assertIn(keyword.value.value, source[section]["abort"])
