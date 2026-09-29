"""神器觉醒与符文镶嵌系统"""
import random
from dataclasses import dataclass, field

@dataclass
class Rune:
    rid: str
    name: str
    slot_type: str  # attack/defense/special
    series: str
    stats: dict = field(default_factory=dict)

@dataclass
class Artifact:
    aid: str
    name: str
    awakening_level: int = 0
    max_awakening: int = 10
    rune_slots: dict[str, Rune | None] = field(default_factory=dict)
    skills: dict = field(default_factory=dict)  # level -> skill

class AwakeningSystem:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.artifacts: dict[str, Artifact] = {}

    def awaken(self, artifact: Artifact, materials_quality: int) -> tuple[bool, str]:
        if artifact.awakening_level >= artifact.max_awakening:
            return False, "max_level"
        # 成功率 = 基础50% + 材料品质加成 - 当前等级惩罚，下限5%
        rate = 0.5 + 0.05 * materials_quality - 0.03 * artifact.awakening_level
        rate = max(0.05, min(1.0, rate))
        if self.rng.random() < rate:
            artifact.awakening_level += 1
            return True, "success"
        # 失败保底：不掉级
        return False, "failed"

    def can_socket_rune(self, artifact: Artifact, rune: Rune, slot: str) -> bool:
        return rune.slot_type == slot

    def get_set_bonus(self, artifact: Artifact) -> dict:
        series_count: dict[str, int] = {}
        for rune in artifact.rune_slots.values():
            if rune:
                series_count[rune.series] = series_count.get(rune.series, 0) + 1
        bonuses = {}
        for series, count in series_count.items():
            if count >= 3:
                bonuses[f"{series}_set_bonus"] = 10
        return bonuses

    def get_awakening_stats(self, artifact: Artifact) -> dict:
        # 指数增长：高觉醒等级产生质变
        return {"atk": round(10 * (1.5 ** artifact.awakening_level))}

    def get_rune_limit_per_type(self, slot_type: str) -> int:
        return {"attack": 2, "defense": 2, "special": 1}.get(slot_type, 1)

    def can_use_awakening_skill(self, artifact: Artifact, skill_level: int) -> bool:
        return artifact.awakening_level >= skill_level

    def remove_rune(self, artifact: Artifact, slot: str) -> Rune | None:
        rune = artifact.rune_slots.get(slot)
        artifact.rune_slots[slot] = None
        return rune
