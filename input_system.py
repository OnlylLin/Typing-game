"""
输入系统模块 - 实时打字、幽灵竞速、暂停功能、错误追踪
"""

import os
import sys
import time
from collections import defaultdict

from ui import c, C, DarkTheme, bar_fg, move_up, move_to_col1, clear_line


# ==================== 实时错误追踪系统 ====================

class RealtimeErrorTracker:
    """
    实时错误追踪器
    记录所有错误，包括用户按退格改正的错误
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """重置追踪器"""
        self.errors = []  # 错误事件列表
        self.error_chars = defaultdict(lambda: {"count": 0, "positions": [], "corrected": 0})
        self.error_positions = defaultdict(int)  # 位置->错误次数
        self.error_types = {"wrong": 0, "extra": 0, "miss": 0}
        self.total_keystrokes = 0
        self.backspaces = 0
        self.corrections = 0  # 成功改正的错误数

    def on_char_input(self, char, expected, position, timestamp=None):
        """
        记录字符输入

        Returns:
            bool: 是否是错误
        """
        self.total_keystrokes += 1
        if timestamp is None:
            timestamp = time.time()

        if char != expected:
            # 记录错误
            error_type = self._classify_error(expected, char)
            error_event = {
                "position": position,
                "expected": expected,
                "actual": char,
                "timestamp": timestamp,
                "corrected": False,
                "error_type": error_type
            }
            self.errors.append(error_event)

            # 更新统计
            self.error_chars[expected]["count"] += 1
            self.error_chars[expected]["positions"].append(position)
            self.error_positions[position] += 1
            self.error_types[error_type] += 1

            return True
        return False

    def on_backspace(self, position, timestamp=None):
        """
        处理退格事件
        标记上一个错误为"已改正"
        """
        self.backspaces += 1
        if timestamp is None:
            timestamp = time.time()

        # 查找最近的未改正错误
        for error in reversed(self.errors):
            if not error["corrected"] and error["position"] == position - 1:
                error["corrected"] = True
                error["corrected_at"] = timestamp

                # 更新字符统计
                expected = error["expected"]
                self.error_chars[expected]["corrected"] += 1
                self.corrections += 1
                break

    def _classify_error(self, expected, actual):
        """分类错误类型"""
        if expected and not actual:
            return "miss"      # 少打
        elif actual and not expected:
            return "extra"     # 多打
        else:
            return "wrong"     # 打错

    def get_error_rate(self):
        """获取错误率"""
        if self.total_keystrokes == 0:
            return 0
        return len(self.errors) / self.total_keystrokes * 100

    def get_correction_rate(self):
        """获取错误改正率"""
        if len(self.errors) == 0:
            return 100
        return self.corrections / len(self.errors) * 100

    def get_top_error_chars(self, n=5):
        """获取错误最多的字符"""
        sorted_chars = sorted(
            self.error_chars.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        return sorted_chars[:n]

    def get_error_hotspots(self, threshold=2):
        """获取错误热点位置"""
        return {pos: count for pos, count in self.error_positions.items()
                if count >= threshold}

    def get_type_distribution(self):
        """获取错误类型分布"""
        total = sum(self.error_types.values())
        if total == 0:
            return {"wrong": 0, "extra": 0, "miss": 0}
        return {k: v / total for k, v in self.error_types.items()}

    def get_summary(self):
        """获取错误摘要"""
        return {
            "total_errors": len(self.errors),
            "corrected_errors": self.corrections,
            "correction_rate": self.get_correction_rate(),
            "error_rate": self.get_error_rate(),
            "top_errors": self.get_top_error_chars(5),
            "hotspots": self.get_error_hotspots(),
            "type_distribution": self.get_type_distribution(),
            "backspaces": self.backspaces,
            "total_keystrokes": self.total_keystrokes
        }

    def generate_practice_suggestions(self):
        """生成针对性练习建议"""
        suggestions = []

        # 1. 高频错误字符
        top_errors = self.get_top_error_chars(3)
        if top_errors:
            chars = [f"'{ch}'" for ch, _ in top_errors]
            suggestions.append(f"💡 重点练习: {', '.join(chars)} 字符")

        # 2. 错误类型建议
        dist = self.get_type_distribution()
        if dist.get("extra", 0) > 0.3:
            suggestions.append("💡 控制输入速度，减少多打字符")
        if dist.get("miss", 0) > 0.3:
            suggestions.append("💡 注意目标文本，避免跳过字符")
        if dist.get("wrong", 0) > 0.5:
            suggestions.append("💡 注意手指位置，减少按错键")

        # 3. 改正率建议
        if self.get_correction_rate() < 50:
            suggestions.append("💡 发现错误后及时使用退格改正")
        elif self.get_correction_rate() > 80:
            suggestions.append("💡 很好！保持及时改正错误的习惯")

        # 4. 热点区域
        hotspots = self.get_error_hotspots()
        if hotspots:
            suggestions.append(f"💡 注意文本中段位置，容易出错")

        return suggestions if suggestions else ["💡 继续练习，保持良好状态！"]


# 全局错误追踪器实例
_error_tracker = RealtimeErrorTracker()


def get_error_tracker():
    """获取全局错误追踪器"""
    return _error_tracker


def reset_error_tracker():
    """重置全局错误追踪器"""
    _error_tracker.reset()


# ==================== 跨平台输入 ====================

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


# ==================== 暂停系统 ====================

class PauseState:
    """暂停状态管理"""
    paused = False
    elapsed_before_pause = 0

    @classmethod
    def reset(cls):
        cls.paused = False
        cls.elapsed_before_pause = 0


def show_pause_menu(elapsed, progress, target_len):
    """显示暂停菜单"""
    print()
    print(c("═" * 50, C.BYELLOW))
    print(c("  ⏸️  游戏暂停", C.BYELLOW, C.BOLD))
    print(c("═" * 50, C.BYELLOW))
    print(f"  已用时间: {c(f'{elapsed:.1f}s', C.BCYAN)}")
    print(f"  当前进度: {c(f'{progress}/{target_len}', C.BGREEN)}")
    print(c("─" * 50, C.BBLACK))
    print(f"  {c('C', C.BGREEN)} 继续游戏")
    print(f"  {c('Q', C.BRED)} 退出本局")
    print(c("═" * 50, C.BYELLOW))
    return input(c("  请选择: ", C.BCYAN)).strip().lower()


def handle_pause(start_t, typed_len, target_len, allow_pause=False):
    """处理暂停逻辑，返回 (should_continue, should_exit)"""
    if not allow_pause:
        return True, False

    PauseState.elapsed_before_pause = time.time() - start_t
    PauseState.paused = True

    # 保存光标位置后显示暂停菜单
    choice = show_pause_menu(PauseState.elapsed_before_pause, typed_len, target_len)

    PauseState.paused = False

    if choice == 'q':
        return False, True  # 退出
    return True, False  # 继续


# ==================== 幽灵进度可视化 ====================

def ghost_progress_bar(player_pos, ghost_pos, target_len, width=30):
    """
    生成玩家与幽灵的对比进度条
    返回: (玩家进度条, 幽灵进度条, 差距指示)
    """
    p_ratio = min(player_pos / target_len, 1.0) if target_len > 0 else 0
    g_ratio = min(ghost_pos / target_len, 1.0) if target_len > 0 else 0

    # 玩家进度条（绿色）
    p_filled = int(p_ratio * width)
    p_bar = C.BGREEN + "#" * p_filled + C.BBLACK + "-" * (width - p_filled) + C.RESET

    # 幽灵进度条（紫色）
    g_filled = int(g_ratio * width)
    g_bar = C.BMAGENTA + "#" * g_filled + C.BBLACK + "-" * (width - g_filled) + C.RESET

    # 差距指示
    diff = player_pos - ghost_pos
    if diff > 0:
        diff_str = c(f"⬆ 超前 {diff} 字", C.BGREEN, C.BOLD)
    elif diff < 0:
        diff_str = c(f"⬇ 落后 {-diff} 字", C.BRED, C.BOLD)
    else:
        diff_str = c("⬌ 并驾齐驱", C.BYELLOW)

    return p_bar, g_bar, diff_str


def speed_dashboard(player_wpm, ghost_wpm, width=15):
    """
    生成速度对比仪表盘
    """
    max_wpm = max(player_wpm, ghost_wpm, 1)
    p_ratio = player_wpm / max_wpm
    g_ratio = ghost_wpm / max_wpm

    p_filled = int(p_ratio * width)
    g_filled = int(g_ratio * width)

    p_bar = C.BGREEN + "#" * p_filled + C.BBLACK + "-" * (width - p_filled) + C.RESET
    g_bar = C.BMAGENTA + "#" * g_filled + C.BBLACK + "-" * (width - g_filled) + C.RESET

    return (
        f"  你: {c(str(player_wpm), C.BGREEN, C.BOLD):>3} WPM {p_bar}\n"
        f"  鬼: {c(str(ghost_wpm), C.BMAGENTA, C.BOLD):>3} WPM {g_bar}"
    )


def ghost_position_marker(target, ghost_pos):
    """
    在目标文本上标记幽灵当前位置（残影效果）
    """
    if ghost_pos >= len(target):
        return ""

    # 显示幽灵位置附近的文本
    start = max(0, ghost_pos - 10)
    end = min(len(target), ghost_pos + 20)

    result = ""
    for i in range(start, end):
        if i == ghost_pos:
            result += c(target[i], C.BG_MAGENTA, C.WHITE, C.BOLD)
        else:
            result += c(target[i], C.BBLACK)

    return result


# ==================== 游戏性增强 ====================

def show_goal_hint(target_len, ghost_wpm=0, best_wpm=0):
    """
    显示本局小目标提示
    """
    hints = []

    if ghost_wpm > 0:
        hints.append(f"🎯 击败幽灵 {ghost_wpm} WPM")
    if best_wpm > 0:
        hints.append(f"⭐ 超越最佳 {best_wpm} WPM")

    # 根据目标长度给出建议
    if target_len < 30:
        hints.append("💡 专注准确率")
    elif target_len < 80:
        hints.append("💡 保持节奏")
    else:
        hints.append("💡 耐力挑战")

    return hints


def error_hotspot_warning(target, char_errors):
    """
    错误热区预警 - 分析目标文本中容易出现错误的字符
    """
    if not char_errors:
        return ""

    # 找出目标文本中错误率高的字符
    hot_chars = []
    for ch in target:
        if ch in char_errors and char_errors[ch].get("count", 0) >= 3:
            if ch not in hot_chars:
                hot_chars.append(ch)

    if not hot_chars:
        return ""

    return c(f"⚠️ 注意: {' '.join(hot_chars[:5])} 是你的弱键", C.BYELLOW)


def progress_percentage(current, total):
    """
    生成进度百分比和预计剩余时间
    """
    if total == 0:
        return "0%", ""

    pct = int(current / total * 100)
    return f"{pct}%", f"{current}/{total}"


# ==================== 实时打字核心 ====================

def realtime_type(target, mode_label="", ghost_wpm=0, allow_pause=False,
                  char_errors=None, best_wpm=0):
    """
    实时打字核心函数（增强版）

    新增功能:
    - 幽灵进度可视化
    - 速度仪表盘
    - 暂停功能
    - 目标提示
    - 错误热区预警

    返回: (user_input: str, elapsed: float) 或 (None, 0) 若退出
    """
    # 确保之前的输出被刷新，避免黑屏
    sys.stdout.flush()

    typed   = []
    start_t = None
    LINES   = 5  # 目标 + 输入 + 幽灵进度 + 统计 + 提示

    # 扩展属性
    realtime_type.max_combo = 0
    realtime_type.total_errors_made = 0
    realtime_type.is_perfect = True

    dynamic_ghost_wpm = ghost_wpm
    ghost_chars = 0  # 幽灵已打字符数

    # 目标提示
    goal_hints = show_goal_hint(len(target), ghost_wpm, best_wpm)
    error_hint = error_hotspot_warning(target, char_errors or {})

    def _render(typed_list, elapsed_time):
        nonlocal dynamic_ghost_wpm, ghost_chars
        tt = "".join(typed_list)
        tl = len(target)

        # === 目标行 ===
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
            tgt += c("|", C.BCYAN) if len(tt) == tl else ""
        extra_str = c(tt[tl:], C.BYELLOW, C.BOLD) if len(tt) > tl else ""

        # === 输入行 ===
        inp = ""
        for i, uc in enumerate(tt):
            if i < tl:
                inp += c(uc, C.BGREEN if uc == target[i] else C.BRED + C.BOLD)
            else:
                inp += c(uc, C.BYELLOW, C.BOLD)

        # === 统计数据 ===
        correct_chars = sum(1 for i, uc in enumerate(tt[:tl]) if uc == target[i])
        errors        = len(tt) - correct_chars if tt else 0

        # 连击计算
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

        prog_bar = bar_fg(min(len(tt), tl), tl, width=20,
                          full_char=">", empty_char=".",
                          full_color=C.BGREEN, empty_color=C.BBLACK)

        # === 幽灵进度（增强版） ===
        ghost_str = ""
        ghost_visual = ""
        if ghost_wpm > 0 and start_t:
            # 橡皮筋机制
            if correct_chars > 0:
                current_wpm = int((correct_chars / 5) / (elapsed_time / 60))
                if current_wpm > dynamic_ghost_wpm + 3:
                    dynamic_ghost_wpm += 0.5
                elif current_wpm < dynamic_ghost_wpm - 3:
                    dynamic_ghost_wpm -= 0.5
                dynamic_ghost_wpm = max(ghost_wpm * 0.7, min(dynamic_ghost_wpm, ghost_wpm * 1.3))

            # 计算幽灵位置
            ghost_chars = int((dynamic_ghost_wpm * 5) * (elapsed_time / 60))

            # 进度条对比
            p_bar, g_bar, diff_str = ghost_progress_bar(len(tt), ghost_chars, tl, width=25)
            ghost_visual = (
                f"\n  {c('你', C.BGREEN)} {p_bar}\n"
                f"  {c('鬼', C.BMAGENTA)} {g_bar}  {diff_str}"
            )

        # === 主统计行 ===
        if start_t and tt:
            el   = max(0.001, elapsed_time)
            gross = int((len(tt) / 5) / (el / 60))
            net   = max(0, int(((correct_chars / 5) - (errors / 5)) / (el / 60)))
            wc    = wpm_color(net)

            # 进度百分比
            pct, progress_str = progress_percentage(min(len(tt), tl), tl)

            stats_str = (
                f" {c(str(net)+'净', wc, C.BOLD)}/{c(str(gross)+'毛WPM', C.BBLACK)}"
                f"  {c(str(correct_chars)+'✓', C.BGREEN)}"
                + (f" {c(str(errors)+'✗', C.BRED)}" if errors else "")
                + f"  {prog_bar} {c(pct, C.BCYAN)}"
                + combo_str
            )
        else:
            stats_str = (
                f" {c('等待输入...', C.BBLACK, C.ITALIC)}"
                + (f"  {c('👻 对抗幽灵: '+str(ghost_wpm)+' WPM', C.BMAGENTA)}" if ghost_wpm > 0 else "")
                + f"  {prog_bar}"
                + combo_str
            )

        # === 提示行 ===
        hint_str = ""
        if goal_hints and not start_t:
            hint_str = c("  " + " | ".join(goal_hints[:2]), C.BBLACK, C.ITALIC)
        elif error_hint and not start_t:
            hint_str = error_hint

        return tgt + extra_str, inp, stats_str, ghost_visual, hint_str

    # 首次绘制
    tgt_d, inp_d, stats_d, ghost_d, hint_d = _render([], 0)
    pause_hint = c(" P=暂停", C.BBLACK) if allow_pause else ""
    hint_suffix = f"  {c('['+mode_label+'] ESC=退出'+pause_hint+' Backspace=删除', C.BBLACK, C.ITALIC)}" if mode_label else ""

    print(f" {c('目标', C.BBLACK)}: {tgt_d}{hint_suffix}")
    print(f" {c('输入', C.BBLACK)}: {inp_d}")
    print(ghost_d if ghost_d else "")
    print(f"{stats_d}")
    print(hint_d)
    sys.stdout.flush()  # 立即刷新输出，避免黑屏

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
                    # 记录退格改正
                    _error_tracker.on_backspace(len(typed))
                    typed.pop()
            elif ch == '\x1b':
                print()
                return None, 0
            elif ch.lower() == 'p' and allow_pause:
                # 暂停处理
                if start_t:
                    elapsed_before = time.time() - start_t
                    should_continue, should_exit = handle_pause(
                        start_t, len(typed), len(target), allow_pause
                    )
                    if should_exit:
                        return None, 0
                    if should_continue:
                        # 调整开始时间以补偿暂停时间
                        pause_duration = time.time() - start_t - elapsed_before
                        start_t += pause_duration

                        # 重绘
                        sys.stdout.write((move_up() + move_to_col1() + clear_line()) * LINES)
                        continue
            elif ch.isprintable():
                if start_t is None:
                    start_t = time.time()
                    # 重置错误追踪器
                    _error_tracker.reset()

                # 错误检测与追踪
                if len(typed) < len(target):
                    expected = target[len(typed)]
                    is_error = _error_tracker.on_char_input(ch, expected, len(typed))
                    if is_error:
                        is_new_error = True
                        realtime_type.total_errors_made += 1
                        realtime_type.is_perfect = False
                elif len(typed) >= len(target):
                    # 超出目标长度也算错误
                    _error_tracker.on_char_input(ch, None, len(typed))
                    is_new_error = True
                    realtime_type.total_errors_made += 1
                    realtime_type.is_perfect = False

                typed.append(ch)
            else:
                continue

            # 计算当前时间
            current_elapsed = time.time() - (start_t or time.time()) if start_t else 0

            # 重绘
            sys.stdout.write((move_up() + move_to_col1() + clear_line()) * LINES)
            tgt_d, inp_d, stats_d, ghost_d, hint_d = _render(typed, current_elapsed)

            # Error Flash
            if is_new_error:
                sys.stdout.write(f"{C.BG_RED} {c('目标', C.BBLACK)}: {tgt_d} {C.RESET}\n")
                sys.stdout.write(f"{C.BG_RED} {c('输入', C.BBLACK)}: {inp_d} {C.RESET}\n")
                sys.stdout.write(f"{C.BG_RED}{ghost_d if ghost_d else ''}{C.RESET}\n")
                sys.stdout.write(f"{C.BG_RED}{stats_d}{C.RESET}\n")
                sys.stdout.write(f"{C.BG_RED}{hint_d}{C.RESET}\n")
                sys.stdout.flush()
                time.sleep(0.04)
                sys.stdout.write((move_up() + move_to_col1() + clear_line()) * LINES)

            sys.stdout.write(f" {c('目标', C.BBLACK)}: {tgt_d}\n")
            sys.stdout.write(f" {c('输入', C.BBLACK)}: {inp_d}\n")
            sys.stdout.write(f"{ghost_d if ghost_d else ''}\n")
            sys.stdout.write(f"{stats_d}\n")
            sys.stdout.write(f"{hint_d}\n")
            sys.stdout.flush()

    except KeyboardInterrupt:
        print()
        return None, 0

    elapsed = time.time() - (start_t or time.time())

    # 保存错误追踪摘要到函数属性
    realtime_type.error_summary = _error_tracker.get_summary()
    realtime_type.error_suggestions = _error_tracker.generate_practice_suggestions()

    return "".join(typed), max(0.01, elapsed)


def wpm_color(wpm):
    """根据WPM返回颜色"""
    if wpm >= 100: return C.BMAGENTA
    if wpm >= 70:  return C.BGREEN
    if wpm >= 40:  return C.BYELLOW
    return C.BRED
