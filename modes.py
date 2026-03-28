"""
游戏模式模块 - 11种游戏模式的实现（含Boss关卡模式）
"""

import random
import time
from datetime import date

from ui import (
    c, C, DarkTheme, bar_fg, exp_bar, separator, wpm_color, acc_color,
    get_rating, get_rpg_title, clear_screen, diff_display, hp_bar,
    celebrate_boss_defeat, celebrate_perfect, attack_flash, heal_effect,
    shield_effect, freeze_effect, loading_animation, draw_box,
    draw_result_card, Celebrations, Transitions, get_rank_display
)
from data import (
    TEXTS, WORD_BANKS, DAILY_POOL, ACHIEVEMENTS, SKILLS, DAILY_TASKS,
    load_stats, save_stats, load_config, load_custom_words, save_custom_word,
    calculate_accuracy, calculate_net_wpm, track_key_errors, check_daily_reset,
    finish_game, get_level
)
from input_system import realtime_type
from boss_system import (
    Player, Boss, BattleSystem, StageManager, BOSSES, PLAYER_SKILLS,
    show_battle_intro, show_skill_menu, show_battle_result,
    get_boss_save_key, save_boss_progress
)
from vocabulary import VocabularyManager
from quiz_system import play_quiz_level, boss_cloze_challenge


# ==================== 结果展示 ====================

def show_result(target, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_level, level, new_ach, daily_tasks=None, combo=0,
                mode="", prev_best_net=0, ghost_beat=False, reward_info=None):
    """显示游戏结果（卡片式设计）"""
    from ui import draw_result_card, Celebrations, Transitions, get_rank_display, bar_fg

    clear_screen()

    # 进入结果动画
    Transitions.scanline(0.15)

    # 绘制结果卡片
    rank, rank_title, rank_color, rank_icon = get_rank_display(net_wpm, accuracy)
    is_new_record = prev_best_net > 0 and net_wpm > prev_best_net

    card = draw_result_card(
        target, user_input, elapsed, wpm, net_wpm, accuracy,
        rating, text, rating_col, exp_gain, combo,
        prev_best_net, is_new_record
    )
    print(card)

    # 历史对比
    if prev_best_net > 0:
        diff_v = net_wpm - prev_best_net
        diff_s = (c(f"+{diff_v}", C.BGREEN) if diff_v >= 0 else c(str(diff_v), C.BRED))
        print(f"  {c('历史最佳净WPM: '+str(prev_best_net), C.BBLACK)}  本局差值: {diff_s}")
    if ghost_beat:
        print(c("  👻 击败幽灵记录！经验 x1.5！", C.BMAGENTA, C.BOLD))

    # 等级显示
    print(separator("─", 56, C.BBLACK))
    lv_str = (c(f"Lv.{old_level}", C.BYELLOW) + " ➜ " + c(f"Lv.{level}", C.BGREEN, C.BOLD)
              if level > old_level else c(f"Lv.{level}", C.BYELLOW))
    print(f"  {c('+'+str(exp_gain)+'XP', C.BGREEN)}  {lv_str}")

    # 升级动画
    if level > old_level:
        Celebrations.level_up(old_level, level)

    # 显示奖励详情
    if reward_info:
        print(separator("─", 56, C.BBLACK))
        print(c("  🎁 奖励明细", C.BCYAN, C.BOLD))

        # 随机事件
        if reward_info.get("random_event"):
            evt = reward_info["random_event"]
            print(f"    {c('🎲 随机事件:', C.BYELLOW)} {evt.get('name', '神秘')}")
            if evt.get("exp_mult", 1) != 1:
                print(f"      {c('经验 x'+str(evt['exp_mult']), C.BGREEN)}")

        # 首次奖励
        if reward_info.get("first_rewards"):
            for fr in reward_info["first_rewards"]:
                # fr 是 (reward_key, reward_data) 元组
                reward_key, reward_data = fr
                icon_map = {"first_game": "🎮", "first_boss": "🐉", "first_perfect": "✨",
                           "first_ghost": "👻", "first_daily": "📅", "first_combo": "🔥",
                           "first_classic": "🎮", "first_word": "📝", "first_timed": "⏱️",
                           "first_sprint": "⚡", "first_blind": "🙈", "first_gauntlet": "⚔️",
                           "first_speed_100": "🚀"}
                ri = icon_map.get(reward_key, "⭐")
                print(f"    {ri} {c(reward_data.get('desc', '首次'), C.BMAGENTA)} {c('+'+str(reward_data.get('exp', 0))+'XP', C.BGREEN)}")

        # 挑战奖励
        if reward_info.get("challenge_rewards"):
            for cr in reward_info["challenge_rewards"]:
                print(f"    🏅 {c(cr.get('name', '挑战'), C.BYELLOW)} {c('+'+str(cr.get('exp', 0))+'XP', C.BGREEN)}")

        # 连胜奖励
        if reward_info.get("streak_bonus", 0) > 0:
            print(f"    🔥 {c('连胜奖励', C.BRED)} {c('+'+str(reward_info['streak_bonus'])+'XP', C.BGREEN)}")

        # 总计
        total = reward_info.get("total_exp", exp_gain)
        base = reward_info.get("base_exp", exp_gain)
        if total != base:
            print(f"    {c('基础经验:', C.BBLACK)} {base} → {c('总计: '+str(total), C.BGREEN, C.BOLD)}")

    if daily_tasks:
        print(separator("─", 56, C.BBLACK))
        print(c("  📋 每日任务完成！", C.BYELLOW))
        for task in daily_tasks:
            print(f"    ✅ {task['desc']}  {c('+'+str(task['reward'])+'XP', C.BGREEN)}")

    if new_ach:
        print(separator("─", 56, C.BBLACK))
        print(c("  🏆 成就解锁！", C.BYELLOW, C.BOLD))
        for a in new_ach:
            # 成就解锁动画
            Celebrations.achievement_unlock(ACHIEVEMENTS[a]['name'], ACHIEVEMENTS[a]['icon'])
            print(f"    {ACHIEVEMENTS[a]['icon']} {c(ACHIEVEMENTS[a]['name'], C.BMAGENTA, C.BOLD)}"
                  f"  {c(ACHIEVEMENTS[a]['desc'], C.BBLACK)}")

    # 新纪录庆祝
    if is_new_record:
        Celebrations.new_record("净WPM", net_wpm)

    print(separator("═", 56, DarkTheme.GOLD_YELLOW))
    input(c("\n按 Enter 继续...", C.BBLACK))


def show_session_summary(stats):
    """显示会话总结"""
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


# ==================== 难度/词库选择 ====================

def choose_difficulty():
    """选择难度"""
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
    """选择词库"""
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
    """添加自定义词组"""
    clear_screen()
    print(separator())
    print(c("  添加自定义词组", C.BCYAN, C.BOLD))
    print(separator())
    word = input("输入词组（回车结束）: ").strip()
    if word:
        save_custom_word(word)
        print(c("  添加成功！", C.BGREEN))
    input(c("\n按 Enter 返回...", C.BBLACK))


# ==================== 游戏模式 ====================

def play_classic():
    """经典模式"""
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

    char_errors = stats.get("char_errors", {})
    prev_best  = stats.get("mode_bests", {}).get("classic", {}).get("net_wpm", 0)

    if cfg.get("use_realtime", True):
        user_input, elapsed = realtime_type(target, mode_label="经典", char_errors=char_errors, best_wpm=prev_best)
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
    ghost_beat = raw_net_wpm > prev_best and prev_best > 0

    rt_max_combo = getattr(realtime_type, 'max_combo', 0)
    rt_is_perfect = getattr(realtime_type, 'is_perfect', False)

    res = finish_game(stats, "classic", raw_wpm, raw_net_wpm, raw_acc, exp_base,
                      target, user_input, elapsed, difficulty=difficulty,
                      ghost_beat=ghost_beat,
                      realtime_max_combo=rt_max_combo, realtime_is_perfect=rt_is_perfect)
    new_ach, daily_done, old_lv, new_lv, exp_gain, combo, wpm, net_wpm, accuracy, reward_info = res

    rating, text, rating_col, icon = get_rating(net_wpm, accuracy)
    show_result(target, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_lv, new_lv, new_ach, daily_done, combo,
                mode="classic", prev_best_net=prev_best, ghost_beat=ghost_beat,
                reward_info=reward_info)


def play_sprint():
    """极速挑战"""
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

    new_ach, daily_done, old_lv, new_lv, exp_gain, _, wpm, net_wpm, _, reward_info = finish_game(
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
    """盲打模式"""
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
    res = finish_game(stats, "blind", raw_wpm, raw_net_wpm, raw_acc, exp_base,
                      target, user_input, elapsed, difficulty="")
    new_ach, daily_done, old_lv, new_lv, exp_gain, combo, wpm, net_wpm, accuracy, reward_info = res

    rating, text, rating_col, icon = get_rating(net_wpm, accuracy)
    show_result(target, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_lv, new_lv, new_ach, daily_done, combo,
                reward_info=reward_info)


def play_word_practice():
    """词库练习"""
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

    char_errors = stats.get("char_errors", {})
    prev_best  = stats.get("mode_bests", {}).get("word", {}).get("net_wpm", 0)

    if cfg.get("use_realtime", True):
        user_input, elapsed = realtime_type(words, mode_label="词库", char_errors=char_errors, best_wpm=prev_best)
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
    rt_max_combo = getattr(realtime_type, 'max_combo', 0)
    rt_is_perfect = getattr(realtime_type, 'is_perfect', False)

    res = finish_game(stats, "word", raw_wpm, raw_net_wpm, raw_acc, exp_base,
                      words, user_input, elapsed, difficulty="",
                      realtime_max_combo=rt_max_combo, realtime_is_perfect=rt_is_perfect)
    new_ach, daily_done, old_lv, new_lv, exp_gain, combo, wpm, net_wpm, accuracy, reward_info = res

    rating, text, rating_col, icon = get_rating(net_wpm, accuracy)
    show_result(words, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_lv, new_lv, new_ach, daily_done, combo,
                reward_info=reward_info)


def play_timed():
    """计时挑战"""
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

    new_ach, daily_done, old_lv, new_lv, exp_gain, _, wpm, _, _, reward_info = finish_game(
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
    """渐进挑战（带暂停和存档点）"""
    clear_screen()
    print(separator())
    print(c("  ⚔️  渐进挑战模式", C.BMAGENTA, C.BOLD))
    print(separator("─"))
    print("  共 9 关，难度逐步提升，限时递减。全通方算胜利。")
    print(c("  新增：按 P 暂停，每 3 关一个存档点！", C.BGREEN))
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
    checkpoints = [0, 3, 6]  # 存档点

    for no, (diff, limit) in enumerate(stages, 1):
        target   = random.choice(TEXTS[diff])
        diff_c   = {"easy": C.BGREEN, "medium": C.BYELLOW, "hard": C.BRED}[diff]
        diff_lbl = {"easy":"简单","medium":"中等","hard":"困难"}[diff]

        # 存档点提示
        checkpoint_hint = ""
        if no - 1 in checkpoints and no > 1:
            checkpoint_hint = c(f"  ✓ 存档点已保存", C.BGREEN)

        clear_screen()
        print(separator())
        print(c(f"  ⚔️  第 {no}/9 关  {c(diff_lbl, diff_c)}  限时 {limit} 秒", C.BMAGENTA, C.BOLD))
        if checkpoint_hint:
            print(checkpoint_hint)
        print(separator("─"))
        print()
        input(c(f" 按 Enter 开始第 {no} 关...", C.BBLACK))

        char_errors = stats.get("char_errors", {})

        if cfg.get("use_realtime", True):
            user_input, elapsed = realtime_type(target, mode_label=f"渐进第{no}关 P=暂停",
                                                allow_pause=True, char_errors=char_errors)
        else:
            print(f" {c('目标', C.BBLACK)}: {c(target, C.BWHITE, C.BOLD)}\n")
            start      = time.time()
            user_input = input(c(" >>> ", C.BCYAN))
            elapsed    = time.time() - start

        if user_input is None:
            print(c("  已放弃当关！", C.BRED))
            alive = False
            time.sleep(1)
            break

        if elapsed > limit:
            print(c(f"  ❌ 超时！{elapsed:.1f}s > {limit}s", C.BRED))
            alive = False
            time.sleep(1.5)
            break

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

    new_ach, daily_done, old_lv, new_lv, exp_gain, _, _, _, _, reward_info = finish_game(
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
    """弱键练习"""
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
        user_input, elapsed = realtime_type(target, mode_label="弱键", char_errors=char_errors)
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
    rt_max_combo = getattr(realtime_type, 'max_combo', 0)
    rt_is_perfect = getattr(realtime_type, 'is_perfect', False)

    res = finish_game(stats, "weak", raw_wpm, raw_net_wpm, raw_acc, exp_base,
                      target, user_input, elapsed, difficulty="",
                      realtime_max_combo=rt_max_combo, realtime_is_perfect=rt_is_perfect)
    new_ach, daily_done, old_lv, new_lv, exp_gain, combo, wpm, net_wpm, accuracy, reward_info = res

    rating, text, rating_col, icon = get_rating(net_wpm, accuracy)
    show_result(target, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_lv, new_lv, new_ach, daily_done, combo,
                reward_info=reward_info)


def play_daily_challenge():
    """每日一挑"""
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

    char_errors = stats.get("char_errors", {})
    prev_best  = stats.get("mode_bests", {}).get("daily", {}).get("net_wpm", 0)

    if cfg.get("use_realtime", True):
        user_input, elapsed = realtime_type(target, mode_label="每日一挑",
                                            char_errors=char_errors, best_wpm=prev_best)
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

    rt_max_combo = getattr(realtime_type, 'max_combo', 0)
    rt_is_perfect = getattr(realtime_type, 'is_perfect', False)

    res = finish_game(stats, "daily", raw_wpm, raw_net_wpm, raw_acc, exp_base,
                      target, user_input, elapsed, difficulty="", is_daily_ch=is_dc,
                      realtime_max_combo=rt_max_combo, realtime_is_perfect=rt_is_perfect)
    new_ach, daily_done, old_lv, new_lv, exp_gain, combo, wpm, net_wpm, accuracy, reward_info = res

    rating, text, rating_col, icon = get_rating(net_wpm, accuracy)
    show_result(target, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_lv, new_lv, new_ach, daily_done, combo, mode="daily",
                reward_info=reward_info)


def play_ghost_race():
    """幽灵竞速（增强版）"""
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
    print(c("  实时进度对比，击败幽灵获得 1.5x 经验！", C.BGREEN))
    print(separator("─"))
    print()

    char_errors = stats.get("char_errors", {})

    if cfg.get("use_realtime", True):
        user_input, elapsed = realtime_type(target, mode_label="幽灵竞速",
                                            ghost_wpm=ghost_wpm, char_errors=char_errors,
                                            best_wpm=ghost_wpm)
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

    rt_max_combo = getattr(realtime_type, 'max_combo', 0)
    rt_is_perfect = getattr(realtime_type, 'is_perfect', False)

    res = finish_game(stats, "classic", raw_wpm, raw_net_wpm, raw_acc, exp_base,
                      target, user_input, elapsed, difficulty=difficulty,
                      ghost_beat=ghost_beat,
                      realtime_max_combo=rt_max_combo, realtime_is_perfect=rt_is_perfect)
    new_ach, daily_done, old_lv, new_lv, exp_gain, combo, wpm, net_wpm, accuracy, reward_info = res

    rating, text, rating_col, icon = get_rating(net_wpm, accuracy)
    show_result(target, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_lv, new_lv, new_ach, daily_done, combo,
                mode="classic", prev_best_net=ghost_wpm, ghost_beat=ghost_beat,
                reward_info=reward_info)


def play_paragraph():
    """段落挑战（带暂停）"""
    stats  = load_stats()
    cfg    = load_config()
    target = random.choice(TEXTS["paragraph"])

    clear_screen()
    print(separator())
    print(c("  📖 段落挑战  完整段落输入", C.BCYAN, C.BOLD))
    print(c("  更长文本，考验持久正确率与耐力", C.BBLACK))
    print(c("  按 P 可暂停！", C.BGREEN))
    print(separator("─"))
    print()

    char_errors = stats.get("char_errors", {})
    prev_best  = stats.get("mode_bests", {}).get("paragraph", {}).get("net_wpm", 0)

    if cfg.get("use_realtime", True):
        user_input, elapsed = realtime_type(target, mode_label="段落 P=暂停",
                                            allow_pause=True, char_errors=char_errors,
                                            best_wpm=prev_best)
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

    rt_max_combo = getattr(realtime_type, 'max_combo', 0)
    rt_is_perfect = getattr(realtime_type, 'is_perfect', False)

    res = finish_game(stats, "paragraph", raw_wpm, raw_net_wpm, raw_acc, exp_base,
                      target, user_input, elapsed, difficulty="hard", is_para=True,
                      realtime_max_combo=rt_max_combo, realtime_is_perfect=rt_is_perfect)
    new_ach, daily_done, old_lv, new_lv, exp_gain, combo, wpm, net_wpm, accuracy, reward_info = res

    rating, text, rating_col, icon = get_rating(net_wpm, accuracy)
    show_result(target, user_input, elapsed, wpm, net_wpm, accuracy,
                rating, rating_col, text, icon, exp_gain,
                old_lv, new_lv, new_ach, daily_done, combo,
                reward_info=reward_info)


# ==================== Boss关卡模式 ====================

def play_boss_stage():
    """Boss关卡模式主入口"""
    stats = load_stats()
    stage_manager = StageManager(stats)
    vocab = VocabularyManager()

    while True:
        clear_screen()

        # 显示关卡选择界面
        print(stage_manager.get_stage_list_display(width=60))
        print()
        print(f"  {c('1', DarkTheme.GOLD_YELLOW)}. 开始当前关卡")
        print(f"  {c('2', DarkTheme.GOLD_YELLOW)}. 选择关卡")
        print(f"  {c('3', DarkTheme.GOLD_YELLOW)}. 查看Boss列表")
        print(f"  {c('0', C.BRED)}. 返回主菜单")
        print()

        choice = input(c("选择: ", DarkTheme.SOUL_BLUE)).strip()

        if choice == "0":
            save_stats(stats)
            break
        elif choice == "1":
            stage_num = stage_manager.stage_progress["unlocked"]
            play_single_stage(stats, stage_manager, vocab, stage_num)
        elif choice == "2":
            try:
                stage_input = input(c("输入关卡号: ", DarkTheme.SOUL_BLUE)).strip()
                stage_num = int(stage_input)
                if 1 <= stage_num <= 30:
                    if stage_num <= stage_manager.stage_progress["unlocked"]:
                        play_single_stage(stats, stage_manager, vocab, stage_num)
                    else:
                        print(c("  该关卡尚未解锁!", DarkTheme.BLOOD_RED))
                        time.sleep(1)
                else:
                    print(c("  无效关卡号!", DarkTheme.BLOOD_RED))
                    time.sleep(1)
            except ValueError:
                print(c("  请输入数字!", DarkTheme.BLOOD_RED))
                time.sleep(1)
        elif choice == "3":
            show_boss_list()


def play_single_stage(stats, stage_manager, vocab, stage_num):
    """游玩单个关卡"""
    stage_type = stage_manager.get_stage_type(stage_num)

    if stage_type == "boss":
        play_boss_battle(stats, stage_manager, vocab, stage_num)
    elif stage_type == "quiz":
        result = play_quiz_level(vocab, quiz_type="mixed", level="medium", question_count=5)
        if result.get("success"):
            stage_manager.complete_stage(stage_num, 0, result.get("exp", 0))
            stats["exp"] = stats.get("exp", 0) + result.get("exp", 0)
            save_stats(stats)
    else:
        play_normal_stage(stats, stage_manager, vocab, stage_num)


def play_normal_stage(stats, stage_manager, vocab, stage_num):
    """普通小怪关卡"""
    clear_screen()
    print(separator("═", 50, DarkTheme.FIRE_ORANGE))
    print(c(f"  ⚔️ 第 {stage_num} 关 - 小怪战", DarkTheme.FIRE_ORANGE, C.BOLD))
    print(separator("─", 50, C.BBLACK))
    print(c("  击败所有小怪通过关卡!", C.BWHITE))
    print(separator("═", 50, DarkTheme.FIRE_ORANGE))
    input(c("\n  按 Enter 开始...", C.BBLACK))

    vocab_level = stage_manager.get_vocab_level(stage_num)
    battle_words = vocab.get_battle_words(vocab_level, count=5)

    player = Player(max_hp=100, base_attack=10 + stats.get("level", 1))
    monsters_defeated = 0
    total_damage_taken = 0
    start_time = time.time()

    for i, word_data in enumerate(battle_words):
        if not player.is_alive:
            break

        monster_hp = 30 + stage_num * 5
        monster_attack = 5 + stage_num

        clear_screen()
        print(separator("═", 50, C.BBLACK))
        print(c(f"  👹 小怪 {i+1}/5", DarkTheme.BLOOD_RED, C.BOLD))
        monster_bar, _ = hp_bar(monster_hp, monster_hp, 20)
        print(f"  HP: {monster_bar}")
        print(separator("─", 50, C.BBLACK))

        player_bar, player_hp_text = hp_bar(player.hp, player.max_hp, 20)
        print(f"  {c('🧙 玩家', DarkTheme.SOUL_BLUE)} HP: {player_bar} {player_hp_text}")
        print(separator("═", 50, C.BBLACK))

        print(c(f"\n  🎯 攻击词汇: {word_data['word']}", DarkTheme.GOLD_YELLOW, C.BOLD))
        print(c(f"     {word_data['meaning']}", C.BBLACK))

        try:
            user_input = input(c("\n  输入: ", DarkTheme.SOUL_BLUE)).strip()

            if user_input.lower() == word_data['word'].lower():
                attack_flash()
                monsters_defeated += 1
                print(c("  ✅ 击败!", DarkTheme.POISON_GREEN, C.BOLD))
            else:
                damage, _ = player.take_damage(monster_attack)
                total_damage_taken += damage
                print(c(f"  ❌ 错误! 受到 {damage} 伤害!", DarkTheme.BLOOD_RED, C.BOLD))

            time.sleep(0.8)

        except KeyboardInterrupt:
            break

    elapsed = time.time() - start_time

    clear_screen()
    print(separator("═", 50, DarkTheme.GOLD_YELLOW))

    if player.is_alive and monsters_defeated >= 5:
        print(c("  🎉 关卡通过!", DarkTheme.GOLD_YELLOW, C.BOLD))
        exp_base = 20 + stage_num * 3 + monsters_defeated * 5
        stage_manager.complete_stage(stage_num, elapsed, exp_base)
        stats["exp"] = stats.get("exp", 0) + exp_base
        print(f"  ⭐ 经验: {c('+'+str(exp_base)+'XP', DarkTheme.POISON_GREEN, C.BOLD)}")
    else:
        print(c("  💀 关卡失败...", DarkTheme.BLOOD_RED, C.BOLD))

    print(f"  📊 击败: {monsters_defeated}/5  用时: {elapsed:.1f}秒")
    print(separator("═", 50, DarkTheme.GOLD_YELLOW))

    save_stats(stats)
    input(c("\n按 Enter 继续...", C.BBLACK))


def play_boss_battle(stats, stage_manager, vocab, stage_num):
    """Boss战斗"""
    boss_data = stage_manager.get_boss_for_stage(stage_num)
    if not boss_data:
        print(c("  Boss数据错误!", DarkTheme.BLOOD_RED))
        time.sleep(1)
        return

    multiplier = stage_manager.get_level_multiplier(stage_num)
    boss = Boss(boss_data, multiplier)
    player = Player(max_hp=100, base_attack=10 + stats.get("level", 1) * 2)

    show_battle_intro(boss)
    battle = BattleSystem(player, boss)

    start_time = time.time()

    while battle.is_active:
        dot_damage, effects = battle.process_turn_start()

        clear_screen()
        print(battle.get_display())

        if effects:
            print(c(f"  状态效果: {', '.join(effects)}", DarkTheme.GOLD_YELLOW))

        if player.frozen or player.stunned:
            print(c("  你无法行动!", DarkTheme.ICE_CYAN))
            time.sleep(1)
        else:
            vocab_level = stage_manager.get_vocab_level(stage_num)
            word_data = vocab.get_battle_words(vocab_level, count=1)[0]

            print()
            print(c(f"  🎯 攻击词汇: {word_data['word']}", DarkTheme.GOLD_YELLOW, C.BOLD))
            print(c(f"     {word_data['meaning']}", C.BBLACK))
            print()
            print(c("  💡 输入单词攻击 | 输入技能编号(1-5)使用技能 | ESC退出", C.BBLACK))
            print(show_skill_menu(player))

            try:
                user_input = input(c("\n  >>> ", DarkTheme.SOUL_BLUE)).strip()

                if user_input == "\x1b":
                    print(c("  退出战斗...", DarkTheme.BLOOD_RED))
                    time.sleep(1)
                    return

                if user_input.isdigit():
                    skill_index = int(user_input)
                    skill_names = list(PLAYER_SKILLS.keys())
                    if 1 <= skill_index <= len(skill_names):
                        skill_name = skill_names[skill_index - 1]
                        success, message = player.use_skill(skill_name)

                        if success:
                            if message == "freeze":
                                boss.frozen = True
                                print(c(f"  ❄️ {boss.name} 被冰冻了!", DarkTheme.ICE_CYAN, C.BOLD))
                            else:
                                print(c(f"  ✅ {message}", DarkTheme.POISON_GREEN))

                            if skill_name == "HEAL":
                                heal_effect()
                            elif skill_name == "SHIELD":
                                shield_effect()
                        else:
                            print(c(f"  ❌ {message}", DarkTheme.BLOOD_RED))
                        time.sleep(0.8)
                        # 技能使用后继续玩家回合
                        continue

                if user_input.lower() == word_data['word'].lower():
                    # 单词拼写正确，进入释义选择环节
                    print(c("  ✓ 拼写正确!", DarkTheme.POISON_GREEN))
                    time.sleep(0.3)

                    # 生成释义选择题
                    meaning_options = vocab.get_meaning_options(word_data['meaning'], word_data['word'])
                    if meaning_options and len(meaning_options) >= 2:
                        # 找到正确答案的索引
                        correct_index = chr(65 + meaning_options.index(word_data['meaning']))

                        print()
                        print(c("  📖 选择正确的中文释义:", DarkTheme.GOLD_YELLOW, C.BOLD))
                        print()
                        for i, opt in enumerate(meaning_options):
                            label = chr(65 + i)  # A, B, C, D
                            print(f"    {c(f'[{label}]', DarkTheme.GOLD_YELLOW)} {opt}")
                        print(f"    {c('[E]', DarkTheme.GOLD_YELLOW)} 不知道")
                        print()

                        meaning_choice = input(c("  选择: ", DarkTheme.SOUL_BLUE)).strip().upper()

                        if meaning_choice == correct_index:
                            # 释义选择正确，造成全额伤害
                            damage = player.attack
                            if player.critical_next:
                                damage *= 2
                                player.critical_next = False

                            actual_damage, blocked = boss.take_damage(damage)

                            if blocked:
                                print(c(f"  ⚔️ 攻击被护盾抵消!", C.BBLACK))
                            else:
                                attack_flash()
                                print(c(f"  ⚔️ 攻击命中! 造成 {actual_damage} 伤害!", DarkTheme.FIRE_ORANGE, C.BOLD))
                        elif meaning_choice == "E":
                            # 选择"不知道"，伤害减半
                            damage = player.attack // 2
                            if player.critical_next:
                                damage *= 2
                                player.critical_next = False

                            actual_damage, blocked = boss.take_damage(damage)
                            print(c(f"  📖 正确答案: {word_data['meaning']}", C.BCYAN))
                            print(c(f"  ⚔️ 攻击命中! 造成 {actual_damage} 伤害（减半）!", C.BYELLOW))
                        else:
                            # 释义选择错误，伤害减半
                            damage = player.attack // 2
                            if player.critical_next:
                                damage *= 2
                                player.critical_next = False

                            actual_damage, blocked = boss.take_damage(damage)
                            print(c(f"  ❌ 释义错误! 正确答案: {word_data['meaning']}", DarkTheme.BLOOD_RED))
                            print(c(f"  ⚔️ 攻击命中! 造成 {actual_damage} 伤害（减半）!", C.BYELLOW))
                    else:
                        # 无法生成选项，直接攻击
                        damage = player.attack
                        if player.critical_next:
                            damage *= 2
                            player.critical_next = False

                        actual_damage, blocked = boss.take_damage(damage)

                        if blocked:
                            print(c(f"  ⚔️ 攻击被护盾抵消!", C.BBLACK))
                        else:
                            attack_flash()
                            print(c(f"  ⚔️ 造成 {actual_damage} 伤害!", DarkTheme.FIRE_ORANGE, C.BOLD))
                else:
                    print(c("  ❌ 输入错误!", DarkTheme.BLOOD_RED))

                time.sleep(0.5)

            except KeyboardInterrupt:
                break

        ended, result = battle.check_battle_end()
        if ended:
            break

        # Boss回合（即使被冰冻也要进入，让boss_turn处理状态）
        if boss.is_alive:
            print()
            print(c("  ═══ Boss回合 ═══", DarkTheme.BLOOD_RED, C.BOLD))

            boss_result = battle.boss_turn()

            # 检查是否被冰冻
            if boss_result.get("skill") == "冰冻中":
                print(c(f"  ❄️ {boss_result['message']}", DarkTheme.ICE_CYAN, C.BOLD))
            elif boss_result.get("effect") == "blind":
                print(c("  🌑 Boss发动[盲眼攻击]!", DarkTheme.SHADOW_PURPLE, C.BOLD))
                success, _, _ = boss_cloze_challenge(vocab, difficulty=stage_num // 10 + 1)
                if success == "skip":
                    # 跳过，伤害减半
                    half_damage = boss_result["damage"] // 2
                    if half_damage > 0:
                        damage, _ = player.take_damage(half_damage)
                        print(c(f"  💔 跳过惩罚：受到 {damage} 伤害（减半）!", C.BYELLOW))
                elif not success:
                    damage, _ = player.take_damage(boss_result["damage"])
                    print(c(f"  💔 受到 {damage} 伤害!", DarkTheme.BLOOD_RED))
            else:
                # 显示Boss技能效果
                skill_name = boss_result.get("skill", "攻击")
                damage = boss_result.get("damage", 0)
                effect = boss_result.get("effect")
                blocked = boss_result.get("blocked", False)

                if blocked:
                    print(c(f"  🛡️ {boss.name} 的攻击被护盾抵消!", DarkTheme.SOUL_BLUE))
                else:
                    print(c(f"  ⚔️ {boss.name} 使用 [{skill_name}]!", DarkTheme.FIRE_ORANGE, C.BOLD))

                    if damage > 0:
                        print(c(f"  💔 受到 {damage} 伤害!", DarkTheme.BLOOD_RED))

                    # 显示特殊效果
                    if effect == "poison":
                        print(c("  🧪 你中毒了! (每回合扣血)", DarkTheme.POISON_GREEN))
                    elif effect == "burn":
                        print(c("  🔥 你被灼烧了!", DarkTheme.FIRE_ORANGE))
                    elif effect == "freeze_player":
                        print(c("  ❄️ 你被冰冻了!", DarkTheme.ICE_CYAN))
                    elif effect == "stun":
                        print(c("  💫 你被眩晕了!", DarkTheme.GOLD_YELLOW))
                    elif effect == "fear":
                        print(c("  😱 你感到恐惧! (攻击力降低)", DarkTheme.SHADOW_PURPLE))

                    if not blocked:
                        attack_flash()

            time.sleep(1)

            time.sleep(1)

        ended, result = battle.check_battle_end()
        if ended:
            break

    elapsed = time.time() - start_time

    if battle.victory:
        celebrate_boss_defeat(boss.name)
        exp_base = 50 + stage_num * 10 + int(elapsed // 10)
        stage_manager.complete_stage(stage_num, elapsed, exp_base)
        stats["exp"] = stats.get("exp", 0) + exp_base
        save_boss_progress(stats, stage_num, True, elapsed, exp_base)
        show_battle_result(True, boss, exp_base, elapsed)
    else:
        save_boss_progress(stats, stage_num, False, elapsed, 0)
        show_battle_result(False, boss, 0, elapsed)

    save_stats(stats)


def show_boss_list():
    """显示Boss列表"""
    clear_screen()
    print(separator("═", 50, DarkTheme.BLOOD_RED))
    print(c("  👹 Boss图鉴", DarkTheme.BLOOD_RED, C.BOLD))
    print(separator("─", 50, C.BBLACK))

    stats = load_stats()
    boss_progress = stats.get("boss_progress", {})

    for stage, boss_data in BOSSES.items():
        key = get_boss_save_key(stage)
        progress = boss_progress.get(key, {})
        victories = progress.get("victories", 0)
        best_time = progress.get("best_time")

        if victories > 0:
            time_str = f"{best_time:.1f}s" if best_time else "-"
            status = c(f"✓ 击败{victories}次 最佳:{time_str}", DarkTheme.POISON_GREEN)
        else:
            status = c("🔒 未解锁", C.BBLACK)

        print(f"  {boss_data['icon']} {c(boss_data['name'], DarkTheme.FIRE_ORANGE, C.BOLD)}")
        print(f"     {c(boss_data['description'], C.BBLACK)}")
        print(f"     {status}")
        print()

    print(separator("═", 50, DarkTheme.BLOOD_RED))
    input(c("\n按 Enter 返回...", C.BBLACK))
