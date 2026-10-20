"""Tests for the Wiser Zigbee network response."""

import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace

SPEC = importlib.util.spec_from_file_location(
    "wiser_zigbee",
    Path(__file__).resolve().parents[1] / "custom_components/wiser/zigbee.py",
)
ZIGBEE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ZIGBEE)
build_zigbee_network_data = ZIGBEE.build_zigbee_network_data


def device(
    node_id: int,
    device_id: int,
    name: str,
    product_type: str = "DimmableLight",
) -> SimpleNamespace:
    """Create a minimal Wiser device for graph tests."""
    return SimpleNamespace(
        node_id=node_id,
        id=device_id,
        name=name,
        product_type=product_type,
        parent_node_id=0,
        signal=SimpleNamespace(
            displayed_signal_strength="VeryGood",
            controller_signal_strength=92,
        ),
    )


class ZigbeeNetworkTests(unittest.TestCase):
    """Test physical Zigbee graph generation."""

    def test_logical_devices_sharing_a_node_are_merged(self) -> None:
        """Expose one graph node for a multi-function physical device."""
        dimmer = device(47777, 2, "Loftlampe")
        button_panel = device(47777, 2, "DimmableLight-2")
        relay_channel_one = device(
            51538, 3001, "Dobbeltrelæ Loftlampe", "OnOffLight"
        )
        relay_channel_two = device(
            51538, 3002, "Dobbeltrelæ Bordlampe", "OnOffLight"
        )
        rooms = SimpleNamespace(
            get_by_device_id=lambda device_id: SimpleNamespace(name="Stue")
        )
        wiserhub = SimpleNamespace(
            devices=SimpleNamespace(
                all=[dimmer, button_panel, relay_channel_one, relay_channel_two]
            ),
            rooms=rooms,
        )

        result = build_zigbee_network_data(wiserhub)

        self.assertEqual(
            [node["id"] for node in result["nodes"]], [0, 47777, 51538]
        )
        self.assertEqual(
            [node["label"] for node in result["nodes"]],
            ["Wiser Hub", "Loftlampe\n(Stue)", "Dobbeltrelæ Loftlampe\n(Stue)"],
        )
        self.assertEqual(
            [edge["id"] for edge in result["edges"]],
            ["47777-0", "51538-0"],
        )


if __name__ == "__main__":
    unittest.main()
