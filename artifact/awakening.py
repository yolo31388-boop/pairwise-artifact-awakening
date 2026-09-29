"""神器觉醒与符文镶嵌系统 - 含7个bug"""
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
        # bug1: 100%成功
        artifact.awakening_level += 1
        return True, "success"

    def can_socket_rune(self, artifact: Artifact, rune: Rune, slot: str) -> bool:
        # bug2: 不检查槽位类型
        return True

    def get_set_bonus(self, artifact: Artifact) -> dict:
        # bug3: 只看数量不看系列
        count = sum(1 for r in artifact.rune_slots.values() if r)
        if count >= 3:
            return {"set_bonus": 10}
        return {}

    def get_awakening_stats(self, artifact: Artifact) -> dict:
        # bug4: 线性增长
        return {"atk": artifact.awakening_level * 10}

    def get_rune_limit_per_type(self, slot_type: str) -> int:
        # bug5: 无数量限制
        return 999

    def can_use_awakening_skill(self, artifact: Artifact, skill_level: int) -> bool:
        # bug6: 无阶段要求
        return True

    def remove_rune(self, artifact: Artifact, slot: str) -> Rune | None:
        # bug7: 拆除不返还
        rune = artifact.rune_slots.get(slot)
        artifact.rune_slots[slot] = None
        return None
