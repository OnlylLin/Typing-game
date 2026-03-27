"""
UI模块 - 颜色系统、进度条、可视化组件、暗黑主题、动画效果
"""

import os
import sys
import time
import random

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
    if max_val <= 0:
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

    result = []

    # 顶部边框
    if title:
        title_str = f" {title} "
        title_len = len(title_str)
        top = c(tl + h * 3 + title_str + h * (width - 5 - title_len) + tr, color)
    else:
        top = c(tl + h * (width - 2) + tr, color)
    result.append(top)

    # 内容行
    for line in lines:
        # 处理中文字符宽度
        line_display = line
        padding = width - 4 - len(line_display)
        if padding < 0:
            padding = 0
            line_display = line_display[:width-4]
        result.append(c(v, color) + " " + line_display + " " * padding + " " + c(v, color))

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
    result = []
    result.append(c("╔" + "═" * (width - 2) + "╗", color))

    for line in lines:
        padding = width - 4 - len(str(line))
        if padding < 0:
            padding = 0
        result.append(c("║", color) + " " + str(line)[:width-4] + " " * padding + " " + c("║", color))

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
