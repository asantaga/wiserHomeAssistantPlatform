"""Helpers for publishing the Wiser Zigbee network."""

from __future__ import annotations

from typing import Any


def build_zigbee_network_data(wiserhub: Any) -> dict[str, list[dict[str, Any]]]:
    """Build a physical Zigbee graph from the hub's logical devices."""
    nodes = [{"id": 0, "label": "Wiser Hub", "group": "Controller"}]
    edges = []
    seen_node_ids = {0}

    for device in wiserhub.devices.all:
        node_id = device.node_id
        if node_id in seen_node_ids:
            continue
        seen_node_ids.add(node_id)

        room = wiserhub.rooms.get_by_device_id(device.id)
        nodes.append(
            {
                "id": node_id,
                "label": f"{device.name}\n({room.name if room else 'No Room'})",
                "group": device.product_type,
            }
        )

        if device.product_type in ["SmartPlug", "HeatingActuator"]:
            lqi = device.signal.displayed_signal_strength
        else:
            lqi = (
                f"{device.signal.displayed_signal_strength} "
                f"({device.signal.controller_signal_strength}%)"
            )

        edge = {
            "id": f"{node_id}-{device.parent_node_id}",
            "from": node_id,
            "to": device.parent_node_id,
            "label": lqi,
        }
        if lqi == "NoSignal":
            edge["color"] = "#db4437"

        edges.append(edge)

    return {"nodes": nodes, "edges": edges}
