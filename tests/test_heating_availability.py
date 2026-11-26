"""Exercise heating refresh failures without a Home Assistant installation."""

import ast
import asyncio
from datetime import datetime
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

from test_ui_options import load_functions


class UpdateFailed(Exception):
    pass


class HubError(Exception):
    pass


class HeatingRefreshAvailabilityTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.dispatch = Mock()
        self.update = load_functions("coordinator.py", {"async_update_data"}, {
            "asyncio": asyncio,
            "datetime": datetime,
            "_LOGGER": logging.getLogger(__name__),
            "WiserHubConnectionError": HubError,
            "WiserHubAuthenticationError": HubError,
            "WiserHubRESTError": HubError,
            "UpdateFailed": UpdateFailed,
            "DOMAIN": "wiser",
            "CONF_NAME": "name",
            "async_dispatcher_send": self.dispatch,
        }).async_update_data
        self.coordinator = SimpleNamespace(
            wiserhub=SimpleNamespace(
                read_hub_data=AsyncMock(),
                system=SimpleNamespace(hardware_generation=1, name="hub"),
            ),
            external_room_control=SimpleNamespace(async_update=AsyncMock()),
            config_entry=SimpleNamespace(data={"name": "hub"}),
            hass=object(),
        )

    async def test_failed_read_raises_update_failed_and_can_recover(self):
        for error in (HubError("offline"), ValueError("bad response")):
            with self.subTest(error=type(error).__name__):
                self.coordinator.wiserhub.read_hub_data.side_effect = error
                with self.assertRaises(UpdateFailed) as caught:
                    await self.update(self.coordinator)
                self.assertIs(caught.exception.__cause__, error)
                self.assertEqual(self.coordinator.last_update_status, "Failed")
                self.dispatch.assert_not_called()
                self.coordinator.external_room_control.async_update.assert_not_awaited()
        self.coordinator.wiserhub.read_hub_data.side_effect = None
        self.assertTrue(await self.update(self.coordinator))
        self.assertEqual(self.coordinator.last_update_status, "Success")
        self.dispatch.assert_called_once()

    async def test_cancellation_propagates(self):
        for target in (
            self.coordinator.wiserhub.read_hub_data,
            self.coordinator.external_room_control.async_update,
        ):
            with self.subTest(target=target):
                target.side_effect = asyncio.CancelledError()
                with self.assertRaises(asyncio.CancelledError):
                    await self.update(self.coordinator)
                target.side_effect = None
        self.dispatch.assert_not_called()

    async def test_external_control_failure_does_not_hide_fresh_hub_data(self):
        self.coordinator.external_room_control.async_update.side_effect = ValueError(
            "external entity failed"
        )
        self.assertTrue(await self.update(self.coordinator))
        self.assertEqual(self.coordinator.last_update_status, "Success")


class RoomHeatingActionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = Path(__file__).parents[1] / "custom_components/wiser/climate.py"
        tree = ast.parse(source.read_text())
        entity = next(
            n for n in tree.body
            if isinstance(n, ast.ClassDef) and n.name == "WiserRoom"
        )
        entity.bases = [ast.Name(id="Base", ctx=ast.Load())]
        entity.body = [
            n for n in entity.body if isinstance(n, ast.FunctionDef)
            and n.name in {"hvac_action", "extra_state_attributes"}
        ]
        base = type("Base", (), {"state_attributes": property(lambda self: {})})
        namespace = {
            "Base": base,
            "HVACAction": SimpleNamespace(HEATING="heating", IDLE="idle"),
        }
        module = ast.Module(body=[entity], type_ignores=[])
        ast.fix_missing_locations(module)
        exec(compile(module, str(source), "exec"), namespace)
        cls.entity_class = namespace["WiserRoom"]

    def test_unknown_heating_is_not_reported_as_idle(self):
        for heating, expected in ((True, "heating"), (False, "idle"), (None, None)):
            with self.subTest(heating=heating):
                entity = self.entity_class()
                entity._room = SimpleNamespace(is_heating=heating)
                self.assertEqual(entity.hvac_action, expected)

    def test_unknown_heating_attributes_do_not_claim_output_is_off(self):
        for heating, output in ((True, "On"), (False, "Off"), (None, None)):
            with self.subTest(heating=heating):
                entity = self.entity_class()
                entity._room_id = 1
                entity._room = Mock(
                    is_heating=heating, is_override=False, is_boosted=False,
                    is_passive_mode=False, boost_time_remaining=0, schedule=None,
                    devices=[],
                )
                entity._data = SimpleNamespace(
                    hub_version=1, wiser_climate_controls=False,
                    wiserhub=SimpleNamespace(system=SimpleNamespace(opentherm=None)),
                    external_room_control=Mock(
                        has_passive_override=Mock(return_value=False),
                        has_assignment=Mock(return_value=False),
                        is_active=Mock(return_value=False),
                    ),
                )
                entity.data = entity._data
                entity._external_temperature_attributes = lambda: {}
                attributes = entity.extra_state_attributes
                self.assertIs(attributes["is_heating"], heating)
                self.assertEqual(attributes["control_output_state"], output)
