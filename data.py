"""
数据管理模块 - 存档、统计、成就、技能、每日任务
"""

import os
import json
from datetime import datetime, date
from collections import Counter

from ui import c, C, bar_fg, exp_bar, separator, wpm_color, acc_color


# ==================== 配置数据 ====================

WORD_BANKS = {
    "tech": [
        "python java javascript typescript algorithm database server cloud api endpoint framework library",
        "function variable class object method interface abstract inheritance polymorphism encapsulation",
        "debug compile execute deploy build test merge pull push commit repository branch workflow",
        "frontend backend fullstack database cache server client request response api gateway proxy",
        "kubernetes docker container microservice scalable distributed system architecture devops",
        "machine learning neural network deep learning dataset training validation accuracy model",
        "refactor optimize benchmark profile latency throughput concurrency thread async await event",
        "encryption authentication authorization token session cookie middleware cors webhook",
        "recursion memoization dynamic programming greedy algorithm binary search hash table graph",
    ],
    "code": [
        "def function_name(param): return param",
        "if condition: print(True) else: print(False)",
        "for i in range(10): print(i)",
        "class MyClass: def __init__(self): pass",
        "import os sys json datetime from typing import List Dict Optional Union Tuple",
        "if __name__ == '__main__': main()",
        "try: pass except Exception as e: print(e) finally: cleanup()",
        "result = [x ** 2 for x in range(100) if x % 2 == 0]",
        "with open('file.txt', 'r', encoding='utf-8') as f: data = f.read()",
        "async def fetch(url): async with session.get(url) as r: return await r.json()",
        "lambda x: x if x > 0 else -x",
        "sorted(items, key=lambda x: x['score'], reverse=True)[:10]",
        "dict(zip(keys, values))",
        "any(x > 0 for x in nums)",
        "from functools import reduce; reduce(lambda a, b: a + b, nums)",
    ],
    "quote": [
        "code is like humor when you have to explain it it is bad",
        "first solve the problem then write the code",
        "talk is cheap show me the code",
        "any fool can write code that a computer can understand",
        "programming is the art of algorithm design and elegant problem solving",
        "the best way to predict the future is to create it",
        "success is not final failure is not fatal it is the courage that counts",
        "simplicity is the soul of efficiency",
        "make it work make it right make it fast",
        "perfection is not when there is nothing to add but when there is nothing to remove",
        "a ship in harbor is safe but that is not what ships are built for",
        "done is better than perfect",
        "move fast and break things",
        "stay hungry stay foolish",
        "the only way to do great work is to love what you do",
    ],
    "science": [
        "the speed of light in vacuum is approximately 299792 kilometers per second",
        "photosynthesis converts carbon dioxide and water into glucose using sunlight",
        "DNA is a double helix structure made of nucleotide base pairs",
        "quantum mechanics describes the behavior of particles at the subatomic scale",
        "the periodic table organizes elements by atomic number and chemical properties",
        "entropy is a measure of disorder in a thermodynamic system",
        "neurons transmit electrical signals across synapses in the brain",
        "relativity states that time dilates as velocity approaches the speed of light",
        "mitochondria generate ATP through oxidative phosphorylation in the cell",
    ],
    "literature": [
        "it was the best of times it was the worst of times",
        "to be or not to be that is the question",
        "all happy families are alike each unhappy family is unhappy in its own way",
        "it is a truth universally acknowledged that a single man must be in want of a wife",
        "call me ishmael",
        "the only people for me are the mad ones who are mad to live mad to talk",
        "we are all mad here",
        "not all those who wander are lost",
        "in the beginning was the word and the word was with god",
    ],
    "random": [
        "the quick brown fox jumps over the lazy dog",
        "pack my box with five dozen liquor jugs",
        "how vexingly quick daft zebras jump",
        "the five boxing wizards jump quickly",
        "sphinx of black quartz judge my vow",
        "two driven jocks help fax my big quiz",
        "bright vixens jump dozing fowl quack",
        "glib jocks quiz nymph to vex dwarf",
        "five quacking zephyrs jolt my wax bed",
        "the job requires extra pluck and zeal from every young wage earner",
    ],
    "chinese": [
        "编程是一门艺术也是一门科学",
        "代码改变世界创新引领未来",
        "算法是程序的灵魂数据是程序的血液",
        "学习使人进步实践使人成长",
        "实践出真知理论指导实践",
        "坚持就是胜利放弃就是失败",
        "熟能生巧勤能补拙持之以恒",
        "千里之行始于足下不积跬步无以至千里",
        "不积小流无以成江海业精于勤荒于嬉",
        "博观而约取厚积而薄发行成于思毁于随",
        "锲而不舍金石可镂水滴石穿绳锯木断",
        "路漫漫其修远兮吾将上下而求索",
    ],
}

CUSTOM_WORDS_FILE = os.path.expanduser("~/.motip_custom_words.txt")

TEXTS = {
    "easy": [
        "The quick brown fox.",
        "Python is fun.",
        "Keep it simple.",
        "Practice daily.",
        "Code is poetry.",
        "Hello world!",
        "Learning is growing.",
        "Type with rhythm.",
        "Stay focused.",
        "Small steps matter.",
        "Think then code.",
        "Build good habits.",
    ],
    "medium": [
        "The quick brown fox jumps over the lazy dog.",
        "Python is a powerful programming language.",
        "Practice makes perfect in everything we do.",
        "Artificial intelligence is changing the world.",
        "Learning to code opens many doors of opportunity.",
        "Success is not final failure is not fatal.",
        "Consistency is the key to mastery.",
        "Every expert was once a beginner.",
        "The best investment you can make is in yourself.",
        "Write code that is easy to delete not easy to extend.",
        "Debugging is twice as hard as writing code.",
        "Programs must be written for people to read.",
        "The most important property of a program is correctness.",
    ],
    "hard": [
        "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs.",
        "Python is a powerful programming language that supports multiple paradigms including procedural, object-oriented, and functional programming.",
        "In computer science, algorithmic efficiency is a property of an algorithm which relates to the number of computational resources used.",
        "The discipline of programming is concerned with the art of constructing and formulating algorithms and encoding them in a programming language.",
        "Consistent refactoring and thoughtful architecture decisions lead to maintainable, scalable, and high-performance software systems.",
        "Distributed systems must handle network partitions, node failures, and message delays while maintaining consistency and availability.",
        "Cryptographic hash functions produce a fixed-size output from variable-length input and are designed to be collision-resistant and one-way.",
    ],
    "paragraph": [
        "In the beginning there was chaos, and from chaos came order. The universe expanded from a singularity, cooling as it grew, forming hydrogen and helium. Stars ignited, lived, and died, seeding the cosmos with heavier elements.",
        "Software engineering is not just about writing code. It encompasses requirements analysis, system design, testing, deployment, and maintenance. A great engineer communicates clearly and thinks about the long-term impact of every decision.",
        "The art of asking the right question is more than half the battle of finding the answer. Science advances not by accumulating facts but by transforming how we think about problems, and every revolution starts with a better question.",
        "Discipline is choosing between what you want now and what you want most. Champions are made in the moments when they want to stop. Every repetition, every session, every practice builds the foundation of excellence.",
    ],
}

DAILY_POOL = (
    TEXTS["medium"] + TEXTS["hard"][:3]
    + [v for bank in WORD_BANKS.values() for v in bank[::2]]
)

ACHIEVEMENTS = {
    # 游玩
    "first_game":   {"name": "初出茅庐",   "desc": "完成第一局",            "icon": "🎮", "category": "游玩"},
    "games_10":     {"name": "资深玩家",   "desc": "完成 10 局",            "icon": "🎯", "category": "游玩"},
    "games_50":     {"name": "打字老手",   "desc": "完成 50 局",            "icon": "💪", "category": "游玩"},
    "games_100":    {"name": "传奇人物",   "desc": "完成 100 局",           "icon": "🏅", "category": "游玩"},
    "games_500":    {"name": "不朽传说",   "desc": "完成 500 局",           "icon": "🔱", "category": "游玩"},
    # 速度（净 WPM）
    "speed_30":     {"name": "初窥门径",   "desc": "净 WPM ≥ 30",          "icon": "🌱", "category": "速度"},
    "speed_50":     {"name": "初级速手",   "desc": "净 WPM ≥ 50",          "icon": "⚡", "category": "速度"},
    "speed_80":     {"name": "中级速手",   "desc": "净 WPM ≥ 80",          "icon": "🚀", "category": "速度"},
    "speed_100":    {"name": "打字大师",   "desc": "净 WPM ≥ 100",         "icon": "🌟", "category": "速度"},
    "speed_150":    {"name": "极速传说",   "desc": "净 WPM ≥ 150",         "icon": "☄️", "category": "速度"},
    # 精准
    "perfect":      {"name": "完美主义者", "desc": "100% 正确率",           "icon": "💎", "category": "精准"},
    "acc_100_3":    {"name": "精准连射",   "desc": "连续 3 局 100%",        "icon": "🎯", "category": "精准"},
    "combo_20":     {"name": "连击大师",   "desc": "单局词语连击达到 20",   "icon": "🔥", "category": "精准"},
    # 连胜
    "streak_3":     {"name": "三连胜",     "desc": "连续 3 局 90%+",        "icon": "✨", "category": "连胜"},
    "streak_5":     {"name": "五连胜",     "desc": "连续 5 局 90%+",        "icon": "🌈", "category": "连胜"},
    "streak_10":    {"name": "十连胜",     "desc": "连续 10 局 90%+",       "icon": "👑", "category": "连胜"},
    # 模式
    "timed_master": {"name": "计时王者",   "desc": "计时挑战完成 10 句",    "icon": "⏱️", "category": "模式"},
    "sprint_king":  {"name": "极速之王",   "desc": "极速挑战 200 字符",     "icon": "🏎️", "category": "模式"},
    "blind_master": {"name": "盲打大师",   "desc": "盲打模式 95%+",         "icon": "🦅", "category": "模式"},
    "gauntlet_win": {"name": "闯关勇士",   "desc": "渐进挑战全通",          "icon": "⚔️", "category": "模式"},
    "weak_hero":    {"name": "克服弱点",   "desc": "完成弱键练习",          "icon": "💡", "category": "模式"},
    "daily_done":   {"name": "每日打卡",   "desc": "完成一次每日一挑",      "icon": "📅", "category": "模式"},
    "ghost_win":    {"name": "超越自我",   "desc": "幽灵竞速击败最佳记录",  "icon": "👻", "category": "模式"},
    "para_finish":  {"name": "长篇征服者", "desc": "完成一篇段落挑战",      "icon": "📖", "category": "模式"},
    # 成长
    "level_5":      {"name": "小试牛刀",   "desc": "达到 5 级",             "icon": "🌿", "category": "成长"},
    "level_10":     {"name": "熟能生巧",   "desc": "达到 10 级",            "icon": "🌳", "category": "成长"},
    "level_20":     {"name": "打字之神",   "desc": "达到 20 级",            "icon": "⭐", "category": "成长"},
    "level_50":     {"name": "传奇巅峰",   "desc": "达到 50 级",            "icon": "🌌", "category": "成长"},
    "daily_7":      {"name": "坚持不懈",   "desc": "连续 7 天登录",         "icon": "📆", "category": "成长"},
    "daily_30":     {"name": "月度达人",   "desc": "连续 30 天登录",        "icon": "🗓️", "category": "成长"},
    # 累计
    "word_10k":     {"name": "码字达人",   "desc": "累计输入 10000 字符",   "icon": "📝", "category": "累计"},
    "word_50k":     {"name": "文字海洋",   "desc": "累计输入 50000 字符",   "icon": "🌊", "category": "累计"},
    "word_100k":    {"name": "文字宇宙",   "desc": "累计输入 100000 字符",  "icon": "🌌", "category": "累计"},
    "all_modes":    {"name": "全能选手",   "desc": "所有模式都玩过",        "icon": "🎪", "category": "累计"},
}

SKILLS = {
    "focus":    {"name": "专注",  "desc": "每级额外 +5 正确率展示上限",    "level": 0, "max": 5, "cost": 50,  "icon": "🎯"},
    "speed":    {"name": "速度",  "desc": "每级经验奖励额外 +5%",          "level": 0, "max": 5, "cost": 50,  "icon": "⚡"},
    "stamina":  {"name": "耐力",  "desc": "计时模式时限 +10 秒/级",        "level": 0, "max": 3, "cost": 80,  "icon": "💪"},
    "streak":   {"name": "连胜",  "desc": "连胜经验奖励 +15%/级",          "level": 0, "max": 3, "cost": 60,  "icon": "🔥"},
    "accuracy": {"name": "精准",  "desc": "极速挑战时限 +5 秒/级",         "level": 0, "max": 3, "cost": 70,  "icon": "🎪"},
    "exp_boost":{"name": "经验",  "desc": "所有经验获取 +10%/级",          "level": 0, "max": 5, "cost": 90,  "icon": "✨"},
}

DAILY_TASKS = [
    {"id": "play_1",    "desc": "完成任意 1 局",        "target": 1,   "type": "games",    "reward": 20},
    {"id": "play_3",    "desc": "完成任意 3 局",        "target": 3,   "type": "games",    "reward": 50},
    {"id": "play_5",    "desc": "今日坚持 5 局",        "target": 5,   "type": "games",    "reward": 80},
    {"id": "wpm_40",    "desc": "净 WPM 达到 40",       "target": 40,  "type": "wpm",      "reward": 30},
    {"id": "wpm_60",    "desc": "净 WPM 达到 60",       "target": 60,  "type": "wpm",      "reward": 50},
    {"id": "acc_90",    "desc": "正确率达到 90%",       "target": 90,  "type": "accuracy", "reward": 30},
    {"id": "acc_100",   "desc": "达成 100% 完美作答",   "target": 100, "type": "accuracy", "reward": 60},
    {"id": "chars_200", "desc": "单局输入超 200 字符",  "target": 200, "type": "chars",    "reward": 40},
    {"id": "daily_ch",  "desc": "完成每日一挑",         "target": 1,   "type": "daily_ch", "reward": 100},
]

STATS_FILE  = os.path.expanduser("~/.motip_stats.json")
CONFIG_FILE = os.path.expanduser("~/.motip_config.json")


# ==================== 等级计算 ====================

def get_level(exp):
    """根据经验值计算等级"""
    level, needed = 1, 100
    while exp >= needed:
        exp -= needed
        level += 1
        needed = int(100 * level * 1.5)
    return level, exp, needed


# ==================== 存档函数 ====================

def load_stats():
    """加载统计数据"""
    defaults = {
        "games": [], "best_wpm": 0, "best_net_wpm": 0, "best_accuracy": 0,
        "total_games": 0, "achievements": [], "streak": 0, "perfect_streak": 0,
        "exp": 0, "level": 1, "skills": {k: 0 for k in SKILLS},
        "daily": {"date": "", "games": 0, "tasks": {}, "daily_ch_done": False},
        "key_stats": {}, "char_errors": {}, "played_modes": [], "total_chars": 0,
        "last_play_date": "", "login_days": 0, "wpm_history": [],
        "net_wpm_history": [], "max_combo": 0,
        "mode_bests": {},
        "daily_ch_streak": 0,
        "session": {"games": 0, "wpm_sum": 0, "acc_sum": 0, "start": ""},
    }
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in defaults.items():
            data.setdefault(k, v)
        return data
    return defaults


def save_stats(stats):
    """保存统计数据"""
    out = dict(stats)
    if isinstance(out.get("key_stats"), Counter):
        out["key_stats"] = dict(out["key_stats"])
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)


def load_config():
    """加载配置"""
    defaults = {"show_tips": True, "difficulty": "medium",
                "use_realtime": True, "theme": "default"}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        for k, v in defaults.items():
            cfg.setdefault(k, v)
        return cfg
    return defaults


def save_config(config):
    """保存配置"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def load_custom_words():
    """加载自定义词库"""
    if os.path.exists(CUSTOM_WORDS_FILE):
        with open(CUSTOM_WORDS_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    return []


def save_custom_word(word):
    """保存自定义词组"""
    with open(CUSTOM_WORDS_FILE, 'a', encoding='utf-8') as f:
        f.write(word + '\n')


# ==================== 计算函数 ====================

def calculate_accuracy(original, typed):
    """计算准确率（使用编辑距离）"""
    if not original or not typed:
        return 0
    m, n = len(original), len(typed)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if original[i - 1] == typed[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
    return max(0, int((m - dp[m][n]) / m * 100))


def calculate_net_wpm(target, typed, elapsed):
    """净 WPM = (正确字符数/5 - 错误字符数/5) / 分钟数"""
    if elapsed <= 0 or not typed:
        return 0
    correct = sum(1 for i, uc in enumerate(typed[:len(target)]) if uc == target[i])
    errors  = len(typed) - correct
    return max(0, int(((correct / 5) - (errors / 5)) / (elapsed / 60)))


def word_combo_score(target_words, typed_words):
    """计算词语连击"""
    max_combo = cur = 0
    for tw, uw in zip(target_words, typed_words):
        if tw == uw:
            cur += 1
            max_combo = max(max_combo, cur)
        else:
            cur = 0
    return max_combo


# ==================== 统计更新函数 ====================

def track_key_errors(target, typed, stats):
    """追踪错误键位"""
    ke = stats.get("key_stats", {})
    ce = stats.get("char_errors", {})
    for i, (t, u) in enumerate(zip(target, typed[:len(target)])):
        if t != u:
            ke[t] = ke.get(t, 0) + 1
            ce.setdefault(t, {"count": 0, "positions": []})
            ce[t]["count"] += 1
            ce[t]["positions"].append(i)
    stats["key_stats"]   = ke
    stats["char_errors"] = ce
    stats["total_chars"] = stats.get("total_chars", 0) + len(typed)


def check_daily_reset(stats):
    """检查每日重置"""
    today = date.today().isoformat()
    if stats.get("daily", {}).get("date") != today:
        last_date = stats.get("last_play_date", "")
        if last_date:
            try:
                diff = (date.today() - datetime.fromisoformat(last_date).date()).days
                if diff == 1:
                    stats["login_days"] = stats.get("login_days", 0) + 1
                    if stats.get("daily", {}).get("daily_ch_done"):
                        stats["daily_ch_streak"] = stats.get("daily_ch_streak", 0) + 1
                    else:
                        stats["daily_ch_streak"] = 0
                else:
                    stats["login_days"]      = 1
                    stats["daily_ch_streak"] = 0
            except Exception:
                stats["login_days"] = 1
        else:
            stats["login_days"] = 1
        stats["daily"]          = {"date": today, "games": 0, "tasks": {}, "daily_ch_done": False}
        stats["last_play_date"] = today


def check_daily_tasks(stats, wpm, accuracy, typed_chars=0, is_daily_ch=False):
    """检查每日任务完成"""
    check_daily_reset(stats)
    daily = stats["daily"]
    daily["games"] = daily.get("games", 0) + 1
    if is_daily_ch:
        daily["daily_ch_done"] = True
    new_completed = []
    for task in DAILY_TASKS:
        tid = task["id"]
        if daily.get("tasks", {}).get(tid):
            continue
        t    = task["type"]
        done = (
            (t == "games"    and daily["games"] >= task["target"])  or
            (t == "wpm"      and wpm >= task["target"])             or
            (t == "accuracy" and accuracy >= task["target"])        or
            (t == "chars"    and typed_chars >= task["target"])     or
            (t == "daily_ch" and is_daily_ch)
        )
        if done:
            daily.setdefault("tasks", {})[tid] = True
            new_completed.append(task)
            stats["exp"] += task["reward"]
    return new_completed


def check_achievements(stats, wpm, net_wpm, accuracy, mode="classic",
                       completed=0, chars=0, combo=0, ghost_beat=False,
                       is_daily_ch=False, is_para=False):
    """检查成就解锁"""
    new_ach = []
    ach = stats.setdefault("achievements", [])

    def unlock(key):
        if key not in ach:
            new_ach.append(key)
            ach.append(key)

    unlock("first_game")

    for th, key in [(30,"speed_30"),(50,"speed_50"),(80,"speed_80"),(100,"speed_100"),(150,"speed_150")]:
        if net_wpm >= th: unlock(key)

    if accuracy == 100:
        unlock("perfect")
        stats["perfect_streak"] = stats.get("perfect_streak", 0) + 1
        if stats["perfect_streak"] >= 3: unlock("acc_100_3")
    else:
        stats["perfect_streak"] = 0

    s = stats.get("streak", 0)
    if s >= 3:  unlock("streak_3")
    if s >= 5:  unlock("streak_5")
    if s >= 10: unlock("streak_10")

    total = stats.get("total_games", 0)
    for cnt, key in [(10,"games_10"),(50,"games_50"),(100,"games_100"),(500,"games_500")]:
        if total >= cnt: unlock(key)

    if mode == "timed"    and completed >= 10: unlock("timed_master")
    if mode == "sprint"   and chars >= 200:    unlock("sprint_king")
    if mode == "blind"    and accuracy >= 95:  unlock("blind_master")
    if mode == "gauntlet":                     unlock("gauntlet_win")
    if mode == "weak":                         unlock("weak_hero")
    if is_daily_ch:                            unlock("daily_done")
    if ghost_beat:                             unlock("ghost_win")
    if is_para:                                unlock("para_finish")

    level = stats.get("level", 1)
    for lv, key in [(5,"level_5"),(10,"level_10"),(20,"level_20"),(50,"level_50")]:
        if level >= lv: unlock(key)

    tc = stats.get("total_chars", 0)
    if tc >= 10000:  unlock("word_10k")
    if tc >= 50000:  unlock("word_50k")
    if tc >= 100000: unlock("word_100k")

    if len(set(stats.get("played_modes", []))) >= 7: unlock("all_modes")

    ld = stats.get("login_days", 0)
    if ld >= 7:  unlock("daily_7")
    if ld >= 30: unlock("daily_30")

    if combo >= 20: unlock("combo_20")
    if combo > stats.get("max_combo", 0):
        stats["max_combo"] = combo

    return new_ach


def record_wpm(stats, wpm, net_wpm=None):
    """记录WPM历史"""
    h = stats.setdefault("wpm_history", [])
    h.append(wpm)
    if len(h) > 200: stats["wpm_history"] = h[-200:]
    if net_wpm is not None:
        nh = stats.setdefault("net_wpm_history", [])
        nh.append(net_wpm)
        if len(nh) > 200: stats["net_wpm_history"] = nh[-200:]


def update_mode_best(stats, mode, wpm, net_wpm, accuracy):
    """更新模式最佳记录"""
    bests = stats.setdefault("mode_bests", {})
    prev  = bests.get(mode, {"wpm": 0, "net_wpm": 0, "accuracy": 0})
    prev["wpm"]      = max(prev.get("wpm", 0), wpm)
    prev["net_wpm"]  = max(prev.get("net_wpm", 0), net_wpm)
    prev["accuracy"] = max(prev.get("accuracy", 0), accuracy)
    bests[mode] = prev


def finish_game(stats, mode, raw_wpm, raw_net_wpm, raw_acc, exp_base,
                target="", user_input="", elapsed=0,
                completed=0, chars=0, difficulty="medium", extra=None,
                ghost_beat=False, is_daily_ch=False, is_para=False,
                realtime_max_combo=0, realtime_is_perfect=True):
    """游戏结算核心函数"""
    skills      = stats.get("skills", {k: 0 for k in SKILLS})
    streak_mult = 1 + skills.get("streak", 0) * 0.15
    exp_mult    = 1 + skills.get("exp_boost", 0) * 0.10

    wpm      = raw_wpm
    net_wpm  = raw_net_wpm
    accuracy = min(100, raw_acc)

    combo = 0
    if target and user_input:
        combo = word_combo_score(target.split(), user_input.split())

    if accuracy >= 90:
        stats["streak"] = stats.get("streak", 0) + 1
    else:
        stats["streak"] = 0

    combo_bonus = (combo // 5) * 5
    exp_gain    = int((exp_base * streak_mult + combo_bonus) * exp_mult)

    # 完美/高连击奖励
    if realtime_is_perfect and target and user_input:
        exp_gain = int(exp_gain * 1.5)
    elif realtime_max_combo >= 100:
        exp_gain = int(exp_gain * 1.2)

    if ghost_beat:
        exp_gain = int(exp_gain * 1.5)

    old_level = stats.get("level", 1)
    stats["total_games"]   = stats.get("total_games", 0) + 1
    stats["exp"]           = stats.get("exp", 0) + exp_gain
    new_level, _, _        = get_level(stats["exp"])
    stats["level"]         = new_level
    stats["best_wpm"]      = max(stats.get("best_wpm",     0), wpm)
    stats["best_net_wpm"]  = max(stats.get("best_net_wpm", 0), net_wpm)
    stats["best_accuracy"] = max(stats.get("best_accuracy",0), accuracy)
    stats["played_modes"]  = list(set(stats.get("played_modes", []) + [mode]))

    update_mode_best(stats, mode, wpm, net_wpm, accuracy)
    record_wpm(stats, wpm, net_wpm)

    # 会话统计
    sess = stats.setdefault("session", {"games": 0, "wpm_sum": 0, "acc_sum": 0, "start": ""})
    if not sess.get("start"):
        sess["start"] = datetime.now().isoformat()
    sess["games"]   = sess.get("games", 0) + 1
    sess["wpm_sum"] = sess.get("wpm_sum", 0) + net_wpm
    sess["acc_sum"] = sess.get("acc_sum", 0) + accuracy

    # 记录本局
    record = {
        "date": datetime.now().isoformat(), "mode": mode,
        "wpm": wpm, "net_wpm": net_wpm, "accuracy": accuracy,
        "exp": exp_gain, "combo": combo, "elapsed": round(elapsed, 2),
    }
    if difficulty: record["difficulty"] = difficulty
    if completed:  record["completed"]  = completed
    if chars:      record["chars"]      = chars
    if extra:      record.update(extra)
    stats["games"].append(record)

    new_ach    = check_achievements(stats, wpm, net_wpm, accuracy, mode,
                                    completed, chars, combo, ghost_beat,
                                    is_daily_ch, is_para)
    daily_done = check_daily_tasks(stats, net_wpm, accuracy, len(user_input), is_daily_ch)
    save_stats(stats)
    return new_ach, daily_done, old_level, new_level, exp_gain, combo, wpm, net_wpm, accuracy
