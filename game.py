"""
MOTIP - Master Of Typing Interactivity Practice
打字速度测试游戏 - 
  - 实时打字反馈（字符级高亮 + 光标 + 实时 WPM）
  - 净 WPM 计算（错误字符会扣分，更真实）
  - 新模式：每日一挑（日期种子固定题目）
  - 新模式：幽灵竞速（对抗个人最佳记录）
  - 新模式：段落挑战（更长文本测耐力）
  - 大幅扩充词库（科学 / 文学 / 更多 code 片段）
  - 每日任务在主菜单实时显示进度
  - 本局会话统计（游玩后汇总）
  - 技能系统重平衡（更直观的加成）
  - 全新成就（新模式 + 净 WPM 里程碑）
  - Sprint 模式加入实时 WPM 竞速感
"""

import random
import time
import os
import sys
import json
from datetime import datetime, date
from collections import Counter

# ==================== 颜色系统 ====================

class C:
    """ANSI 颜色常量，Windows 10+ 原生支持"""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    ITALIC  = "\033[3m"

    BLACK   = "\033[30m";  BBLACK   = "\033[90m"
    RED     = "\033[31m";  BRED     = "\033[91m"
    GREEN   = "\033[32m";  BGREEN   = "\033[92m"
    YELLOW  = "\033[33m";  BYELLOW  = "\033[93m"
    BLUE    = "\033[34m";  BBLUE    = "\033[94m"
    MAGENTA = "\033[35m";  BMAGENTA = "\033[95m"
    CYAN    = "\033[36m";  BCYAN    = "\033[96m"
    WHITE   = "\033[37m";  BWHITE   = "\033[97m"

    BG_RED     = "\033[41m"
    BG_GREEN   = "\033[42m"
    BG_YELLOW  = "\033[43m"
    BG_BLUE    = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN    = "\033[46m"
    BG_WHITE   = "\033[47m"
    BG_BLACK   = "\033[40m"
    BG_BWHITE  = "\033[107m"

# ANSI 光标控制
_UP   = "\033[1A"
_COL1 = "\r"
_CLR  = "\033[2K"

def enable_ansi():
    """Windows 终端启用 ANSI 颜色"""
    if os.name == 'nt':
        import ctypes
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass

def c(text, *styles):
    return "".join(styles) + str(text) + C.RESET

def bar_fg(cur, max_val, width=20, full_char="█", empty_char="░",
           full_color=C.BGREEN, empty_color=C.BBLACK):
    filled = int(cur / max_val * width) if max_val > 0 else 0
    filled = min(filled, width)
    return (full_color + full_char * filled +
            empty_color + empty_char * (width - filled) + C.RESET)

def exp_bar(cur, need, width=24):
    return bar_fg(cur, need, width, "▰", "▱", C.BCYAN, C.BBLACK)

def separator(char="─", width=60, color=C.BBLUE):
    return c(char * width, color)

def wpm_color(wpm):
    if wpm >= 100: return C.BMAGENTA
    if wpm >= 70:  return C.BGREEN
    if wpm >= 40:  return C.BYELLOW
    return C.BRED

def acc_color(acc):
    if acc >= 95: return C.BGREEN
    if acc >= 80: return C.BYELLOW
    return C.BRED

# ==================== 实时输入系统 ====================

def _getch():
    """跨平台单字符读取"""
    if os.name == 'nt':
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ('\x00', '\xe0'):   # 特殊键（方向键等）跳过
            msvcrt.getwch()
            return None
        return ch
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch

def realtime_type(target, mode_label="", ghost_wpm=0):
    """
    实时打字核心函数。
    - 字符级高亮：绿=正确，红=错误，暗=未到，青色背景=光标
    - 实时 WPM 和净字符计数
    - ghost_wpm > 0 时显示幽灵提示
    返回: (user_input: str, elapsed: float) 或 (None, 0) 若按 ESC
    """
    typed   = []
    start_t = None
    LINES   = 3  # target + input + stats
    
    # 注入扩展属性以供外部提取结算时的统计
    realtime_type.max_combo = 0
    realtime_type.total_errors_made = 0
    realtime_type.is_perfect = True
    
    dynamic_ghost_wpm = ghost_wpm

    def _render(typed_list):
        nonlocal dynamic_ghost_wpm
        tt = "".join(typed_list)
        tl = len(target)

        # 构建带颜色的目标行
        tgt = ""
        for i, tc in enumerate(target):
            if i < len(tt):
                tgt += c(tc, C.BGREEN if tc == tt[i] else C.BRED + C.BOLD)
            elif i == len(tt):
                bg = C.BG_CYAN if tc != " " else C.BG_BLUE
                tgt += c(tc, bg, C.BLACK, C.BOLD)
            else:
                tgt += c(tc, C.BBLACK)
        if len(tt) >= tl:
            tgt += c("▌", C.BCYAN) if len(tt) == tl else ""
        extra_str = c(tt[tl:], C.BYELLOW, C.BOLD) if len(tt) > tl else ""

        # 构建带颜色的输入行
        inp = ""
        for i, uc in enumerate(tt):
            if i < tl:
                inp += c(uc, C.BGREEN if uc == target[i] else C.BRED + C.BOLD)
            else:
                inp += c(uc, C.BYELLOW, C.BOLD)

        # 统计数据
        correct_chars = sum(1 for i, uc in enumerate(tt[:tl]) if uc == target[i])
        errors        = len(tt) - correct_chars if tt else 0
        
        # 连击系统计算
        streak = 0
        for i, uc in enumerate(tt[:tl]):
            if uc == target[i]:
                streak += 1
            else:
                streak = 0
                
        if streak > realtime_type.max_combo:
            realtime_type.max_combo = streak
            
        combo_str = ""
        if streak >= 10:
            combo_c = C.BYELLOW if streak < 30 else C.BCYAN if streak < 50 else C.BMAGENTA
            shake = C.BOLD if streak >= 30 else ""
            combo_str = f"  {c('🔥 '+str(streak)+' 連擊!', combo_c, shake, C.ITALIC)}"

        prog_bar      = bar_fg(min(len(tt), tl), tl, width=20,
                               full_char="▸", empty_char="·",
                               full_color=C.BGREEN, empty_color=C.BBLACK)

        if start_t and tt:
            el   = max(0.001, time.time() - start_t)
            gross = int((len(tt) / 5) / (el / 60))
            net   = max(0, int(((correct_chars / 5) - (errors / 5)) / (el / 60)))
            wc    = wpm_color(net)
            
            # [游戏性提升] 动态难度：幽灵赛橡皮筋机制
            ghost_str = ""
            if ghost_wpm > 0:
                if net > dynamic_ghost_wpm + 3:
                    dynamic_ghost_wpm += 0.5
                elif net < dynamic_ghost_wpm - 3:
                    dynamic_ghost_wpm -= 0.5
                dynamic_ghost_wpm = max(ghost_wpm * 0.7, min(dynamic_ghost_wpm, ghost_wpm * 1.3))
                
                expected_ghost_chars = (dynamic_ghost_wpm * 5) * (el / 60)
                ghost_lead = expected_ghost_chars - correct_chars
                gl_str = f"超前{int(ghost_lead)}字" if ghost_lead > 0 else f"落后{int(-ghost_lead)}字"
                ghost_str = f"  | {c('👻 幽灵 '+str(int(dynamic_ghost_wpm))+'WPM ('+gl_str+')', C.BMAGENTA)}"

            stats_str = (
                f" {c(str(net)+'净', wc, C.BOLD)}/{c(str(gross)+'毛WPM', C.BBLACK)}"
                f"  {c(str(correct_chars)+'✓', C.BGREEN)}"
                + (f" {c(str(errors)+'✗', C.BRED)}" if errors else "")
                + f"  {prog_bar}"
                + ghost_str
                + combo_str
            )
        else:
            stats_str = (
                f" {c('等待输入...', C.BBLACK, C.ITALIC)}"
                + (f"  {c('👻 对抗幽灵: '+str(ghost_wpm)+' WPM', C.BMAGENTA)}" if ghost_wpm > 0 else "")
                + f"  {prog_bar}"
                + combo_str
            )

        return tgt + extra_str, inp, stats_str

    # 首次绘制
    tgt_d, inp_d, stats_d = _render([])
    hint_suffix = f"  {c('['+mode_label+'] ESC=退出 Backspace=删除 Enter=确认', C.BBLACK, C.ITALIC)}" if mode_label else ""
    print(f" {c('目标', C.BBLACK)}: {tgt_d}{hint_suffix}")
    print(f" {c('输入', C.BBLACK)}: {inp_d}")
    print(f"{stats_d}")

    try:
        while True:
            ch = _getch()

            if ch is None:
                continue
                
            is_new_error = False

            if ch in ('\r', '\n'):
                print()
                break
            elif ch in ('\x08', '\x7f'):
                if typed:
                    typed.pop()
            elif ch == '\x1b':
                print()
                return None, 0
            elif ch.isprintable():
                if start_t is None:
                    start_t = time.time()
                
                # [游戏性提升] 错误检测用于闪烁和统计
                if len(typed) < len(target) and ch != target[len(typed)]:
                    is_new_error = True
                    realtime_type.total_errors_made += 1
                    realtime_type.is_perfect = False
                elif len(typed) >= len(target):
                    is_new_error = True
                    realtime_type.total_errors_made += 1
                    realtime_type.is_perfect = False
                    
                typed.append(ch)
            else:
                continue

            # 重绘 3 行
            sys.stdout.write((_UP + _COL1 + _CLR) * LINES)
            tgt_d, inp_d, stats_d = _render(typed)
            
            # [游戏性提升] 视觉反馈：Error Flash
            if is_new_error:
                sys.stdout.write(f"{C.BG_RED} {c('目标', C.BBLACK)}: {tgt_d} {C.RESET}\n")
                sys.stdout.write(f"{C.BG_RED} {c('输入', C.BBLACK)}: {inp_d} {C.RESET}\n")
                sys.stdout.write(f"{C.BG_RED}{stats_d}{C.RESET}\n")
                sys.stdout.flush()
                time.sleep(0.04) # 短促闪烁
                sys.stdout.write((_UP + _COL1 + _CLR) * LINES)
            
            sys.stdout.write(f" {c('目标', C.BBLACK)}: {tgt_d}\n")
            sys.stdout.write(f" {c('输入', C.BBLACK)}: {inp_d}\n")
            sys.stdout.write(f"{stats_d}\n")
            sys.stdout.flush()

    except KeyboardInterrupt:
        print()
        return None, 0

    elapsed = time.time() - (start_t or time.time())
    return "".join(typed), max(0.01, elapsed)

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

def load_custom_words():
    if os.path.exists(CUSTOM_WORDS_FILE):
        with open(CUSTOM_WORDS_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    return []

def save_custom_word(word):
    with open(CUSTOM_WORDS_FILE, 'a', encoding='utf-8') as f:
        f.write(word + '\n')

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

# ==================== 工具函数 ====================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def load_stats():
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
    out = dict(stats)
    if isinstance(out.get("key_stats"), Counter):
        out["key_stats"] = dict(out["key_stats"])
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

def load_config():
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
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def get_level(exp):
    level, needed = 1, 100
    while exp >= needed:
        exp -= needed
        level += 1
        needed = int(100 * level * 1.5)
    return level, exp, needed

def calculate_accuracy(original, typed):
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

def diff_display(target, typed):
    r_target, r_typed = "", ""
    for i, tc in enumerate(target):
        if i < len(typed):
            uc = typed[i]
            if tc == uc:
                r_target += c(tc, C.BGREEN);  r_typed += c(uc, C.BGREEN)
            else:
                r_target += c(tc, C.BRED, C.BOLD); r_typed += c(uc, C.BRED, C.BOLD)
        else:
            r_target += c(tc, C.BBLACK)
    if len(typed) > len(target):
        r_typed += c(typed[len(target):], C.BYELLOW)
    return r_target, r_typed

def track_key_errors(target, typed, stats):
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
    new_ach = []
    ach = stats.setdefault("achievements", [])

    def unlock(key):
        if key not in ach:
            new_ach.append(key); ach.append(key)

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

def get_rating(net_wpm, accuracy):
    if   net_wpm >= 120 and accuracy >= 95: return "SSS", "神级打字大师！",  c("SSS", C.BMAGENTA, C.BOLD), "👑"
    elif net_wpm >= 80  and accuracy >= 90: return "S",   "炉火纯青！",      c("S",   C.BYELLOW,  C.BOLD), "⭐"
    elif net_wpm >= 60  and accuracy >= 85: return "A",   "优秀！",          c("A",   C.BGREEN,   C.BOLD), "✨"
    elif net_wpm >= 40  and accuracy >= 75: return "B",   "不错！",          c("B",   C.BCYAN,    C.BOLD), "👍"
    elif net_wpm >= 20  and accuracy >= 60: return "C",   "继续加油！",      c("C",   C.BYELLOW         ), "💪"
    else:                                   return "D",   "多多练习！",      c("D",   C.BRED             ), "🌱"

def ascii_wpm_chart(wpm_history, net_history=None, width=46, height=7):
    if not wpm_history:
        return "  暂无 WPM 历史记录"
    data  = wpm_history[-width:]
    ndata = (net_history or [])[-width:]
    max_v = max(data) or 1
    min_v = min(data)
    lines = []
    for row in range(height, 0, -1):
        threshold = min_v + (max_v - min_v) * row / height
        line = ""
        for i, val in enumerate(data):
            net_val = ndata[i] if i < len(ndata) else val
            if val >= threshold:
                line += c("█", C.BCYAN)
            elif net_val >= threshold:
                line += c("▒", C.BBLUE)
            else:
                line += c("░", C.BBLACK)
        lines.append("  " + c(f"{int(threshold):>3}", C.BBLACK) + " " + line)
    lines.append("  " + c("─" * (len(data) + 5), C.BBLACK))
    lines.append(
        f"  最低:{c(str(min_v), C.BRED)}  最高:{c(str(max_v), C.BGREEN)}"
        f"  最近毛:{c(str(wpm_history[-1]), C.BCYAN)}"
        + (f"  净:{c(str(ndata[-1]), C.BBLUE)}" if ndata else "")
    )
    lines.append(f"  {c('█', C.BCYAN)}=毛WPM  {c('▒', C.BBLUE)}=净WPM  {c('░', C.BBLACK)}=低于线")
    return "\n".join(lines)

def record_wpm(stats, wpm, net_wpm=None):
    h = stats.setdefault("wpm_history", [])
    h.append(wpm)
    if len(h) > 200: stats["wpm_history"] = h[-200:]
    if net_wpm is not None:
        nh = stats.setdefault("net_wpm_history", [])
        nh.append(net_wpm)
        if len(nh) > 200: stats["net_wpm_history"] = nh[-200:]

def word_combo_score(target_words, typed_words):
    max_combo = cur = 0
    for tw, uw in zip(target_words, typed_words):
        if tw == uw: cur += 1; max_combo = max(max_combo, cur)
        else: cur = 0
    return max_combo

def update_mode_best(stats, mode, wpm, net_wpm, accuracy):
    bests = stats.setdefault("mode_bests", {})
    prev  = bests.get(mode, {"wpm": 0, "net_wpm": 0, "accuracy": 0})
    prev["wpm"]      = max(prev.get("wpm", 0), wpm)
    prev["net_wpm"]  = max(prev.get("net_wpm", 0), net_wpm)
    prev["accuracy"] = max(prev.get("accuracy", 0), accuracy)
    bests[mode] = prev

# ==================== 核心结算函数 ====================

def _finish_game(stats, mode, raw_wpm, raw_net_wpm, raw_acc, exp_base,
                 target="", user_input="", elapsed=0,
                 completed=0, chars=0, difficulty="medium", extra=None,
                 ghost_beat=False, is_daily_ch=False, is_para=False):
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
    
    # [游戏性提升] 长线追求深化：经验值加倍关联
    rt_max_combo = getattr(realtime_type, 'max_combo', 0)
    rt_is_perfect = getattr(realtime_type, 'is_perfect', False)
    
    if rt_is_perfect and target and user_input:
        exp_gain = int(exp_gain * 1.5)
    elif rt_max_combo >= 100:
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

    sess = stats.setdefault("session", {"games": 0, "wpm_sum": 0, "acc_sum": 0, "start": ""})
    if not sess.get("start"):
        sess["start"] = datetime.now().isoformat()
    sess["games"]   = sess.get("games", 0) + 1
    sess["wpm_sum"] = sess.get("wpm_sum", 0) + net_wpm
    sess["acc_sum"] = sess.get("acc_sum", 0) + accuracy

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

# ==================== 结果展示 ====================

def show_result(target, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_level, level, new_ach, daily_tasks=None, combo=0,
                mode="", prev_best_net=0, ghost_beat=False):
    clear_screen()
    print(separator("═"))
    print(c("  游戏结果", C.BCYAN, C.BOLD))
    print(separator("─"))

    r_target, r_typed = diff_display(target, user_input)
    print(f" {c('目标', C.BBLACK)}: {r_target}")
    print(f" {c('输入', C.BBLACK)}: {r_typed}")
    print(separator("─"))

    wc = wpm_color(net_wpm)
    ac = acc_color(accuracy)
    print(
        f"  ⏱  {c(f'{elapsed:.2f}s', C.BCYAN)}"
        f"   ⚡{c(str(net_wpm)+'净WPM', wc, C.BOLD)}"
        f"  {c('(毛'+str(wpm)+')', C.BBLACK)}"
        f"   🎯{c(str(accuracy)+'%', ac)}"
        f"   🔥{c('x'+str(combo), C.BMAGENTA)}"
    )

    if prev_best_net > 0:
        diff_v = net_wpm - prev_best_net
        diff_s = (c(f"+{diff_v}", C.BGREEN) if diff_v >= 0 else c(str(diff_v), C.BRED))
        print(f"  {c('历史最佳净WPM: '+str(prev_best_net), C.BBLACK)}  本局差值: {diff_s}")
    if ghost_beat:
        print(c("  👻 击败幽灵记录！经验 x1.5！", C.BMAGENTA, C.BOLD))

    print(separator("─"))
    print(f"  {icon}  {rating_col}  {c(text, C.BOLD)}")

    lv_str = (c(f"Lv.{old_level}", C.BYELLOW) + " ➜ " + c(f"Lv.{level}", C.BGREEN, C.BOLD)
              if level > old_level else c(f"Lv.{level}", C.BYELLOW))
    print(f"  {c('+'+str(exp_gain)+'XP', C.BGREEN)}  {lv_str}")

    if daily_tasks:
        print(separator("─"))
        print(c("  📋 每日任务完成！", C.BYELLOW))
        for task in daily_tasks:
            print(f"    ✅ {task['desc']}  {c('+'+str(task['reward'])+'XP', C.BGREEN)}")

    if new_ach:
        print(separator("─"))
        print(c("  🏆 成就解锁！", C.BYELLOW, C.BOLD))
        for a in new_ach:
            print(f"    {ACHIEVEMENTS[a]['icon']} {c(ACHIEVEMENTS[a]['name'], C.BMAGENTA, C.BOLD)}"
                  f"  {c(ACHIEVEMENTS[a]['desc'], C.BBLACK)}")

    print(separator("═"))
    input(c("\n按 Enter 继续...", C.BBLACK))

# ==================== UI 函数 ====================

def get_rpg_title(level):
    if level < 5: return "打字学徒"
    if level < 10: return "键盘游侠"
    if level < 20: return "键盘黑客"
    if level < 30: return "代码刺客"
    if level < 40: return "极速掌控者"
    if level < 50: return "赛博打字机"
    return "打字之神"

def show_menu(stats):
    check_daily_reset(stats)
    save_stats(stats)

    level, cur_exp, need_exp = get_level(stats.get("exp", 0))
    bar = exp_bar(cur_exp, need_exp)

    daily       = stats.get("daily", {})
    tasks_done  = sum(1 for t in DAILY_TASKS if daily.get("tasks", {}).get(t["id"]))
    tasks_total = len(DAILY_TASKS)

    print(separator("═"))
    print(c("  ███╗   ███╗ ██████╗ ████████╗██╗██████╗", C.BCYAN, C.BOLD))
    print(c("  ████╗ ████║██╔═══██╗╚══██╔══╝██║██╔══██╗", C.CYAN))
    print(c("  ██╔████╔██║██║   ██║   ██║   ██║██████╔╝  v6.0", C.BCYAN))
    print(c("  ██║╚██╔╝██║██║   ██║   ██║   ██║██╔═══╝", C.CYAN))
    print(c("  ██║ ╚═╝ ██║╚██████╔╝   ██║   ██║██║", C.BCYAN))
    print(c("  ╚═╝     ╚═╝ ╚═════╝    ╚═╝   ╚═╝╚═╝  打字速度测试  旗舰版", C.BBLACK))
    print(separator("─"))
    title = get_rpg_title(level)
    print(f"  {c('Lv.'+str(level)+' ['+title+']', C.BMAGENTA, C.BOLD)} {bar} {c(str(cur_exp)+'/'+str(need_exp)+'XP', C.BBLACK)}")
    print(
        f"  📅登录 {c(str(stats.get('login_days',0))+'天', C.BCYAN)}"
        f"  🔥连胜 {c(str(stats.get('streak',0))+'局', C.BRED)}"
        f"  ⚡最高 {c(str(stats.get('best_net_wpm',0))+'净WPM', wpm_color(stats.get('best_net_wpm',0)), C.BOLD)}"
    )
    task_bar    = bar_fg(tasks_done, tasks_total, width=tasks_total,
                         full_char="●", empty_char="○",
                         full_color=C.BGREEN, empty_color=C.BBLACK)
    daily_ch_icon = c("✓已打卡", C.BGREEN) if daily.get("daily_ch_done") else c("★未打卡", C.BYELLOW)
    print(
        f"  📋今日 {c(str(daily.get('games',0))+'局', C.BCYAN)}"
        f"  任务 {task_bar} {c(str(tasks_done)+'/'+str(tasks_total), C.BYELLOW)}"
        f"  每日一挑 {daily_ch_icon}"
    )
    print(separator("─"))
    print(f"  {c('1', C.BYELLOW)} 经典模式      {c('2', C.BYELLOW)} 极速挑战")
    print(f"  {c('3', C.BYELLOW)} 词库练习      {c('4', C.BYELLOW)} 计时挑战")
    print(f"  {c('5', C.BYELLOW)} 盲打模式      {c('6', C.BYELLOW)} 渐进挑战")
    print(f"  {c('7', C.BYELLOW)} 弱键练习      {c('8', C.BYELLOW)} 每日一挑 {'✓' if daily.get('daily_ch_done') else '★'}")
    print(f"  {c('9', C.BYELLOW)} 幽灵竞速      {c('10', C.BYELLOW)} 段落挑战")
    print(separator("─"))
    print(f"  {c('s', C.BCYAN)} 数据统计   {c('k', C.BCYAN)} 技能系统   {c('a', C.BCYAN)} 成就列表")
    print(f"  {c('c', C.BCYAN)} 设置       {c('h', C.BCYAN)} 帮助说明   {c('0', C.BRED)} 退出")
    print(separator("═"))
    ach_count = len(stats.get("achievements", []))
    print(f"  成就 {c(str(ach_count)+'/'+str(len(ACHIEVEMENTS)), C.BGREEN)}"
          f"  累计字符 {c('{:,}'.format(stats.get('total_chars',0)), C.BBLACK)}")

def choose_difficulty():
    clear_screen()
    print(separator())
    print(f"  {c('1', C.BGREEN)} 简单   {c('2', C.BYELLOW)} 中等   {c('3', C.BRED)} 困难")
    print(separator())
    c_map = {"1": "easy", "2": "medium", "3": "hard"}
    while True:
        ch = input(c("选择难度（Enter=中等）: ", C.BCYAN)).strip()
        if ch in c_map: return c_map[ch]
        if ch == "":    return "medium"

def choose_wordbank():
    clear_screen()
    custom = load_custom_words()
    print(separator())
    print(f"  {c('1',C.BYELLOW)} tech       {c('2',C.BYELLOW)} code      {c('3',C.BYELLOW)} quote")
    print(f"  {c('4',C.BYELLOW)} science    {c('5',C.BYELLOW)} literature {c('6',C.BYELLOW)} random")
    print(f"  {c('7',C.BYELLOW)} chinese", end="")
    print(f"    {c('8',C.BYELLOW)} 自定义({len(custom)}条)" if custom else "")
    print(separator())
    banks = {"1":"tech","2":"code","3":"quote","4":"science",
             "5":"literature","6":"random","7":"chinese"}
    while True:
        ch = input(c("选择词库（Enter 随机）: ", C.BCYAN)).strip()
        if ch == "":    return random.choice(list(banks.values()))
        if ch in banks: return banks[ch]
        if ch == "8" and custom: return "custom"
        print(c("  无效选项，请重新输入", C.BRED))

def add_custom_word():
    clear_screen()
    print(separator())
    print(c("  添加自定义词组", C.BCYAN, C.BOLD))
    print(separator())
    word = input("输入词组（回车结束）: ").strip()
    if word:
        save_custom_word(word)
        print(c("  添加成功！", C.BGREEN))
    input(c("\n按 Enter 返回...", C.BBLACK))

def show_session_summary(stats):
    sess  = stats.get("session", {})
    games = sess.get("games", 0)
    if games < 2:
        return
    avg_wpm = int(sess.get("wpm_sum", 0) / games)
    avg_acc = int(sess.get("acc_sum", 0) / games)
    print(separator("─"))
    print(
        c(f"  本次会话：{games} 局  "
          f"平均净WPM {c(str(avg_wpm), wpm_color(avg_wpm), C.BOLD)}  "
          f"平均正确率 {c(str(avg_acc)+'%', acc_color(avg_acc))}", C.BCYAN)
    )

# ==================== 游戏模式 ====================

def play_classic():
    difficulty = choose_difficulty()
    target     = random.choice(TEXTS[difficulty])
    stats      = load_stats()
    cfg        = load_config()
    diff_label = {"easy": c("简单",C.BGREEN), "medium": c("中等",C.BYELLOW), "hard": c("困难",C.BRED)}

    clear_screen()
    print(separator())
    print(c(f"  经典模式  {diff_label[difficulty]}难度", C.BCYAN, C.BOLD))
    print(separator("─"))
    print()

    if cfg.get("use_realtime", True):
        user_input, elapsed = realtime_type(target, mode_label="经典")
    else:
        print(f" {c('目标', C.BBLACK)}: {c(target, C.BWHITE, C.BOLD)}\n")
        input(c(" 按 Enter 开始计时...", C.BBLACK))
        start      = time.time()
        user_input = input(c(" >>> ", C.BCYAN))
        elapsed    = time.time() - start

    if user_input is None:
        return

    raw_wpm     = int((len(user_input) / 5) / (elapsed / 60))
    raw_net_wpm = calculate_net_wpm(target, user_input, elapsed)
    raw_acc     = calculate_accuracy(target, user_input)
    track_key_errors(target, user_input, stats)

    exp_base   = 10 + raw_wpm // 10 + raw_acc // 10
    prev_best  = stats.get("mode_bests", {}).get("classic", {}).get("net_wpm", 0)
    ghost_beat = raw_net_wpm > prev_best and prev_best > 0

    res = _finish_game(stats, "classic", raw_wpm, raw_net_wpm, raw_acc, exp_base,
                       target, user_input, elapsed, difficulty=difficulty,
                       ghost_beat=ghost_beat)
    new_ach, daily_done, old_lv, new_lv, exp_gain, combo, wpm, net_wpm, accuracy = res

    rating, text, rating_col, icon = get_rating(net_wpm, accuracy)
    show_result(target, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_lv, new_lv, new_ach, daily_done, combo,
                mode="classic", prev_best_net=prev_best, ghost_beat=ghost_beat)

def play_sprint():
    stats      = load_stats()
    skills     = stats.get("skills", {k: 0 for k in SKILLS})
    cfg        = load_config()
    time_limit = 15 + skills.get("accuracy", 0) * 5

    clear_screen()
    print(separator())
    print(c(f"  极速挑战  {time_limit} 秒！尽可能多打！", C.BYELLOW, C.BOLD))
    print(c("  提示：只计算正确字符，错误不得分", C.BBLACK))
    print(separator())
    input(c(" 按 Enter 开始...", C.BBLACK))

    total_correct, total_typed, completed = 0, 0, 0
    start_time = time.time()

    while True:
        remaining = time_limit - (time.time() - start_time)
        if remaining <= 0:
            break
        target = random.choice(TEXTS["easy"] + TEXTS["medium"][:5])
        clear_screen()
        print(separator())
        rt = c(f"{remaining:.1f}", C.BRED, C.BOLD)
        wpm_now = int((total_correct / 5) / ((time.time() - start_time) / 60)) if total_correct > 0 else 0
        print(c("  ⚡极速挑战  剩余 ", C.BYELLOW) + rt + c("s", C.BYELLOW))
        print(
            f"  ✅{c(str(completed)+'句', C.BGREEN)}"
            f"  ⌨️{c(str(total_correct)+'字符', C.BCYAN)}"
            f"  ⚡{c(str(wpm_now)+'WPM', wpm_color(wpm_now))}"
        )
        print(separator("─"))
        print()

        if cfg.get("use_realtime", True):
            user_input, _ = realtime_type(target, mode_label="极速-Enter提交")
        else:
            print(f" {c('目标', C.BBLACK)}: {c(target, C.BWHITE, C.BOLD)}\n")
            user_input = input(c(" >>> ", C.BCYAN))

        if user_input is None:
            break
        if time.time() - start_time >= time_limit:
            break

        correct = sum(1 for a, b in zip(target, user_input) if a == b)
        total_correct += correct
        total_typed   += len(user_input)
        if user_input.strip() == target.strip():
            completed += 1

    elapsed  = time.time() - start_time
    raw_wpm  = int((total_correct / 5) / (elapsed / 60)) if elapsed > 0 else 0
    exp_base = 20 + total_correct // 10
    stats["total_chars"] = stats.get("total_chars", 0) + total_correct

    prev_best  = stats.get("mode_bests", {}).get("sprint", {}).get("net_wpm", 0)
    ghost_beat = raw_wpm > prev_best and prev_best > 0

    new_ach, daily_done, old_lv, new_lv, exp_gain, _, wpm, net_wpm, _ = _finish_game(
        stats, "sprint", raw_wpm, raw_wpm, 100, exp_base,
        chars=total_correct, completed=completed, difficulty="",
        ghost_beat=ghost_beat)

    clear_screen()
    print(separator("═"))
    print(c("  ⚡ 极速挑战结束！", C.BYELLOW, C.BOLD))
    print(separator("─"))
    print(f"  ✅{c(str(completed)+'句', C.BGREEN)}  ⌨️{c(str(total_correct)+'字符', C.BCYAN)}")
    print(f"  ⏱{c(f'{elapsed:.1f}s', C.BCYAN)}   ⚡{c(str(wpm)+'WPM', wpm_color(wpm), C.BOLD)}")
    if ghost_beat:
        print(c("  👻 击败幽灵记录！", C.BMAGENTA, C.BOLD))
    print(separator("─"))
    print(f"  {c('+'+str(exp_gain)+'XP', C.BGREEN)}  Lv.{old_lv} ➜ Lv.{new_lv}")
    if new_ach:
        print(c("\n  🏆 成就解锁！", C.BYELLOW))
        for a in new_ach:
            print(f"    {ACHIEVEMENTS[a]['icon']} {c(ACHIEVEMENTS[a]['name'], C.BMAGENTA)}")
    print(separator("═"))
    input(c("\n按 Enter 继续...", C.BBLACK))

def play_blind():
    target = random.choice(TEXTS["medium"])
    stats  = load_stats()

    clear_screen()
    print(separator())
    print(c("  盲打模式  记忆后盲打", C.BCYAN, C.BOLD))
    print(separator("─"))
    print(f"\n {c('【请记忆】', C.BYELLOW, C.BOLD)} {c(target, C.BWHITE, C.BOLD)}\n")
    input(c(" 按 Enter 开始倒计时（3 秒后隐藏）...", C.BBLACK))

    for i in range(3, 0, -1):
        clear_screen()
        print(c(f"\n  {i}...", C.BRED, C.BOLD))
        time.sleep(1)

    clear_screen()
    print(separator())
    print(c("  盲打模式  开始输入！", C.BCYAN, C.BOLD))
    print(separator("─"))
    print(f"  {c('字符数', C.BBLACK)}: {c(str(len(target)), C.BCYAN)}\n")

    start      = time.time()
    user_input = input(c(" >>> ", C.BCYAN))
    elapsed    = time.time() - start

    raw_wpm     = int((len(user_input) / 5) / (elapsed / 60)) if elapsed > 0 else 0
    raw_net_wpm = calculate_net_wpm(target, user_input, elapsed)
    raw_acc     = calculate_accuracy(target, user_input)
    track_key_errors(target, user_input, stats)

    exp_base = 15 + raw_wpm // 10 + raw_acc // 10
    res = _finish_game(stats, "blind", raw_wpm, raw_net_wpm, raw_acc, exp_base,
                       target, user_input, elapsed, difficulty="")
    new_ach, daily_done, old_lv, new_lv, exp_gain, combo, wpm, net_wpm, accuracy = res

    rating, text, rating_col, icon = get_rating(net_wpm, accuracy)
    show_result(target, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_lv, new_lv, new_ach, daily_done, combo)

def play_word_practice():
    wordbank = choose_wordbank()
    if wordbank == "custom":
        words_list = load_custom_words()
        if not words_list:
            print(c("  自定义词库为空，请先在设置中添加！", C.BRED))
            time.sleep(1.5)
            return
        words = random.choice(words_list)
    else:
        words = random.choice(WORD_BANKS[wordbank])

    stats = load_stats()
    cfg   = load_config()
    clear_screen()
    print(separator())
    print(c(f"  词库练习  [{wordbank}]", C.BCYAN, C.BOLD))
    print(separator("─"))
    print()

    if cfg.get("use_realtime", True):
        user_input, elapsed = realtime_type(words, mode_label="词库")
    else:
        print(f" {c('目标', C.BBLACK)}: {c(words, C.BWHITE, C.BOLD)}\n")
        input(c(" 按 Enter 开始...", C.BBLACK))
        start      = time.time()
        user_input = input(c(" >>> ", C.BCYAN))
        elapsed    = time.time() - start

    if user_input is None:
        return

    raw_wpm     = int((len(user_input) / 5) / (elapsed / 60))
    raw_net_wpm = calculate_net_wpm(words, user_input, elapsed)
    raw_acc     = calculate_accuracy(words, user_input)
    track_key_errors(words, user_input, stats)

    exp_base = 10 + raw_wpm // 10 + raw_acc // 10
    res = _finish_game(stats, "word", raw_wpm, raw_net_wpm, raw_acc, exp_base,
                       words, user_input, elapsed, difficulty="")
    new_ach, daily_done, old_lv, new_lv, exp_gain, combo, wpm, net_wpm, accuracy = res

    rating, text, rating_col, icon = get_rating(net_wpm, accuracy)
    show_result(words, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_lv, new_lv, new_ach, daily_done, combo)

def play_timed():
    clear_screen()
    print(separator())
    print(c("  计时挑战  选择时长", C.BCYAN, C.BOLD))
    print(separator("─"))
    stats  = load_stats()
    skills = stats.get("skills", {k: 0 for k in SKILLS})
    cfg    = load_config()
    bonus  = skills.get("stamina", 0) * 10
    print(f"  {c('1',C.BYELLOW)} 30 秒 (+{bonus}s)"
          f"   {c('2',C.BYELLOW)} 60 秒 (+{bonus}s)"
          f"   {c('3',C.BYELLOW)} 120 秒 (+{bonus}s)")
    print(separator())
    ch = input(c("选择（Enter=60s）: ", C.BCYAN)).strip()
    base_time  = {"1": 30, "2": 60, "3": 120}.get(ch, 60)
    time_limit = base_time + bonus

    input(c(f"\n  {time_limit} 秒挑战，按 Enter 开始...", C.BBLACK))

    total_correct, total_typed, completed = 0, 0, 0
    start_time = time.time()

    while True:
        remaining = time_limit - (time.time() - start_time)
        if remaining <= 0:
            break
        target = random.choice(TEXTS["medium"])
        clear_screen()
        print(separator())
        rt      = c(f"{remaining:.1f}", C.BRED, C.BOLD)
        wpm_now = int((total_correct / 5) / ((time.time() - start_time) / 60)) if total_correct > 0 else 0
        print(c("  ⏱ 计时挑战  剩余 ", C.BCYAN) + rt + c("s", C.BCYAN))
        print(f"  ✅{c(str(completed)+'句', C.BGREEN)}"
              f"  ⌨️{c(str(total_correct)+'字符', C.BCYAN)}"
              f"  ⚡{c(str(wpm_now)+'WPM', wpm_color(wpm_now))}")
        print(separator("─"))
        print()

        if cfg.get("use_realtime", True):
            user_input, _ = realtime_type(target, mode_label="计时")
        else:
            print(f" {c('目标', C.BBLACK)}: {c(target, C.BWHITE, C.BOLD)}\n")
            user_input = input(c(" >>> ", C.BCYAN))

        if user_input is None:
            break
        if time.time() - start_time >= time_limit:
            break

        correct = sum(1 for a, b in zip(target, user_input) if a == b)
        total_correct += correct
        total_typed   += len(user_input)
        if user_input.strip() == target.strip():
            completed += 1

    elapsed  = time.time() - start_time
    raw_wpm  = int((total_correct / 5) / (elapsed / 60)) if elapsed > 0 else 0
    exp_base = 15 + completed * 5 + raw_wpm // 10
    stats["total_chars"] = stats.get("total_chars", 0) + total_correct

    new_ach, daily_done, old_lv, new_lv, exp_gain, _, wpm, _, _ = _finish_game(
        stats, "timed", raw_wpm, raw_wpm, 100, exp_base,
        chars=total_correct, completed=completed, difficulty="")

    clear_screen()
    print(separator("═"))
    print(c("  ⏱ 计时挑战结束！", C.BCYAN, C.BOLD))
    print(separator("─"))
    print(f"  ✅{c(str(completed)+'句', C.BGREEN)}  ⌨️{c(str(total_correct)+'字符', C.BCYAN)}")
    print(f"  ⏱{c(f'{elapsed:.1f}s', C.BCYAN)}   ⚡{c(str(wpm)+'WPM', wpm_color(wpm), C.BOLD)}")
    print(separator("─"))
    print(f"  {c('+'+str(exp_gain)+'XP', C.BGREEN)}  Lv.{old_lv} ➜ Lv.{new_lv}")
    if new_ach:
        print(c("\n  🏆 成就解锁！", C.BYELLOW))
        for a in new_ach:
            print(f"    {ACHIEVEMENTS[a]['icon']} {c(ACHIEVEMENTS[a]['name'], C.BMAGENTA)}")
    print(separator("═"))
    input(c("\n按 Enter 继续...", C.BBLACK))

def play_gauntlet():
    clear_screen()
    print(separator())
    print(c("  ⚔️  渐进挑战模式", C.BMAGENTA, C.BOLD))
    print(separator("─"))
    print("  共 9 关，难度逐步提升，限时递减。全通方算胜利。")
    print(separator())
    input(c(" 按 Enter 开始...", C.BBLACK))

    stages = (
        [("easy",   35)] * 3 +
        [("medium", 28)] * 3 +
        [("hard",   22)] * 3
    )
    stats = load_stats()
    cfg   = load_config()
    total_wpm, total_acc, alive = [], [], True

    for no, (diff, limit) in enumerate(stages, 1):
        target   = random.choice(TEXTS[diff])
        diff_c   = {"easy": C.BGREEN, "medium": C.BYELLOW, "hard": C.BRED}[diff]
        diff_lbl = {"easy":"简单","medium":"中等","hard":"困难"}[diff]

        clear_screen()
        print(separator())
        print(c(f"  ⚔️  第 {no}/9 关  {c(diff_lbl, diff_c)}  限时 {limit} 秒", C.BMAGENTA, C.BOLD))
        print(separator("─"))
        print()
        input(c(f" 按 Enter 开始第 {no} 关...", C.BBLACK))

        if cfg.get("use_realtime", True):
            user_input, elapsed = realtime_type(target, mode_label=f"渐进第{no}关")
        else:
            print(f" {c('目标', C.BBLACK)}: {c(target, C.BWHITE, C.BOLD)}\n")
            start      = time.time()
            user_input = input(c(" >>> ", C.BCYAN))
            elapsed    = time.time() - start

        if user_input is None:
            print(c("  已放弃当关！", C.BRED)); alive = False
            time.sleep(1); break

        if elapsed > limit:
            print(c(f"  ❌ 超时！{elapsed:.1f}s > {limit}s", C.BRED))
            alive = False; time.sleep(1.5); break

        net_wpm = calculate_net_wpm(target, user_input, elapsed)
        acc     = calculate_accuracy(target, user_input)
        track_key_errors(target, user_input, stats)
        total_wpm.append(net_wpm)
        total_acc.append(acc)
        print(c(f"  ✓ 第 {no} 关通过！  ⚡{net_wpm}净WPM  🎯{acc}%", C.BGREEN))
        time.sleep(0.8)

    avg_wpm  = int(sum(total_wpm) / len(total_wpm)) if total_wpm else 0
    avg_acc  = int(sum(total_acc) / len(total_acc)) if total_acc else 0
    exp_base = (40 + avg_wpm // 5) if alive else (10 + avg_wpm // 10)
    mode     = "gauntlet" if alive else "classic"

    new_ach, daily_done, old_lv, new_lv, exp_gain, _, _, _, _ = _finish_game(
        stats, mode, avg_wpm, avg_wpm, avg_acc, exp_base, difficulty="")

    clear_screen()
    print(separator())
    print(c("  ⚔️  渐进挑战全通！🎉", C.BMAGENTA, C.BOLD) if alive
          else c("  ⚔️  挑战结束", C.BRED, C.BOLD))
    print(separator("─"))
    print(f"  通关数: {c(str(len(total_wpm))+'/9', C.BCYAN)}")
    print(f"  平均净WPM: {c(str(avg_wpm), wpm_color(avg_wpm), C.BOLD)}"
          f"  平均正确率: {c(str(avg_acc)+'%', acc_color(avg_acc))}")
    print(separator("─"))
    print(f"  {c('+'+str(exp_gain)+'XP', C.BGREEN)}  Lv.{old_lv} ➜ Lv.{new_lv}")
    if new_ach:
        print(c("\n  🏆 成就解锁！", C.BYELLOW))
        for a in new_ach:
            print(f"    {ACHIEVEMENTS[a]['icon']} {c(ACHIEVEMENTS[a]['name'], C.BMAGENTA)}")
    print(separator())
    input(c("\n按 Enter 继续...", C.BBLACK))

def play_weak_key():
    stats       = load_stats()
    char_errors = stats.get("char_errors", {})

    if not char_errors:
        clear_screen()
        print(separator())
        print(c("  💪 弱键练习", C.BCYAN, C.BOLD))
        print(separator("─"))
        print("  暂无错误记录，请先完成几局经典或词库练习！")
        print(separator())
        input(c("\n按 Enter 返回...", C.BBLACK))
        return

    top_chars = sorted(char_errors.items(),
                       key=lambda x: x[1].get("count", 0), reverse=True)[:5]
    weak_set  = [ch for ch, _ in top_chars]

    all_words = []
    for bank in WORD_BANKS.values():
        for sentence in bank:
            for word in sentence.split():
                if any(ch in word for ch in weak_set):
                    all_words.append(word)
    all_words = list(set(all_words))
    random.shuffle(all_words)
    target = " ".join(all_words[:15]) if len(all_words) >= 15 else " ".join(all_words)
    if not target:
        target = " ".join(ch * 6 for ch in weak_set)

    cfg = load_config()
    clear_screen()
    print(separator())
    print(c("  💪 弱键专项练习", C.BCYAN, C.BOLD))
    print(separator("─"))
    print("  高频错误键位: " + "  ".join(
        c(f"'{ch}'({data['count']}次)", C.BRED) for ch, data in top_chars))
    print(separator("─"))
    print()

    if cfg.get("use_realtime", True):
        user_input, elapsed = realtime_type(target, mode_label="弱键")
    else:
        print(f" {c('目标', C.BBLACK)}: {c(target, C.BWHITE, C.BOLD)}\n")
        input(c(" 按 Enter 开始...", C.BBLACK))
        start      = time.time()
        user_input = input(c(" >>> ", C.BCYAN))
        elapsed    = time.time() - start

    if user_input is None:
        return

    raw_wpm     = int((len(user_input) / 5) / (elapsed / 60))
    raw_net_wpm = calculate_net_wpm(target, user_input, elapsed)
    raw_acc     = calculate_accuracy(target, user_input)
    track_key_errors(target, user_input, stats)

    exp_base = 12 + raw_wpm // 10 + raw_acc // 10
    res = _finish_game(stats, "weak", raw_wpm, raw_net_wpm, raw_acc, exp_base,
                       target, user_input, elapsed, difficulty="")
    new_ach, daily_done, old_lv, new_lv, exp_gain, combo, wpm, net_wpm, accuracy = res

    rating, text, rating_col, icon = get_rating(net_wpm, accuracy)
    show_result(target, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_lv, new_lv, new_ach, daily_done, combo)

# ==================== 新模式：每日一挑 ====================

def play_daily_challenge():
    stats = load_stats()
    cfg   = load_config()
    today = date.today().isoformat()

    check_daily_reset(stats)
    already_done = stats.get("daily", {}).get("daily_ch_done", False)

    seed_rng = random.Random(today)
    target   = seed_rng.choice(DAILY_POOL)

    clear_screen()
    print(separator("═"))
    print(c("  📅  每日一挑", C.BYELLOW, C.BOLD))
    print(c(f"  {today}  每天一题，全球同题！", C.BBLACK))
    if already_done:
        print(c("  ✅ 今日已完成，可再刷练习，奖励已领取。", C.BGREEN))
    print(separator("─"))
    print()

    if cfg.get("use_realtime", True):
        user_input, elapsed = realtime_type(target, mode_label="每日一挑")
    else:
        print(f" {c('目标', C.BBLACK)}: {c(target, C.BWHITE, C.BOLD)}\n")
        input(c(" 按 Enter 开始...", C.BBLACK))
        start      = time.time()
        user_input = input(c(" >>> ", C.BCYAN))
        elapsed    = time.time() - start

    if user_input is None:
        return

    raw_wpm     = int((len(user_input) / 5) / (elapsed / 60))
    raw_net_wpm = calculate_net_wpm(target, user_input, elapsed)
    raw_acc     = calculate_accuracy(target, user_input)
    track_key_errors(target, user_input, stats)

    is_dc    = not already_done
    exp_base = 20 + raw_wpm // 8 + raw_acc // 8
    if is_dc:
        exp_base = int(exp_base * 1.5)

    res = _finish_game(stats, "daily", raw_wpm, raw_net_wpm, raw_acc, exp_base,
                       target, user_input, elapsed, difficulty="", is_daily_ch=is_dc)
    new_ach, daily_done, old_lv, new_lv, exp_gain, combo, wpm, net_wpm, accuracy = res

    rating, text, rating_col, icon = get_rating(net_wpm, accuracy)
    show_result(target, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_lv, new_lv, new_ach, daily_done, combo, mode="daily")

# ==================== 新模式：幽灵竞速 ====================

def play_ghost_race():
    stats      = load_stats()
    mode_bests = stats.get("mode_bests", {})
    cfg        = load_config()

    clear_screen()
    print(separator())
    print(c("  👻 幽灵竞速", C.BMAGENTA, C.BOLD))
    print(c("  对抗你的历史最佳记录，超越自己！", C.BBLACK))
    print(separator("─"))

    mode_map = {"classic":"经典","timed":"计时","sprint":"极速",
                "blind":"盲打","word":"词库","gauntlet":"渐进",
                "weak":"弱键","daily":"每日一挑","paragraph":"段落"}
    has_record = False
    for mk, mv in mode_map.items():
        best = mode_bests.get(mk, {})
        if best.get("net_wpm", 0) > 0:
            print(f"  {c(mv, C.BCYAN)}: "
                  f"{c(str(best['net_wpm'])+'净WPM', wpm_color(best['net_wpm']), C.BOLD)}"
                  f"  正确率 {c(str(best['accuracy'])+'%', acc_color(best['accuracy']))}")
            has_record = True

    if not has_record:
        print(c("  暂无历史记录，请先完成几局游戏！", C.BRED))
        print(separator())
        input(c("\n按 Enter 返回...", C.BBLACK))
        return

    print(separator("─"))
    difficulty = choose_difficulty()
    target     = random.choice(TEXTS[difficulty])
    ghost_wpm  = max(
        (mode_bests.get(m, {}).get("net_wpm", 0) for m in ["classic","word","daily","paragraph"]),
        default=0
    )

    clear_screen()
    print(separator())
    print(c(f"  👻 幽灵竞速  对抗 {ghost_wpm} 净WPM", C.BMAGENTA, C.BOLD))
    print(separator("─"))
    print()

    if cfg.get("use_realtime", True):
        user_input, elapsed = realtime_type(target, mode_label="幽灵竞速", ghost_wpm=ghost_wpm)
    else:
        print(f" {c('目标', C.BBLACK)}: {c(target, C.BWHITE, C.BOLD)}\n")
        print(c(f" 👻 幽灵最佳: {ghost_wpm} WPM", C.BMAGENTA))
        input(c(" 按 Enter 开始...", C.BBLACK))
        start      = time.time()
        user_input = input(c(" >>> ", C.BCYAN))
        elapsed    = time.time() - start

    if user_input is None:
        return

    raw_wpm     = int((len(user_input) / 5) / (elapsed / 60))
    raw_net_wpm = calculate_net_wpm(target, user_input, elapsed)
    raw_acc     = calculate_accuracy(target, user_input)
    track_key_errors(target, user_input, stats)

    ghost_beat = raw_net_wpm > ghost_wpm
    exp_base   = 15 + raw_wpm // 10 + raw_acc // 10

    res = _finish_game(stats, "classic", raw_wpm, raw_net_wpm, raw_acc, exp_base,
                       target, user_input, elapsed, difficulty=difficulty,
                       ghost_beat=ghost_beat)
    new_ach, daily_done, old_lv, new_lv, exp_gain, combo, wpm, net_wpm, accuracy = res

    rating, text, rating_col, icon = get_rating(net_wpm, accuracy)
    show_result(target, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_lv, new_lv, new_ach, daily_done, combo,
                mode="classic", prev_best_net=ghost_wpm, ghost_beat=ghost_beat)

# ==================== 新模式：段落挑战 ====================

def play_paragraph():
    stats  = load_stats()
    cfg    = load_config()
    target = random.choice(TEXTS["paragraph"])

    clear_screen()
    print(separator())
    print(c("  📖 段落挑战  完整段落输入", C.BCYAN, C.BOLD))
    print(c("  更长文本，考验持久正确率与耐力", C.BBLACK))
    print(separator("─"))
    print()

    if cfg.get("use_realtime", True):
        user_input, elapsed = realtime_type(target, mode_label="段落")
    else:
        print(f" {c('目标', C.BBLACK)}: {c(target, C.BWHITE, C.BOLD)}\n")
        input(c(" 按 Enter 开始...", C.BBLACK))
        start      = time.time()
        user_input = input(c(" >>> ", C.BCYAN))
        elapsed    = time.time() - start

    if user_input is None:
        return

    raw_wpm     = int((len(user_input) / 5) / (elapsed / 60))
    raw_net_wpm = calculate_net_wpm(target, user_input, elapsed)
    raw_acc     = calculate_accuracy(target, user_input)
    track_key_errors(target, user_input, stats)

    exp_base = 25 + raw_wpm // 8 + raw_acc // 8
    res = _finish_game(stats, "paragraph", raw_wpm, raw_net_wpm, raw_acc, exp_base,
                       target, user_input, elapsed, difficulty="hard", is_para=True)
    new_ach, daily_done, old_lv, new_lv, exp_gain, combo, wpm, net_wpm, accuracy = res

    rating, text, rating_col, icon = get_rating(net_wpm, accuracy)
    show_result(target, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_lv, new_lv, new_ach, daily_done, combo)

# ==================== 统计与系统 ====================

def show_stats():
    stats = load_stats()
    level, cur_exp, need_exp = get_level(stats.get("exp", 0))

    clear_screen()
    print(separator("═"))
    print(c("  📊 数据统计", C.BCYAN, C.BOLD))
    print(separator("─"))
    print(f"  等级       {c('Lv.'+str(level), C.BYELLOW, C.BOLD)}  ({cur_exp}/{need_exp} XP)")
    print(f"  总场次     {c(str(stats.get('total_games',0))+'局', C.BCYAN)}")
    print(f"  最高净WPM  {c(str(stats.get('best_net_wpm',0)), wpm_color(stats.get('best_net_wpm',0)), C.BOLD)}"
          f"  {c('(毛'+str(stats.get('best_wpm',0))+')', C.BBLACK)}")
    print(f"  最高正确率 {c(str(stats.get('best_accuracy',0))+'%', acc_color(stats.get('best_accuracy',0)))}")
    print(f"  当前连胜   {c(str(stats.get('streak',0))+'局', C.BRED)}")
    print(f"  历史最大连击 {c('x'+str(stats.get('max_combo',0)), C.BMAGENTA)}")
    print(f"  累计字符   {c('{:,}'.format(stats.get('total_chars',0)), C.BCYAN)}")
    print(f"  登录天数   {c(str(stats.get('login_days',0))+'天', C.BBLUE)}")
    print(f"  每日一挑连续 {c(str(stats.get('daily_ch_streak',0))+'天', C.BYELLOW)}")
    print(separator("─"))

    mode_map   = {"classic":"经典","timed":"计时","sprint":"极速",
                  "blind":"盲打","word":"词库","gauntlet":"渐进",
                  "weak":"弱键","daily":"每日一挑","paragraph":"段落"}
    mode_bests = stats.get("mode_bests", {})
    if mode_bests:
        print(c("  🏆 各模式最佳（净WPM）", C.BYELLOW))
        for mk, mv in mode_map.items():
            best = mode_bests.get(mk, {})
            if best.get("net_wpm", 0) > 0:
                wc = wpm_color(best['net_wpm'])
                print(f"    {c(mv, C.BCYAN):8}  "
                      f"{c(str(best['net_wpm'])+'WPM', wc, C.BOLD):12}"
                      f"  {c(str(best['accuracy'])+'%', acc_color(best['accuracy']))}")
        print(separator("─"))

    print(c("  📈 WPM 历史趋势（青=毛 / 蓝=净）", C.BYELLOW))
    print(ascii_wpm_chart(stats.get("wpm_history", []), stats.get("net_wpm_history", [])))
    print(separator("─"))

    char_errors = stats.get("char_errors", {})
    if char_errors:
        print(c("  🔴 Top5 高频错误键位", C.BRED))
        top5    = sorted(char_errors.items(), key=lambda x: x[1].get("count",0), reverse=True)[:5]
        max_cnt = max(d.get("count",0) for _,d in top5) or 1
        for ch, data in top5:
            cnt = data.get("count",0)
            b   = bar_fg(cnt, max_cnt, width=12, full_color=C.BRED, empty_color=C.BBLACK)
            print(f"    {c(repr(ch), C.BWHITE)} {b} {c(str(cnt)+'次', C.BRED)}")

    print(separator("─"))
    modes = Counter(g.get("mode","?") for g in stats.get("games",[]))
    if modes:
        print(c("  📋 模式分布", C.BYELLOW))
        for m, cnt in modes.most_common():
            print(f"    {c(mode_map.get(m,m), C.BCYAN):10} {c(str(cnt)+'局', C.BBLACK)}")

    print(separator("─"))
    check_daily_reset(stats)
    daily = stats.get("daily", {})
    print(c("  🗓️  今日任务", C.BYELLOW))
    for task in DAILY_TASKS:
        tid  = task["id"]
        done = daily.get("tasks", {}).get(tid, False)
        mk   = c("✓", C.BGREEN) if done else c("✗", C.BRED)
        if task["type"] == "games":
            cur = daily.get("games", 0)
            b   = bar_fg(cur, task["target"], width=6, full_color=C.BGREEN, empty_color=C.BBLACK)
            print(f"    {mk} {task['desc']} {b} {cur}/{task['target']}"
                  f"  {c('+'+str(task['reward'])+'XP', C.BGREEN)}")
        else:
            print(f"    {mk} {task['desc']}"
                  f"  {c('+'+str(task['reward'])+'XP', C.BGREEN)}")

    print(separator("─"))
    print(c("  📜 最近 10 局", C.BYELLOW))
    for i, g in enumerate(reversed(stats.get("games",[])[-10:]), 1):
        mn      = mode_map.get(g.get("mode",""), "?")
        nwpm    = g.get("net_wpm", g.get("wpm", "-"))
        acc     = g.get("accuracy", "-")
        combo   = g.get("combo", 0)
        elapsed = g.get("elapsed", 0)
        wc      = wpm_color(nwpm) if isinstance(nwpm, int) else C.BBLACK
        ac      = acc_color(acc) if isinstance(acc, int) else C.BBLACK
        print(f"  {c(str(i), C.BBLACK)}.  {g.get('date','')[:16]}"
              f"  {c(mn, C.BCYAN):8}"
              f"  {c(str(nwpm)+'净WPM', wc):10}"
              f"  {c(str(acc)+'%', ac):6}"
              f"  {c('x'+str(combo), C.BMAGENTA):4}"
              f"  {c(str(elapsed)+'s', C.BBLACK)}")

    print(separator("═"))
    show_session_summary(stats)
    input(c("\n按 Enter 返回...", C.BBLACK))

def show_achievements():
    stats    = load_stats()
    unlocked = stats.get("achievements", [])

    clear_screen()
    print(separator("═"))
    print(c("  🏆 成就列表", C.BYELLOW, C.BOLD))
    print(separator("─"))

    categories = {}
    for key, ach in ACHIEVEMENTS.items():
        cat = ach.get("category", "其他")
        categories.setdefault(cat, []).append((key, ach))

    for cat, items in categories.items():
        done = sum(1 for k, _ in items if k in unlocked)
        bar  = bar_fg(done, len(items), width=max(len(items),1),
                      full_char="●", empty_char="○",
                      full_color=C.BYELLOW, empty_color=C.BBLACK)
        print(c(f"  [{cat}]", C.BCYAN) + f"  {bar}  {done}/{len(items)}")
        for key, ach in items:
            if key in unlocked:
                print(f"    {c('✓', C.BGREEN)} {ach['icon']} "
                      f"{c(ach['name'], C.BWHITE, C.BOLD)}: {c(ach['desc'], C.BBLACK)}")
            else:
                print(f"    {c('○', C.BBLACK)} 🔒 "
                      f"{c(ach['name'], C.BBLACK)}: {ach['desc']}")
        print()

    print(separator("─"))
    print(f"  已解锁 {c(str(len(unlocked)), C.BGREEN)} / {len(ACHIEVEMENTS)}")
    print(separator("═"))
    input(c("\n按 Enter 返回...", C.BBLACK))

def show_skills():
    stats       = load_stats()
    skills_data = stats.get("skills", {k: 0 for k in SKILLS})

    while True:
        level, cur_exp, need_exp = get_level(stats.get("exp", 0))
        clear_screen()
        print(separator("═"))
        print(c("  ⚡ 技能系统", C.BMAGENTA, C.BOLD))
        print(separator("─"))
        print(f"  {c('Lv.'+str(level), C.BYELLOW)}  经验: {c(str(cur_exp)+'/'+str(need_exp), C.BCYAN)}")
        print(separator("─"))

        for i, (key, skill) in enumerate(SKILLS.items(), 1):
            cur   = skills_data.get(key, 0)
            max_l = skill["max"]
            cost  = skill["cost"]
            b     = bar_fg(cur, max_l, width=max_l * 3,
                           full_char="▰", empty_char="▱",
                           full_color=C.BMAGENTA, empty_color=C.BBLACK)
            print(f"  {c(str(i), C.BYELLOW)}. {skill['icon']} {c(skill['name'], C.BWHITE, C.BOLD)}"
                  f"  {b}  {c(str(cur)+'/'+str(max_l), C.BYELLOW)}")
            print(f"     {c(skill['desc'], C.BBLACK)}")
            if cur < max_l:
                can = (c(f"✓ 升级 (-{cost}XP)", C.BGREEN)
                       if cur_exp >= cost else c(f"✗ 需要 {cost}XP（不足）", C.BRED))
                print(f"     {can}")
            else:
                print(f"     {c('⭐ 满级', C.BYELLOW)}")
            print()

        print(separator("─"))
        print(c("  输入编号升级技能   0 返回", C.BBLACK))
        print(separator("═"))

        choice = input(c("选择: ", C.BCYAN)).strip()
        if choice == "0":
            break
        keys = list(SKILLS.keys())
        if choice.isdigit() and 1 <= int(choice) <= len(keys):
            key   = keys[int(choice) - 1]
            skill = SKILLS[key]
            cur   = skills_data.get(key, 0)
            if cur >= skill["max"]:
                print(c("  已满级！", C.BRED))
            elif cur_exp >= skill["cost"]:
                skills_data[key] = cur + 1
                stats["skills"]  = skills_data
                stats["exp"]    -= skill["cost"]
                save_stats(stats)
                _, cur_exp, _ = get_level(stats["exp"])
                print(c(f"  ✓ {skill['name']} 升至 Lv.{cur+1}！", C.BGREEN))
            else:
                print(c(f"  经验不足（需 {skill['cost']}，当前 {cur_exp}）", C.BRED))
            time.sleep(1)

def show_settings():
    config = load_config()
    while True:
        clear_screen()
        print(separator("═"))
        print(c("  ⚙️  设置", C.BCYAN, C.BOLD))
        print(separator("─"))
        print(f"  {c('1',C.BYELLOW)} 实时打字模式:  "
              f"{c('开（推荐）', C.BGREEN) if config.get('use_realtime', True) else c('关（传统输入）', C.BRED)}")
        print(f"  {c('2',C.BYELLOW)} 游戏提示:      "
              f"{c('开', C.BGREEN) if config.get('show_tips') else c('关', C.BRED)}")
        print(f"  {c('3',C.BYELLOW)} 默认难度:       {c(config.get('difficulty','medium'), C.BYELLOW)}")
        print(f"  {c('4',C.BYELLOW)} 添加自定义词组")
        print(f"  {c('5',C.BYELLOW)} 查看自定义词库")
        print(f"  {c('6',C.BYELLOW)} 重置本次会话统计")
        print(f"  {c('0',C.BRED)} 返回")
        print(separator("═"))

        ch = input(c("选择: ", C.BCYAN)).strip()
        if ch == "0":
            break
        elif ch == "1":
            config["use_realtime"] = not config.get("use_realtime", True)
            save_config(config)
        elif ch == "2":
            config["show_tips"] = not config.get("show_tips", True)
            save_config(config)
        elif ch == "3":
            d = input(c("1.简单 2.中等 3.困难: ", C.BCYAN)).strip()
            config["difficulty"] = {"1":"easy","2":"medium","3":"hard"}.get(d, "medium")
            save_config(config)
        elif ch == "4":
            add_custom_word()
        elif ch == "5":
            words = load_custom_words()
            clear_screen()
            print(separator())
            if words:
                for i, w in enumerate(words, 1):
                    print(f"  {c(str(i), C.BBLACK)}. {w}")
            else:
                print(c("  (空)", C.BBLACK))
            print(separator())
            input(c("\n按 Enter 返回...", C.BBLACK))
        elif ch == "6":
            sts = load_stats()
            sts["session"] = {"games": 0, "wpm_sum": 0, "acc_sum": 0, "start": ""}
            save_stats(sts)
            print(c("  会话统计已重置", C.BGREEN))
            time.sleep(1)

def show_help():
    clear_screen()
    print(separator("═"))
    print(c("  📖 游戏说明  v6.0", C.BCYAN, C.BOLD))
    print(separator("─"))
    for mode, desc in [
        ("经典模式",   "输入目标句子，实时高亮反馈，测速与测准"),
        ("极速挑战",   "时限内尽量多打，只计正确字符"),
        ("词库练习",   "tech/code/quote/science/文学/随机/中文/自定义"),
        ("计时挑战",   "自选 30/60/120 秒，完成尽量多"),
        ("盲打模式",   "记忆后隐藏，凭记忆完成（使用传统输入）"),
        ("渐进挑战",   "9 关由易到难，限时递减，全通胜利"),
        ("弱键练习",   "自动分析错误，生成针对性训练"),
        ("每日一挑",   "每天同一题，首次完成奖励 x1.5，连续打卡有成就"),
        ("幽灵竞速",   "对抗你的历史最佳净 WPM，击败自己获 1.5x 经验"),
        ("段落挑战",   "更长段落文本，考验持久耐力，基础经验更高"),
    ]:
        print(f"  {c('【'+mode+'】', C.BYELLOW, C.BOLD)} {desc}")
    print(separator("─"))
    for sys_name, desc in [
        ("净 WPM",    "正确字符/5 - 错误字符/5，比毛 WPM 更真实公正"),
        ("实时反馈",  "绿=正确，红=错误，暗=未输入，青底=当前光标"),
        ("技能系统",  "消耗经验升级，增强游戏各方面属性"),
        ("连击系统",  "连续正确词组获得额外经验，每 5 连击 +5XP"),
        ("每日任务",  "每天刷新，完成 9 项任务，每日一挑额外 +100XP"),
        ("幽灵记录",  "各模式历史最佳净 WPM，击败可获 1.5x 经验"),
        ("会话统计",  "退出时显示本次游玩局数、平均成绩"),
    ]:
        print(f"  {c('【'+sys_name+'】', C.BCYAN)} {desc}")
    print(separator("═"))
    input(c("\n按 Enter 返回...", C.BBLACK))

# ==================== 主程序 ====================

def main():
    enable_ansi()
    funcs = {
        "1": play_classic,       "2": play_sprint,
        "3": play_word_practice, "4": play_timed,
        "5": play_blind,         "6": play_gauntlet,
        "7": play_weak_key,      "8": play_daily_challenge,
        "9": play_ghost_race,    "10": play_paragraph,
        "s": show_stats,         "k": show_skills,
        "a": show_achievements,  "c": show_settings,
        "h": show_help,
    }
    while True:
        clear_screen()
        stats = load_stats()
        show_menu(stats)
        choice = input(c("\n请选择: ", C.BCYAN)).strip().lower()
        if choice == "0":
            clear_screen()
            show_session_summary(load_stats())
            print(c("\n  感谢使用 MOTIP v6.0！再见！\n", C.BCYAN, C.BOLD))
            break
        elif choice in funcs:
            funcs[choice]()

if __name__ == "__main__":
    main()
