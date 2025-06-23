from __future__ import annotations
import re
from typing import List

from domain.ports.observation_builder_port import ObservationBuilderPort
from domain.models import Observation, Event, Task

class MinecraftObservationBuilder(ObservationBuilderPort):
    """Adapter for converting Mineflayer's observation to Domain `Observation`."""

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    def build(
        self,
        *,
        event: Event,
        completed: List[Task],
        failed: List[Task],
    ) -> Observation:
        # --------- format basic fields ------------------------
        inv_text = (
            f"Inventory ({len(event.inventory)}/36): "
            f"{event.inventory or 'Empty'}"
        )

        obs = Observation(
            context="",                             # 後で QA で追記しても良い
            biome=f"Biome: {event.biome}",
            time=f"Time: {event.time}",
            nearby_blocks=f"Nearby blocks: {', '.join(event.nearby_blocks) or 'None'}",
            other_blocks=f"Other blocks: {event.other_blocks or 'None'}",
            nearby_entities=f"Nearby entities: {event.nearby_entities or 'None'}",
            health=f"Health: {event.health:.1f}/20",
            hunger=f"Hunger: {event.hunger:.1f}/20",
            position=(
                f"Position: x={event.position['x']:.1f}, "
                f"y={event.position['y']:.1f}, "
                f"z={event.position['z']:.1f}"
            ),
            equipment=f"Equipment: {event.equipment}",
            inventory=inv_text,
            chests=event.chests,
            completed_tasks="\n".join(t.command for t in completed),
            failed_tasks="\n".join(t.command for t in failed),
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
        chests="Chest 1: iron_ingot: 8",
    )

    tasks = [
        Task(command="Mine 1 wood log", reasoning="Need wood", context="Tutorial"),
        Task(command="Craft wooden pickaxe", reasoning="Need tool", context="Early-game crafting"),
    ]

    print(builder.build(event=event, completed=tasks[:1], failed=tasks[1:]))