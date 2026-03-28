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
        "blockchain cryptocurrency smart contract consensus protocol decentralized distributed ledger",
        "serverless lambda function trigger event stream queue message broker rabbitmq kafka",
        "graphql restful websocket grpc protocol buffer serialization deserialization schema",
        "continuous integration deployment pipeline jenkins gitlab github actions artifact registry",
        "monitoring observability logging tracing metrics prometheus grafana alert dashboard",
        "redis mongodb postgresql mysql elasticsearch nosql relational database sql query index",
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
        "@decorator def wrapped(): pass",
        "class Derived(Base): def __init__(self): super().__init__()",
        "match value: case 1: pass case _: pass",
        "async with context_manager() as cm: await cm.do_something()",
        "generator = (x * 2 for x in range(100) if x % 3 == 0)",
        "dataclass decorator generates init repr eq hash methods automatically",
        "protocol typing structural subtyping duck typing interface definition",
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
        "premature optimization is the root of all evil",
        "there are only two hard things in computer science cache invalidation and naming things",
        "good code is its own best documentation",
        "the computer was born to solve problems that did not exist before",
        "the function of good software is to make the complex appear simple",
        "any sufficiently advanced technology is indistinguishable from magic",
        "programmers are tools for converting caffeine into code",
        "before software can be reusable it first has to be usable",
        "it works on my machine is not a valid excuse",
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
        "the big bang theory describes the origin of the universe from a singularity",
        "black holes have gravitational fields so strong that light cannot escape",
        "evolution by natural selection explains the diversity of life on earth",
        "the human genome contains approximately three billion base pairs",
        "antibiotics work by targeting bacterial cell walls or protein synthesis",
        "climate change is driven by increased greenhouse gas emissions",
        "the theory of plate tectonics explains continental drift and earthquakes",
        "stem cells can differentiate into specialized cell types in the body",
        "vaccines train the immune system to recognize specific pathogens",
        "CRISPR technology enables precise gene editing in living organisms",
        "the uncertainty principle states that position and momentum cannot both be precisely known",
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
        "it was a bright cold day in april and the clocks were striking thirteen",
        "all animals are equal but some animals are more equal than others",
        "the only thing we have to fear is fear itself",
        "i have a dream that one day this nation will rise up",
        "ask not what your country can do for you ask what you can do for your country",
        "the unexamined life is not worth living",
        "i think therefore i am",
        "to err is human to forgive divine",
        "the pen is mightier than the sword",
        "a journey of a thousand miles begins with a single step",
        "the only thing constant in life is change",
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
        "jackdaws love my big sphinx of quartz",
        "the quick onyx goblin jumps over the lazy dwarf",
        "crazy frederick bought many very exquisite opal jewels",
        "we promptly judged antique ivory buckles for the next prize",
        "a quick movement of the enemy will jeopardize six gunboats",
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
        "学而时习之不亦说乎有朋自远方来不亦乐乎",
        "三人行必有我师焉择其善者而从之其不善者而改之",
        "知之为知之不知为不知是知也",
        "工欲善其事必先利其器",
        "敏而好学不耻下问",
        "温故而知新可以为师矣",
        "学而不思则罔思而不学则殆",
        "天行健君子以自强不息地势坤君子以厚德载物",
    ],
    "business": [
        "quarterly revenue profit margin fiscal year annual report financial statement",
        "market share competitive advantage strategic partnership stakeholder value",
        "supply chain logistics inventory management procurement vendor negotiation",
        "human resources talent acquisition employee retention performance review",
        "customer satisfaction net promoter score brand loyalty market segmentation",
        "return on investment cost benefit analysis break even point cash flow projection",
        "merger acquisition due diligence intellectual property patent trademark",
        "agile methodology scrum sprint backlog kanban retrospective stakeholder",
        "key performance indicator dashboard analytics data driven decision making",
        "digital transformation automation artificial intelligence machine learning adoption",
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
        "Start small dream big.",
        "Never give up hope.",
        "Trust the process.",
        "Embrace the journey.",
        "Learn from mistakes.",
        "Celebrate small wins.",
        "Progress not perfection.",
        "Be patient with yourself.",
        "Focus on the present.",
        "Challenge yourself daily.",
        "Growth takes time.",
        "Stay curious always.",
        "Keep pushing forward.",
        "Believe in yourself.",
        "Take breaks often.",
        "Rest is productive.",
        "Quality over quantity.",
        "Done is better than perfect.",
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
        "Technology is best when it brings people together.",
        "Innovation distinguishes between a leader and a follower.",
        "The only way to do great work is to love what you do.",
        "Code never lies comments sometimes do.",
        "First solve the problem then write the code.",
        "Make it work make it right make it fast.",
        "Simplicity is the ultimate sophistication.",
        "The best code is no code at all.",
        "Premature optimization is the root of all evil.",
        "Programs must be written for humans to read and only incidentally for machines to execute.",
        "Walking on water and developing software from a specification are easy if both are frozen.",
        "The most disastrous mistake is to assume that software development is easy.",
        "Any fool can write code that a computer can understand but good programmers write code that humans understand.",
        "The difference between a good programmer and a great programmer is knowing when to stop.",
        "Testing shows the presence of bugs not their absence.",
    ],
    "hard": [
        "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs.",
        "Python is a powerful programming language that supports multiple paradigms including procedural, object-oriented, and functional programming.",
        "In computer science, algorithmic efficiency is a property of an algorithm which relates to the number of computational resources used.",
        "The discipline of programming is concerned with the art of constructing and formulating algorithms and encoding them in a programming language.",
        "Consistent refactoring and thoughtful architecture decisions lead to maintainable, scalable, and high-performance software systems.",
        "Distributed systems must handle network partitions, node failures, and message delays while maintaining consistency and availability.",
        "Cryptographic hash functions produce a fixed-size output from variable-length input and are designed to be collision-resistant and one-way.",
        "Machine learning algorithms can be categorized into supervised learning unsupervised learning and reinforcement learning paradigms.",
        "The CAP theorem states that a distributed computer system cannot simultaneously provide all three of consistency availability and partition tolerance.",
        "Concurrency control mechanisms ensure that concurrent transactions execute without violating data integrity in multi-user database systems.",
        "Microservices architecture decomposes applications into small independent services that communicate through well-defined APIs.",
        "The observer pattern defines a one-to-many dependency between objects so that when one object changes state all dependents are notified.",
        "Garbage collection is a form of automatic memory management that attempts to reclaim memory occupied by objects that are no longer in use.",
        "Functional programming treats computation as the evaluation of mathematical functions and avoids changing state and mutable data.",
        "The SOLID principles are five design principles intended to make software designs more understandable flexible and maintainable.",
    ],
    "paragraph": [
        "In the beginning there was chaos, and from chaos came order. The universe expanded from a singularity, cooling as it grew, forming hydrogen and helium. Stars ignited, lived, and died, seeding the cosmos with heavier elements.",
        "Software engineering is not just about writing code. It encompasses requirements analysis, system design, testing, deployment, and maintenance. A great engineer communicates clearly and thinks about the long-term impact of every decision.",
        "The art of asking the right question is more than half the battle of finding the answer. Science advances not by accumulating facts but by transforming how we think about problems, and every revolution starts with a better question.",
        "Discipline is choosing between what you want now and what you want most. Champions are made in the moments when they want to stop. Every repetition, every session, every practice builds the foundation of excellence.",
        "The greatest glory in living lies not in never falling, but in rising every time we fall. Success is not measured by the position one has reached in life, but by the obstacles one has overcome while trying to succeed.",
        "In the realm of software development, the pursuit of perfection often leads to paralysis. The most successful products are not those that waited until everything was perfect, but those that iterated rapidly based on real user feedback.",
        "The relationship between complexity and reliability is inverse. As systems become more complex, they become harder to understand, test, and maintain. Simplicity is not just a virtue; it is a survival strategy.",
        "Every expert was once a beginner. The journey from novice to master is paved with countless mistakes, endless practice, and persistent curiosity. The difference between the expert and the novice is not talent but time and dedication.",
        "Technology shapes society in profound and often unexpected ways. The printing press democratized knowledge, the industrial revolution transformed labor, and now the digital age is redefining how we connect, work, and think.",
        "The scientific method is humanity's most powerful tool for understanding reality. Through observation, hypothesis, experimentation, and analysis, we have uncovered the laws of nature and extended our reach to the stars.",
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

# ==================== 新增奖励系统 ====================

# 连胜加成配置
STREAK_BONUSES = {
    3:  {"exp_mult": 1.1, "title": "三连胜",  "icon": "🔥"},
    5:  {"exp_mult": 1.2, "title": "五连胜",  "icon": "🔥🔥"},
    10: {"exp_mult": 1.5, "title": "十连胜",  "icon": "🔥🔥🔥"},
    15: {"exp_mult": 1.8, "title": "十五连胜", "icon": "⚡"},
    20: {"exp_mult": 2.0, "title": "二十连胜", "icon": "⚡⚡"},
}

# 首次奖励配置
FIRST_REWARDS = {
    "first_game":        {"exp": 30,  "desc": "首次完成游戏",       "icon": "🎮"},
    "first_classic":     {"exp": 50,  "desc": "首次完成经典模式",   "icon": "⚔️"},
    "first_sprint":      {"exp": 50,  "desc": "首次完成极速挑战",   "icon": "⚡"},
    "first_word":        {"exp": 50,  "desc": "首次完成词库练习",   "icon": "📚"},
    "first_timed":       {"exp": 50,  "desc": "首次完成计时挑战",   "icon": "⏱️"},
    "first_blind":       {"exp": 80,  "desc": "首次完成盲打模式",   "icon": "🦅"},
    "first_gauntlet":    {"exp": 100, "desc": "首次通关渐进挑战",   "icon": "🏰"},
    "first_ghost_win":   {"exp": 100, "desc": "首次击败幽灵记录",   "icon": "👻"},
    "first_boss":        {"exp": 150, "desc": "首次击败Boss",       "icon": "👹"},
    "first_perfect":     {"exp": 200, "desc": "首次100%正确率",     "icon": "💎"},
    "first_speed_100":   {"exp": 150, "desc": "首次达到100WPM",     "icon": "🚀"},
}

# 挑战奖励配置
CHALLENGE_REWARDS = {
    "perfect_game":      {"exp": 100, "desc": "单局100%正确率",     "icon": "💎"},
    "speed_demon":       {"exp": 80,  "desc": "净WPM达到100",       "icon": "🚀"},
    "combo_master":      {"exp": 50,  "desc": "单局连击达到50",     "icon": "🔥"},
    "gauntlet_clear":    {"exp": 150, "desc": "通关渐进挑战",       "icon": "🏰"},
    "boss_slayer":       {"exp": 100, "desc": "无伤击败Boss",       "icon": "⚔️"},
    "ghost_crusher":     {"exp": 80,  "desc": "击败幽灵记录10次",   "icon": "👻"},
    "daily_7_streak":    {"exp": 200, "desc": "连续7天完成每日一挑", "icon": "📅"},
    "marathon":          {"exp": 100, "desc": "单局输入500+字符",   "icon": "🏃"},
}

# 随机事件配置
RANDOM_EVENTS = {
    "double_exp": {
        "chance": 0.08,
        "effect": "exp_mult",
        "value": 2.0,
        "desc": "🌟 幸运时刻：经验翻倍！",
        "icon": "✨"
    },
    "bonus_exp": {
        "chance": 0.10,
        "effect": "bonus_exp",
        "value": 30,
        "desc": "💰 意外收获：+30经验！",
        "icon": "💰"
    },
    "triple_combo": {
        "chance": 0.05,
        "effect": "combo_mult",
        "value": 3.0,
        "desc": "🔥 连击狂潮：连击经验×3！",
        "icon": "🔥"
    },
    "easy_mode": {
        "chance": 0.06,
        "effect": "difficulty_down",
        "value": 1,
        "desc": "💚 轻松时刻：难度降低！",
        "icon": "💚"
    },
    "time_gift": {
        "chance": 0.07,
        "effect": "time_add",
        "value": 5,
        "desc": "⏰ 时间馈赠：+5秒！",
        "icon": "⏰"
    },
    "lucky_streak": {
        "chance": 0.04,
        "effect": "streak_protect",
        "value": 1,
        "desc": "🛡️ 幸运护盾：本局失败不中断连胜！",
        "icon": "🛡️"
    },
    "golden_touch": {
        "chance": 0.03,
        "effect": "golden_mode",
        "value": 1,
        "desc": "👑 黄金之手：本局经验×1.5，必定触发随机事件！",
        "icon": "👑"
    },
}

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
                realtime_max_combo=0, realtime_is_perfect=True,
                boss_damage_taken=None):
    """游戏结算核心函数（增强版 - 集成完整奖励系统）"""
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

    # === 新奖励系统集成 ===
    # 1. 触发随机事件
    random_event = trigger_random_event()
    game_state = {"exp_mult": 1.0, "bonus_exp": 0, "combo_mult": 1.0}
    if random_event:
        game_state = apply_event_effect(random_event, game_state)

    # 2. 计算基础经验
    combo_bonus = (combo // 5) * 5
    base_exp = exp_base + combo_bonus

    # 3. 使用总经验计算（含连胜加成）
    total_exp, exp_breakdown = calculate_total_exp(base_exp, stats, game_state)

    # 4. 完美/高连击/幽灵加成
    if realtime_is_perfect and target and user_input:
        total_exp = int(total_exp * 1.5)
        exp_breakdown.append(("💎 完美奖励", "x1.5"))
    elif realtime_max_combo >= 100:
        total_exp = int(total_exp * 1.2)
        exp_breakdown.append(("🔥 百连奖励", "x1.2"))

    if ghost_beat:
        total_exp = int(total_exp * 1.5)
        exp_breakdown.append(("👻 击败幽灵", "x1.5"))

    exp_gain = total_exp

    # 5. 检查首次奖励
    first_rewards = check_first_rewards(stats, mode, net_wpm, accuracy)
    for reward_key, reward_data in first_rewards:
        exp_gain += reward_data["exp"]
        exp_breakdown.append((f"🆕 {reward_data['desc']}", f"+{reward_data['exp']}"))

    # 6. 检查挑战奖励
    challenge_rewards = check_challenge_rewards(
        stats, net_wpm=net_wpm, accuracy=accuracy, combo=combo,
        chars=chars, ghost_beat=ghost_beat, boss_damage_taken=boss_damage_taken
    )
    for reward_key, reward_data in challenge_rewards:
        exp_gain += reward_data["exp"]
        exp_breakdown.append((f"🏆 {reward_data['desc']}", f"+{reward_data['exp']}"))

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
    if random_event: record["random_event"] = random_event["desc"]
    stats["games"].append(record)

    new_ach    = check_achievements(stats, wpm, net_wpm, accuracy, mode,
                                    completed, chars, combo, ghost_beat,
                                    is_daily_ch, is_para)
    daily_done = check_daily_tasks(stats, net_wpm, accuracy, len(user_input), is_daily_ch)
    save_stats(stats)

    # 返回增强的结果（包含奖励明细和随机事件）
    reward_info = {
        "exp_breakdown": exp_breakdown,
        "random_event": random_event,
        "first_rewards": first_rewards,
        "challenge_rewards": challenge_rewards,
        "streak_mult": streak_mult,
    }
    return new_ach, daily_done, old_level, new_level, exp_gain, combo, wpm, net_wpm, accuracy, reward_info


# ==================== 新增奖励系统函数 ====================

import random


def get_streak_bonus(streak):
    """
    获取连胜加成

    Args:
        streak: 当前连胜局数

    Returns:
        dict: {"mult": 倍率, "title": 称号, "icon": 图标}
    """
    for threshold in sorted(STREAK_BONUSES.keys(), reverse=True):
        if streak >= threshold:
            bonus = STREAK_BONUSES[threshold]
            return {
                "mult": bonus["exp_mult"],
                "title": bonus["title"],
                "icon": bonus["icon"],
                "threshold": threshold
            }
    return {"mult": 1.0, "title": "", "icon": "", "threshold": 0}


def check_first_rewards(stats, mode, net_wpm=0, accuracy=0):
    """
    检查首次奖励

    Args:
        stats: 统计数据
        mode: 游戏模式
        net_wpm: 净WPM
        accuracy: 正确率

    Returns:
        list: 获得的首次奖励列表
    """
    first_rewards_done = stats.setdefault("first_rewards", [])
    rewards = []

    # 模式首次奖励映射
    mode_first_map = {
        "classic": "first_classic",
        "sprint": "first_sprint",
        "word": "first_word",
        "timed": "first_timed",
        "blind": "first_blind",
        "gauntlet": "first_gauntlet",
    }

    # 首次游戏
    if "first_game" not in first_rewards_done:
        rewards.append(("first_game", FIRST_REWARDS["first_game"]))
        first_rewards_done.append("first_game")

    # 模式首次
    if mode in mode_first_map:
        reward_key = mode_first_map[mode]
        if reward_key not in first_rewards_done:
            rewards.append((reward_key, FIRST_REWARDS[reward_key]))
            first_rewards_done.append(reward_key)

    # 首次100%正确率
    if accuracy == 100 and "first_perfect" not in first_rewards_done:
        rewards.append(("first_perfect", FIRST_REWARDS["first_perfect"]))
        first_rewards_done.append("first_perfect")

    # 首次100WPM
    if net_wpm >= 100 and "first_speed_100" not in first_rewards_done:
        rewards.append(("first_speed_100", FIRST_REWARDS["first_speed_100"]))
        first_rewards_done.append("first_speed_100")

    stats["first_rewards"] = first_rewards_done
    return rewards


def check_challenge_rewards(stats, net_wpm=0, accuracy=0, combo=0,
                            chars=0, ghost_beat=False, boss_damage_taken=0):
    """
    检查挑战奖励

    Args:
        stats: 统计数据
        net_wpm: 净WPM
        accuracy: 正确率
        combo: 连击数
        chars: 字符数
        ghost_beat: 是否击败幽灵
        boss_damage_taken: Boss战受到的伤害

    Returns:
        list: 获得的挑战奖励列表
    """
    challenge_done = stats.setdefault("challenge_rewards", [])
    rewards = []

    # 完美游戏
    if accuracy == 100 and "perfect_game" not in challenge_done:
        rewards.append(("perfect_game", CHALLENGE_REWARDS["perfect_game"]))
        challenge_done.append("perfect_game")

    # 速度恶魔
    if net_wpm >= 100 and "speed_demon" not in challenge_done:
        rewards.append(("speed_demon", CHALLENGE_REWARDS["speed_demon"]))
        challenge_done.append("speed_demon")

    # 连击大师
    if combo >= 50 and "combo_master" not in challenge_done:
        rewards.append(("combo_master", CHALLENGE_REWARDS["combo_master"]))
        challenge_done.append("combo_master")

    # 马拉松
    if chars >= 500 and "marathon" not in challenge_done:
        rewards.append(("marathon", CHALLENGE_REWARDS["marathon"]))
        challenge_done.append("marathon")

    # Boss杀手（无伤）
    if boss_damage_taken is not None and boss_damage_taken == 0 and "boss_slayer" not in challenge_done:
        rewards.append(("boss_slayer", CHALLENGE_REWARDS["boss_slayer"]))
        challenge_done.append("boss_slayer")

    stats["challenge_rewards"] = challenge_done
    return rewards


def trigger_random_event():
    """
    触发随机事件

    Returns:
        dict or None: 触发的事件，包含effect, value, desc, icon
    """
    for event_id, event in RANDOM_EVENTS.items():
        if random.random() < event["chance"]:
            return {
                "id": event_id,
                "effect": event["effect"],
                "value": event["value"],
                "desc": event["desc"],
                "icon": event["icon"]
            }
    return None


def apply_event_effect(event, game_state):
    """
    应用随机事件效果

    Args:
        event: 事件数据
        game_state: 游戏状态字典

    Returns:
        dict: 修改后的游戏状态
    """
    if not event:
        return game_state

    effect = event["effect"]
    value = event["value"]

    if effect == "exp_mult":
        game_state["exp_mult"] = game_state.get("exp_mult", 1.0) * value
    elif effect == "bonus_exp":
        game_state["bonus_exp"] = game_state.get("bonus_exp", 0) + value
    elif effect == "combo_mult":
        game_state["combo_mult"] = game_state.get("combo_mult", 1.0) * value
    elif effect == "difficulty_down":
        game_state["difficulty_mod"] = game_state.get("difficulty_mod", 0) - value
    elif effect == "time_add":
        game_state["bonus_time"] = game_state.get("bonus_time", 0) + value
    elif effect == "streak_protect":
        game_state["streak_protect"] = True
    elif effect == "golden_mode":
        game_state["exp_mult"] = game_state.get("exp_mult", 1.0) * 1.5
        game_state["golden_mode"] = True

    return game_state


def calculate_total_exp(base_exp, stats, game_state=None):
    """
    计算总经验（包含所有加成）

    Args:
        base_exp: 基础经验
        stats: 统计数据
        game_state: 游戏状态（包含各种加成）

    Returns:
        tuple: (总经验, 加成明细列表)
    """
    game_state = game_state or {}
    breakdown = []

    total = base_exp
    breakdown.append(("基础经验", base_exp))

    # 连胜加成
    streak = stats.get("streak", 0)
    streak_bonus = get_streak_bonus(streak)
    if streak_bonus["mult"] > 1:
        add = int(base_exp * (streak_bonus["mult"] - 1))
        total += add
        breakdown.append((f"{streak_bonus['icon']} {streak_bonus['title']}", f"+{add}"))

    # 技能加成
    skills = stats.get("skills", {})
    exp_boost = 1 + skills.get("exp_boost", 0) * 0.10
    if exp_boost > 1:
        add = int(base_exp * (exp_boost - 1))
        total += add
        breakdown.append(("⚡ 经验技能", f"+{add}"))

    # 随机事件加成
    event_mult = game_state.get("exp_mult", 1.0)
    if event_mult > 1:
        add = int(base_exp * (event_mult - 1))
        total += add
        breakdown.append(("✨ 事件加成", f"+{add}"))

    # 额外经验
    bonus_exp = game_state.get("bonus_exp", 0)
    if bonus_exp > 0:
        total += bonus_exp
        breakdown.append(("💰 意外收获", f"+{bonus_exp}"))

    return total, breakdown


# ==================== 进度反馈系统函数 ====================

def get_level_progress(stats):
    """
    获取升级进度信息

    Args:
        stats: 统计数据

    Returns:
        dict: 进度信息
    """
    level, cur_exp, need_exp = get_level(stats.get("exp", 0))
    progress_pct = (cur_exp / need_exp * 100) if need_exp > 0 else 0

    # 计算平均每局经验
    games = stats.get("games", [])
    if games:
        recent = games[-10:]
        avg_exp = sum(g.get("exp", 0) for g in recent) / len(recent) if recent else 30
    else:
        avg_exp = 30

    games_to_level = max(1, int((need_exp - cur_exp) / avg_exp)) if avg_exp > 0 else 1

    return {
        "level": level,
        "cur_exp": cur_exp,
        "need_exp": need_exp,
        "progress_pct": progress_pct,
        "games_to_level": games_to_level,
        "next_level": level + 1
    }


def get_achievement_progress(stats):
    """
    获取接近解锁的成就进度

    Args:
        stats: 统计数据

    Returns:
        list: 进度列表
    """
    unlocked = stats.get("achievements", [])
    progress_list = []

    total_games = stats.get("total_games", 0)
    total_chars = stats.get("total_chars", 0)
    best_net_wpm = stats.get("best_net_wpm", 0)
    login_days = stats.get("login_days", 0)
    max_combo = stats.get("max_combo", 0)

    # 检查游戏局数成就
    game_milestones = [("games_10", 10), ("games_50", 50), ("games_100", 100), ("games_500", 500)]
    for ach_id, target in game_milestones:
        if ach_id not in unlocked and total_games > 0:
            pct = min(100, total_games / target * 100)
            if pct >= 30:
                progress_list.append({
                    "id": ach_id,
                    "name": ACHIEVEMENTS[ach_id]["name"],
                    "icon": ACHIEVEMENTS[ach_id]["icon"],
                    "progress": pct,
                    "current": total_games,
                    "target": target
                })

    # 检查WPM成就
    wpm_milestones = [("speed_30", 30), ("speed_50", 50), ("speed_80", 80), ("speed_100", 100)]
    for ach_id, target in wpm_milestones:
        if ach_id not in unlocked:
            pct = min(100, best_net_wpm / target * 100)
            if pct >= 50:
                progress_list.append({
                    "id": ach_id,
                    "name": ACHIEVEMENTS[ach_id]["name"],
                    "icon": ACHIEVEMENTS[ach_id]["icon"],
                    "progress": pct,
                    "current": best_net_wpm,
                    "target": target
                })

    # 检查字符成就
    char_milestones = [("word_10k", 10000), ("word_50k", 50000), ("word_100k", 100000)]
    for ach_id, target in char_milestones:
        if ach_id not in unlocked and total_chars > 0:
            pct = min(100, total_chars / target * 100)
            if pct >= 30:
                progress_list.append({
                    "id": ach_id,
                    "name": ACHIEVEMENTS[ach_id]["name"],
                    "icon": ACHIEVEMENTS[ach_id]["icon"],
                    "progress": pct,
                    "current": total_chars,
                    "target": target
                })

    # 按进度排序，取前3个
    progress_list.sort(key=lambda x: x["progress"], reverse=True)
    return progress_list[:3]


def get_daily_task_progress(stats):
    """
    获取每日任务进度

    Args:
        stats: 统计数据

    Returns:
        list: 任务进度列表
    """
    check_daily_reset(stats)
    daily = stats.get("daily", {})
    tasks = []

    for task in DAILY_TASKS:
        tid = task["id"]
        done = daily.get("tasks", {}).get(tid, False)

        if not done:
            if task["type"] == "games":
                current = daily.get("games", 0)
            elif task["type"] == "wpm":
                # 使用今日最高WPM
                current = max((g.get("net_wpm", 0) for g in stats.get("games", [])[-20:]
                              if g.get("mode") != "daily"), default=0)
            elif task["type"] == "accuracy":
                current = max((g.get("accuracy", 0) for g in stats.get("games", [])[-20:]
                              if g.get("mode") != "daily"), default=0)
            elif task["type"] == "chars":
                current = max((len(g.get("user_input", "")) for g in stats.get("games", [])[-20:]), default=0)
            elif task["type"] == "daily_ch":
                current = 1 if daily.get("daily_ch_done") else 0
            else:
                current = 0

            progress = min(100, current / task["target"] * 100) if task["target"] > 0 else 0

            tasks.append({
                "id": tid,
                "desc": task["desc"],
                "reward": task["reward"],
                "current": current,
                "target": task["target"],
                "progress": progress
            })

    return tasks


def generate_weekly_report(stats):
    """
    生成周报

    Args:
        stats: 统计数据

    Returns:
        dict: 周报数据
    """
    from datetime import datetime, timedelta

    games = stats.get("games", [])
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    # 本周游戏
    this_week_games = [
        g for g in games
        if datetime.fromisoformat(g.get("date", "2000-01-01")) >= week_ago
    ]

    # 上周游戏
    last_week_games = [
        g for g in games
        if two_weeks_ago <= datetime.fromisoformat(g.get("date", "2000-01-01")) < week_ago
    ]

    # 本周统计
    this_week_wpm = [g.get("net_wpm", 0) for g in this_week_games]
    this_week_acc = [g.get("accuracy", 0) for g in this_week_games]

    # 上周统计
    last_week_wpm = [g.get("net_wpm", 0) for g in last_week_games]
    last_week_acc = [g.get("accuracy", 0) for g in last_week_games]

    avg_wpm_this = sum(this_week_wpm) / len(this_week_wpm) if this_week_wpm else 0
    avg_wpm_last = sum(last_week_wpm) / len(last_week_wpm) if last_week_wpm else 0
    avg_acc_this = sum(this_week_acc) / len(this_week_acc) if this_week_acc else 0
    avg_acc_last = sum(last_week_acc) / len(last_week_acc) if last_week_acc else 0

    # 本周成就
    recent_achievements = []
    for ach_id in stats.get("achievements", []):
        # 简化：假设最近添加的成就是本周的
        if ach_id not in stats.get("achievements", [])[:-10]:
            recent_achievements.append(ACHIEVEMENTS.get(ach_id, {}).get("name", ach_id))

    # 亮点
    highlights = []
    if this_week_wpm and max(this_week_wpm) > (stats.get("best_net_wpm", 0) * 0.9):
        highlights.append(f"🎯 本周最高WPM: {max(this_week_wpm)}")
    if len(this_week_games) >= 20:
        highlights.append(f"🎮 本周游玩{len(this_week_games)}局，坚持练习！")
    if avg_wpm_this > avg_wpm_last and avg_wpm_last > 0:
        highlights.append(f"📈 WPM提升 {int(avg_wpm_this - avg_wpm_last)} 点")

    return {
        "period": "本周",
        "games_played": len(this_week_games),
        "total_chars": sum(g.get("chars", 0) for g in this_week_games),
        "avg_wpm": int(avg_wpm_this),
        "avg_accuracy": int(avg_acc_this),
        "best_wpm": max(this_week_wpm) if this_week_wpm else 0,
        "levels_gained": 0,  # 需要更复杂的计算
        "achievements_unlocked": recent_achievements[:5],
        "improvement": {
            "wpm_change": int(avg_wpm_this - avg_wpm_last),
            "acc_change": int(avg_acc_this - avg_acc_last),
        },
        "highlights": highlights
    }


# ==================== 动态难度系统 ====================

class DynamicDifficulty:
    """动态难度调整系统"""

    # 难度等级定义 (1-5)
    DIFFICULTY_LEVELS = {
        1: {"name": "初级", "color": "92m", "wpm_range": (0, 30), "acc_range": (0, 70)},
        2: {"name": "中级", "color": "93m", "wpm_range": (30, 50), "acc_range": (70, 85)},
        3: {"name": "高级", "color": "94m", "wpm_range": (50, 70), "acc_range": (85, 92)},
        4: {"name": "专家", "color": "95m", "wpm_range": (70, 90), "acc_range": (92, 97)},
        5: {"name": "大师", "color": "93m", "wpm_range": (90, 200), "acc_range": (97, 100)},
    }

    def __init__(self, stats):
        self.stats = stats
        self.difficulty_range = [1, 5]
        self.adjustment_threshold = 0.15

    def get_current_difficulty(self):
        """获取当前动态难度"""
        base = self._calculate_base_difficulty()
        adjustment = self._calculate_adjustment()
        final = base + adjustment
        return max(1, min(5, round(final, 1)))

    def _calculate_base_difficulty(self):
        """计算基础难度"""
        level = self.stats.get("level", 1)
        avg_wpm = self._get_recent_avg_wpm()

        # 综合等级和速度
        difficulty = 1 + (level / 15) + (avg_wpm / 80)
        return min(5, difficulty)

    def _calculate_adjustment(self):
        """计算难度调整"""
        recent = self._analyze_recent_performance()
        if not recent:
            return 0

        # 根据最近表现调整
        wpm = recent.get("wpm", 50)
        acc = recent.get("accuracy", 85)

        adjustment = 0

        # WPM调整
        if wpm > 80:
            adjustment += 0.3
        elif wpm > 60:
            adjustment += 0.1
        elif wpm < 30:
            adjustment -= 0.2

        # 准确率调整
        if acc > 95:
            adjustment += 0.2
        elif acc < 70:
            adjustment -= 0.3

        return adjustment

    def _get_recent_avg_wpm(self):
        """获取最近平均WPM"""
        games = self.stats.get("games", [])[-10:]
        if not games:
            return 50
        return sum(g.get("net_wpm", 0) for g in games) / len(games)

    def _analyze_recent_performance(self):
        """分析最近表现"""
        games = self.stats.get("games", [])[-10:]
        if not games:
            return None

        avg_wpm = sum(g.get("net_wpm", 0) for g in games) / len(games)
        avg_acc = sum(g.get("accuracy", 0) for g in games) / len(games)

        return {"wpm": avg_wpm, "accuracy": avg_acc}

    def get_difficulty_name(self, difficulty):
        """获取难度名称"""
        level = max(1, min(5, int(difficulty)))
        return self.DIFFICULTY_LEVELS[level]["name"]

    def get_difficulty_color(self, difficulty):
        """获取难度颜色代码"""
        level = max(1, min(5, int(difficulty)))
        return "\033[" + self.DIFFICULTY_LEVELS[level]["color"]

    def select_text_by_difficulty(self, texts, difficulty):
        """根据难度选择文本"""
        # 将难度映射到文本难度级别
        if difficulty <= 1.5:
            level = "easy"
        elif difficulty <= 3:
            level = "medium"
        else:
            level = "hard"

        available = texts.get(level, [])
        if not available:
            # 回退到任意可用文本
            for lvl in ["easy", "medium", "hard"]:
                if texts.get(lvl):
                    available = texts[lvl]
                    break

        return random.choice(available) if available else ""


# 全局动态难度实例
_dynamic_difficulty = None


def get_dynamic_difficulty(stats):
    """获取动态难度实例"""
    global _dynamic_difficulty
    if _dynamic_difficulty is None or _dynamic_difficulty.stats != stats:
        _dynamic_difficulty = DynamicDifficulty(stats)
    return _dynamic_difficulty


def get_adaptive_difficulty(stats):
    """
    获取自适应难度值（简化接口）

    Args:
        stats: 统计数据

    Returns:
        float: 难度值 (1.0 - 5.0)
    """
    dd = get_dynamic_difficulty(stats)
    return dd.get_current_difficulty()
