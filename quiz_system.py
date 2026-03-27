"""
选择题系统 - 英中互选、形态选择、完形填空
"""

import random
import time
from typing import List, Dict, Optional, Tuple

from ui import (
    c, C, DarkTheme, separator, draw_box, clear_screen,
    celebrate_perfect, attack_flash
)
from vocabulary import VocabularyManager, CLOZE_EXERCISES


# ==================== 选择题类型 ====================

QUIZ_TYPES = {
    "en_to_cn": {
        "name": "英译中",
        "icon": "🔤",
        "description": "看英文选中文释义"
    },
    "cn_to_en": {
        "name": "中译英",
        "icon": "🔠",
        "description": "看中文选英文单词"
    },
    "form": {
        "name": "形态选择",
        "icon": "📝",
        "description": "选择正确的单词形态"
    },
    "cloze": {
        "name": "完形填空",
        "icon": "✏️",
        "description": "根据语境填入正确单词"
    },
}


# ==================== 选择题界面 ====================

def show_quiz_question(question_data, question_num=1, total=5):
    """显示选择题界面"""
    clear_screen()

    quiz_type = question_data.get("type", "en_to_cn")
    type_info = QUIZ_TYPES.get(quiz_type, {})

    lines = []
    lines.append(separator("═", 55, DarkTheme.SOUL_BLUE))
    lines.append(c(f"  {type_info.get('icon', '❓')} {type_info.get('name', '选择题')}", DarkTheme.SOUL_BLUE, C.BOLD))
    lines.append(c(f"  第 {question_num}/{total} 题", C.BBLACK))
    lines.append(separator("─", 55, C.BBLACK))
    lines.append("")

    # 题目
    if quiz_type == "cloze":
        # 完形填空特殊显示
        lines.append(c("  请选择正确的单词填入空格:", C.BWHITE))
        lines.append("")
        lines.append(f"  {c(question_data['sentence'], C.BWHITE, C.BOLD)}")
    else:
        lines.append(c(f"  {question_data['question']}", DarkTheme.GOLD_YELLOW, C.BOLD))

    lines.append("")
    lines.append(separator("─", 55, C.BBLACK))
    lines.append("")

    # 选项
    options = question_data.get("options", [])
    for i, option in enumerate(options):
        label = chr(65 + i)  # A, B, C, D
        lines.append(f"    {c(f'[{label}]', DarkTheme.GOLD_YELLOW)} {option}")

    lines.append("")
    lines.append(separator("─", 55, C.BBLACK))
    lines.append(f"    {c('[E]', DarkTheme.GOLD_YELLOW)} 不知道（惩罚减半）")
    lines.append("")
    lines.append(separator("═", 55, DarkTheme.SOUL_BLUE))
    lines.append(c("  输入 A/B/C/D 选择答案，E 表示不知道", C.BBLACK))

    print("\n".join(lines))


def show_quiz_result(is_correct, question_data, user_answer, is_skip=False):
    """显示答题结果"""
    if is_correct:
        print(c("\n  ✅ 正确!", DarkTheme.POISON_GREEN, C.BOLD))
        if question_data.get("type") == "cloze":
            # 显示语法解析
            explanation = question_data.get("explanation", "")
            grammar = question_data.get("grammar_point", "")
            if explanation:
                print(c(f"  📚 {explanation}", C.BCYAN))
            if grammar:
                print(c(f"  📖 知识点: {grammar}", C.BBLACK))
        time.sleep(1)
    elif is_skip:
        # 进入学习模式
        _show_learning_mode(question_data)
    else:
        print(c("\n  ❌ 错误!", DarkTheme.BLOOD_RED, C.BOLD))
        correct = question_data.get("answer", "")
        print(c(f"  正确答案: {correct}", DarkTheme.POISON_GREEN))

        if question_data.get("type") == "cloze":
            explanation = question_data.get("explanation", "")
            grammar = question_data.get("grammar_point", "")
            if explanation:
                print(c(f"  📚 {explanation}", C.BCYAN))
            if grammar:
                print(c(f"  📖 知识点: {grammar}", C.BBLACK))
        time.sleep(1.5)


def _show_learning_mode(question_data):
    """跳过后的学习模式 - 让用户拼写单词"""
    quiz_type = question_data.get("type", "en_to_cn")

    # 获取要学习的单词
    if quiz_type == "cloze":
        word = question_data.get("word", "")
        meaning = question_data.get("answer", "")
        sentence = question_data.get("sentence", "")
    elif quiz_type == "en_to_cn":
        word = question_data.get("question", "")
        meaning = question_data.get("answer", "")
        sentence = None
    elif quiz_type == "cn_to_en":
        word = question_data.get("answer", "")
        meaning = question_data.get("question", "")
        sentence = None
    else:  # form
        # 形态选择题的答案格式是 "word  meaning"
        answer_display = question_data.get("answer", "")
        word = question_data.get("answer_word", answer_display.split()[0] if answer_display else "")
        meaning = question_data.get("base_meaning", question_data.get("question", ""))
        sentence = None

    if not word:
        time.sleep(1)
        return

    print()
    print(c("═" * 50, DarkTheme.SOUL_BLUE))
    print(c("  📖 学习模式", DarkTheme.SOUL_BLUE, C.BOLD))
    print(c("═" * 50, DarkTheme.SOUL_BLUE))

    # 显示题目回顾
    if quiz_type == "cloze":
        print(c(f"\n  原句: {sentence}", C.BWHITE))
        print(c(f"  填空: {word}", DarkTheme.GOLD_YELLOW, C.BOLD))
        print(c(f"  释义: {meaning}", C.BCYAN))
    elif quiz_type == "en_to_cn":
        print(c(f"\n  单词: {word}", DarkTheme.GOLD_YELLOW, C.BOLD))
        print(c(f"  释义: {meaning}", C.BCYAN))
    elif quiz_type == "cn_to_en":
        print(c(f"\n  释义: {meaning}", C.BWHITE))
        print(c(f"  单词: {word}", DarkTheme.GOLD_YELLOW, C.BOLD))
    else:
        print(c(f"\n  正确形式: {word}", DarkTheme.GOLD_YELLOW, C.BOLD))
        print(c(f"  释义: {meaning}", C.BCYAN))

    print(c("─" * 50, C.BBLACK))
    print(c("  💡 请拼写一遍加深记忆", C.BBLACK, C.ITALIC))
    print()

    # 让用户拼写
    attempts = 0
    while True:
        user_spell = input(c(f"  输入 [{word}]: ", DarkTheme.SOUL_BLUE)).strip()

        if user_spell.lower() == word.lower():
            print(c("  ✓ 拼写正确!", DarkTheme.POISON_GREEN, C.BOLD))
            break
        elif user_spell == "":
            # 直接回车，显示答案后继续
            print(c(f"  答案: {word}", C.BYELLOW))
            break
        else:
            attempts += 1
            if attempts >= 3:
                print(c(f"  答案: {word}", C.BYELLOW))
                print(c("  请再试一次...", C.BBLACK))
                user_spell = input(c(f"  输入 [{word}]: ", DarkTheme.SOUL_BLUE)).strip()
                if user_spell.lower() == word.lower():
                    print(c("  ✓ 拼写正确!", DarkTheme.POISON_GREEN, C.BOLD))
                break
            else:
                print(c(f"  ✗ 拼写错误，请重试 ({3-attempts}次机会)", DarkTheme.BLOOD_RED))

    print(c("═" * 50, DarkTheme.SOUL_BLUE))


def show_quiz_summary(correct_count, total_count, exp_gained, rewards=None, skip_count=0, wrong_count=0):
    """显示选择题总结"""
    clear_screen()

    accuracy = int(correct_count / total_count * 100) if total_count > 0 else 0

    lines = []
    lines.append(separator("═", 50, DarkTheme.SOUL_BLUE))
    lines.append(c("  📝 选择题挑战完成!", DarkTheme.SOUL_BLUE, C.BOLD))
    lines.append(separator("─", 50, C.BBLACK))

    # 正确率
    if accuracy >= 80:
        acc_color = DarkTheme.POISON_GREEN
        emoji = "🌟"
    elif accuracy >= 60:
        acc_color = DarkTheme.GOLD_YELLOW
        emoji = "👍"
    else:
        acc_color = DarkTheme.BLOOD_RED
        emoji = "💪"

    lines.append(f"  {emoji} 正确率: {c(f'{accuracy}%', acc_color, C.BOLD)}")
    lines.append(f"  ✓ 正确: {c(str(correct_count), DarkTheme.POISON_GREEN)} / {total_count}")
    if skip_count > 0:
        lines.append(f"  🤔 跳过: {c(str(skip_count), C.BYELLOW)} (惩罚减半)")
    if wrong_count > 0:
        lines.append(f"  ✗ 错误: {c(str(wrong_count), DarkTheme.BLOOD_RED)}")
    lines.append(f"  ⭐ 经验: {c(f'+{exp_gained}XP', DarkTheme.GOLD_YELLOW, C.BOLD)}")

    if rewards:
        lines.append(separator("─", 50, C.BBLACK))
        lines.append(c("  🎁 奖励:", DarkTheme.GOLD_YELLOW))
        for item, value in rewards.items():
            lines.append(f"    • {item}: {c(str(value), DarkTheme.POISON_GREEN)}")

    lines.append(separator("═", 50, DarkTheme.SOUL_BLUE))

    print("\n".join(lines))
    input(c("\n  按 Enter 继续...", C.BBLACK))


# ==================== 选择题游戏逻辑 ====================

class QuizGame:
    """选择题游戏类"""

    def __init__(self, vocabulary_manager=None):
        self.vocab = vocabulary_manager or VocabularyManager()
        self.questions = []
        self.current_index = 0
        self.correct_count = 0
        self.answers = []  # 记录每题的答案

    def generate_questions(self, quiz_type="mixed", level="medium", count=5):
        """生成选择题序列"""
        self.questions = []
        self.current_index = 0
        self.correct_count = 0
        self.answers = []

        if quiz_type == "mixed":
            # 混合题型
            types = ["en_to_cn", "cn_to_en", "form", "cloze"]
            type_distribution = [2, 2, 1, count - 5] if count > 5 else [2, 2, 1, 0]

            for i in range(count):
                # 根据位置选择题型
                if i < type_distribution[0]:
                    q_type = "en_to_cn"
                elif i < type_distribution[0] + type_distribution[1]:
                    q_type = "cn_to_en"
                elif i < type_distribution[0] + type_distribution[1] + type_distribution[2]:
                    q_type = "form"
                else:
                    q_type = "cloze"

                if q_type == "cloze":
                    question = self.vocab.get_cloze_question()
                else:
                    question = self.vocab.get_quiz_question(q_type, level)

                if question:
                    question["question_index"] = i
                    self.questions.append(question)
        else:
            # 单一题型
            for i in range(count):
                if quiz_type == "cloze":
                    question = self.vocab.get_cloze_question()
                else:
                    question = self.vocab.get_quiz_question(quiz_type, level)

                if question:
                    question["question_index"] = i
                    self.questions.append(question)

        return len(self.questions)

    def get_current_question(self):
        """获取当前题目"""
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    def answer_question(self, user_choice):
        """回答当前问题"""
        question = self.get_current_question()
        if not question:
            return None, False, False

        # 检查是否是"不知道"
        is_skip = False
        if isinstance(user_choice, str) and user_choice.upper() == "E":
            is_skip = True

        # 转换用户输入 (A->0, B->1, etc.)
        if isinstance(user_choice, str) and not is_skip:
            user_choice = ord(user_choice.upper()) - ord('A')

        # 检查答案
        options = question.get("options", [])
        if is_skip:
            user_answer = "(不知道)"
            is_correct = False
        elif 0 <= user_choice < len(options):
            user_answer = options[user_choice]
            is_correct = user_answer == question.get("answer")
        else:
            user_answer = ""
            is_correct = False

        # 记录答案
        self.answers.append({
            "question_index": self.current_index,
            "user_choice": user_choice,
            "user_answer": user_answer,
            "is_correct": is_correct,
            "is_skip": is_skip
        })

        if is_correct:
            self.correct_count += 1

        return question, is_correct, is_skip

    def next_question(self):
        """下一题"""
        self.current_index += 1
        return self.current_index < len(self.questions)

    def calculate_reward(self):
        """计算奖励"""
        total = len(self.questions)
        correct = self.correct_count

        # 统计跳过数量
        skip_count = sum(1 for a in self.answers if a.get("is_skip", False))
        wrong_count = total - correct - skip_count

        # 计算加权正确率（跳过惩罚是答错的一半）
        # 正确=1分, 跳过=0.5分（相对于答错的0分）
        weighted_score = correct + (skip_count * 0.5)
        weighted_accuracy = weighted_score / total if total > 0 else 0

        # 基础经验
        base_exp = 10 * total

        # 根据加权正确率计算经验
        if weighted_accuracy >= 1.0:
            exp = int(base_exp * 2.0)  # 全对双倍
        elif weighted_accuracy >= 0.8:
            exp = int(base_exp * 1.5)
        elif weighted_accuracy >= 0.6:
            exp = int(base_exp * 1.2)
        else:
            exp = int(base_exp * weighted_accuracy)

        return {
            "exp": exp,
            "correct": correct,
            "total": total,
            "accuracy": correct / total if total > 0 else 0,
            "weighted_accuracy": weighted_accuracy,
            "skip_count": skip_count,
            "wrong_count": wrong_count
        }


# ==================== 完形填空特殊处理 ====================

def show_cloze_with_context(question_data):
    """显示带上下文的完形填空"""
    lines = []
    lines.append(separator("═", 60, DarkTheme.ICE_CYAN))
    lines.append(c("  ✏️ 完形填空", DarkTheme.ICE_CYAN, C.BOLD))
    lines.append(separator("─", 60, C.BBLACK))
    lines.append("")

    # 显示句子
    sentence = question_data["sentence"]
    lines.append(c("  请选择正确的单词填入空格:", C.BWHITE))
    lines.append("")
    lines.append(f"  {c(sentence, C.BWHITE, C.BOLD)}")
    lines.append("")

    # 显示选项
    lines.append(separator("─", 60, C.BBLACK))
    options = question_data.get("options", [])
    for i, option in enumerate(options):
        label = chr(65 + i)
        lines.append(f"    {c(f'[{label}]', DarkTheme.GOLD_YELLOW)} {option}")

    lines.append("")
    lines.append(separator("─", 60, C.BBLACK))
    lines.append(f"    {c('[E]', DarkTheme.GOLD_YELLOW)} 不知道（惩罚减半）")
    lines.append("")
    lines.append(separator("═", 60, DarkTheme.ICE_CYAN))
    lines.append(c("  输入 A/B/C/D 选择答案，E 表示不知道", C.BBLACK))

    print("\n".join(lines))


def show_cloze_explanation(question_data, is_correct, is_skip=False):
    """显示完形填空解析"""
    lines = []

    # 获取正确答案文本（answer 可能是索引或文本）
    answer_value = question_data.get("answer", "")
    options = question_data.get("options", [])

    # 如果 answer 是数字索引，转换为实际文本
    if isinstance(answer_value, int) and 0 <= answer_value < len(options):
        correct_answer = options[answer_value]
    else:
        correct_answer = str(answer_value)

    sentence = question_data.get("sentence", "")

    if is_correct:
        lines.append(c("\n  ✅ 正确!", DarkTheme.POISON_GREEN, C.BOLD))
        # 详细解析
        lines.append("")
        lines.append(c("  ─────── 解析 ───────", DarkTheme.SOUL_BLUE))
        explanation = question_data.get("explanation", "")
        grammar = question_data.get("grammar_point", "")
        if explanation:
            lines.append(c(f"  📚 {explanation}", C.BWHITE))
        if grammar:
            lines.append(c(f"  📖 语法点: {grammar}", C.BCYAN))
        lines.append(c("  ────────────────────", DarkTheme.SOUL_BLUE))
        print("\n".join(lines))
        time.sleep(1.5)
    elif is_skip:
        # 进入学习模式
        _show_cloze_learning_mode(question_data, correct_answer, sentence)
    else:
        lines.append(c("\n  ❌ 错误!", DarkTheme.BLOOD_RED, C.BOLD))
        # 显示完整句子和正确答案
        lines.append(c(f"  📝 完整句子: {sentence.replace('___', correct_answer)}", C.BWHITE))
        lines.append(c(f"  ✅ 正确答案: {correct_answer}", DarkTheme.POISON_GREEN))
        # 详细解析
        lines.append("")
        lines.append(c("  ─────── 解析 ───────", DarkTheme.SOUL_BLUE))
        explanation = question_data.get("explanation", "")
        grammar = question_data.get("grammar_point", "")
        if explanation:
            lines.append(c(f"  📚 {explanation}", C.BWHITE))
        if grammar:
            lines.append(c(f"  📖 语法点: {grammar}", C.BCYAN))
        lines.append(c("  ────────────────────", DarkTheme.SOUL_BLUE))
        print("\n".join(lines))
        time.sleep(1.5)


def _show_cloze_learning_mode(question_data, correct_answer=None, sentence=None):
    """完形填空的学习模式"""
    # 获取正确答案
    if correct_answer is None:
        answer_value = question_data.get("answer", "")
        options = question_data.get("options", [])
        if isinstance(answer_value, int) and 0 <= answer_value < len(options):
            correct_answer = options[answer_value]
        else:
            correct_answer = str(answer_value)

    if sentence is None:
        sentence = question_data.get("sentence", "")

    explanation = question_data.get("explanation", "")
    grammar = question_data.get("grammar_point", "")

    if not correct_answer:
        return

    word = correct_answer

    print()
    print(c("═" * 55, DarkTheme.ICE_CYAN))
    print(c("  📖 学习模式", DarkTheme.ICE_CYAN, C.BOLD))
    print(c("═" * 55, DarkTheme.ICE_CYAN))

    # 显示完整句子
    full_sentence = sentence.replace("___", word) if sentence else ""
    print(c(f"\n  完整句子: {full_sentence}", C.BWHITE))
    print(c(f"  填空答案: {word}", DarkTheme.GOLD_YELLOW, C.BOLD))

    if explanation:
        print(c(f"\n  📚 {explanation}", C.BCYAN))
    if grammar:
        print(c(f"  📖 语法点: {grammar}", C.BBLACK))

    print(c("─" * 55, C.BBLACK))
    print(c("  💡 请拼写一遍加深记忆", C.BBLACK, C.ITALIC))
    print()

    # 让用户拼写
    attempts = 0
    while True:
        user_spell = input(c(f"  输入 [{word}]: ", DarkTheme.SOUL_BLUE)).strip()

        if user_spell.lower() == word.lower():
            print(c("  ✓ 拼写正确!", DarkTheme.POISON_GREEN, C.BOLD))
            break
        elif user_spell == "":
            print(c(f"  答案: {word}", C.BYELLOW))
            break
        else:
            attempts += 1
            if attempts >= 3:
                print(c(f"  答案: {word}", C.BYELLOW))
                print(c("  请再试一次...", C.BBLACK))
                user_spell = input(c(f"  输入 [{word}]: ", DarkTheme.SOUL_BLUE)).strip()
                if user_spell.lower() == word.lower():
                    print(c("  ✓ 拼写正确!", DarkTheme.POISON_GREEN, C.BOLD))
                break
            else:
                print(c(f"  ✗ 拼写错误，请重试 ({3-attempts}次机会)", DarkTheme.BLOOD_RED))

    print(c("═" * 55, DarkTheme.ICE_CYAN))


# ==================== Boss战中的完形填空 ====================

def boss_cloze_challenge(vocab_manager, difficulty=1):
    """
    Boss战完形填空挑战

    Args:
        vocab_manager: 词汇管理器
        difficulty: 难度等级 (1-3)

    Returns:
        tuple: (is_success, damage_prevented, exp_gained)
    """
    clear_screen()

    # 获取题目
    question = vocab_manager.get_cloze_question(difficulty)
    if not question:
        return True, 0, 0

    # 显示题目
    show_cloze_with_context(question)

    # 获取答案
    try:
        user_input = input(c("\n  你的选择: ", DarkTheme.SOUL_BLUE)).strip().upper()

        if not user_input:
            return False, 0, 0

        # 检查是否是"不知道"
        is_skip = user_input == "E"

        # 转换答案
        user_index = ord(user_input) - ord('A')
        options = question.get("options", [])
        answer_index = question.get("answer", 0)  # answer 是索引

        # 判断正确性：用户选择的索引 == 正确答案索引
        is_correct = not is_skip and 0 <= user_index < len(options) and user_index == answer_index

        # 显示结果
        show_cloze_explanation(question, is_correct, is_skip)

        if is_correct:
            return True, 0, 5  # 成功，无伤害，+5经验
        elif is_skip:
            return "skip", 0, 2  # 跳过，惩罚减半，+2经验
        else:
            return False, 0, 0  # 失败

    except Exception:
        return False, 0, 0


# ==================== 选择题关卡 ====================

def play_quiz_level(vocab_manager=None, quiz_type="mixed", level="medium", question_count=5):
    """
    游玩选择题关卡

    Args:
        vocab_manager: 词汇管理器
        quiz_type: 题目类型 ("mixed", "en_to_cn", "cn_to_en", "form", "cloze")
        level: 难度
        question_count: 题目数量

    Returns:
        dict: 游戏结果
    """
    vocab = vocab_manager or VocabularyManager()
    game = QuizGame(vocab)

    # 生成题目
    actual_count = game.generate_questions(quiz_type, level, question_count)
    if actual_count == 0:
        print(c("  无法生成题目!", DarkTheme.BLOOD_RED))
        return {"success": False, "exp": 0}

    # 开始答题
    while True:
        question = game.get_current_question()
        if not question:
            break

        # 显示题目
        show_quiz_question(question, game.current_index + 1, actual_count)

        # 获取答案
        try:
            user_input = input(c("\n  选择: ", DarkTheme.SOUL_BLUE)).strip().upper()

            if user_input == "\x1b":  # ESC - 退出整个关卡
                break

            if user_input not in ["A", "B", "C", "D", "E"]:
                print(c("  请输入 A/B/C/D/E!", DarkTheme.BLOOD_RED))
                time.sleep(0.5)
                continue

            # 回答问题
            q, is_correct, is_skip = game.answer_question(user_input)

            # 显示结果
            show_quiz_result(is_correct, q, user_input, is_skip)

            # 下一题
            if not game.next_question():
                break

        except KeyboardInterrupt:
            break

    # 计算奖励
    reward = game.calculate_reward()

    # 显示总结
    show_quiz_summary(reward["correct"], reward["total"], reward["exp"],
                      skip_count=reward.get("skip_count", 0),
                      wrong_count=reward.get("wrong_count", 0))

    return {
        "success": True,
        "correct": reward["correct"],
        "total": reward["total"],
        "accuracy": reward["accuracy"],
        "exp": reward["exp"]
    }


# ==================== 快速选择题（Boss战用） ====================

def quick_quiz(vocab_manager, quiz_type="en_to_cn", level="medium", timeout=10):
    """
    快速选择题（带时间限制）

    Args:
        vocab_manager: 词汇管理器
        quiz_type: 题目类型
        level: 难度
        timeout: 超时秒数

    Returns:
        tuple: (is_correct, time_used, exp_gained)
    """
    import threading

    question = vocab_manager.get_quiz_question(quiz_type, level)
    if not question:
        return True, 0, 0

    # 简化显示
    print()
    print(c(f"  ⚡ 快速答题 ({timeout}秒)", DarkTheme.GOLD_YELLOW, C.BOLD))
    print(c(f"  {question['question']}", C.BWHITE))
    print()

    options = question.get("options", [])
    for i, option in enumerate(options):
        label = chr(65 + i)
        print(f"    {c(f'[{label}]', DarkTheme.GOLD_YELLOW)} {option}")
    print(f"    {c('[E]', DarkTheme.GOLD_YELLOW)} 不知道")

    print()

    start_time = time.time()
    result = {"answered": False, "correct": False, "is_skip": False, "choice": None}

    def get_input():
        try:
            user_input = input(c("  选择: ", DarkTheme.SOUL_BLUE)).strip().upper()
            result["answered"] = True
            result["choice"] = user_input

            if user_input == "E":
                result["is_skip"] = True
            elif user_input in ["A", "B", "C", "D"]:
                user_index = ord(user_input) - ord('A')
                if 0 <= user_index < len(options):
                    result["correct"] = options[user_index] == question.get("answer")
        except:
            pass

    # 使用线程实现超时（简化版）
    input_thread = threading.Thread(target=get_input)
    input_thread.daemon = True
    input_thread.start()
    input_thread.join(timeout)

    time_used = time.time() - start_time

    if not result["answered"]:
        print(c("\n  ⏰ 超时!", DarkTheme.BLOOD_RED))
        return False, time_used, 0

    if result["is_skip"]:
        correct = question.get("answer", "")
        print(c(f"  🤔 跳过! 正确答案: {correct}", C.BYELLOW))
        return "skip", time_used, 1  # 跳过，给1点经验（惩罚减半）
    elif result["correct"]:
        print(c("  ✅ 正确!", DarkTheme.POISON_GREEN))
        # 时间奖励
        time_bonus = max(0, int((timeout - time_used) * 0.5))
        return True, time_used, 3 + time_bonus
    else:
        correct = question.get("answer", "")
        print(c(f"  ❌ 错误! 正确答案: {correct}", DarkTheme.BLOOD_RED))
        return False, time_used, 0
