from __future__ import annotations
from domain.ports.observation_builder_port import ObservationBuilderPort
from domain.models.value_objects.observation import Observation
from typing import List

class MinecraftObservationBuilder(ObservationBuilderPort):
    """Adapter for converting Mineflayer's event to Domain `Observation`."""

    def build(self, *, events: List[List[dict]]) -> Observation:
        error_messages = []
        chat_messages = []

        status = {}
        inventory_dict = {}
        chests_dict = {}
        equipment_list = []
        voxels = []
        block_records = []
        entities = {}

        for event_type, event in events:
            if event_type == "onError":
                msg = event.get("onError")
                if msg:
                    error_messages.append(msg)
            elif event_type == "onChat":
                msg = event.get("onChat")
                if msg:
                    chat_messages.append(msg)
            elif event_type == "observe":
                status = event.get("status", {})
                inventory_dict = event.get("inventory", {})
                chests_dict = event.get("nearbyChests", {})
                equipment_list = status.get("equipment", [None]*6)
                voxels = event.get("voxels", [])
                block_records = event.get("blockRecords", [])
                entities = status.get("entities", {})

        inventory_items = [f"{item}: {count}" for item, count in inventory_dict.items()]
        inventory_text = (
            f"Inventory ({len(inventory_dict)}/36): " + ", ".join(inventory_items)
            if inventory_items else "Inventory (0/36): Empty"
        )

        chests_text = ", ".join(f"[{k}: {v}]" for k, v in chests_dict.items()) or "None"
        equipment_text = ", ".join(item if item else "None" for item in equipment_list)

        obs = Observation(
            biome=status.get("biome", "unknown"),
            time=status.get("timeOfDay", "unknown"),
            nearby_blocks=", ".join(voxels) or "None",
            other_blocks=", ".join(block_records) or "None",
            nearby_entities=", ".join(f"{k}: {v}" for k, v in entities.items()) or "None",
            health=f"{status.get('health', 0):.1f}/20",
            hunger=f"{status.get('food', 0):.1f}/20",
            position=status.get("position", {}),
            equipment=equipment_text,
            inventory=inventory_text,
            chests=chests_text,
            
            error_message=", ".join(filter(None, error_messages)) or "None",
            chat_message=", ".join(filter(None, chat_messages)) or "None",
        )

        return obs


# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
if __name__ == "__main__":
    builder = MinecraftObservationBuilder()

    sample_events = [['onChat', {'onChat': 'Explore success.', 'voxels': ['dirt', 'grass_block', 'grass', 'tall_grass', 'sand'], 'status': {'health': 15.499998092651367, 'food': 14, 'saturation': 0, 'oxygen': 20, 'position': {'x': 12.484598755708154, 'y': 65, 'z': 103.5}, 'velocity': {'x': 0, 'y': -0.0784000015258789, 'z': 0}, 'yaw': -3.0944688436804477, 'pitch': -6.6579310953329696e-09, 'onGround': True, 'equipment': [None, None, None, None, 'beef', None], 'name': 'bot', 'isInWater': False, 'isInLava': False, 'isCollidedHorizontally': False, 'isCollidedVertically': True, 'biome': 'plains', 'entities': {'squid': 12.692193555553986, 'salmon': 24.628961959274285}, 'timeOfDay': 'day', 'inventoryUsed': 3, 'elapsedTime': 5}, 'inventory': {'beef': 3, 'leather': 2, 'gray_wool': 1}, 'nearbyChests': {}, 'blockRecords': ['dirt', 'grass_block', 'grass', 'tall_grass', 'sand']}], ['onError', {'onError': 'Evaluation error: Runtime error: Took to long to decide path to goal!', 'voxels': ['dirt', 'grass_block', 'water', 'grass', 'tall_grass', 'tall_seagrass', 'seagrass', 'sand'], 'status': {'health': 15.499998092651367, 'food': 13, 'saturation': 0, 'oxygen': 20, 'position': {'x': 11.5, 'y': 64, 'z': 105.58307312183041}, 'velocity': {'x': 0, 'y': -0.0784000015258789, 'z': 0}, 'yaw': -1.691224125077094, 'pitch': -6.6579310953329696e-09, 'onGround': True, 'equipment': [None, None, None, None, 'beef', None], 'name': 'bot', 'isInWater': False, 'isInLava': False, 'isCollidedHorizontally': False, 'isCollidedVertically': True, 'biome': 'plains', 'entities': {'squid': 12.09025123758174, 'salmon': 18.625828873977103}, 'timeOfDay': 'day', 'inventoryUsed': 3, 'elapsedTime': 131}, 'inventory': {'beef': 3, 'leather': 2, 'gray_wool': 1}, 'nearbyChests': {}, 'blockRecords': ['dirt', 'grass_block', 'grass', 'tall_grass', 'sand', 'water', 'tall_seagrass', 'seagrass']}], ['observe', {'voxels': ['dirt', 'grass_block', 'water', 'grass', 'tall_grass', 'tall_seagrass', 'seagrass', 'sand'], 'status': {'health': 15.499998092651367, 'food': 13, 'saturation': 0, 'oxygen': 20, 'position': {'x': 11.5, 'y': 64, 'z': 105.58307312183041}, 'velocity': {'x': 0, 'y': -0.0784000015258789, 'z': 0}, 'yaw': -1.691224125077094, 'pitch': -6.6579310953329696e-09, 'onGround': True, 'equipment': [None, None, None, None, 'beef', None], 'name': 'bot', 'isInWater': False, 'isInLava': False, 'isCollidedHorizontally': False, 'isCollidedVertically': True, 'biome': 'plains', 'entities': {'squid': 12.985522953864312, 'salmon': 19.03879458392034}, 'timeOfDay': 'day', 'inventoryUsed': 3, 'elapsedTime': 139}, 'inventory': {'beef': 3, 'leather': 2, 'gray_wool': 1}, 'nearbyChests': {}, 'blockRecords': ['dirt', 'grass_block', 'grass', 'tall_grass', 'sand', 'water', 'tall_seagrass', 'seagrass']}]]

    obs = builder.build(events=sample_events)
    print(obs)