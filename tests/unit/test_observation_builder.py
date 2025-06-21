# tests/unit/prompts/test_minecraft_observation_builder.py
import pytest
from domain.ports.observation_builder_port import ObservationBuilderPort
from domain.models import Event, Task, Observation


# ---------- Fixtures -------------------------------------------------
@pytest.fixture(scope="module")
def builder() -> ObservationBuilderPort:
    return ObservationBuilderPort()


@pytest.fixture
def base_event() -> Event:
    """最小構成の Event。各 parametrize ケースで .copy(update=…) して改変。"""
    return Event(
        position={"x": 10.5, "y": 64.0, "z": -5.2},
        inventory={"wooden_pickaxe": 1},
        health=20.0,
        hunger=20.0,
        biome="plains",
        nearby_blocks=["grass"],
        nearby_entities={},
        time="day",
        other_blocks="",
        equipment={},
        chests="",
    )


# ---------- 1. 型と必須フィールドだけをまとめて確認 ----------------------
def test_basic_shape(builder, base_event):
    obs = builder.build(event=base_event, completed=[], failed=[])
    assert isinstance(obs, Observation)
    for attr in (
        "biome",
        "time",
        "nearby_blocks",
        "health",
        "hunger",
        "position",
        "inventory",
    ):
        assert getattr(obs, attr)  # 空文字列でない


# ---------- 2. health / hunger の境界値は parametrize 1 本で ----------
@pytest.mark.parametrize(
    "health,hunger,expect",
    [
        (20.0, 20.0, ("Health: 20.0/20\n\n", "Hunger: 20.0/20\n\n")),
        (0.0, 0.0, ("Health: 0.0/20\n\n", "Hunger: 0.0/20\n\n")),
    ],
)
def test_health_hunger_format(builder, base_event, health, hunger, expect):
    e = base_event.copy(update={"health": health, "hunger": hunger})
    obs = builder.build(event=e, completed=[], failed=[])
    assert (obs.health, obs.hunger) == expect


# ---------- 3. インベントリ件数のバリエーション --------------------------
@pytest.mark.parametrize("inv_size", [0, 5, 20])
def test_inventory_count(builder, base_event, inv_size):
    inventory = {f"item_{i}": 1 for i in range(inv_size)}
    e = base_event.copy(update={"inventory": inventory})
    obs = builder.build(event=e, completed=[], failed=[])
    assert f"Inventory ({inv_size}/36)" in obs.inventory


# ---------- 4. completed / failed task の描画 ---------------------------
def test_task_strings(builder, base_event):
    completed = [Task(task="Mine wood", reasoning="", context="")]
    failed = [Task(task="Craft diamond", reasoning="", context="")]
    obs = builder.build(event=base_event, completed=completed, failed=failed)
    assert obs.completed_tasks == "Mine wood"
    assert obs.failed_tasks == "Craft diamond"


# ---------- 5. 複数チェスト行はそのまま保持 ------------------------------
def test_chest_multiline(builder, base_event):
    chest_text = "Chest 1: iron_ingot\nChest 2: coal"
    e = base_event.copy(update={"chests": chest_text})
    obs = builder.build(event=e, completed=[], failed=[])
    assert obs.chests == chest_text
