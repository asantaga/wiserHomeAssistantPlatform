from .const import ENTITY_PREFIX

def get_device_name(data, id, type = "device"):
    if type == "device":
        device = data.wiserhub.devices.get_by_id(id)

        if id == 0:
            return f"{ENTITY_PREFIX} HeatHub ({data.wiserhub.system.name})"

        if device.product_type in ["iTRV", "RoomStat"]:
            device_room = data.wiserhub.rooms.get_by_device_id(id)
            return f"{ENTITY_PREFIX} {device.product_type} {device_room.name}"

        if device.product_type == "SmartPlug":
            return f"{ENTITY_PREFIX} {device.name}"

        return f"{ENTITY_PREFIX} {device.serial_number}"

    elif type == "room":
        room = data.wiserhub.rooms.get_by_id(id)
        return f"{ENTITY_PREFIX} {room.name}"

    else:
        return f"{ENTITY_PREFIX} {type}"
    

def get_identifier(data, id, type = "device"):
    return f"{data.wiserhub.system.name} {get_device_name(data, id, type)}"

def get_unique_id(data, device_type, entity_type, id):
    return f"{data.wiserhub.system.name}-{device_type}-{entity_type}-{id}"

def get_room_name(data, room_id):
    return f"{ENTITY_PREFIX} {data.wiserhub.rooms.get_by_id(room_id).name}"

