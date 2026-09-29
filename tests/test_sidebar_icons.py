"""Check custom sidebar icons load without opening a Lovelace dashboard."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

ROOT = Path(__file__).resolve().parents[1] / "custom_components/wiser/frontend"


class SidebarIconsTest(unittest.IsolatedAsyncioTestCase):
    def test_icons_include_official_wiser_w(self):
        source = (ROOT / "wiser-icons.js").read_text()
        self.assertIn('wiser: {', source)
        self.assertIn('viewBox: "0 0 877 768"', source)
        self.assertIn('{ name: "wiser", keywords:', source)

    async def test_icons_register_after_static_path_without_lovelace(self):
        tree = ast.parse((ROOT / "__init__.py").read_text())
        cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "JSModuleRegistration")
        method = next(node for node in cls.body if isinstance(node, ast.AsyncFunctionDef) and node.name == "async_register")
        register = Mock()
        version = Mock(return_value="sha256-icons")
        namespace = {
            "__file__": str(ROOT / "__init__.py"), "Path": Path,
            "card_version": version, "add_extra_js_url": register,
            "async_load_registry": AsyncMock(),
            "URL_BASE": "/wiser", "MODE_STORAGE": "storage",
        }
        exec(compile(ast.Module(body=[method], type_ignores=[]), str(ROOT / "__init__.py"), "exec"), namespace)
        host = SimpleNamespace(
            hass=SimpleNamespace(async_add_executor_job=AsyncMock(side_effect=lambda fn, *args: fn(*args))),
            lovelace=None,
            _async_register_path=AsyncMock(),
            _async_wait_for_lovelace_resources=AsyncMock(),
        )
        register.side_effect = lambda *args: host._async_register_path.assert_awaited_once()
        await namespace["async_register"](host)
        version.assert_called_once_with(ROOT / "wiser-icons.js")
        register.assert_called_once_with(host.hass, "/wiser/wiser-icons.js?v=sha256-icons")
        host._async_wait_for_lovelace_resources.assert_not_awaited()
