"""神器觉醒与符文镶嵌系统 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from artifact.awakening import AwakeningSystem, Artifact, Rune

class TestAwakeningFailure:
    def test_awakening_can_fail(self):
        aw = AwakeningSystem(seed=1)
        art = Artifact("a1", "sword", awakening_level=5)
        results = [aw.awaken(art, materials_quality=1) for _ in range(20)]
        success_count = sum(1 for r, _ in results if r)
        assert success_count < 20  # bug1: 全成功

class TestRuneSlotType:
    def test_attack_rune_cannot_go_defense_slot(self):
        aw = AwakeningSystem()
        art = Artifact("a1", "sword")
        rune = Rune("r1", "atk", slot_type="attack", series="fire")
        assert aw.can_socket_rune(art, rune, "defense") == False  # bug2: True
        assert aw.can_socket_rune(art, rune, "attack") == True

class TestSetBonusBySeries:
    def test_mismatched_series_no_set_bonus(self):
        aw = AwakeningSystem()
        art = Artifact("a1", "sword")
        art.rune_slots = {
            "s1": Rune("r1", "a", "attack", "fire"),
            "s2": Rune("r2", "b", "attack", "water"),
            "s3": Rune("r3", "c", "attack", "earth"),
        }
        bonus = aw.get_set_bonus(art)
        assert bonus == {}  # bug3: 3个不同系列也触发套装

class TestExponentialGrowth:
    def test_high_awakening_has_quantitative_leap(self):
        aw = AwakeningSystem()
        a1 = Artifact("a1", "sword", awakening_level=1)
        a10 = Artifact("a10", "sword", awakening_level=10)
        s1 = aw.get_awakening_stats(a1)
        s10 = aw.get_awakening_stats(a10)
        # 10级应该远大于10倍1级
        assert s10["atk"] > s1["atk"] * 10  # bug4: 线性=10倍

class TestRuneLimit:
    def test_same_type_rune_has_limit(self):
        aw = AwakeningSystem()
        assert aw.get_rune_limit_per_type("attack") < 5  # bug5: 999

class TestSkillGate:
    def test_low_awakening_cannot_use_high_skill(self):
        aw = AwakeningSystem()
        art = Artifact("a1", "sword", awakening_level=1)
        assert aw.can_use_awakening_skill(art, skill_level=10) == False  # bug6: True

class TestRuneRemovalRefund:
    def test_removed_rune_returned(self):
        aw = AwakeningSystem()
        art = Artifact("a1", "sword")
        rune = Rune("r1", "atk", "attack", "fire")
        art.rune_slots["s1"] = rune
        removed = aw.remove_rune(art, "s1")
        assert removed is not None  # bug7: 返回None
        assert removed.rid == "r1"
