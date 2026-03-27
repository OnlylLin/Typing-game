"""
Boss战斗系统 - 回合制战斗、技能系统、关卡管理
"""

import random
import time
import json
import os
from datetime import datetime

from ui import (
    c, C, DarkTheme, hp_bar, boss_hp_bar, draw_box, draw_panel,
    separator, attack_flash, heal_effect, shield_effect, freeze_effect,
    critical_hit_effect, celebrate_boss_defeat, loading_animation,
    clear_screen
)


# ==================== Boss数据定义 ====================

BOSSES = {
    1: {
        "name": "史莱姆王",
        "hp": 80,
        "attack": 8,
        "skills": ["普通攻击"],
        "vocab_level": "easy",
        "icon": "🟢",
        "description": "软弱的史莱姆之王，新手试炼"
    },
    3: {
        "name": "暗影蝙蝠",
        "hp": 120,
        "attack": 12,
        "skills": ["普通攻击", "毒害攻击"],
        "vocab_level": "medium",
        "icon": "🦇",
        "description": "来自黑暗洞穴的吸血蝙蝠"
    },
    5: {
        "name": "骷髅战士",
        "hp": 180,
        "attack": 15,
        "skills": ["普通攻击", "重击攻击"],
        "vocab_level": "medium",
        "icon": "💀",
        "description": "不死的骷髅战士，守卫古墓"
    },
    8: {
        "name": "暗影刺客",
        "hp": 250,
        "attack": 20,
        "skills": ["普通攻击", "毒害攻击", "盲眼攻击"],
        "vocab_level": "medium",
        "icon": "🗡️",
        "description": "隐匿于暗处的致命刺客"
    },
    10: {
        "name": "烈焰魔龙",
        "hp": 350,
        "attack": 25,
        "skills": ["普通攻击", "重击攻击", "盲眼攻击"],
        "vocab_level": "hard",
        "icon": "🐉",
        "description": "喷吐烈焰的远古巨龙"
    },
    13: {
        "name": "寒冰女王",
        "hp": 400,
        "attack": 22,
        "skills": ["普通攻击", "毒害攻击", "冰冻攻击"],
        "vocab_level": "hard",
        "icon": "❄️",
        "description": "永冻之地的冰雪女王"
    },
    15: {
        "name": "死灵法师",
        "hp": 450,
        "attack": 28,
        "skills": ["普通攻击", "毒害攻击", "盲眼攻击", "召唤亡灵"],
        "vocab_level": "hard",
        "icon": "🔮",
        "description": "操控死亡的邪恶法师"
    },
    18: {
        "name": "地狱三头犬",
        "hp": 500,
        "attack": 30,
        "skills": ["普通攻击", "重击攻击", "烈焰吐息"],
        "vocab_level": "expert",
        "icon": "🐕",
        "description": "守卫地狱之门的三头恶犬"
    },
    20: {
        "name": "暗黑骑士",
        "hp": 600,
        "attack": 35,
        "skills": ["普通攻击", "重击攻击", "毒害攻击", "黑暗护盾"],
        "vocab_level": "expert",
        "icon": "⚔️",
        "description": "堕落的圣骑士，被黑暗吞噬"
    },
    25: {
        "name": "远古巨像",
        "hp": 800,
        "attack": 40,
        "skills": ["普通攻击", "重击攻击", "地震"],
        "vocab_level": "expert",
        "icon": "🗿",
        "description": "上古文明创造的战争机器"
    },
    30: {
        "name": "深渊领主",
        "hp": 1000,
        "attack": 50,
        "skills": ["普通攻击", "毒害攻击", "重击攻击", "盲眼攻击", "深渊凝视"],
        "vocab_level": "master",
        "icon": "👹",
        "description": "深渊的统治者，终极挑战"
    },
}

# 玩家技能定义
PLAYER_SKILLS = {
    "HEAL": {
        "name": "回血",
        "icon": "💚",
        "effect": "heal",
        "value": 30,
        "cooldown": 3,
        "description": "恢复30点HP"
    },
    "SHIELD": {
        "name": "护盾",
        "icon": "🛡️",
        "effect": "shield",
        "value": 2,
        "cooldown": 4,
        "description": "获得2层护盾"
    },
    "CRITICAL": {
        "name": "暴击",
        "icon": "⚡",
        "effect": "critical",
        "value": 2.0,
        "cooldown": 5,
        "description": "下次攻击伤害翻倍"
    },
    "FREEZE": {
        "name": "冰冻",
        "icon": "❄️",
        "effect": "freeze",
        "value": 1,
        "cooldown": 6,
        "description": "冻结Boss一回合"
    },
    "CURE": {
        "name": "解毒",
        "icon": "💊",
        "effect": "cure",
        "value": 1,
        "cooldown": 2,
        "description": "解除中毒状态"
    },
}

# Boss技能效果定义
BOSS_SKILLS = {
    "普通攻击": {
        "damage_multiplier": 1.0,
        "effect": None,
        "description": "Boss的普通攻击"
    },
    "毒害攻击": {
        "damage_multiplier": 0.5,
        "effect": "poison",
        "poison_damage": 5,
        "poison_duration": 3,
        "description": "使玩家中毒，每回合扣血"
    },
    "重击攻击": {
        "damage_multiplier": 1.5,
        "effect": None,
        "description": "造成150%伤害的重击"
    },
    "盲眼攻击": {
        "damage_multiplier": 0.3,
        "effect": "blind",
        "description": "触发完形填空挑战"
    },
    "冰冻攻击": {
        "damage_multiplier": 0.8,
        "effect": "freeze_player",
        "description": "冻结玩家一回合"
    },
    "烈焰吐息": {
        "damage_multiplier": 1.2,
        "effect": "burn",
        "burn_damage": 8,
        "burn_duration": 2,
        "description": "造成灼烧效果"
    },
    "召唤亡灵": {
        "damage_multiplier": 0.5,
        "effect": "summon",
        "summon_count": 2,
        "description": "召唤小怪助战"
    },
    "黑暗护盾": {
        "damage_multiplier": 0.3,
        "effect": "boss_shield",
        "shield_value": 3,
        "description": "Boss获得护盾"
    },
    "地震": {
        "damage_multiplier": 1.0,
        "effect": "stun",
        "stun_chance": 0.3,
        "description": "可能眩晕玩家"
    },
    "深渊凝视": {
        "damage_multiplier": 1.3,
        "effect": "fear",
        "description": "造成恐惧，降低攻击力"
    },
}


# ==================== 玩家类 ====================

class Player:
    """玩家角色类"""

    def __init__(self, max_hp=100, base_attack=10):
        self.max_hp = max_hp
        self.hp = max_hp
        self.base_attack = base_attack
        self.shield = 0

        # 状态效果
        self.poison = 0        # 中毒剩余回合
        self.poison_damage = 0 # 中毒伤害
        self.burn = 0          # 灼烧剩余回合
        self.burn_damage = 0   # 灼烧伤害
        self.frozen = False    # 是否被冰冻
        self.stunned = False   # 是否眩晕
        self.fear = 0          # 恐惧减益

        # 技能冷却
        self.skill_cooldowns = {skill: 0 for skill in PLAYER_SKILLS}

        # Buff
        self.critical_next = False  # 下次暴击
        self.attack_bonus = 0       # 攻击力加成

    @property
    def attack(self):
        """计算当前攻击力"""
        base = self.base_attack + self.attack_bonus
        if self.fear > 0:
            base = int(base * 0.7)  # 恐惧降低30%攻击
        return max(1, base)

    @property
    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        """受到伤害（考虑护盾）"""
        if self.shield > 0:
            self.shield -= 1
            return 0, True  # 护盾抵消

        self.hp = max(0, self.hp - damage)
        return damage, False

    def heal(self, amount):
        """治疗"""
        self.hp = min(self.max_hp, self.hp + amount)
        return amount

    def add_shield(self, layers):
        """添加护盾"""
        self.shield += layers
        return layers

    def apply_poison(self, damage, duration):
        """施加中毒"""
        self.poison = duration
        self.poison_damage = damage

    def apply_burn(self, damage, duration):
        """施加灼烧"""
        self.burn = duration
        self.burn_damage = damage

    def process_status_effects(self):
        """处理状态效果（每回合开始调用）"""
        total_damage = 0
        effects = []

        # 中毒伤害
        if self.poison > 0:
            self.hp = max(0, self.hp - self.poison_damage)
            total_damage += self.poison_damage
            effects.append(f"中毒 -{self.poison_damage}HP")
            self.poison -= 1

        # 灼烧伤害
        if self.burn > 0:
            self.hp = max(0, self.hp - self.burn_damage)
            total_damage += self.burn_damage
            effects.append(f"灼烧 -{self.burn_damage}HP")
            self.burn -= 1

        # 减少恐惧
        if self.fear > 0:
            self.fear -= 1

        # 清除冰冻和眩晕（回合结束时）
        self.frozen = False
        self.stunned = False

        return total_damage, effects

    def use_skill(self, skill_name):
        """使用技能"""
        if skill_name not in PLAYER_SKILLS:
            return False, "未知技能"

        if self.skill_cooldowns[skill_name] > 0:
            return False, f"技能冷却中（{self.skill_cooldowns[skill_name]}回合）"

        skill = PLAYER_SKILLS[skill_name]
        self.skill_cooldowns[skill_name] = skill["cooldown"]

        effect = skill["effect"]
        value = skill["value"]

        if effect == "heal":
            healed = self.heal(value)
            return True, f"恢复了 {healed} HP"
        elif effect == "shield":
            self.add_shield(value)
            return True, f"获得 {value} 层护盾"
        elif effect == "critical":
            self.critical_next = True
            return True, "下次攻击将造成双倍伤害"
        elif effect == "freeze":
            return True, "freeze"  # 特殊标记，由战斗系统处理
        elif effect == "cure":
            self.poison = 0
            self.burn = 0
            return True, "解除了所有负面状态"

        return False, "技能效果未知"

    def reduce_cooldowns(self):
        """减少所有技能冷却"""
        for skill in self.skill_cooldowns:
            if self.skill_cooldowns[skill] > 0:
                self.skill_cooldowns[skill] -= 1

    def get_status_display(self):
        """获取状态显示"""
        status = []
        if self.shield > 0:
            status.append(c(f"🛡️{self.shield}", DarkTheme.SOUL_BLUE))
        if self.poison > 0:
            status.append(c(f"🧪{self.poison}", DarkTheme.POISON_GREEN))
        if self.burn > 0:
            status.append(c(f"🔥{self.burn}", DarkTheme.FIRE_ORANGE))
        if self.frozen:
            status.append(c("❄️冰冻", DarkTheme.ICE_CYAN))
        if self.stunned:
            status.append(c("💫眩晕", DarkTheme.GOLD_YELLOW))
        if self.fear > 0:
            status.append(c("😱恐惧", DarkTheme.SHADOW_PURPLE))
        if self.critical_next:
            status.append(c("⚡暴击Ready", DarkTheme.GOLD_YELLOW))

        return " ".join(status) if status else c("正常", C.BBLACK)


# ==================== Boss类 ====================

class Boss:
    """Boss类"""

    def __init__(self, boss_data, level_multiplier=1.0):
        self.name = boss_data["name"]
        self.icon = boss_data["icon"]
        self.max_hp = int(boss_data["hp"] * level_multiplier)
        self.hp = self.max_hp
        self.base_attack = int(boss_data["attack"] * level_multiplier)
        self.skills = boss_data["skills"]
        self.vocab_level = boss_data["vocab_level"]
        self.description = boss_data.get("description", "")

        self.shield = 0
        self.frozen = False

    @property
    def attack(self):
        return self.base_attack

    @property
    def is_alive(self):
        return self.hp > 0

    def take_damage(self, damage):
        """受到伤害"""
        if self.shield > 0:
            self.shield -= 1
            return 0, True

        self.hp = max(0, self.hp - damage)
        return damage, False

    def choose_skill(self):
        """选择技能"""
        # 根据权重选择技能
        weights = []
        for skill in self.skills:
            if skill == "普通攻击":
                weights.append(50)
            elif skill in ["重击攻击", "烈焰吐息"]:
                weights.append(20)
            else:
                weights.append(30)

        return random.choices(self.skills, weights=weights)[0]

    def execute_skill(self, skill_name):
        """执行技能"""
        if skill_name not in BOSS_SKILLS:
            skill_name = "普通攻击"

        skill = BOSS_SKILLS[skill_name]
        damage = int(self.attack * skill["damage_multiplier"])

        return {
            "skill": skill_name,
            "damage": damage,
            "effect": skill.get("effect"),
            "params": {k: v for k, v in skill.items() if k not in ["damage_multiplier", "effect", "description"]},
            "description": skill["description"]
        }


# ==================== 战斗系统 ====================

class BattleSystem:
    """战斗系统"""

    def __init__(self, player, boss, vocabulary_manager=None, quiz_system=None):
        self.player = player
        self.boss = boss
        self.vocabulary = vocabulary_manager
        self.quiz = quiz_system

        self.turn = 0
        self.player_turn = True
        self.battle_log = []
        self.is_active = True
        self.victory = False

        # 临时奖励词
        self.bonus_words = {
            "item": None,      # 道具词
            "skip": None,      # 跳过词
            "double": None,    # 双倍伤害词
            "heal": None,      # 回血词
        }
        self._generate_bonus_words()

    def _generate_bonus_words(self):
        """生成临时奖励词"""
        if self.vocabulary:
            words = self.vocabulary.get_words_by_level(self.boss.vocab_level, count=4)
            self.bonus_words = {
                "item": words[0] if len(words) > 0 else None,
                "skip": words[1] if len(words) > 1 else None,
                "double": words[2] if len(words) > 2 else None,
                "heal": words[3] if len(words) > 3 else None,
            }

    def add_log(self, message, color=None):
        """添加战斗日志"""
        timestamp = f"[T{self.turn}]"
        if color:
            self.battle_log.append(c(f"{timestamp} {message}", color))
        else:
            self.battle_log.append(f"{timestamp} {message}")

        # 只保留最近10条日志
        if len(self.battle_log) > 10:
            self.battle_log = self.battle_log[-10:]

    def player_attack(self, word, correct=True, time_bonus=0):
        """
        玩家攻击

        Args:
            word: 输入的单词
            correct: 是否正确
            time_bonus: 时间奖励（快速输入加成）

        Returns:
            (damage_dealt, effect_triggered, message)
        """
        if not correct:
            return 0, None, "输入错误，未造成伤害"

        # 基础伤害
        base_damage = self.player.attack

        # 时间奖励
        base_damage = int(base_damage * (1 + time_bonus * 0.1))

        # 检查是否是奖励词
        bonus_type = None
        for btype, bword in self.bonus_words.items():
            if bword and word.lower() == bword.lower():
                bonus_type = btype
                break

        # 暴击检查
        critical = self.player.critical_next
        if critical:
            base_damage *= 2
            self.player.critical_next = False

        # 计算最终伤害
        damage = base_damage
        if bonus_type == "double":
            damage *= 2

        # 造成伤害
        actual_damage, blocked = self.boss.take_damage(damage)

        # 构建消息
        msg_parts = [f"造成 {actual_damage} 点伤害"]
        if critical:
            msg_parts.append("⚡暴击!")
        if blocked:
            msg_parts = ["Boss的护盾抵消了攻击"]

        effect = None
        if bonus_type:
            effect = self._apply_bonus(bonus_type)

        return actual_damage, effect, " ".join(msg_parts)

    def _apply_bonus(self, bonus_type):
        """应用奖励效果"""
        if bonus_type == "item":
            # 随机道具
            items = ["小治疗药水(+15HP)", "护盾卷轴(+1护盾)", "经验卷轴(+50XP)"]
            return ("item", random.choice(items))
        elif bonus_type == "skip":
            return ("skip", "Boss跳过下回合!")
        elif bonus_type == "double":
            return ("double", "双倍伤害!")
        elif bonus_type == "heal":
            healed = self.player.heal(10)
            return ("heal", f"恢复 {healed} HP")

        return None

    def player_use_skill(self, skill_name):
        """玩家使用技能"""
        success, result = self.player.use_skill(skill_name)

        if not success:
            return False, result

        if result == "freeze":
            self.boss.frozen = True
            result = f"{self.boss.name} 被冰冻了!"

        return True, result

    def boss_turn(self):
        """
        Boss回合

        Returns:
            dict: 包含技能信息、伤害、效果等
        """
        if self.boss.frozen:
            self.boss.frozen = False
            return {
                "skill": "冰冻中",
                "damage": 0,
                "effect": None,
                "message": f"{self.boss.name} 被冰冻，无法行动!",
                "blocked": False
            }

        # 选择并执行技能
        skill_name = self.boss.choose_skill()
        skill_result = self.boss.execute_skill(skill_name)

        # 造成伤害
        damage = skill_result["damage"]
        effect = skill_result["effect"]
        params = skill_result["params"]

        actual_damage, blocked = self.player.take_damage(damage)

        # 处理特殊效果
        effect_data = None
        if effect == "poison" and not blocked:
            self.player.apply_poison(params["poison_damage"], params["poison_duration"])
            effect_data = ("poison", params)
        elif effect == "burn" and not blocked:
            self.player.apply_burn(params["burn_damage"], params["burn_duration"])
            effect_data = ("burn", params)
        elif effect == "freeze_player" and not blocked:
            self.player.frozen = True
            effect_data = ("freeze", None)
        elif effect == "blind":
            effect_data = ("blind", None)  # 完形填空
        elif effect == "boss_shield":
            self.boss.shield += params["shield_value"]
            effect_data = ("boss_shield", params)
        elif effect == "stun":
            if random.random() < params["stun_chance"]:
                self.player.stunned = True
                effect_data = ("stun", None)
        elif effect == "fear" and not blocked:
            self.player.fear = 3
            effect_data = ("fear", None)

        message = f"{self.boss.name} 使用 {skill_name}"
        if blocked:
            message += " (被护盾抵消)"
        else:
            message += f" 造成 {actual_damage} 伤害"

        return {
            "skill": skill_name,
            "damage": actual_damage,
            "effect": effect,
            "effect_data": effect_data,
            "message": message,
            "blocked": blocked
        }

    def process_turn_start(self):
        """回合开始处理"""
        self.turn += 1

        # 处理玩家状态效果
        dot_damage, effects = self.player.process_status_effects()

        # 减少技能冷却
        self.player.reduce_cooldowns()

        return dot_damage, effects

    def check_battle_end(self):
        """检查战斗是否结束"""
        if not self.boss.is_alive:
            self.is_active = False
            self.victory = True
            return True, "victory"
        elif not self.player.is_alive:
            self.is_active = False
            self.victory = False
            return True, "defeat"
        return False, None

    def get_display(self):
        """获取战斗界面显示"""
        lines = []

        # Boss信息
        lines.append("")
        boss_display = boss_hp_bar(self.boss.hp, self.boss.max_hp, 30, f"{self.boss.icon} {self.boss.name}")
        lines.append(boss_display)

        # 分隔
        lines.append(separator("═", 50, DarkTheme.FIRE_ORANGE))

        # 玩家信息
        player_bar, player_hp = hp_bar(self.player.hp, self.player.max_hp, 20)
        status = self.player.get_status_display()
        lines.append(f"  {c('🧙 玩家', DarkTheme.SOUL_BLUE, C.BOLD)}")
        lines.append(f"  HP: {player_bar} {c(player_hp, C.BWHITE)}")
        lines.append(f"  状态: {status}")

        # 技能冷却显示
        cd_parts = []
        for skill_name, cd in self.player.skill_cooldowns.items():
            skill = PLAYER_SKILLS[skill_name]
            if cd > 0:
                cd_parts.append(f"{skill['icon']}{cd}")
            else:
                cd_parts.append(c(f"{skill['icon']}✓", DarkTheme.POISON_GREEN))
        lines.append(f"  技能: {' '.join(cd_parts)}")

        return "\n".join(lines)


# ==================== 关卡系统 ====================

STAGE_CONFIG = {
    "total_stages": 30,
    "boss_stages": [3, 5, 8, 10, 13, 15, 18, 20, 25, 30],
    "quiz_stages": [4, 9, 14, 19, 24],  # 选择题关卡
    "reward_multiplier": {
        "normal": 1.0,
        "boss": 2.0,
        "quiz": 1.5,
    }
}


class StageManager:
    """关卡管理器"""

    def __init__(self, stats=None):
        self.current_stage = 1
        self.stats = stats
        self.stage_progress = self._load_progress()

    def _load_progress(self):
        """加载关卡进度"""
        if self.stats:
            return self.stats.get("stage_progress", {"unlocked": 1, "completed": [], "best_times": {}})
        return {"unlocked": 1, "completed": [], "best_times": {}}

    def _save_progress(self):
        """保存关卡进度"""
        if self.stats:
            self.stats["stage_progress"] = self.stage_progress

    def get_stage_type(self, stage_num):
        """获取关卡类型"""
        if stage_num in STAGE_CONFIG["boss_stages"]:
            return "boss"
        elif stage_num in STAGE_CONFIG["quiz_stages"]:
            return "quiz"
        else:
            return "normal"

    def get_boss_for_stage(self, stage_num):
        """获取关卡的Boss"""
        # 找到小于等于当前关卡的最大Boss关卡
        boss_stages = sorted([s for s in STAGE_CONFIG["boss_stages"] if s <= stage_num], reverse=True)
        if boss_stages:
            boss_stage = boss_stages[0]
            if boss_stage in BOSSES:
                return BOSSES[boss_stage]
        return BOSSES[1]  # 默认返回第一个Boss

    def get_level_multiplier(self, stage_num):
        """获取关卡难度乘数"""
        return 1.0 + (stage_num - 1) * 0.05

    def get_vocab_level(self, stage_num):
        """获取关卡词汇难度"""
        if stage_num <= 5:
            return "easy"
        elif stage_num <= 12:
            return "medium"
        elif stage_num <= 20:
            return "hard"
        elif stage_num <= 25:
            return "expert"
        else:
            return "master"

    def complete_stage(self, stage_num, time_used, exp_gained):
        """完成关卡"""
        if stage_num not in self.stage_progress["completed"]:
            self.stage_progress["completed"].append(stage_num)

        # 记录最佳时间
        best_key = str(stage_num)
        if best_key not in self.stage_progress["best_times"] or time_used < self.stage_progress["best_times"][best_key]:
            self.stage_progress["best_times"][best_key] = time_used

        # 解锁下一关
        if stage_num >= self.stage_progress["unlocked"]:
            self.stage_progress["unlocked"] = min(stage_num + 1, STAGE_CONFIG["total_stages"])

        self._save_progress()

    def calculate_reward(self, stage_num, stage_type, performance_bonus=0):
        """计算关卡奖励"""
        base_exp = {
            "normal": 15 + stage_num * 2,
            "boss": 50 + stage_num * 5,
            "quiz": 25 + stage_num * 3,
        }

        exp = base_exp.get(stage_type, 20)
        exp = int(exp * STAGE_CONFIG["reward_multiplier"].get(stage_type, 1.0))
        exp += performance_bonus

        # 金币奖励
        gold = int(exp * 0.5)

        return {"exp": exp, "gold": gold}

    def get_stage_list_display(self, width=60):
        """获取关卡列表显示"""
        lines = []
        lines.append(separator("═", width, DarkTheme.FIRE_ORANGE))
        lines.append(c("  🏰 Boss关卡模式", DarkTheme.FIRE_ORANGE, C.BOLD, C.UNDERLINE))
        lines.append(separator("─", width, C.BBLACK))

        # 显示关卡进度
        completed = len(self.stage_progress["completed"])
        total = STAGE_CONFIG["total_stages"]
        progress_bar = ""
        for i in range(1, total + 1):
            if i in self.stage_progress["completed"]:
                progress_bar += c("█", DarkTheme.POISON_GREEN)
            elif i == self.stage_progress["unlocked"]:
                progress_bar += c("▶", DarkTheme.GOLD_YELLOW)
            else:
                progress_bar += c("░", C.BBLACK)

        lines.append(f"  进度: {progress_bar}")
        lines.append(f"  已完成: {c(str(completed), DarkTheme.POISON_GREEN)}/{total}")

        lines.append(separator("─", width, C.BBLACK))

        # 显示最近的关卡
        start = max(1, self.stage_progress["unlocked"] - 2)
        end = min(total, start + 8)

        for i in range(start, end + 1):
            stage_type = self.get_stage_type(i)
            is_unlocked = i <= self.stage_progress["unlocked"]
            is_completed = i in self.stage_progress["completed"]

            # 图标
            if stage_type == "boss":
                icon = c("👹", DarkTheme.BLOOD_RED)
            elif stage_type == "quiz":
                icon = c("📝", DarkTheme.SOUL_BLUE)
            else:
                icon = c("⚔️", C.BBLACK)

            # 状态
            if is_completed:
                status = c("✓", DarkTheme.POISON_GREEN)
            elif is_unlocked:
                status = c("→", DarkTheme.GOLD_YELLOW)
            else:
                status = c("🔒", C.BBLACK)

            # 难度
            vocab = self.get_vocab_level(i)
            difficulty_stars = {
                "easy": "⭐",
                "medium": "⭐⭐",
                "hard": "⭐⭐⭐",
                "expert": "⭐⭐⭐⭐",
                "master": "⭐⭐⭐⭐⭐"
            }.get(vocab, "⭐")

            line = f"  {status} 第{i:02d}关 {icon} {difficulty_stars}"
            lines.append(line)

        lines.append(separator("═", width, DarkTheme.FIRE_ORANGE))
        lines.append(c(f"  当前可挑战: 第{self.stage_progress['unlocked']}关", DarkTheme.GOLD_YELLOW))

        return "\n".join(lines)


# ==================== 战斗界面显示 ====================

def show_battle_intro(boss):
    """显示战斗开始界面"""
    clear_screen()

    lines = []
    lines.append(separator("═", 50, DarkTheme.BLOOD_RED))
    lines.append(c("  ⚔️  BOSS战  ⚔️", DarkTheme.BLOOD_RED, C.BOLD, C.BLINK))
    lines.append(separator("═", 50, DarkTheme.BLOOD_RED))
    lines.append("")
    lines.append(f"  {boss.icon} {c(boss.name, DarkTheme.FIRE_ORANGE, C.BOLD)}")
    lines.append(f"  {c(boss.description, C.BBLACK, C.ITALIC)}")
    lines.append("")
    lines.append(f"  HP: {boss.hp}")
    lines.append(f"  技能: {', '.join(boss.skills)}")
    lines.append("")
    lines.append(separator("─", 50, C.BBLACK))
    lines.append(c("  准备战斗!", DarkTheme.GOLD_YELLOW, C.BOLD))
    lines.append(separator("═", 50, DarkTheme.BLOOD_RED))

    print("\n".join(lines))
    input(c("\n  按 Enter 开始战斗...", C.BBLACK))


def show_skill_menu(player):
    """显示技能菜单"""
    lines = []
    lines.append(c("  ⚡ 技能列表", DarkTheme.SOUL_BLUE, C.BOLD))
    lines.append(separator("─", 40, C.BBLACK))

    for i, (skill_name, skill) in enumerate(PLAYER_SKILLS.items(), 1):
        cd = player.skill_cooldowns[skill_name]
        if cd > 0:
            status = c(f"冷却{cd}回合", C.BRED)
        else:
            status = c("可用", DarkTheme.POISON_GREEN)

        line = f"  {c(str(i), DarkTheme.GOLD_YELLOW)}. {skill['icon']} {skill['name']} - {skill['description']}"
        line += f" [{status}]"
        lines.append(line)

    lines.append(separator("─", 40, C.BBLACK))
    lines.append(c("  输入技能编号使用，或输入单词攻击", C.BBLACK))

    return "\n".join(lines)


def show_battle_result(victory, boss, exp_gained, time_used, rewards=None):
    """显示战斗结果"""
    clear_screen()

    if victory:
        lines = []
        lines.append(c("\n  🎉 胜利! 🎉", DarkTheme.GOLD_YELLOW, C.BOLD, C.BLINK))
        lines.append(separator("═", 50, DarkTheme.GOLD_YELLOW))
        lines.append(f"  击败了 {boss.icon} {c(boss.name, DarkTheme.FIRE_ORANGE, C.BOLD)}!")
        lines.append("")
        lines.append(f"  ⏱️ 用时: {c(f'{time_used:.1f}秒', DarkTheme.SOUL_BLUE)}")
        lines.append(f"  ⭐ 经验: {c(f'+{exp_gained}XP', DarkTheme.POISON_GREEN, C.BOLD)}")

        if rewards:
            lines.append(separator("─", 50, C.BBLACK))
            lines.append(c("  🎁 获得奖励:", DarkTheme.GOLD_YELLOW))
            for item, value in rewards.items():
                lines.append(f"    • {item}: {c(str(value), DarkTheme.POISON_GREEN)}")

        lines.append(separator("═", 50, DarkTheme.GOLD_YELLOW))
    else:
        lines = []
        lines.append(c("\n  💀 战败... 💀", DarkTheme.BLOOD_RED, C.BOLD))
        lines.append(separator("═", 50, DarkTheme.BLOOD_RED))
        lines.append(f"  被 {boss.icon} {c(boss.name, DarkTheme.FIRE_ORANGE)} 击败了")
        lines.append("")
        lines.append(c("  不要气馁，再来一次!", DarkTheme.GOLD_YELLOW))
        lines.append(f"  💡 提示: 尝试使用技能或提升等级", C.BBLACK)
        lines.append(separator("═", 50, DarkTheme.BLOOD_RED))

    print("\n".join(lines))
    input(c("\n  按 Enter 继续...", C.BBLACK))


# ==================== 存档相关 ====================

def get_boss_save_key(stage_num):
    """获取Boss存档键"""
    return f"boss_stage_{stage_num}"


def save_boss_progress(stats, stage_num, victory, time_used, exp_gained):
    """保存Boss战斗进度"""
    if "boss_progress" not in stats:
        stats["boss_progress"] = {}

    key = get_boss_save_key(stage_num)
    if key not in stats["boss_progress"]:
        stats["boss_progress"][key] = {
            "attempts": 0,
            "victories": 0,
            "best_time": None,
            "total_exp": 0
        }

    stats["boss_progress"][key]["attempts"] += 1
    if victory:
        stats["boss_progress"][key]["victories"] += 1
        stats["boss_progress"][key]["total_exp"] += exp_gained

        best = stats["boss_progress"][key]["best_time"]
        if best is None or time_used < best:
            stats["boss_progress"][key]["best_time"] = time_used
