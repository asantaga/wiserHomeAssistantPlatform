"""Regression tests for Wiser services."""

import ast
from pathlib import Path
import unittest


SERVICES_PATH = (
    Path(__file__).resolve().parents[1] / "custom_components/wiser/services.py"
)


class ScheduleExportDirectoryTest(unittest.TestCase):
    """Test schedule export directory creation."""

    def test_directory_creation_does_not_depend_on_aiofiles_os(self) -> None:
        """Directory creation uses the HA executor without importing aiofiles."""
        source = SERVICES_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported_modules = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }

        self.assertFalse(
            any(
                module == "aiofiles" or module.startswith("aiofiles.")
                for module in imported_modules
            )
        )
        self.assertIn("hass.async_add_executor_job", source)
        self.assertIn(
            "partial(os.makedirs, file_dir, exist_ok=True)",
            source,
        )
