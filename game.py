"""
MOTIP - Master Of Typing Interactivity Practice
打字速度测试游戏 v7.0 - 模块化重构版

新增功能:
  - 幽灵模式可视化进度条对比
  - 段落挑战和渐进挑战支持暂停（按P）
  - 错误热区预警
  - 目标提示系统
  - 代码模块化重构
"""

from ui import c, C, DarkTheme, bar_fg, exp_bar, separator, wpm_color, acc_color, clear_screen, get_rpg_title, ascii_wpm_chart
from data import (
    ACHIEVEMENTS, SKILLS, DAILY_TASKS,
    load_stats, save_stats, load_config, save_config, get_level, check_daily_reset
)
from modes import (
    play_classic, play_sprint, play_blind, play_word_practice, play_timed,
    play_gauntlet, play_weak_key, play_daily_challenge, play_ghost_race, play_paragraph,
    show_session_summary, add_custom_word, choose_wordbank, play_boss_stage
)


# ==================== 菜单显示 ====================

def show_menu(stats):
    """显示主菜单"""
    check_daily_reset(stats)
    save_stats(stats)

    level, cur_exp, need_exp = get_level(stats.get("exp", 0))
    bar = exp_bar(cur_exp, need_exp)

    daily       = stats.get("daily", {})
    tasks_done  = sum(1 for t in DAILY_TASKS if daily.get("tasks", {}).get(t["id"]))
    tasks_total = len(DAILY_TASKS)

    print(separator("═"))
    print(c("  __  __  ___  ___   _   _    ___ ___ ", C.BCYAN, C.BOLD))
    print(c(" |  \\/  |/ _ \\|  _ \\| | | |  / __|_ _|", C.CYAN))
    print(c(" | |\\/| | | | | |_) | |_| | | (_ || |  v7.0", C.BCYAN))
    print(c(" |_|  |_|_| |_|  __/ \\___/   \\___|___|", C.CYAN))
    print(c("              |_|   打字速度测试  旗舰版", C.BBLACK))
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
    print(f"  {c('11', C.BMAGENTA)} 🏰Boss关卡 ⭐NEW", C.BMAGENTA)
    print(separator("─"))
    print(f"  {c('s', C.BCYAN)} 数据统计   {c('k', C.BCYAN)} 技能系统   {c('a', C.BCYAN)} 成就列表")
    print(f"  {c('c', C.BCYAN)} 设置       {c('h', C.BCYAN)} 帮助说明   {c('0', C.BRED)} 退出")
    print(separator("═"))
    ach_count = len(stats.get("achievements", []))
    print(f"  成就 {c(str(ach_count)+'/'+str(len(ACHIEVEMENTS)), C.BGREEN)}"
          f"  累计字符 {c('{:,}'.format(stats.get('total_chars',0)), C.BBLACK)}")


# ==================== 统计与系统界面 ====================

def show_stats():
    """显示统计数据"""
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
    from collections import Counter
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

    # 错误热力图
    print(separator("─"))
    from input_system import get_error_tracker
    tracker = get_error_tracker()
    summary = tracker.get_summary()

    if summary.get("total_errors", 0) > 0:
        print(c("  🔥 本局错误分析", DarkTheme.BLOOD_RED, C.BOLD))
        print(f"  总错误: {c(str(summary['total_errors']), DarkTheme.BLOOD_RED)}  "
              f"已改正: {c(str(summary['corrected_errors'])+'('+str(int(summary['correction_rate']))+'%)', DarkTheme.POISON_GREEN)}  "
              f"退格: {c(str(summary['backspaces']), C.BBLACK)}")

        # 错误类型分布
        dist = summary.get("type_distribution", {})
        if dist:
            wrong_pct = int(dist.get("wrong", 0) * 100)
            extra_pct = int(dist.get("extra", 0) * 100)
            miss_pct = int(dist.get("miss", 0) * 100)
            print(f"  错误类型: 打错 {wrong_pct}% | 多打 {extra_pct}% | 少打 {miss_pct}%")

        # 练习建议
        suggestions = tracker.generate_practice_suggestions()
        if suggestions:
            print(c("  💡 针对性建议:", DarkTheme.SOUL_BLUE))
            for sug in suggestions[:3]:
                print(f"     {sug}")

    print(separator("═"))
    show_session_summary(stats)
    input(c("\n按 Enter 返回...", C.BBLACK))


def show_achievements():
    """显示成就列表"""
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
    """显示技能系统"""
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
                           full_char="=", empty_char="-",
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
            import time
            time.sleep(1)


def show_settings():
    """显示设置"""
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
            from data import load_custom_words
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
            import time
            time.sleep(1)


def show_help():
    """显示帮助"""
    clear_screen()
    print(separator("═"))
    print(c("  📖 游戏说明  v7.0", C.BCYAN, C.BOLD))
    print(separator("─"))
    for mode, desc in [
        ("经典模式",   "输入目标句子，实时高亮反馈，测速与测准"),
        ("极速挑战",   "时限内尽量多打，只计正确字符"),
        ("词库练习",   "tech/code/quote/science/文学/随机/中文/自定义"),
        ("计时挑战",   "自选 30/60/120 秒，完成尽量多"),
        ("盲打模式",   "记忆后隐藏，凭记忆完成（使用传统输入）"),
        ("渐进挑战",   "9 关由易到难，限时递减，全通胜利。支持暂停(P)"),
        ("弱键练习",   "自动分析错误，生成针对性训练"),
        ("每日一挑",   "每天同一题，首次完成奖励 x1.5，连续打卡有成就"),
        ("幽灵竞速",   "对抗你的历史最佳净 WPM，实时进度对比！击败自己获 1.5x 经验"),
        ("段落挑战",   "更长段落文本，考验持久耐力，基础经验更高。支持暂停(P)"),
    ]:
        print(f"  {c('【'+mode+'】', C.BYELLOW, C.BOLD)} {desc}")
    print(separator("─"))
    for sys_name, desc in [
        ("净 WPM",    "正确字符/5 - 错误字符/5，比毛 WPM 更真实公正"),
        ("实时反馈",  "绿=正确，红=错误，暗=未输入，青底=当前光标"),
        ("幽灵进度",  "【新增】并排显示玩家与幽灵的进度条，实时对比"),
        ("暂停功能",  "【新增】段落/渐进挑战按 P 暂停，C继续 Q退出"),
        ("技能系统",  "消耗经验升级，增强游戏各方面属性"),
        ("连击系统",  "连续正确词组获得额外经验，每 5 连击 +5XP"),
        ("每日任务",  "每天刷新，完成 9 项任务，每日一挑额外 +100XP"),
        ("会话统计",  "退出时显示本次游玩局数、平均成绩"),
    ]:
        print(f"  {c('【'+sys_name+'】', C.BCYAN)} {desc}")
    print(separator("═"))
    input(c("\n按 Enter 返回...", C.BBLACK))


# ==================== 主程序 ====================

def main():
    import sys
    import io

    # 设置控制台编码为UTF-8
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    from ui import enable_ansi
    enable_ansi()

    funcs = {
        "1": play_classic,       "2": play_sprint,
        "3": play_word_practice, "4": play_timed,
        "5": play_blind,         "6": play_gauntlet,
        "7": play_weak_key,      "8": play_daily_challenge,
        "9": play_ghost_race,    "10": play_paragraph,
        "11": play_boss_stage,
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
            print(c("\n  感谢使用 MOTIP v7.0！再见！\n", C.BCYAN, C.BOLD))
            break
        elif choice in funcs:
            funcs[choice]()


if __name__ == "__main__":
    main()
