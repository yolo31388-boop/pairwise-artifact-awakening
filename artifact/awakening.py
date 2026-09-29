"""神器觉醒与符文镶嵌系统"""
import random
from dataclasses import dataclass, field

# 符文槽位类型
SLOT_TYPES = ("attack", "defense", "special")
# 同类型符文镶嵌数量上限
RUNE_LIMITS = {"attack": 2, "defense": 2, "special": 1}
# 套装触发所需同系列符文数量
SET_BONUS_THRESHOLD = 3
# 觉醒关键阶段（达到这些等级解锁对应阶段技能/质变）
AWAKENING_STAGES = (1, 3, 5, 7, 10)
# 符文拆除冷却（秒）
REMOVE_RUNE_COOLDOWN = 60


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
        self._remove_cooldowns: dict[str, int] = {}  # slot -> 剩余冷却

    def _success_rate(self, artifact: Artifact, materials_quality: int) -> float:
        """觉醒成功率：材料品质提升成功率，觉醒等级越高越难。"""
        quality = max(0, materials_quality)
        rate = 0.3 + 0.1 * quality - 0.03 * artifact.awakening_level
        return min(0.95, max(0.05, rate))

    def awaken(self, artifact: Artifact, materials_quality: int) -> tuple[bool, str]:
        # fix1: 按成功率判定，失败有保底不掉级
        if artifact.awakening_level >= artifact.max_awakening:
            return False, "max_level"
        if self.rng.random() < self._success_rate(artifact, materials_quality):
            artifact.awakening_level += 1
            return True, "success"
        return False, "failed_no_downgrade"

    def can_socket_rune(self, artifact: Artifact, rune: Rune, slot: str) -> bool:
        # fix2: 槽位类型必须匹配符文类型
        if slot not in SLOT_TYPES or rune.slot_type != slot:
            return False
        # fix5: 同类型符文数量上限
        same_type = sum(
            1 for r in artifact.rune_slots.values()
            if r is not None and r.slot_type == rune.slot_type
        )
        return same_type < self.get_rune_limit_per_type(rune.slot_type)

    def get_set_bonus(self, artifact: Artifact) -> dict:
        # fix3: 按系列分组，同系列达到数量才触发套装效果
        series_count: dict[str, int] = {}
        for r in artifact.rune_slots.values():
            if r is not None:
                series_count[r.series] = series_count.get(r.series, 0) + 1
        bonus = {}
        for series, count in series_count.items():
            if count >= SET_BONUS_THRESHOLD:
                bonus[f"{series}_set_bonus"] = 10
        return bonus

    def get_awakening_stats(self, artifact: Artifact) -> dict:
        # fix4: 按阶段指数增长，关键等级质变
        level = artifact.awakening_level
        atk = int(10 * (1.5 ** level))
        for stage in AWAKENING_STAGES:
            if level >= stage:
                atk += stage * 20  # 关键等级质变加成
        return {"atk": atk}

    def get_rune_limit_per_type(self, slot_type: str) -> int:
        # fix5: 同类型符文有数量上限
        return RUNE_LIMITS.get(slot_type, 1)

    def can_use_awakening_skill(self, artifact: Artifact, skill_level: int) -> bool:
        # fix6: 觉醒技能有阶段要求，未达阶段不能激活
        return artifact.awakening_level >= skill_level

    def remove_rune(self, artifact: Artifact, slot: str) -> Rune | None:
        # fix7: 拆除返还符文本身，有冷却但不消失
        if self._remove_cooldowns.get(slot, 0) > 0:
            return None
        rune = artifact.rune_slots.get(slot)
        if rune is None:
            return None
        artifact.rune_slots[slot] = None
        self._remove_cooldowns[slot] = REMOVE_RUNE_COOLDOWN
        return rune
