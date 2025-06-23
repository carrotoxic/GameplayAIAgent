from __future__ import annotations
import re

from domain.ports.observation_builder_port import ObservationBuilderPort
from domain.models import Observation, Event

class MinecraftObservationBuilder(ObservationBuilderPort):
    """Adapter for converting Mineflayer's observation to Domain `Observation`."""

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    def build(self, *,event: Event) -> Observation:
        # --------- format basic fields ------------------------
        inv_text = (
            f"Inventory ({len(event.inventory)}/36): "
            f"{event.inventory or 'Empty'}"
        )

        obs = Observation(
            biome=event.biome,
            time=event.time,
            nearby_blocks=', '.join(event.nearby_blocks) or 'None',
            other_blocks=event.other_blocks or 'None',
            nearby_entities=event.nearby_entities or 'None',
            health=f"{event.health:.1f}/20",
            hunger=f"{event.hunger:.1f}/20",
            position=event.position,
            equipment=event.equipment,
            inventory=inv_text,
            # TODO: ここのchestsのフォーマットを修正する
            chests=event.chests,
        )

        # TODO: add warmup filtering
        # # ---- Warm-up フィルタリング --------------------------------------
        # filtered_lines = {
        #     key: val
        #     for key, val in lines.items()
        #     if progress >= warmup[key]
        # }

        return obs


# ------------------------------------------------------------
# Test
# ------------------------------------------------------------
if __name__ == "__main__":
    builder = MinecraftObservationBuilder()

    event = Event(
        position={"x": 10.5, "y": 64.0, "z": -5.2},
        inventory={"oak_log": 3, "wooden_pickaxe": 1},
        health=18.5,
        hunger=15.0,
        biome="forest",
        nearby_blocks=["grass", "dirt", "stone", "oak_log"],
        nearby_entities={"cow": 5.0},
        time="day",
        other_blocks="iron_ore",
        equipment={"helmet": "leather_helmet"},
        chests={"Chest 1": "iron_ingot: 8", "Chest 2": "iron_ingot: 8"},
    )

    print(builder.build(event=event))