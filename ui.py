"""
UI模块 - 颜色系统、进度条、可视化组件、暗黑主题、动画效果
"""

import os
import sys
import time
import random
import re

# ==================== 显示宽度计算 ====================

def _display_width(s):
    """计算字符串显示宽度（中文=2，英文=1，ANSI转义码=0）"""
    # 先移除ANSI转义码
    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    clean = ansi_escape.sub('', str(s))
    width = 0
    for ch in clean:
        if '\u4e00' <= ch <= '\u9fff' or '\u3000' <= ch <= '\u303f':
            width += 2
        else:
            width += 1
    return width

def _pad_to_width(content, target_width):
    """将内容填充到指定显示宽度"""
    current = _display_width(content)
    padding = target_width - current
    return content + " " * max(0, padding)

# ==================== 颜色系统 ====================

class C:
    """ANSI 颜色常量，Windows 10+ 原生支持"""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    ITALIC  = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK   = "\033[5m"

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
    BG_BBLACK  = "\033[100m"


# ==================== 暗黑游戏风格主题 ====================

class DarkTheme:
    """暗黑游戏风格配色方案"""

    # 重置
    RESET        = "\033[0m"

    # 背景色
    BG_DARK      = "\033[40m"       # 深黑背景
    BG_DARKER    = "\033[100m"      # 灰黑背景
    BG_PANEL     = "\033[48;5;235m" # 面板背景

    # 核心颜色
    BLOOD_RED    = "\033[91m"       # 血红 - 伤害/危险
    SOUL_BLUE    = "\033[94m"       # 灵魂蓝 - 魔法/技能
    GOLD_YELLOW  = "\033[93m"       # 金黄 - 奖励/成就
    POISON_GREEN = "\033[92m"       # 毒绿 - 治疗/生命
    FIRE_ORANGE  = "\033[38;5;208m" # 火焰橙 - Boss/攻击
    SHADOW_PURPLE= "\033[95m"       # 暗紫 - 神秘/稀有
    ICE_CYAN     = "\033[96m"       # 冰霜青 - 冰冻效果
    HOLY_WHITE   = "\033[97m"       # 神圣白 - 高亮/圣光

    # 状态颜色
    HP_HIGH      = "\033[92m"       # HP高 (>60%)
    HP_MID       = "\033[93m"       # HP中 (30-60%)
    HP_LOW       = "\033[91m"       # HP低 (<30%)

    # 稀有度颜色
    COMMON       = "\033[90m"       # 普通 - 灰色
    UNCOMMON     = "\033[92m"       # 优秀 - 绿色
    RARE         = "\033[94m"       # 稀有 - 蓝色
    EPIC         = "\033[95m"       # 史诗 - 紫色
    LEGENDARY    = "\033[93m"       # 传说 - 金色
    MYTHIC       = "\033[38;5;201m" # 神话 - 粉紫色

    # 模块分区颜色（用于菜单分类）
    CATEGORY_BASIC    = "\033[38;5;46m"   # 基础练习 - 绿
    CATEGORY_SPEED    = "\033[38;5;226m"  # 速度挑战 - 黄
    CATEGORY_ADVANCED = "\033[38;5;93m"   # 进阶模式 - 紫
    CATEGORY_SPECIAL  = "\033[38;5;196m"  # 特殊模式 - 红
    CATEGORY_SYSTEM   = "\033[38;5;81m"   # 系统功能 - 蓝

    # 评价等级颜色
    RANK_D      = "\033[38;5;242m"  # D级 - 灰
    RANK_C      = "\033[38;5;214m"  # C级 - 橙
    RANK_B      = "\033[38;5;81m"   # B级 - 蓝
    RANK_A      = "\033[38;5;46m"   # A级 - 绿
    RANK_S      = "\033[38;5;226m"  # S级 - 金
    RANK_SS     = "\033[38;5;93m"   # SS级 - 紫
    RANK_SSS    = "\033[38;5;201m"  # SSS级 - 粉紫

    # 边框字符
    CORNER_TL = "╔"
    CORNER_TR = "╗"
    CORNER_BL = "╚"
    CORNER_BR = "╝"
    H_LINE    = "═"
    V_LINE    = "║"
    T_DOWN    = "╦"
    T_UP      = "╩"
    T_LEFT    = "╣"
    T_RIGHT   = "╠"
    CROSS     = "╬"

    # 简易边框
    SIMPLE_CORNER_TL = "┌"
    SIMPLE_CORNER_TR = "┐"
    SIMPLE_CORNER_BL = "└"
    SIMPLE_CORNER_BR = "┘"
    SIMPLE_H         = "─"
    SIMPLE_V         = "│"


# ==================== 基础工具函数 ====================

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
    """给文本添加颜色样式"""
    return "".join(styles) + str(text) + C.RESET


def bar_fg(cur, max_val, width=20, full_char="#", empty_char="-",
           full_color=C.BGREEN, empty_color=C.BBLACK):
    """生成进度条"""
    if max_val <= 0 or cur < 0:
        filled = 0
    else:
        filled = int(cur / max_val * width)
    filled = min(filled, width)
    return (full_color + full_char * filled +
            empty_color + empty_char * (width - filled) + C.RESET)


def hp_bar(cur, max_val, width=20):
    """HP血条（带颜色变化）"""
    if max_val <= 0:
        ratio = 0
    else:
        ratio = cur / max_val

    filled = int(ratio * width)
    filled = min(filled, width)

    if ratio > 0.6:
        color = DarkTheme.HP_HIGH
    elif ratio > 0.3:
        color = DarkTheme.HP_MID
    else:
        color = DarkTheme.HP_LOW

    bar = color + "█" * filled + C.BBLACK + "░" * (width - filled) + C.RESET
    return bar, f"{cur}/{max_val}"


def boss_hp_bar(cur, max_val, width=30, boss_name="Boss"):
    """Boss血条显示"""
    bar, hp_text = hp_bar(cur, max_val, width)
    ratio = cur / max_val if max_val > 0 else 0

    # Boss名字带颜色
    if ratio > 0.5:
        name_color = DarkTheme.FIRE_ORANGE
    elif ratio > 0.2:
        name_color = DarkTheme.GOLD_YELLOW
    else:
        name_color = DarkTheme.BLOOD_RED

    return f"  {c('🔥', DarkTheme.FIRE_ORANGE)} {c(boss_name, name_color, C.BOLD)}\n  HP: {bar} {c(hp_text, C.BWHITE)}"


def exp_bar(cur, need, width=24):
    """经验条"""
    return bar_fg(cur, need, width, "█", "░", C.BCYAN, C.BBLACK)


def separator(char="─", width=60, color=C.BBLUE):
    """分隔线"""
    return c(char * width, color)


# ==================== ASCII 艺术边框 ====================

def draw_box(content, width=60, title="", style="double", color=C.BCYAN):
    """
    绘制带边框的内容框

    Args:
        content: 内容字符串（可以是多行）
        width: 框宽度
        title: 标题（可选）
        style: 边框样式 "double"(双线) / "single"(单线) / "dark"(暗黑)
        color: 边框颜色
    """
    if style == "double":
        tl, tr, bl, br, h, v = "╔", "╗", "╚", "╝", "═", "║"
    elif style == "dark":
        tl, tr, bl, br, h, v = "█▄", "▄█", "█▀", "▀█", "▄", "█"
    else:  # single
        tl, tr, bl, br, h, v = "┌", "┐", "└", "┘", "─", "│"

    lines = content.split('\n') if content else [""]
    inner_width = width - 4  # 内容区域宽度

    result = []

    # 顶部边框
    if title:
        title_str = f" {title} "
        title_len = _display_width(title_str)
        top = c(tl + h * 3 + title_str + h * (width - 5 - title_len) + tr, color)
    else:
        top = c(tl + h * (width - 2) + tr, color)
    result.append(top)

    # 内容行
    for line in lines:
        line_content = _pad_to_width(" " + str(line), inner_width)[:inner_width]
        result.append(c(v, color) + line_content + " " + c(v, color))

    # 底部边框
    result.append(c(bl + h * (width - 2) + br, color))

    return "\n".join(result)


def draw_panel(lines, width=60, color=C.BCYAN):
    """
    绘制面板（多行内容）

    Args:
        lines: 内容行列表
        width: 宽度
        color: 颜色
    """
    inner_width = width - 4  # 内容区域宽度
    result = []
    result.append(c("╔" + "═" * (width - 2) + "╗", color))

    for line in lines:
        line_content = _pad_to_width(" " + str(line), inner_width)[:inner_width]
        result.append(c("║", color) + line_content + " " + c("║", color))

    result.append(c("╚" + "═" * (width - 2) + "╝", color))
    return "\n".join(result)


def draw_divider(char="─", width=60, color=C.BBLACK, icons=None):
    """
    绘制分隔线（可选图标）

    Args:
        char: 分隔字符
        width: 宽度
        color: 颜色
        icons: 中间显示的图标列表
    """
    if icons:
        icon_str = " ".join(icons)
        icon_len = len(icon_str)
        side_len = (width - icon_len - 2) // 2
        return (c(char * side_len, color) + " " + icon_str + " " +
                c(char * (width - side_len - icon_len - 2), color))
    return c(char * width, color)


# ==================== ASCII 艺术标题 ====================

def ascii_title_mOTIP(width=60):
    """MOTIP 大标题 ASCII 艺术"""
    title = r"""
    ███╗   ███╗ ██████╗ ██████╗  ██████╗
    ████╗ ████║██╔═══██╗██╔══██╗██╔═══██╗
    ██╔████╔██║██║   ██║██║  ██║██║   ██║
    ██║╚██╔╝██║██║   ██║██║  ██║██║   ██║
    ██║ ╚═╝ ██║╚██████╔╝██████╔╝╚██████╔╝
    ╚═╝     ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝
    """
    lines = title.strip().split('\n')
    result = []
    for line in lines:
        padding = (width - len(line)) // 2
        result.append(" " * max(0, padding) + c(line, DarkTheme.FIRE_ORANGE, C.BOLD))
    return "\n".join(result)


def ascii_title_boss(width=60):
    """Boss战标题"""
    title = r"""
    ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
    █ ▀█▀ ▀▀█▀▀ █▀▀█ █▀▀█ ▀█▀ ▀█▀ █   █
    █  █   █  █  █▀▀█ █▄▄█  █   █  █▄▄▄█
    ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
    """
    lines = title.strip().split('\n')
    result = []
    for line in lines:
        padding = (width - len(line)) // 2
        result.append(" " * max(0, padding) + c(line, DarkTheme.BLOOD_RED, C.BOLD))
    return "\n".join(result)


def ascii_title_victory(width=60):
    """胜利标题"""
    title = r"""
    ██╗   ██╗██╗ ██████╗████████╗ ██████╗ ██████╗ ██╗   ██╗
    ██║   ██║██║██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝
    ██║   ██║██║██║        ██║   ██║   ██║██████╔╝ ╚████╔╝
    ╚██╗ ██╔╝██║██║        ██║   ██║   ██║██╔══██╗  ╚██╔╝
     ╚████╔╝ ██║╚██████╗   ██║   ╚██████╔╝██║  ██║   ██║
      ╚═══╝  ╚═╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝
    """
    lines = title.strip().split('\n')
    result = []
    for line in lines:
        padding = (width - len(line)) // 2
        result.append(" " * max(0, padding) + c(line, DarkTheme.GOLD_YELLOW, C.BOLD))
    return "\n".join(result)


# ==================== 动态动画效果 ====================

def loading_animation(duration=2.0, message="加载中"):
    """加载动画"""
    frames = ["⠋", "⠙", "⠹", "⠸", "⼀", "⠖", "⠒", "⠉"]
    colors = [DarkTheme.SOUL_BLUE, DarkTheme.ICE_CYAN, DarkTheme.POISON_GREEN]

    start = time.time()
    i = 0
    while time.time() - start < duration:
        frame = frames[i % len(frames)]
        color = colors[i % len(colors)]
        sys.stdout.write(f"\r  {c(frame, color, C.BOLD)} {message}...")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1

    sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")
    sys.stdout.flush()


def attack_flash(duration=0.15):
    """攻击闪烁效果"""
    flash_chars = ["▓", "▒", "░"]

    for _ in range(2):
        for char in flash_chars:
            sys.stdout.write(f"\r{c(char * 50, DarkTheme.FIRE_ORANGE, C.BOLD)}\r")
            sys.stdout.flush()
            time.sleep(duration / 6)
        for char in reversed(flash_chars):
            sys.stdout.write(f"\r{c(char * 50, DarkTheme.BLOOD_RED, C.BOLD)}\r")
            sys.stdout.flush()
            time.sleep(duration / 6)

    sys.stdout.write("\r" + " " * 55 + "\r")
    sys.stdout.flush()


def heal_effect(duration=0.3):
    """治疗动画效果"""
    chars = ["💚", "✨", "💫", "🌟"]

    for _ in range(3):
        for char in chars:
            sys.stdout.write(f"\r  {c(char + ' 治疗中...', DarkTheme.POISON_GREEN, C.BOLD)}\r")
            sys.stdout.flush()
            time.sleep(duration / 4)

    sys.stdout.write("\r" + " " * 30 + "\r")
    sys.stdout.flush()


def shield_effect(duration=0.3):
    """护盾动画效果"""
    chars = ["🛡️", "◈", "◆", "◇"]

    for _ in range(3):
        for char in chars:
            sys.stdout.write(f"\r  {c(char + ' 护盾激活!', DarkTheme.SOUL_BLUE, C.BOLD)}\r")
            sys.stdout.flush()
            time.sleep(duration / 4)

    sys.stdout.write("\r" + " " * 30 + "\r")
    sys.stdout.flush()


def freeze_effect(duration=0.4):
    """冰冻动画效果"""
    chars = ["❄️", "✻", "✼", "❅"]

    for _ in range(4):
        for char in chars:
            sys.stdout.write(f"\r  {c(char + ' 冰冻!', DarkTheme.ICE_CYAN, C.BOLD)}\r")
            sys.stdout.flush()
            time.sleep(duration / 4)

    sys.stdout.write("\r" + " " * 30 + "\r")
    sys.stdout.flush()


def critical_hit_effect():
    """暴击效果"""
    flash_chars = ["⚡", "💥", "🔥", "✨"]

    for _ in range(3):
        for char in flash_chars:
            print(f"\r{c('  ' + char + ' 暴击! ' + char, DarkTheme.GOLD_YELLOW, C.BOLD, C.BLINK)}")
            time.sleep(0.1)


# ==================== 庆祝特效 ====================

def celebrate_fire_combo(combo_count):
    """火焰连击特效（连击≥50触发）"""
    print()
    width = 50

    # 火焰喷射动画
    for height in range(1, 8):
        # 清除之前的内容
        sys.stdout.write("\033[F" * 2 if height > 1 else "")

        # 生成火焰层
        fire_line = ""
        for _ in range(width):
            fire_chars = [" ", "░", "▒", "▓", "█", "▀", "▄"]
            weights = [max(0, 7-height*2), 2, 2, 1, 1, 1, 1]
            fire_line += random.choices(fire_chars, weights=weights[:height+2])[0]

        fire_line = c(fire_line, DarkTheme.FIRE_ORANGE if height % 2 == 0 else DarkTheme.GOLD_YELLOW)

        # 连击数字
        combo_text = c(f"🔥 {combo_count} 连击! 🔥", DarkTheme.FIRE_ORANGE, C.BOLD, C.BLINK)
        padding = (width - 18) // 2

        print(" " * 5 + fire_line)
        print(" " * 5 + " " * padding + combo_text)
        time.sleep(0.08)

    time.sleep(0.5)

    # 清除火焰
    for _ in range(2):
        sys.stdout.write("\033[F" + "\033[2K")
        sys.stdout.flush()
    print()


def celebrate_perfect():
    """完美挑战特效（100%正确率）"""
    print()
    width = 50

    colors = [C.BRED, C.BYELLOW, C.BGREEN, C.BCYAN, C.BBLUE, C.BMAGENTA]

    # 彩虹汇聚动画
    for frame in range(8):
        sys.stdout.write("\033[F" * 3 if frame > 0 else "")

        # 生成彩虹行
        lines = []
        for row in range(3):
            line = ""
            for col in range(width):
                dist = abs(col - width//2 - frame * 3)
                if dist < 8 - frame:
                    color = colors[(col + frame) % len(colors)]
                    line += c("█", color)
                else:
                    line += " "
            lines.append(line)

        # 完美文字
        perfect_text = c("✨ 完美! 100% ✨", DarkTheme.GOLD_YELLOW, C.BOLD)
        padding = (width - 17) // 2

        for line in lines:
            print(" " * 5 + line)
        print(" " * 5 + " " * padding + perfect_text)
        time.sleep(0.1)

    time.sleep(0.5)

    # 清除
    for _ in range(4):
        sys.stdout.write("\033[F" + "\033[2K")
        sys.stdout.flush()
    print()


def celebrate_record():
    """打破记录特效"""
    print()

    # 皇冠闪烁
    crown_frames = [
        "    👑    ",
        "   👑👑👑   ",
        "  👑👑👑👑👑  ",
        " 👑👑👑👑👑👑👑 ",
        "👑👑👑👑👑👑👑👑👑",
    ]

    stars = ["⭐", "✨", "🌟", "💫"]

    for i, crown in enumerate(crown_frames):
        sys.stdout.write("\033[F" * 4 if i > 0 else "")

        # 生成星星背景
        for _ in range(3):
            star_line = ""
            for _ in range(40):
                if random.random() < 0.3:
                    star_line += c(random.choice(stars), DarkTheme.GOLD_YELLOW)
                else:
                    star_line += " "
            print(" " * 10 + star_line)

        # 皇冠
        crown_colored = c(crown, DarkTheme.GOLD_YELLOW, C.BOLD, C.BLINK)
        padding = (40 - len(crown)) // 2
        print(" " * 10 + " " * padding + crown_colored)

        time.sleep(0.15)

    # 新记录文字
    print()
    print(c("  🎉 新纪录! 🎉", DarkTheme.GOLD_YELLOW, C.BOLD, C.BLINK))
    time.sleep(0.5)


def celebrate_boss_defeat(boss_name):
    """Boss击败特效"""
    print()

    # 爆炸动画
    explosion_chars = ["💥", "🔥", "✨", "⭐", "💫"]

    for frame in range(6):
        sys.stdout.write("\033[F" * 5 if frame > 0 else "")

        for _ in range(4):
            line = ""
            for _ in range(50):
                if random.random() < 0.4 + frame * 0.1:
                    char = random.choice(explosion_chars)
                    color = random.choice([DarkTheme.FIRE_ORANGE, DarkTheme.GOLD_YELLOW, DarkTheme.BLOOD_RED])
                    line += c(char, color)
                else:
                    line += " "
            print(" " * 5 + line)

        time.sleep(0.12)

    # 胜利文字
    print()
    print(c(f"  ⚔️ {boss_name} 被击败! ⚔️", DarkTheme.GOLD_YELLOW, C.BOLD))
    print(c("  🏆 胜利! 🏆", DarkTheme.GOLD_YELLOW, C.BOLD, C.BLINK))
    time.sleep(0.8)


# ==================== 工具函数 ====================

def wpm_color(wpm):
    """根据WPM返回颜色"""
    if wpm >= 100: return DarkTheme.SHADOW_PURPLE
    if wpm >= 70:  return DarkTheme.POISON_GREEN
    if wpm >= 40:  return DarkTheme.GOLD_YELLOW
    return DarkTheme.BLOOD_RED


def acc_color(acc):
    """根据准确率返回颜色"""
    if acc >= 95: return DarkTheme.POISON_GREEN
    if acc >= 80: return DarkTheme.GOLD_YELLOW
    return DarkTheme.BLOOD_RED


def get_rating(net_wpm, accuracy):
    """获取评级"""
    if   net_wpm >= 120 and accuracy >= 95: return "SSS", "神级打字大师！",  c("SSS", DarkTheme.SHADOW_PURPLE, C.BOLD), "👑"
    elif net_wpm >= 80  and accuracy >= 90: return "S",   "炉火纯青！",      c("S",   DarkTheme.GOLD_YELLOW,  C.BOLD), "⭐"
    elif net_wpm >= 60  and accuracy >= 85: return "A",   "优秀！",          c("A",   DarkTheme.POISON_GREEN,   C.BOLD), "✨"
    elif net_wpm >= 40  and accuracy >= 75: return "B",   "不错！",          c("B",   DarkTheme.SOUL_BLUE,    C.BOLD), "👍"
    elif net_wpm >= 20  and accuracy >= 60: return "C",   "继续加油！",      c("C",   DarkTheme.GOLD_YELLOW         ), "💪"
    else:                                   return "D",   "多多练习！",      c("D",   DarkTheme.BLOOD_RED             ), "🌱"


def get_rpg_title(level):
    """根据等级获取称号"""
    titles = [
        (5, "打字学徒", DarkTheme.COMMON),
        (10, "键盘游侠", DarkTheme.UNCOMMON),
        (20, "键盘黑客", DarkTheme.RARE),
        (30, "代码刺客", DarkTheme.EPIC),
        (40, "极速掌控者", DarkTheme.LEGENDARY),
        (50, "赛博打字机", DarkTheme.LEGENDARY),
    ]

    for threshold, title, color in titles:
        if level < threshold:
            return c(title, color)
    return c("打字之神", DarkTheme.LEGENDARY, C.BOLD)


def clear_screen():
    """清屏"""
    os.system("cls" if os.name == "nt" else "clear")


def diff_display(target, typed, C_ref=C):
    """生成带颜色差异的显示"""
    r_target, r_typed = "", ""
    for i, tc in enumerate(target):
        if i < len(typed):
            uc = typed[i]
            if tc == uc:
                r_target += c(tc, C_ref.BGREEN)
                r_typed += c(uc, C_ref.BGREEN)
            else:
                r_target += c(tc, C_ref.BRED, C_ref.BOLD)
                r_typed += c(uc, C_ref.BRED, C_ref.BOLD)
        else:
            r_target += c(tc, C_ref.BBLACK)
    if len(typed) > len(target):
        r_typed += c(typed[len(target):], C_ref.BYELLOW)
    return r_target, r_typed


def ascii_wpm_chart(wpm_history, net_history=None, width=46, height=7):
    """生成ASCII WPM趋势图"""
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
                line += c("█", DarkTheme.SOUL_BLUE)
            elif net_val >= threshold:
                line += c("▄", DarkTheme.ICE_CYAN)
            else:
                line += c("░", C.BBLACK)
        lines.append("  " + c(f"{int(threshold):>3}", C.BBLACK) + " " + line)
    lines.append("  " + c("─" * (len(data) + 5), C.BBLACK))
    lines.append(
        f"  最低:{c(str(min_v), DarkTheme.BLOOD_RED)}  最高:{c(str(max_v), DarkTheme.POISON_GREEN)}"
        f"  最近毛:{c(str(wpm_history[-1]), DarkTheme.SOUL_BLUE)}"
        + (f"  净:{c(str(ndata[-1]), DarkTheme.ICE_CYAN)}" if ndata else "")
    )
    lines.append(f"  {c('█', DarkTheme.SOUL_BLUE)}=毛WPM  {c('▄', DarkTheme.ICE_CYAN)}=净WPM  {c('░', C.BBLACK)}=低于线")
    return "\n".join(lines)


# 光标控制函数
def move_up(lines=1):
    """光标上移"""
    return f"\033[{lines}A"


def move_to_col1():
    """光标移到行首"""
    return "\r"


def clear_line():
    """清除当前行"""
    return "\033[2K"


def hide_cursor():
    """隐藏光标"""
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor():
    """显示光标"""
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


# ==================== 错误热力图 ====================

def error_heatmap(target, error_positions, width=50):
    """
    生成错误位置热力图

    Args:
        target: 目标文本
        error_positions: 错误位置字典 {position: count}
        width: 热力图宽度
    """
    if not error_positions:
        return "  暂无错误记录"

    lines = []
    lines.append(c("  错误位置热力图", DarkTheme.BLOOD_RED, C.BOLD))

    # 生成位置标记
    max_pos = len(target)
    chars_per_unit = max(1, max_pos // width)

    heatmap_line = "  "
    for i in range(0, max_pos, chars_per_unit):
        # 统计这个区间的错误数
        error_count = sum(error_positions.get(p, 0) for p in range(i, min(i + chars_per_unit, max_pos)))

        if error_count == 0:
            heatmap_line += c("░", C.BBLACK)
        elif error_count <= 2:
            heatmap_line += c("▒", DarkTheme.GOLD_YELLOW)
        elif error_count <= 5:
            heatmap_line += c("▓", DarkTheme.FIRE_ORANGE)
        else:
            heatmap_line += c("█", DarkTheme.BLOOD_RED)

    lines.append(heatmap_line)

    # 显示位置刻度
    scale_line = f"  位置: 0{' ' * (width - 8)}{max_pos}"
    lines.append(c(scale_line, C.BBLACK))

    # 图例
    legend = (f"  {c('░', C.BBLACK)}无错误 {c('▒', DarkTheme.GOLD_YELLOW)}1-2次 "
              f"{c('▓', DarkTheme.FIRE_ORANGE)}3-5次 {c('█', DarkTheme.BLOOD_RED)}5次以上")
    lines.append(legend)

    return "\n".join(lines)


# ==================== 边框装饰系统 ====================

class BorderStyles:
    """精美边框样式集合"""

    # 双线边框（主界面）
    DOUBLE = {
        "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
        "h": "═", "v": "║",
        "lt": "╠", "rt": "╣", "tt": "╦", "bt": "╩", "cr": "╬"
    }

    # 单线边框（子面板）
    SINGLE = {
        "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
        "h": "─", "v": "│",
        "lt": "├", "rt": "┤", "tt": "┬", "bt": "┴", "cr": "┼"
    }

    # 暗黑边框（特殊区域）
    DARK = {
        "tl": "█▀", "tr": "▀█", "bl": "█▄", "br": "▄█",
        "h": "▀", "v": "█"
    }

    # 装饰边框（成就/奖励）
    DECORATED = {
        "tl": "✦", "tr": "✦", "bl": "✦", "br": "✦",
        "h": "═", "v": "║",
        "deco": ["◆", "◇", "◈", "◉"]
    }

    # 圆角边框
    ROUNDED = {
        "tl": "╭", "tr": "╮", "bl": "╰", "br": "╯",
        "h": "─", "v": "│"
    }

    # 粗体边框
    HEAVY = {
        "tl": "┏", "tr": "┓", "bl": "┗", "br": "┛",
        "h": "━", "v": "┃"
    }


def draw_fancy_box(content, width=60, title="", style="double", color=None,
                   icon=None, subtitle=None, show_footer=True):
    """
    绘制精美边框内容框

    Args:
        content: 内容字符串（可以是多行）
        width: 框宽度
        title: 标题（可选）
        style: 边框样式 "double"/"single"/"dark"/"decorated"/"rounded"/"heavy"
        color: 边框颜色
        icon: 标题图标
        subtitle: 副标题
        show_footer: 是否显示底部边框
    """
    if color is None:
        color = DarkTheme.SOUL_BLUE

    # 选择边框样式
    styles = {
        "double": BorderStyles.DOUBLE,
        "single": BorderStyles.SINGLE,
        "dark": BorderStyles.DARK,
        "decorated": BorderStyles.DECORATED,
        "rounded": BorderStyles.ROUNDED,
        "heavy": BorderStyles.HEAVY,
    }
    s = styles.get(style, BorderStyles.DOUBLE)

    lines = content.split('\n') if content else [""]
    result = []

    # 构建标题
    if title:
        title_full = f" {icon} {title} " if icon else f" {title} "
        if style == "dark":
            top = c(s["tl"] + s["h"] * 3 + title_full + s["h"] * (width - 6 - len(title_full)) + s["tr"], color)
        else:
            title_len = len(title_full)
            top = c(s["tl"] + s["h"] * 3 + title_full + s["h"] * (width - 6 - title_len) + s["tr"], color)
    else:
        top = c(s["tl"] + s["h"] * (width - 2) + s["tr"], color)
    result.append(top)

    # 副标题
    if subtitle:
        sub_pad = width - 4 - len(subtitle)
        result.append(c(s["v"], color) + " " + c(subtitle, C.BBLACK) + " " * max(0, sub_pad) + " " + c(s["v"], color))

    # 内容行
    for line in lines:
        line_str = str(line)
        padding = width - 4 - len(line_str)
        if padding < 0:
            padding = 0
            line_str = line_str[:width-4]
        result.append(c(s["v"], color) + " " + line_str + " " * padding + " " + c(s["v"], color))

    # 底部边框
    if show_footer:
        result.append(c(s["bl"] + s["h"] * (width - 2) + s["br"], color))

    return "\n".join(result)


def draw_mode_card(mode_id, mode_name, icon, color, selected=False):
    """
    绘制模式选择卡片

    Args:
        mode_id: 模式编号
        mode_name: 模式名称
        icon: 模式图标
        color: 卡片颜色
        selected: 是否选中
    """
    border_color = DarkTheme.GOLD_YELLOW if selected else C.BBLACK
    card_color = color if selected else C.BBLACK

    lines = []
    lines.append(c("┌──────────┐", border_color))
    lines.append(c("│", border_color) + c(f"   [{mode_id}]   ", card_color, C.BOLD if selected else "") + c("│", border_color))
    lines.append(c("│", border_color) + c(f"    {icon}    ", card_color) + c("│", border_color))
    lines.append(c("│", border_color) + c(f"  {mode_name:^6}  ", card_color, C.BOLD if selected else "") + c("│", border_color))
    lines.append(c("└──────────┘", border_color))

    return "\n".join(lines)


def draw_stat_card(title, value, icon, color, width=20):
    """
    绘制统计数据卡片

    Args:
        title: 标题
        value: 数值
        icon: 图标
        color: 颜色
        width: 宽度
    """
    lines = []
    lines.append(c("┌" + "─" * (width - 2) + "┐", color))
    lines.append(c("│", color) + f" {icon} {title}".ljust(width - 2) + c("│", color))
    lines.append(c("│", color) + " " * (width - 2) + c("│", color))
    lines.append(c("│", color) + c(f"  {value}".center(width - 2), C.BWHITE, C.BOLD) + c("│", color))
    lines.append(c("└" + "─" * (width - 2) + "┘", color))

    return "\n".join(lines)


# ==================== 图标系统 ====================

class Icons:
    """统一图标系统"""

    # 模式图标（大尺寸）
    MODES = {
        "classic":    "⚔️",
        "sprint":     "⚡",
        "word":       "📚",
        "timed":      "⏱️",
        "blind":      "🦅",
        "gauntlet":   "🏰",
        "weak":       "💪",
        "daily":      "📅",
        "ghost":      "👻",
        "paragraph":  "📖",
        "boss":       "👹",
    }

    # 小图标（用于列表/统计）
    SMALL = {
        "wpm": "⚡",
        "accuracy": "🎯",
        "combo": "🔥",
        "exp": "✨",
        "level": "⭐",
        "time": "⏱️",
        "chars": "📝",
        "games": "🎮",
        "streak": "🔥",
        "hp": "💚",
        "shield": "🛡️",
        "attack": "⚔️",
    }

    # 状态图标
    STATUS = {
        "success": "✅",
        "fail": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "locked": "🔒",
        "unlocked": "🔓",
        "new": "🆕",
        "hot": "🔥",
        "done": "✓",
        "pending": "○",
    }

    # 分类图标
    CATEGORIES = {
        "basic": "🎯",
        "speed": "⚡",
        "advanced": "🔥",
        "special": "👹",
        "system": "⚙️",
    }

    # 奖励图标
    REWARDS = {
        "exp": "✨",
        "gold": "💰",
        "item": "🎁",
        "achievement": "🏆",
        "title": "👑",
        "skill": "⚡",
    }

    # 战斗图标
    BATTLE = {
        "attack": "⚔️",
        "defend": "🛡️",
        "heal": "💚",
        "critical": "💥",
        "dodge": "💨",
        "freeze": "❄️",
        "burn": "🔥",
        "poison": "🧪",
    }


# ==================== 过渡动画系统 ====================

class Transitions:
    """过渡动画效果"""

    @staticmethod
    def fade_in(text, duration=0.5, color=None):
        """淡入效果"""
        lines = text.split('\n')
        for line in lines:
            if color:
                print(c(line, color))
            else:
                print(line)
            time.sleep(duration / len(lines))

    @staticmethod
    def typewriter(text, speed=0.02, color=None):
        """打字机效果"""
        for char in text:
            if color:
                sys.stdout.write(c(char, color))
            else:
                sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(speed)
        print()

    @staticmethod
    def scanline(duration=0.3):
        """扫描线效果"""
        width = 60
        for i in range(width):
            line = " " * i + c("█", DarkTheme.SOUL_BLUE) + " " * (width - i - 1)
            sys.stdout.write(f"\r{line}\r")
            sys.stdout.flush()
            time.sleep(duration / width)
        sys.stdout.write(" " * width + "\r")
        sys.stdout.flush()

    @staticmethod
    def glitch(text, duration=0.3, iterations=5):
        """故障效果"""
        glitch_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        for _ in range(iterations):
            glitched = "".join(
                random.choice(glitch_chars) if random.random() < 0.3 else char
                for char in text
            )
            sys.stdout.write(f"\r{c(glitched, DarkTheme.BLOOD_RED)}\r")
            sys.stdout.flush()
            time.sleep(duration / iterations)
        sys.stdout.write(f"\r{text}\r")
        sys.stdout.flush()


def transition_to_game(mode_name, icon, color=None):
    """进入游戏动画（增强版）"""
    if color is None:
        color = DarkTheme.SOUL_BLUE

    clear_screen()

    # 顶部边框动画
    width = 50
    for i in range(width // 2):
        left = "═" * i
        right = "═" * i
        sys.stdout.write("\r" + c("╔" + left + "╗" + " " * (width - 2*i - 2) + "╔" + right + "╗", color) + "\r")
        sys.stdout.flush()
        time.sleep(0.015)

    # 显示模式标题
    print()
    title_line = f"  {icon} {mode_name} {icon}"
    padding = (width - len(title_line) - 4) // 2
    print(c("═" * padding, color) + c(title_line, color, C.BOLD, C.BLINK) + c("═" * padding, color))
    print()

    # 底部边框动画
    for i in range(width // 2, -1, -1):
        left = "═" * i
        right = "═" * i
        sys.stdout.write("\r" + c("╚" + left + "╝" + " " * (width - 2*i - 2) + "╚" + right + "╝", color) + "\r")
        sys.stdout.flush()
        time.sleep(0.015)

    sys.stdout.write("\r" + " " * width + "\r")
    sys.stdout.flush()
    Transitions.scanline(0.15)
    time.sleep(0.1)


def transition_to_result(is_victory=True):
    """进入结果界面动画（增强版）"""
    if is_victory:
        color = DarkTheme.GOLD_YELLOW
        frames = ["✨", "⭐", "🌟", "💫"]
        border_char = "═"
    else:
        color = DarkTheme.BLOOD_RED
        frames = ["💔", "💀", "😢", "😞"]
        border_char = "─"

    # 边框闪烁
    for _ in range(2):
        print(c(border_char * 50, color, C.BLINK))
        time.sleep(0.1)
        sys.stdout.write("\033[F\033[2K")
        sys.stdout.flush()

    for frame in frames:
        sys.stdout.write(f"\r  {c(frame, color, C.BOLD, C.BLINK)}\r")
        sys.stdout.flush()
        time.sleep(0.15)

    sys.stdout.write("\r" + " " * 10 + "\r")
    sys.stdout.flush()


# ==================== 庆祝动效系统 ====================

class Celebrations:
    """庆祝动效集合"""

    @staticmethod
    def new_record(record_type="WPM", value=0):
        """打破记录动画"""
        print()
        # 皇冠上升
        crown_frames = [
            "    👑    ",
            "   👑👑👑   ",
            "  👑👑👑👑👑  ",
            " 👑👑👑👑👑👑👑 ",
            "👑👑👑👑👑👑👑👑👑",
        ]

        for crown in crown_frames:
            sys.stdout.write("\033[F" + " " * 50 + "\r")
            sys.stdout.write(c(crown, DarkTheme.GOLD_YELLOW, C.BOLD, C.BLINK) + "\n")
            sys.stdout.flush()
            time.sleep(0.1)

        print(c(f"  🎉 新纪录！{record_type}: {value} 🎉", DarkTheme.GOLD_YELLOW, C.BOLD))
        time.sleep(0.5)

    @staticmethod
    def achievement_unlock(achievement_name, icon="🏆"):
        """成就解锁动画"""
        print()
        # 光圈扩散
        for radius in range(1, 6):
            rings = "○" * radius
            sys.stdout.write("\033[F" + " " * 50 + "\r")
            sys.stdout.write(c(f"  {rings} {icon} {rings}", DarkTheme.LEGENDARY, C.BOLD) + "\n")
            sys.stdout.flush()
            time.sleep(0.08)

        print(c(f"  ✨ 成就解锁: {achievement_name} ✨", DarkTheme.LEGENDARY, C.BOLD))
        time.sleep(0.5)

    @staticmethod
    def level_up(old_level, new_level):
        """升级动画"""
        print()
        # 等级数字变换
        for i in range(3):
            sys.stdout.write("\033[F" + " " * 50 + "\r")
            sys.stdout.write(c(f"  Lv.{old_level} ⮕ Lv.{new_level}", DarkTheme.SOUL_BLUE, C.BOLD, C.BLINK) + "\n")
            sys.stdout.flush()
            time.sleep(0.15)
            sys.stdout.write("\033[F" + " " * 50 + "\r")
            sys.stdout.write(c(f"  Lv.{new_level} ⭐ LEVEL UP! ⭐", DarkTheme.GOLD_YELLOW, C.BOLD) + "\n")
            sys.stdout.flush()
            time.sleep(0.15)

        time.sleep(0.3)

    @staticmethod
    def confetti(duration=1.0):
        """彩纸飘落效果"""
        chars = ["✨", "⭐", "🌟", "💫", "🎉", "🎊", "✧", "★"]
        width = 50

        for _ in range(int(duration / 0.08)):
            line = ""
            for _ in range(width // 3):
                if random.random() < 0.4:
                    char = random.choice(chars)
                    color = random.choice([DarkTheme.GOLD_YELLOW, DarkTheme.SOUL_BLUE,
                                          DarkTheme.POISON_GREEN, DarkTheme.SHADOW_PURPLE])
                    line += c(char, color)
                else:
                    line += " "
            print(f"  {line}")
            time.sleep(0.08)

    @staticmethod
    def boss_defeat(boss_name):
        """Boss击败庆祝"""
        print()

        # 爆炸效果
        explosion_chars = ["💥", "🔥", "✨", "⭐", "💫"]
        for frame in range(5):
            sys.stdout.write("\033[F" * 3 + "\033[2K")

            for _ in range(2):
                line = ""
                for _ in range(30):
                    if random.random() < 0.5 + frame * 0.1:
                        char = random.choice(explosion_chars)
                        color = random.choice([DarkTheme.FIRE_ORANGE, DarkTheme.GOLD_YELLOW,
                                              DarkTheme.BLOOD_RED])
                        line += c(char, color)
                    else:
                        line += " "
                print(f"  {line}")

            time.sleep(0.1)

        print()
        print(c(f"  ⚔️ {boss_name} 被击败！ ⚔️", DarkTheme.GOLD_YELLOW, C.BOLD))
        print(c("  🏆 胜利！ 🏆", DarkTheme.GOLD_YELLOW, C.BOLD, C.BLINK))
        time.sleep(0.8)

    @staticmethod
    def combo_milestone(combo_count):
        """连击里程碑动画（25/50/75/100连击）"""
        print()
        fire_chars = ["🔥", "💥", "⚡", "✨"]

        for _ in range(3):
            sys.stdout.write("\033[F" * 2 + "\033[2K")

            # 火焰行
            fire_line = ""
            for _ in range(20):
                if random.random() < 0.6:
                    fire_line += c(random.choice(fire_chars), DarkTheme.FIRE_ORANGE)
                else:
                    fire_line += " "

            print(f"  {fire_line}")
            print(c(f"  🔥 {combo_count} 连击！ 🔥", DarkTheme.FIRE_ORANGE, C.BOLD, C.BLINK))
            time.sleep(0.15)

        time.sleep(0.3)

    @staticmethod
    def streak_bonus(streak_count, bonus_exp):
        """连胜奖励动画"""
        print()

        streak_icons = ["🔥", "🔥🔥", "🔥🔥🔥", "🔥🔥🔥🔥", "🔥🔥🔥🔥🔥"]
        icon = streak_icons[min(streak_count - 1, 4)] if streak_count > 0 else "🔥"

        for _ in range(3):
            sys.stdout.write("\033[F" + "\033[2K")
            sys.stdout.flush()
            print(c(f"  {icon} 连胜 x{streak_count}！奖励 +{bonus_exp}XP！", DarkTheme.GOLD_YELLOW, C.BOLD))
            time.sleep(0.12)

        time.sleep(0.2)

    @staticmethod
    def perfect_typing():
        """完美打字动画（100%正确率）"""
        print()

        stars = ["⭐", "✨", "🌟", "💫", "✧", "★"]

        for _ in range(4):
            sys.stdout.write("\033[F" * 2 + "\033[2K")

            # 星星背景
            line = ""
            for _ in range(30):
                if random.random() < 0.5:
                    line += c(random.choice(stars), DarkTheme.GOLD_YELLOW)
                else:
                    line += " "

            print(f"  {line}")
            print(c("  ✨ 完美！100%正确率！✨", DarkTheme.POISON_GREEN, C.BOLD, C.BLINK))
            time.sleep(0.15)

        time.sleep(0.3)

    @staticmethod
    def first_time_reward(reward_name, exp):
        """首次奖励动画"""
        print()

        for i in range(3, 0, -1):
            sys.stdout.write("\033[F" + "\033[2K")
            sys.stdout.flush()
            print(c(f"  🎁 {reward_name} 首次达成！", DarkTheme.SHADOW_PURPLE, C.BOLD, C.BLINK) +
                  c(f" +{exp}XP", DarkTheme.POISON_GREEN, C.BOLD))
            time.sleep(0.2)

        time.sleep(0.2)

    @staticmethod
    def random_event(event_name, multiplier):
        """随机事件动画"""
        print()

        event_icons = {
            "双倍经验": "⭐",
            "三倍经验": "🌟",
            "经验风暴": "💫",
            "幸运加成": "🍀",
        }

        icon = event_icons.get(event_name, "🎲")

        for _ in range(4):
            sys.stdout.write("\033[F" + "\033[2K")
            sys.stdout.flush()

            # 闪烁效果
            colors = [DarkTheme.GOLD_YELLOW, DarkTheme.FIRE_ORANGE, DarkTheme.SHADOW_PURPLE]
            color = random.choice(colors)

            print(c(f"  {icon} 随机事件: {event_name}！", color, C.BOLD, C.BLINK) +
                  c(f" 经验 x{multiplier}", DarkTheme.POISON_GREEN, C.BOLD))
            time.sleep(0.15)

        time.sleep(0.3)


# ==================== 评级系统 ====================

def get_rank_display(net_wpm, accuracy):
    """
    获取评级显示（带图标和颜色）

    Returns:
        tuple: (rank, title, color, icon)
    """
    if net_wpm >= 120 and accuracy >= 98:
        return "SSS", "神级打字大师", DarkTheme.MYTHIC, "👑"
    elif net_wpm >= 100 and accuracy >= 95:
        return "SS", "传奇打字手", DarkTheme.LEGENDARY, "⭐"
    elif net_wpm >= 80 and accuracy >= 90:
        return "S", "炉火纯青", DarkTheme.RANK_S, "🌟"
    elif net_wpm >= 60 and accuracy >= 85:
        return "A", "优秀！", DarkTheme.RANK_A, "✨"
    elif net_wpm >= 40 and accuracy >= 75:
        return "B", "不错！", DarkTheme.RANK_B, "👍"
    elif net_wpm >= 20 and accuracy >= 60:
        return "C", "继续加油！", DarkTheme.RANK_C, "💪"
    else:
        return "D", "多多练习！", DarkTheme.RANK_D, "🌱"


# ==================== 主界面组件 ====================

def draw_status_panel(stats, width=58):
    """
    绘制状态面板

    Args:
        stats: 统计数据
        width: 面板宽度
    """
    from data import get_level

    level, cur_exp, need_exp = get_level(stats.get("exp", 0))
    hp_ratio = 0.8  # 模拟HP

    lines = []
    lines.append(c(f"  ┌{'─' * (width - 4)}┐", DarkTheme.SOUL_BLUE))
    lines.append(c("  │", DarkTheme.SOUL_BLUE) + c(f"  📊 状态面板", DarkTheme.SOUL_BLUE, C.BOLD).ljust(width - 3) + c("│", DarkTheme.SOUL_BLUE))

    # HP条
    hp_bar_str = hp_bar(int(hp_ratio * 100), 100, 20)[0]
    lines.append(c("  │", DarkTheme.SOUL_BLUE) + f"  💚 HP: {hp_bar_str} 80/100".ljust(width - 4) + c("│", DarkTheme.SOUL_BLUE))

    # 经验条
    exp_bar_str = exp_bar(cur_exp, need_exp, 20)
    lines.append(c("  │", DarkTheme.SOUL_BLUE) + f"  ⚡ EXP: {exp_bar_str} {cur_exp}/{need_exp}".ljust(width - 20) + c("│", DarkTheme.SOUL_BLUE))

    # 其他状态
    streak = stats.get("streak", 0)
    today_games = stats.get("daily", {}).get("games", 0)
    login_days = stats.get("login_days", 0)

    status_line = f"  🔥连胜:{streak}局  ✨今日:{today_games}局  📅登录:{login_days}天"
    lines.append(c("  │", DarkTheme.SOUL_BLUE) + status_line.ljust(width - 3) + c("│", DarkTheme.SOUL_BLUE))
    lines.append(c(f"  └{'─' * (width - 4)}┘", DarkTheme.SOUL_BLUE))

    return "\n".join(lines)


def draw_category_section(category_name, icon, modes, color, start_key=1):
    """
    绘制模式分类区块

    Args:
        category_name: 分类名称
        icon: 分类图标
        modes: 模式列表 [(id, name, func), ...]
        color: 区块颜色
        start_key: 起始按键
    """
    lines = []
    lines.append(f"  {c(icon + ' ══════', color, C.BOLD)} {c(category_name, color, C.BOLD)} {c('══════ ' + icon, color, C.BOLD)}")

    # 绘制模式卡片行
    cards_per_row = 3
    for i in range(0, len(modes), cards_per_row):
        row_modes = modes[i:i + cards_per_row]
        card_line = "      "
        for mode_id, mode_name, mode_icon in row_modes:
            card = c(f"[{mode_id}]", DarkTheme.GOLD_YELLOW) + f" {mode_icon} {mode_name}"
            card_line += card + "   "
        lines.append(card_line)

    return "\n".join(lines)


# ==================== 结果界面组件 ====================

def draw_result_card(target, user_input, elapsed, wpm, net_wpm, accuracy,
                     rank, rank_title, rank_color, exp_gain, combo=0,
                     prev_best=None, is_new_record=False):
    """
    绘制结果卡片（增强版）

    Args:
        target: 目标文本
        user_input: 用户输入
        elapsed: 用时
        wpm: 毛WPM
        net_wpm: 净WPM
        accuracy: 正确率
        rank: 评级
        rank_title: 评级标题
        rank_color: 评级颜色
        exp_gain: 经验奖励
        combo: 连击数
        prev_best: 之前最佳
        is_new_record: 是否新纪录
    """
    width = 56
    inner_width = width - 2  # 内部内容宽度

    def make_line(content):
        """生成一行，自动处理宽度"""
        return c("║", DarkTheme.GOLD_YELLOW) + _pad_to_width(content, inner_width) + c("║", DarkTheme.GOLD_YELLOW)

    lines = []

    # 顶部装饰边框
    lines.append(c("╔" + "═" * (width - 2) + "╗", DarkTheme.GOLD_YELLOW))

    # 评级区
    lines.append(make_line(""))

    # 动态评级图标
    rank_icons = {"SSS": "👑", "SS": "⭐", "S": "🌟", "A": "✨", "B": "👍", "C": "💪", "D": "🌱"}
    rank_icon = rank_icons.get(rank, "⭐")

    rank_display = c(f"{rank_icon} {rank} 级评价 {rank_icon}", rank_color, C.BOLD, C.BLINK)
    # 手动居中
    rank_dw = _display_width(rank_display)
    rank_pad = (inner_width - rank_dw) // 2
    lines.append(c("║", DarkTheme.GOLD_YELLOW) + " " * rank_pad + rank_display + " " * (inner_width - rank_pad - rank_dw) + c("║", DarkTheme.GOLD_YELLOW))

    title_display = c(rank_title, rank_color)
    title_dw = _display_width(title_display)
    title_pad = (inner_width - title_dw) // 2
    lines.append(c("║", DarkTheme.GOLD_YELLOW) + " " * title_pad + title_display + " " * (inner_width - title_pad - title_dw) + c("║", DarkTheme.GOLD_YELLOW))

    lines.append(make_line(""))

    # 分隔线
    lines.append(c("╠" + "═" * (width - 2) + "╣", DarkTheme.GOLD_YELLOW))

    # 输入对比区
    lines.append(make_line(c("  📝 输入对比", DarkTheme.SOUL_BLUE, C.BOLD)))

    # 截断过长的文本（基于显示宽度）
    max_display_len = inner_width - 8
    target_display = target
    typed_display = user_input
    if _display_width(target) > max_display_len:
        # 逐字截断
        truncated = ""
        for ch in target:
            if _display_width(truncated + ch + "...") > max_display_len:
                break
            truncated += ch
        target_display = truncated + "..."
    if _display_width(user_input) > max_display_len:
        truncated = ""
        for ch in user_input:
            if _display_width(truncated + ch + "...") > max_display_len:
                break
            truncated += ch
        typed_display = truncated + "..."

    r_target, r_typed = diff_display(target_display, typed_display)
    lines.append(make_line(f"  目标: {r_target}"))
    lines.append(make_line(f"  输入: {r_typed}"))

    # 分隔线
    lines.append(c("╠" + "═" * (width - 2) + "╣", DarkTheme.GOLD_YELLOW))

    # 数据区
    lines.append(make_line(c("  📊 本局数据", DarkTheme.SOUL_BLUE, C.BOLD)))

    # WPM
    wpm_bar = bar_fg(min(net_wpm, 120), 120, 16, full_color=wpm_color(net_wpm))
    wpm_line = f"  ⚡ 净WPM   {wpm_bar} {c(str(net_wpm), wpm_color(net_wpm), C.BOLD)}"
    lines.append(make_line(wpm_line))

    # 毛WPM
    lines.append(make_line(f"     毛WPM  {c(str(wpm), C.BBLACK)}"))

    # 准确率
    acc_bar = bar_fg(accuracy, 100, 16, full_color=acc_color(accuracy))
    acc_line = f"  🎯 正确率  {acc_bar} {c(str(accuracy)+'%', acc_color(accuracy), C.BOLD)}"
    lines.append(make_line(acc_line))

    # 连击
    if combo > 0:
        combo_bar = bar_fg(min(combo, 100), 100, 16, full_color=DarkTheme.FIRE_ORANGE)
        combo_line = f"  🔥 连击    {combo_bar} {c('x'+str(combo), DarkTheme.FIRE_ORANGE, C.BOLD)}"
        lines.append(make_line(combo_line))

    # 用时
    lines.append(make_line(f"  ⏱️ 用时    {c(f'{elapsed:.2f}s', C.BCYAN)}"))

    # 历史对比
    if prev_best and prev_best > 0:
        lines.append(c("╠" + "═" * (width - 2) + "╣", DarkTheme.GOLD_YELLOW))
        lines.append(make_line(c("  📈 历史对比", DarkTheme.SOUL_BLUE, C.BOLD)))

        diff = net_wpm - prev_best
        if diff > 0:
            diff_str = c(f"+{diff}", DarkTheme.POISON_GREEN, C.BOLD)
        elif diff < 0:
            diff_str = c(str(diff), DarkTheme.BLOOD_RED)
        else:
            diff_str = c("0", C.BBLACK)

        hist_line = f"  本局: {c(str(net_wpm), wpm_color(net_wpm), C.BOLD)} WPM  最佳: {c(str(prev_best), wpm_color(prev_best))} WPM"
        lines.append(make_line(hist_line))

        if is_new_record:
            lines.append(make_line(""))
            new_record_line = c(f"🎉 新纪录！超越 {diff_str} WPM！🎉", DarkTheme.GOLD_YELLOW, C.BOLD, C.BLINK)
            nr_dw = _display_width(new_record_line)
            nr_pad = (inner_width - nr_dw) // 2
            lines.append(c("║", DarkTheme.GOLD_YELLOW) + " " * nr_pad + new_record_line + " " * (inner_width - nr_pad - nr_dw) + c("║", DarkTheme.GOLD_YELLOW))

    # 经验奖励
    lines.append(c("╠" + "═" * (width - 2) + "╣", DarkTheme.GOLD_YELLOW))
    lines.append(make_line(""))
    exp_line = c(f"  ✨ 经验奖励: {c('+' + str(exp_gain) + ' XP', DarkTheme.POISON_GREEN, C.BOLD)}", DarkTheme.SOUL_BLUE)
    lines.append(make_line(exp_line))
    lines.append(make_line(""))

    lines.append(c("╚" + "═" * (width - 2) + "╝", DarkTheme.GOLD_YELLOW))

    return "\n".join(lines)
