"""Regression tests for shared resource cleanup during entry unload."""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock


INIT_PATH = Path(__file__).parents[1] / "custom_components/wiser/__init__.py"


def _load_service_helpers(setup_services):
    tree = ast.parse(INIT_PATH.read_text())
    names = {"_shared_service_owner", "_async_refresh_shared_services"}
    functions = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in names
    ]
    namespace = {
        "DATA": "data",
        "DOMAIN": "wiser",
        "HomeAssistant": object,
        "WISER_SERVICES": {"FIRST": "first", "SECOND": "second"},
        "async_setup_services": setup_services,
    }
    exec(
        compile(ast.Module(body=functions, type_ignores=[]), str(INIT_PATH), "exec"),
        namespace,
    )
    return namespace


def _coordinator(*, hotwater):
    return SimpleNamespace(wiserhub=SimpleNamespace(hotwater=hotwater))


class UnloadLifecycleTest(unittest.IsolatedAsyncioTestCase):
    async def test_final_hub_removes_services_without_rebinding(self):
        setup_services = AsyncMock()
        helpers = _load_service_helpers(setup_services)
        hass = SimpleNamespace(
            data={"wiser": {}},
            services=SimpleNamespace(async_remove=Mock()),
        )

        await helpers["_async_refresh_shared_services"](hass)

        self.assertEqual(hass.services.async_remove.call_count, 2)
        setup_services.assert_not_awaited()

    async def test_remaining_hub_becomes_service_owner(self):
        setup_services = AsyncMock()
        helpers = _load_service_helpers(setup_services)
        remaining = _coordinator(hotwater=False)
        hass = SimpleNamespace(
            data={"wiser": {"remaining": {"data": remaining}}},
            services=SimpleNamespace(async_remove=Mock()),
        )

        await helpers["_async_refresh_shared_services"](hass)

        setup_services.assert_awaited_once_with(hass, remaining)

    async def test_hot_water_hub_owns_services_when_several_remain(self):
        setup_services = AsyncMock()
        helpers = _load_service_helpers(setup_services)
        heating_only = _coordinator(hotwater=False)
        hot_water = _coordinator(hotwater=True)
        hass = SimpleNamespace(
            data={
                "wiser": {
                    "heating": {"data": heating_only},
                    "hot_water": {"data": hot_water},
                }
            },
            services=SimpleNamespace(async_remove=Mock()),
        )

        await helpers["_async_refresh_shared_services"](hass)

        setup_services.assert_awaited_once_with(hass, hot_water)

    def test_cleanup_occurs_only_after_successful_unload(self):
        source = INIT_PATH.read_text()
        tree = ast.parse(source)
        unload = next(
            node
            for node in tree.body
            if isinstance(node, ast.AsyncFunctionDef)
            and node.name == "async_unload_entry"
        )
        unload_source = ast.get_source_segment(source, unload)

        self.assertNotIn("get_instance_count", unload_source)
        self.assertLess(
            unload_source.index("hass.data[DOMAIN].pop"),
            unload_source.index("await _async_refresh_shared_services"),
        )
        self.assertIn("if not hass.data[DOMAIN]:", unload_source)


if __name__ == "__main__":
    unittest.main()
