"""
词汇库管理模块 - CET4/CET6词汇、难度分级、完形填空题库
"""

import random
import json
import os
from typing import List, Dict, Optional, Tuple

# ==================== CET4 核心词汇示例 ====================
# 实际使用时从外部JSON加载完整词库

CET4_WORDS = {
    # A
    "abandon": {"meaning": "v. 放弃；抛弃", "level": 1, "forms": ["abandoned", "abandoning"]},
    "ability": {"meaning": "n. 能力；才能", "level": 1, "forms": ["abilities"]},
    "absorb": {"meaning": "v. 吸收；理解", "level": 2, "forms": ["absorbed", "absorbing"]},
    "abstract": {"meaning": "adj. 抽象的 n. 摘要", "level": 2, "forms": ["abstractly"]},
    "abundant": {"meaning": "adj. 丰富的；充裕的", "level": 2, "forms": ["abundance"]},
    "academic": {"meaning": "adj. 学术的；学院的", "level": 1, "forms": ["academically"]},
    "accelerate": {"meaning": "v. 加速；促进", "level": 2, "forms": ["accelerated", "acceleration"]},
    "accept": {"meaning": "v. 接受；承认", "level": 1, "forms": ["accepted", "accepting", "acceptable"]},
    "access": {"meaning": "n. 通道；机会 v. 接近", "level": 1, "forms": ["accessible"]},
    "accident": {"meaning": "n. 事故；意外", "level": 1, "forms": ["accidental", "accidentally"]},
    "accomplish": {"meaning": "v. 完成；实现", "level": 2, "forms": ["accomplished", "accomplishment"]},
    "accurate": {"meaning": "adj. 准确的；精确的", "level": 1, "forms": ["accurately", "accuracy"]},
    "achieve": {"meaning": "v. 达到；实现", "level": 1, "forms": ["achieved", "achievement"]},
    "acknowledge": {"meaning": "v. 承认；感谢", "level": 2, "forms": ["acknowledged", "acknowledgment"]},
    "acquire": {"meaning": "v. 获得；学到", "level": 2, "forms": ["acquired", "acquisition"]},
    "adapt": {"meaning": "v. 适应；改编", "level": 1, "forms": ["adapted", "adaptable", "adaptation"]},
    "addition": {"meaning": "n. 增加；加法", "level": 1, "forms": ["additional", "additionally"]},
    "address": {"meaning": "n. 地址 v. 演说；处理", "level": 1, "forms": ["addressed"]},
    "adequate": {"meaning": "adj. 足够的；适当的", "level": 2, "forms": ["adequately", "adequacy"]},
    "adjust": {"meaning": "v. 调整；适应", "level": 1, "forms": ["adjusted", "adjustment"]},
    "administration": {"meaning": "n. 管理；行政", "level": 2, "forms": ["administer", "administrative"]},
    "admire": {"meaning": "v. 钦佩；欣赏", "level": 1, "forms": ["admired", "admiration"]},
    "admit": {"meaning": "v. 承认；允许进入", "level": 1, "forms": ["admitted", "admission"]},
    "adopt": {"meaning": "v. 采用；收养", "level": 1, "forms": ["adopted", "adoption"]},
    "adult": {"meaning": "n. 成年人 adj. 成年的", "level": 1, "forms": []},
    "advance": {"meaning": "v. 前进 n. 进步", "level": 1, "forms": ["advanced", "advancement"]},
    "advantage": {"meaning": "n. 优势；好处", "level": 1, "forms": ["advantageous"]},
    "adventure": {"meaning": "n. 冒险；奇遇", "level": 1, "forms": ["adventurous"]},
    "advertise": {"meaning": "v. 做广告", "level": 1, "forms": ["advertisement", "advertising"]},
    "affect": {"meaning": "v. 影响；感动", "level": 1, "forms": ["affected", "affection"]},
    "afford": {"meaning": "v. 负担得起；提供", "level": 1, "forms": ["affordable"]},
    "agree": {"meaning": "v. 同意；赞成", "level": 1, "forms": ["agreed", "agreement", "agreeable"]},
    "agriculture": {"meaning": "n. 农业", "level": 1, "forms": ["agricultural"]},
    "aircraft": {"meaning": "n. 飞机；航空器", "level": 1, "forms": []},
    "alarm": {"meaning": "n. 警报 v. 使惊恐", "level": 1, "forms": ["alarmed"]},
    "alcohol": {"meaning": "n. 酒精；酒", "level": 1, "forms": ["alcoholic"]},
    "allow": {"meaning": "v. 允许；给予", "level": 1, "forms": ["allowed", "allowance"]},
    "alternative": {"meaning": "n. 替代品 adj. 选择的", "level": 2, "forms": ["alternatively"]},
    "amaze": {"meaning": "v. 使惊奇", "level": 1, "forms": ["amazed", "amazing", "amazement"]},
    "ambition": {"meaning": "n. 野心；抱负", "level": 2, "forms": ["ambitious"]},
    "amount": {"meaning": "n. 数量 v. 总计", "level": 1, "forms": []},
    "analyse": {"meaning": "v. 分析", "level": 1, "forms": ["analyzed", "analysis", "analytical"]},
    "ancient": {"meaning": "adj. 古代的；古老的", "level": 1, "forms": []},
    "angle": {"meaning": "n. 角度；观点", "level": 1, "forms": []},
    "anniversary": {"meaning": "n. 周年纪念日", "level": 1, "forms": []},
    "announce": {"meaning": "v. 宣布；通告", "level": 1, "forms": ["announced", "announcement"]},
    "annual": {"meaning": "adj. 每年的 n. 年刊", "level": 1, "forms": ["annually"]},
    "anticipate": {"meaning": "v. 预期；期待", "level": 2, "forms": ["anticipated", "anticipation"]},
    "anxiety": {"meaning": "n. 焦虑；渴望", "level": 2, "forms": ["anxious", "anxiously"]},
    "apologize": {"meaning": "v. 道歉", "level": 1, "forms": ["apologized", "apology"]},
    "apparent": {"meaning": "adj. 明显的；表面的", "level": 2, "forms": ["apparently"]},
    "appeal": {"meaning": "v. 呼吁；吸引 n. 吸引力", "level": 2, "forms": ["appealing"]},
    "appetite": {"meaning": "n. 胃口；欲望", "level": 1, "forms": []},
    "applaud": {"meaning": "v. 鼓掌；称赞", "level": 2, "forms": ["applause"]},
    "application": {"meaning": "n. 申请；应用", "level": 1, "forms": ["apply", "applicable"]},
    "appoint": {"meaning": "v. 任命；指定", "level": 2, "forms": ["appointed", "appointment"]},
    "appreciate": {"meaning": "v. 感激；欣赏", "level": 1, "forms": ["appreciated", "appreciation"]},
    "approach": {"meaning": "v. 接近 n. 方法", "level": 1, "forms": []},
    "appropriate": {"meaning": "adj. 适当的", "level": 1, "forms": ["appropriately"]},
    "approve": {"meaning": "v. 批准；赞成", "level": 1, "forms": ["approved", "approval"]},
    "architect": {"meaning": "n. 建筑师", "level": 1, "forms": ["architecture", "architectural"]},
    "argue": {"meaning": "v. 争论；论证", "level": 1, "forms": ["argued", "argument"]},
    "arise": {"meaning": "v. 出现；产生", "level": 2, "forms": ["arose", "arisen"]},
    "arrange": {"meaning": "v. 安排；整理", "level": 1, "forms": ["arranged", "arrangement"]},
    "arrest": {"meaning": "v. 逮捕 n. 逮捕", "level": 1, "forms": []},
    "artificial": {"meaning": "adj. 人工的；虚伪的", "level": 2, "forms": []},
    "aspect": {"meaning": "n. 方面；外表", "level": 1, "forms": []},
    "assemble": {"meaning": "v. 集合；装配", "level": 2, "forms": ["assembly"]},
    "assess": {"meaning": "v. 评估；估算", "level": 2, "forms": ["assessment"]},
    "assign": {"meaning": "v. 分配；指派", "level": 2, "forms": ["assigned", "assignment"]},
    "assist": {"meaning": "v. 协助", "level": 1, "forms": ["assisted", "assistance", "assistant"]},
    "associate": {"meaning": "v. 联想；交往 adj. 副的", "level": 2, "forms": ["association"]},
    "assume": {"meaning": "v. 假定；承担", "level": 1, "forms": ["assumed", "assumption"]},
    "assure": {"meaning": "v. 保证；使确信", "level": 2, "forms": ["assured", "assurance"]},
    "astonish": {"meaning": "v. 使惊讶", "level": 2, "forms": ["astonished", "astonishing", "astonishment"]},
    "athlete": {"meaning": "n. 运动员", "level": 1, "forms": ["athletic"]},
    "atmosphere": {"meaning": "n. 气氛；大气", "level": 1, "forms": []},
    "attach": {"meaning": "v. 附上；依恋", "level": 2, "forms": ["attached", "attachment"]},
    "attack": {"meaning": "v. 攻击 n. 攻击", "level": 1, "forms": []},
    "attain": {"meaning": "v. 达到；获得", "level": 2, "forms": ["attainable"]},
    "attempt": {"meaning": "v. 尝试 n. 尝试", "level": 1, "forms": []},
    "attend": {"meaning": "v. 出席；照顾", "level": 1, "forms": ["attended", "attendance", "attention"]},
    "attitude": {"meaning": "n. 态度", "level": 1, "forms": []},
    "attract": {"meaning": "v. 吸引", "level": 1, "forms": ["attracted", "attraction", "attractive"]},
    "attribute": {"meaning": "v. 归因于 n. 属性", "level": 2, "forms": []},
    "audience": {"meaning": "n. 观众；听众", "level": 1, "forms": []},
    "authority": {"meaning": "n. 权威；当局", "level": 1, "forms": ["authorize", "authoritative"]},
    "automatic": {"meaning": "adj. 自动的", "level": 1, "forms": ["automatically"]},
    "available": {"meaning": "adj. 可用的；有空的", "level": 1, "forms": ["availability"]},
    "average": {"meaning": "adj. 平均的 n. 平均", "level": 1, "forms": []},
    "avoid": {"meaning": "v. 避免", "level": 1, "forms": ["avoided", "avoidable"]},
    "award": {"meaning": "n. 奖品 v. 授予", "level": 1, "forms": []},
    "aware": {"meaning": "adj. 意识到的", "level": 1, "forms": ["awareness"]},
    "awful": {"meaning": "adj. 可怕的；糟糕的", "level": 1, "forms": ["awfully"]},

    # B
    "balance": {"meaning": "n. 平衡 v. 使平衡", "level": 1, "forms": []},
    "barrier": {"meaning": "n. 障碍；屏障", "level": 2, "forms": []},
    "base": {"meaning": "n. 基础 v. 基于", "level": 1, "forms": ["basic", "basically", "basis"]},
    "behalf": {"meaning": "n. 代表；利益", "level": 2, "forms": []},
    "behave": {"meaning": "v. 行为；表现", "level": 1, "forms": ["behavior"]},
    "belief": {"meaning": "n. 信念；相信", "level": 1, "forms": ["believe", "believable"]},
    "belong": {"meaning": "v. 属于", "level": 1, "forms": ["belongings"]},
    "benefit": {"meaning": "n. 利益 v. 有益于", "level": 1, "forms": ["beneficial", "beneficiary"]},
    "betray": {"meaning": "v. 背叛；泄露", "level": 2, "forms": ["betrayal"]},
    "beyond": {"meaning": "prep. 超过 adv. 在远处", "level": 1, "forms": []},
    "blame": {"meaning": "v. 责备 n. 过失", "level": 1, "forms": []},
    "blank": {"meaning": "adj. 空白的 n. 空白", "level": 1, "forms": []},
    "blend": {"meaning": "v. 混合 n. 混合物", "level": 2, "forms": []},
    "block": {"meaning": "n. 街区 v. 阻塞", "level": 1, "forms": []},
    "bond": {"meaning": "n. 纽带；债券 v. 结合", "level": 2, "forms": []},
    "bonus": {"meaning": "n. 奖金；红利", "level": 1, "forms": []},
    "boom": {"meaning": "n. 繁荣 v. 激增", "level": 1, "forms": []},
    "boost": {"meaning": "v. 促进；增加", "level": 1, "forms": []},
    "border": {"meaning": "n. 边界 v. 接壤", "level": 1, "forms": []},
    "bother": {"meaning": "v. 打扰；烦恼", "level": 1, "forms": []},
    "bounce": {"meaning": "v. 弹跳 n. 弹跳", "level": 1, "forms": []},
    "boundary": {"meaning": "n. 边界；界限", "level": 1, "forms": []},
    "brand": {"meaning": "n. 品牌 v. 打烙印", "level": 1, "forms": []},
    "breakthrough": {"meaning": "n. 突破", "level": 2, "forms": []},
    "breathe": {"meaning": "v. 呼吸", "level": 1, "forms": ["breath", "breathless"]},
    "breed": {"meaning": "v. 繁殖 n. 品种", "level": 2, "forms": []},
    "brief": {"meaning": "adj. 简短的", "level": 1, "forms": ["briefly"]},
    "brilliant": {"meaning": "adj. 辉煌的；杰出的", "level": 1, "forms": []},
    "broad": {"meaning": "adj. 宽的；广泛的", "level": 1, "forms": ["broaden", "broadly"]},
    "budget": {"meaning": "n. 预算 v. 预算", "level": 1, "forms": []},
    "burden": {"meaning": "n. 负担 v. 负担", "level": 2, "forms": []},
    "bureaucracy": {"meaning": "n. 官僚主义", "level": 2, "forms": ["bureaucratic"]},

    # C
    "calculate": {"meaning": "v. 计算", "level": 1, "forms": ["calculated", "calculation", "calculator"]},
    "campaign": {"meaning": "n. 运动；战役", "level": 1, "forms": []},
    "cancel": {"meaning": "v. 取消", "level": 1, "forms": ["cancelled", "cancellation"]},
    "candidate": {"meaning": "n. 候选人", "level": 1, "forms": []},
    "capable": {"meaning": "adj. 有能力的", "level": 1, "forms": ["capability", "capably"]},
    "capacity": {"meaning": "n. 容量；能力", "level": 1, "forms": []},
    "capture": {"meaning": "v. 捕获；吸引", "level": 2, "forms": []},
    "career": {"meaning": "n. 职业；生涯", "level": 1, "forms": []},
    "cargo": {"meaning": "n. 货物", "level": 1, "forms": []},
    "case": {"meaning": "n. 情况；案例；箱子", "level": 1, "forms": []},
    "cast": {"meaning": "v. 投；掷 n. 铸造", "level": 2, "forms": []},
    "casual": {"meaning": "adj. 随意的；非正式的", "level": 1, "forms": ["casually"]},
    "category": {"meaning": "n. 类别", "level": 1, "forms": ["categorize"]},
    "cease": {"meaning": "v. 停止", "level": 2, "forms": []},
    "celebrate": {"meaning": "v. 庆祝", "level": 1, "forms": ["celebrated", "celebration"]},
    "ceremony": {"meaning": "n. 典礼；仪式", "level": 1, "forms": []},
    "certificate": {"meaning": "n. 证书", "level": 1, "forms": ["certify"]},
    "challenge": {"meaning": "n. 挑战 v. 挑战", "level": 1, "forms": ["challenging"]},
    "champion": {"meaning": "n. 冠军 v. 支持", "level": 1, "forms": ["championship"]},
    "channel": {"meaning": "n. 频道；渠道", "level": 1, "forms": []},
    "chapter": {"meaning": "n. 章节", "level": 1, "forms": []},
    "character": {"meaning": "n. 性格；角色；字符", "level": 1, "forms": ["characteristic", "characterize"]},
    "charge": {"meaning": "v. 收费；指控 n. 费用", "level": 1, "forms": []},
    "charity": {"meaning": "n. 慈善", "level": 1, "forms": []},
    "chart": {"meaning": "n. 图表", "level": 1, "forms": []},
    "chase": {"meaning": "v. 追逐", "level": 1, "forms": []},
    "cheap": {"meaning": "adj. 便宜的", "level": 1, "forms": ["cheaply"]},
    "cheat": {"meaning": "v. 欺骗 n. 欺骗", "level": 1, "forms": []},
    "check": {"meaning": "v. 检查 n. 支票", "level": 1, "forms": []},
    "cheerful": {"meaning": "adj. 快乐的", "level": 1, "forms": ["cheerfully", "cheerfulness"]},
    "chemical": {"meaning": "adj. 化学的 n. 化学品", "level": 1, "forms": ["chemistry"]},
    "circumstance": {"meaning": "n. 情况；环境", "level": 2, "forms": []},
    "citizen": {"meaning": "n. 公民", "level": 1, "forms": ["citizenship"]},
    "civil": {"meaning": "adj. 公民的；文明的", "level": 1, "forms": ["civilization", "civilize"]},
    "claim": {"meaning": "v. 声称；索取 n. 主张", "level": 1, "forms": []},
    "clarify": {"meaning": "v. 澄清", "level": 2, "forms": ["clarification"]},
    "classic": {"meaning": "adj. 经典的 n. 经典", "level": 1, "forms": ["classical"]},
    "classify": {"meaning": "v. 分类", "level": 2, "forms": ["classification"]},
    "client": {"meaning": "n. 客户", "level": 1, "forms": []},
    "climate": {"meaning": "n. 气候", "level": 1, "forms": []},
    "clue": {"meaning": "n. 线索", "level": 1, "forms": []},
    "coach": {"meaning": "n. 教练 v. 训练", "level": 1, "forms": []},
    "collapse": {"meaning": "v. 倒塌 n. 崩溃", "level": 2, "forms": []},
    "colleague": {"meaning": "n. 同事", "level": 1, "forms": []},
    "collect": {"meaning": "v. 收集", "level": 1, "forms": ["collection", "collective"]},
    "collision": {"meaning": "n. 碰撞", "level": 2, "forms": ["collide"]},
    "combine": {"meaning": "v. 结合", "level": 1, "forms": ["combination", "combined"]},
    "comfort": {"meaning": "n. 舒适 v. 安慰", "level": 1, "forms": ["comfortable", "comfortably"]},
    "command": {"meaning": "v. 命令 n. 命令", "level": 1, "forms": ["commander"]},
    "comment": {"meaning": "n. 评论 v. 评论", "level": 1, "forms": []},
    "commercial": {"meaning": "adj. 商业的 n. 广告", "level": 1, "forms": ["commerce"]},
    "commission": {"meaning": "n. 委员会；佣金", "level": 2, "forms": []},
    "commit": {"meaning": "v. 犯罪；承诺", "level": 1, "forms": ["committed", "commitment"]},
    "commodity": {"meaning": "n. 商品", "level": 2, "forms": []},
    "communicate": {"meaning": "v. 交流", "level": 1, "forms": ["communication"]},
    "community": {"meaning": "n. 社区", "level": 1, "forms": []},
    "companion": {"meaning": "n. 同伴", "level": 1, "forms": ["company"]},
    "compare": {"meaning": "v. 比较", "level": 1, "forms": ["comparison", "comparative"]},
    "compel": {"meaning": "v. 强迫", "level": 2, "forms": ["compelling"]},
    "compensate": {"meaning": "v. 补偿", "level": 2, "forms": ["compensation"]},
    "compete": {"meaning": "v. 竞争", "level": 1, "forms": ["competition", "competitive", "competitor"]},
    "complain": {"meaning": "v. 抱怨", "level": 1, "forms": ["complaint"]},
    "complete": {"meaning": "adj. 完整的 v. 完成", "level": 1, "forms": ["completely", "completion"]},
    "complex": {"meaning": "adj. 复杂的", "level": 1, "forms": ["complexity"]},
    "complicated": {"meaning": "adj. 复杂的", "level": 1, "forms": []},
    "component": {"meaning": "n. 组件；成分", "level": 2, "forms": []},
    "compose": {"meaning": "v. 组成；作曲", "level": 2, "forms": ["composition", "composer"]},
    "comprehension": {"meaning": "n. 理解", "level": 1, "forms": ["comprehend", "comprehensive"]},
    "comprise": {"meaning": "v. 包含；由...组成", "level": 2, "forms": []},
    "compromise": {"meaning": "n. 妥协 v. 妥协", "level": 2, "forms": []},
    "compulsory": {"meaning": "adj. 强制的", "level": 2, "forms": []},
    "concentrate": {"meaning": "v. 集中", "level": 1, "forms": ["concentration"]},
    "concept": {"meaning": "n. 概念", "level": 1, "forms": ["conception", "conceptual"]},
    "concern": {"meaning": "v. 涉及；关心 n. 关心", "level": 1, "forms": ["concerned", "concerning"]},
    "conclude": {"meaning": "v. 结束；得出结论", "level": 1, "forms": ["conclusion"]},
    "concrete": {"meaning": "adj. 具体的 n. 混凝土", "level": 1, "forms": []},
    "condemn": {"meaning": "v. 谴责；判刑", "level": 2, "forms": ["condemnation"]},
    "condition": {"meaning": "n. 条件；状况", "level": 1, "forms": ["conditional"]},
    "conduct": {"meaning": "v. 进行 n. 行为", "level": 1, "forms": ["conductor", "conduction"]},
    "conference": {"meaning": "n. 会议", "level": 1, "forms": []},
    "confess": {"meaning": "v. 承认；忏悔", "level": 2, "forms": ["confession"]},
    "confidence": {"meaning": "n. 信心", "level": 1, "forms": ["confident", "confidently"]},
    "confine": {"meaning": "v. 限制", "level": 2, "forms": ["confinement"]},
    "confirm": {"meaning": "v. 确认", "level": 1, "forms": ["confirmation"]},
    "conflict": {"meaning": "n. 冲突 v. 冲突", "level": 1, "forms": []},
    "confuse": {"meaning": "v. 使困惑", "level": 1, "forms": ["confused", "confusing", "confusion"]},
    "congratulate": {"meaning": "v. 祝贺", "level": 1, "forms": ["congratulation"]},
    "congress": {"meaning": "n. 国会；代表大会", "level": 1, "forms": ["congressional"]},
    "connect": {"meaning": "v. 连接", "level": 1, "forms": ["connection", "connected"]},
    "conquer": {"meaning": "v. 征服", "level": 2, "forms": ["conquest"]},
    "conscience": {"meaning": "n. 良心", "level": 2, "forms": ["conscientious"]},
    "conscious": {"meaning": "adj. 有意识的", "level": 1, "forms": ["consciousness", "consciously"]},
    "consensus": {"meaning": "n. 共识", "level": 2, "forms": []},
    "consent": {"meaning": "v. 同意 n. 同意", "level": 2, "forms": []},
    "consequence": {"meaning": "n. 后果", "level": 1, "forms": ["consequent", "consequently"]},
    "conservation": {"meaning": "n. 保护", "level": 1, "forms": ["conserve", "conservative"]},
    "consider": {"meaning": "v. 考虑", "level": 1, "forms": ["consideration", "considerable", "considerate"]},
    "consist": {"meaning": "v. 由...组成", "level": 1, "forms": ["consistent", "consistency"]},
    "constant": {"meaning": "adj. 恒定的 n. 常数", "level": 1, "forms": ["constantly"]},
    "constitute": {"meaning": "v. 组成；设立", "level": 2, "forms": ["constitution", "constitutional"]},
    "construct": {"meaning": "v. 建造", "level": 1, "forms": ["construction", "constructive"]},
    "consult": {"meaning": "v. 咨询", "level": 2, "forms": ["consultant", "consultation"]},
    "consume": {"meaning": "v. 消费", "level": 1, "forms": ["consumer", "consumption"]},
    "contact": {"meaning": "n. 联系 v. 联系", "level": 1, "forms": []},
    "contain": {"meaning": "v. 包含", "level": 1, "forms": ["container"]},
    "contemporary": {"meaning": "adj. 当代的", "level": 2, "forms": []},
    "content": {"meaning": "n. 内容 adj. 满意的", "level": 1, "forms": []},
    "contest": {"meaning": "n. 比赛 v. 争辩", "level": 1, "forms": []},
    "context": {"meaning": "n. 上下文；背景", "level": 1, "forms": []},
    "continent": {"meaning": "n. 大陆", "level": 1, "forms": ["continental"]},
    "continue": {"meaning": "v. 继续", "level": 1, "forms": ["continuous", "continually"]},
    "contract": {"meaning": "n. 合同 v. 收缩", "level": 1, "forms": []},
    "contradict": {"meaning": "v. 反驳", "level": 2, "forms": ["contradiction", "contradictory"]},
    "contrary": {"meaning": "adj. 相反的 n. 相反", "level": 2, "forms": []},
    "contrast": {"meaning": "n. 对比 v. 对比", "level": 1, "forms": []},
    "contribute": {"meaning": "v. 贡献", "level": 1, "forms": ["contribution", "contributor"]},
    "control": {"meaning": "v. 控制 n. 控制", "level": 1, "forms": []},
    "controversial": {"meaning": "adj. 有争议的", "level": 2, "forms": ["controversy"]},
    "convenient": {"meaning": "adj. 方便的", "level": 1, "forms": ["convenience", "conveniently"]},
    "conventional": {"meaning": "adj. 传统的", "level": 1, "forms": ["convention"]},
    "converse": {"meaning": "v. 交谈 adj. 相反的", "level": 2, "forms": ["conversation", "conversely"]},
    "convert": {"meaning": "v. 转换", "level": 2, "forms": ["conversion"]},
    "convey": {"meaning": "v. 传达；运输", "level": 2, "forms": []},
    "convince": {"meaning": "v. 说服", "level": 1, "forms": ["convinced", "convincing", "convincingly"]},
    "cooperate": {"meaning": "v. 合作", "level": 1, "forms": ["cooperation", "cooperative"]},
    "coordinate": {"meaning": "v. 协调 n. 坐标", "level": 2, "forms": ["coordination"]},
    "cope": {"meaning": "v. 应付", "level": 1, "forms": []},
    "core": {"meaning": "n. 核心", "level": 1, "forms": []},
    "corporate": {"meaning": "adj. 公司的", "level": 1, "forms": ["corporation"]},
    "correspond": {"meaning": "v. 通信；符合", "level": 2, "forms": ["correspondence", "correspondent"]},
    "corrupt": {"meaning": "adj. 腐败的 v. 腐蚀", "level": 2, "forms": ["corruption"]},
    "council": {"meaning": "n. 委员会", "level": 1, "forms": []},
    "counsel": {"meaning": "v. 建议 n. 律师", "level": 2, "forms": ["counseling", "counselor"]},
    "counter": {"meaning": "n. 柜台 v. 反驳", "level": 1, "forms": []},
    "court": {"meaning": "n. 法院；球场", "level": 1, "forms": []},
    "cover": {"meaning": "v. 覆盖 n. 封面", "level": 1, "forms": ["coverage"]},
    "crack": {"meaning": "v. 裂开 n. 裂缝", "level": 1, "forms": []},
    "craft": {"meaning": "n. 手艺 v. 精心制作", "level": 1, "forms": []},
    "crash": {"meaning": "v. 坠毁 n. 崩溃", "level": 1, "forms": []},
    "create": {"meaning": "v. 创造", "level": 1, "forms": ["creation", "creative", "creativity", "creator"]},
    "creature": {"meaning": "n. 生物", "level": 1, "forms": []},
    "credit": {"meaning": "n. 信用；学分 v. 归功于", "level": 1, "forms": []},
    "crew": {"meaning": "n. 全体船员", "level": 1, "forms": []},
    "crime": {"meaning": "n. 犯罪", "level": 1, "forms": ["criminal"]},
    "crisis": {"meaning": "n. 危机", "level": 1, "forms": ["crises"]},
    "criterion": {"meaning": "n. 标准", "level": 2, "forms": ["criteria"]},
    "critic": {"meaning": "n. 批评家", "level": 1, "forms": ["critical", "criticize", "criticism"]},
    "crop": {"meaning": "n. 农作物 v. 收割", "level": 1, "forms": []},
    "crowd": {"meaning": "n. 人群 v. 拥挤", "level": 1, "forms": ["crowded"]},
    "crucial": {"meaning": "adj. 关键的", "level": 1, "forms": []},
    "cruel": {"meaning": "adj. 残忍的", "level": 1, "forms": ["cruelty"]},
    "cultivate": {"meaning": "v. 耕种；培养", "level": 2, "forms": ["cultivation"]},
    "culture": {"meaning": "n. 文化", "level": 1, "forms": ["cultural"]},
    "curiosity": {"meaning": "n. 好奇心", "level": 1, "forms": ["curious"]},
    "currency": {"meaning": "n. 货币", "level": 1, "forms": []},
    "current": {"meaning": "adj. 当前的 n. 水流", "level": 1, "forms": ["currently"]},
    "curriculum": {"meaning": "n. 课程", "level": 1, "forms": ["curricula"]},
    "custom": {"meaning": "n. 习惯；风俗", "level": 1, "forms": ["customary", "customize", "customer"]},
    "cycle": {"meaning": "n. 循环 v. 骑自行车", "level": 1, "forms": []},

    # ... 更多词汇可以继续添加
}

# ==================== CET6 核心词汇示例 ====================

CET6_WORDS = {
    "abnormal": {"meaning": "adj. 反常的", "level": 3, "forms": ["abnormality"]},
    "abolish": {"meaning": "v. 废除", "level": 3, "forms": ["abolition"]},
    "abort": {"meaning": "v. 流产；中止", "level": 3, "forms": ["abortion"]},
    "abrupt": {"meaning": "adj. 突然的；粗鲁的", "level": 3, "forms": ["abruptly"]},
    "absurd": {"meaning": "adj. 荒谬的", "level": 3, "forms": ["absurdity"]},
    "abundance": {"meaning": "n. 丰富", "level": 3, "forms": ["abundant", "abundantly"]},
    "accessory": {"meaning": "n. 附件；从犯", "level": 3, "forms": []},
    "accommodate": {"meaning": "v. 容纳；适应", "level": 3, "forms": ["accommodation"]},
    "accord": {"meaning": "v. 给予 n. 协议", "level": 3, "forms": ["accordance", "accordingly"]},
    "accountable": {"meaning": "adj. 有责任的", "level": 3, "forms": ["accountability"]},
    "accumulate": {"meaning": "v. 积累", "level": 3, "forms": ["accumulation"]},
    "accuse": {"meaning": "v. 指控", "level": 3, "forms": ["accusation"]},
    "accustom": {"meaning": "v. 使习惯", "level": 3, "forms": ["accustomed"]},
    "acknowledgement": {"meaning": "n. 承认；感谢", "level": 3, "forms": []},
    "acquaint": {"meaning": "v. 使熟悉", "level": 3, "forms": ["acquaintance"]},
    "activate": {"meaning": "v. 激活", "level": 3, "forms": ["activation", "active"]},
    "addict": {"meaning": "v. 使上瘾 n. 上瘾者", "level": 3, "forms": ["addiction", "addictive"]},
    "adhere": {"meaning": "v. 坚持；粘附", "level": 3, "forms": ["adherence", "adhesive"]},
    "adjacent": {"meaning": "adj. 邻近的", "level": 3, "forms": []},
    "adjoin": {"meaning": "v. 邻接", "level": 3, "forms": []},
    "administer": {"meaning": "v. 管理；执行", "level": 3, "forms": ["administration", "administrative"]},
    "adolescent": {"meaning": "n. 青少年 adj. 青春期的", "level": 3, "forms": ["adolescence"]},
    "adore": {"meaning": "v. 崇拜；爱慕", "level": 3, "forms": ["adorable", "adoration"]},
    "adverse": {"meaning": "adj. 不利的；有害的", "level": 3, "forms": ["adversely"]},
    "advocate": {"meaning": "v. 提倡 n. 提倡者", "level": 3, "forms": []},
    "aesthetic": {"meaning": "adj. 美学的", "level": 3, "forms": ["aesthetically"]},
    "affiliate": {"meaning": "v. 使附属", "level": 3, "forms": ["affiliation"]},
    "affirm": {"meaning": "v. 肯定；确认", "level": 3, "forms": ["affirmation", "affirmative"]},
    "aggravate": {"meaning": "v. 加重；恶化", "level": 3, "forms": ["aggravation"]},
    "aggregate": {"meaning": "v. 聚集 n. 总计", "level": 3, "forms": []},
    "agitate": {"meaning": "v. 煽动；搅动", "level": 3, "forms": ["agitation"]},
    "alienate": {"meaning": "v. 疏远", "level": 3, "forms": ["alienation"]},
    "allegedly": {"meaning": "adv. 据说", "level": 3, "forms": []},
    "alleviate": {"meaning": "v. 减轻", "level": 3, "forms": ["alleviation"]},
    "allocate": {"meaning": "v. 分配", "level": 3, "forms": ["allocation"]},
    "allot": {"meaning": "v. 分配", "level": 3, "forms": ["allotment"]},
    "allude": {"meaning": "v. 暗指", "level": 3, "forms": ["allusion"]},
    "allure": {"meaning": "v. 诱惑 n. 诱惑力", "level": 3, "forms": ["alluring"]},
    "ambiguous": {"meaning": "adj. 模棱两可的", "level": 3, "forms": ["ambiguity"]},
    "amend": {"meaning": "v. 修正", "level": 3, "forms": ["amendment"]},
    "amplify": {"meaning": "v. 放大", "level": 3, "forms": ["amplification"]},
    "analogy": {"meaning": "n. 类比", "level": 3, "forms": ["analogous"]},
    "anecdote": {"meaning": "n. 轶事", "level": 3, "forms": ["anecdotal"]},
    "anguish": {"meaning": "n. 极大痛苦", "level": 3, "forms": []},
    "animate": {"meaning": "v. 使有活力 adj. 有生命的", "level": 3, "forms": ["animation", "animated"]},
    "annex": {"meaning": "v. 兼并 n. 附件", "level": 3, "forms": []},
    "anonymous": {"meaning": "adj. 匿名的", "level": 3, "forms": ["anonymity"]},
    "antagonism": {"meaning": "n. 对抗", "level": 3, "forms": ["antagonist", "antagonistic"]},
    "antenna": {"meaning": "n. 天线；触角", "level": 3, "forms": ["antennae"]},
    "anthropology": {"meaning": "n. 人类学", "level": 3, "forms": ["anthropological"]},
    "antibiotic": {"meaning": "n. 抗生素 adj. 抗菌的", "level": 3, "forms": []},
    "anticipate": {"meaning": "v. 预期", "level": 3, "forms": ["anticipation"]},
    "antique": {"meaning": "adj. 古董的 n. 古董", "level": 3, "forms": []},
    "antonym": {"meaning": "n. 反义词", "level": 3, "forms": []},
    "ape": {"meaning": "n. 猿 v. 模仿", "level": 3, "forms": []},
    "apparatus": {"meaning": "n. 装置；机构", "level": 3, "forms": []},
    "appease": {"meaning": "v. 平息", "level": 3, "forms": ["appeasement"]},
    "appendix": {"meaning": "n. 阑尾；附录", "level": 3, "forms": ["appendices"]},
    "applaud": {"meaning": "v. 鼓掌；称赞", "level": 3, "forms": ["applause"]},
    "appraisal": {"meaning": "n. 评价", "level": 3, "forms": ["appraise"]},
    "apprehend": {"meaning": "v. 逮捕；理解", "level": 3, "forms": ["apprehension", "apprehensive"]},
    "appropriate": {"meaning": "v. 拨款；占用 adj. 适当的", "level": 3, "forms": ["appropriation"]},
    "apt": {"meaning": "adj. 恰当的；有...倾向的", "level": 3, "forms": []},
    "arc": {"meaning": "n. 弧", "level": 3, "forms": []},
    "arch": {"meaning": "n. 拱门 v. 拱起", "level": 3, "forms": []},
    "arena": {"meaning": "n. 竞技场", "level": 3, "forms": []},
    "aristocrat": {"meaning": "n. 贵族", "level": 3, "forms": ["aristocracy", "aristocratic"]},
    "armor": {"meaning": "n. 盔甲", "level": 3, "forms": []},
    "aroma": {"meaning": "n. 香味", "level": 3, "forms": ["aromatic"]},
    "arrogant": {"meaning": "adj. 傲慢的", "level": 3, "forms": ["arrogance"]},
    "articulate": {"meaning": "v. 清楚表达 adj. 善于表达的", "level": 3, "forms": ["articulation"]},
    "artillery": {"meaning": "n. 大炮", "level": 3, "forms": []},
    "ascend": {"meaning": "v. 上升", "level": 3, "forms": ["ascent"]},
    "ascertain": {"meaning": "v. 确定", "level": 3, "forms": []},
    "aspiration": {"meaning": "n. 渴望", "level": 3, "forms": ["aspire"]},
    "assassinate": {"meaning": "v. 暗杀", "level": 3, "forms": ["assassination", "assassin"]},
    "assault": {"meaning": "n. 攻击 v. 攻击", "level": 3, "forms": []},
    "assert": {"meaning": "v. 断言", "level": 3, "forms": ["assertion", "assertive"]},
    "assimilate": {"meaning": "v. 同化；吸收", "level": 3, "forms": ["assimilation"]},
    "astound": {"meaning": "v. 使震惊", "level": 3, "forms": ["astounding"]},
    "astronaut": {"meaning": "n. 宇航员", "level": 3, "forms": []},
    "asylum": {"meaning": "n. 庇护；精神病院", "level": 3, "forms": []},
    "atrocity": {"meaning": "n. 暴行", "level": 3, "forms": []},
    "attic": {"meaning": "n. 阁楼", "level": 3, "forms": []},
    "auction": {"meaning": "n. 拍卖 v. 拍卖", "level": 3, "forms": []},
    "audit": {"meaning": "v. 审计 n. 审计", "level": 3, "forms": []},
    "auditorium": {"meaning": "n. 礼堂", "level": 3, "forms": []},
    "augment": {"meaning": "v. 增加", "level": 3, "forms": ["augmentation"]},
    "aura": {"meaning": "n. 光环；气氛", "level": 3, "forms": []},
    "authentic": {"meaning": "adj. 真实的", "level": 3, "forms": ["authenticity", "authenticate"]},
    "autobiography": {"meaning": "n. 自传", "level": 3, "forms": ["autobiographical"]},
    "autonomy": {"meaning": "n. 自治", "level": 3, "forms": ["autonomous"]},
    "avail": {"meaning": "v. 有用 n. 效用", "level": 3, "forms": ["available"]},
    "avenge": {"meaning": "v. 报复", "level": 3, "forms": ["vengeance"]},
    "aviation": {"meaning": "n. 航空", "level": 3, "forms": []},
    "awaken": {"meaning": "v. 唤醒", "level": 3, "forms": []},
    "axe": {"meaning": "n. 斧头 v. 削减", "level": 3, "forms": []},

    # ... 更多CET6词汇
}

# ==================== 完形填空题库 ====================

CLOZE_EXERCISES = [
    {
        "id": 1,
        "sentence": "The magnificent cathedral was ___ in the 12th century.",
        "options": ["builded", "built", "building", "builds"],
        "answer": 1,
        "explanation": "被动语态 'was built' 表示'被建造于...'",
        "grammar_point": "被动语态 + 过去分词",
        "difficulty": 1,
    },
    {
        "id": 2,
        "sentence": "She has ___ finished her homework.",
        "options": ["yet", "already", "ever", "never"],
        "answer": 1,
        "explanation": "'already' 用于肯定句表示'已经'",
        "grammar_point": "现在完成时 + 副词",
        "difficulty": 1,
    },
    {
        "id": 3,
        "sentence": "The company decided to ___ the contract due to breach of terms.",
        "options": ["terminate", "determine", "examine", "maintain"],
        "answer": 0,
        "explanation": "'terminate' 意为'终止'，符合语境",
        "grammar_point": "词汇辨析 + 不定式",
        "difficulty": 2,
    },
    {
        "id": 4,
        "sentence": "If I ___ you, I would accept the offer.",
        "options": ["am", "was", "were", "be"],
        "answer": 2,
        "explanation": "虚拟语气中，if从句用were而非was",
        "grammar_point": "虚拟语气",
        "difficulty": 2,
    },
    {
        "id": 5,
        "sentence": "The research ___ that exercise improves mental health.",
        "options": ["implies", "infers", "refers", "prefers"],
        "answer": 0,
        "explanation": "'imply' 意为'暗示/表明'，符合语境",
        "grammar_point": "词汇辨析",
        "difficulty": 2,
    },
    {
        "id": 6,
        "sentence": "He apologized ___ being late for the meeting.",
        "options": ["for", "of", "to", "with"],
        "answer": 0,
        "explanation": "'apologize for' 是固定搭配",
        "grammar_point": "介词搭配",
        "difficulty": 1,
    },
    {
        "id": 7,
        "sentence": "The more you practice, ___ you become.",
        "options": ["the better", "better", "the best", "best"],
        "answer": 0,
        "explanation": "'the more...the better...' 是比较级固定句型",
        "grammar_point": "比较级句型",
        "difficulty": 1,
    },
    {
        "id": 8,
        "sentence": "The professor's lecture was so ___ that many students fell asleep.",
        "options": ["boring", "bored", "bore", "boringly"],
        "answer": 0,
        "explanation": "-ing形容词修饰事物，-ed形容词修饰人",
        "grammar_point": "分词形容词",
        "difficulty": 1,
    },
    {
        "id": 9,
        "sentence": "Neither the students nor the teacher ___ aware of the change.",
        "options": ["is", "are", "was", "were"],
        "answer": 2,
        "explanation": "'neither...nor...' 就近原则，teacher是单数",
        "grammar_point": "主谓一致",
        "difficulty": 2,
    },
    {
        "id": 10,
        "sentence": "By the time we arrived, the movie ___.",
        "options": ["has started", "had started", "started", "starts"],
        "answer": 1,
        "explanation": "'By the time + 过去时' 主句用过去完成时",
        "grammar_point": "过去完成时",
        "difficulty": 2,
    },
    {
        "id": 11,
        "sentence": "It is essential that every student ___ the exam on time.",
        "options": ["complete", "completes", "completed", "completing"],
        "answer": 0,
        "explanation": "'It is essential that...' 后用虚拟语气(should+)原形",
        "grammar_point": "虚拟语气",
        "difficulty": 3,
    },
    {
        "id": 12,
        "sentence": "The novel is worth ___.",
        "options": ["reading", "to read", "read", "being read"],
        "answer": 0,
        "explanation": "'be worth doing' 是固定用法",
        "grammar_point": "worth用法",
        "difficulty": 1,
    },
    {
        "id": 13,
        "sentence": "I regret ___ you that your application has been rejected.",
        "options": ["to inform", "informing", "inform", "informed"],
        "answer": 0,
        "explanation": "'regret to do' 表示遗憾要做某事",
        "grammar_point": "regret用法",
        "difficulty": 2,
    },
    {
        "id": 14,
        "sentence": "The number of students ___ increasing every year.",
        "options": ["is", "are", "has", "have"],
        "answer": 0,
        "explanation": "'the number of' 谓语用单数",
        "grammar_point": "主谓一致",
        "difficulty": 1,
    },
    {
        "id": 15,
        "sentence": "Had I known about the traffic, I ___ earlier.",
        "options": ["would leave", "would have left", "left", "had left"],
        "answer": 1,
        "explanation": "虚拟语气倒装，与过去事实相反用would have done",
        "grammar_point": "虚拟语气倒装",
        "difficulty": 3,
    },
    {
        "id": 16,
        "sentence": "The scientist ___ his theory with extensive experiments.",
        "options": ["proved", "improved", "approved", "moved"],
        "answer": 0,
        "explanation": "'prove' 意为'证明'，符合语境",
        "grammar_point": "词汇辨析",
        "difficulty": 1,
    },
    {
        "id": 17,
        "sentence": "It was in this room ___ the meeting was held.",
        "options": ["where", "which", "that", "what"],
        "answer": 2,
        "explanation": "强调句型 'It was...that...'",
        "grammar_point": "强调句",
        "difficulty": 2,
    },
    {
        "id": 18,
        "sentence": "Despite ___ hard, he failed the exam.",
        "options": ["studying", "to study", "study", "studied"],
        "answer": 0,
        "explanation": "'despite' 后接动名词",
        "grammar_point": "介词+动名词",
        "difficulty": 2,
    },
    {
        "id": 19,
        "sentence": "The book, ___ was written by a famous author, became a bestseller.",
        "options": ["that", "which", "who", "what"],
        "answer": 1,
        "explanation": "非限制性定语从句用which",
        "grammar_point": "定语从句",
        "difficulty": 2,
    },
    {
        "id": 20,
        "sentence": "I wish I ___ to the party last night.",
        "options": ["went", "have gone", "had gone", "go"],
        "answer": 2,
        "explanation": "'wish + 过去完成时' 表示与过去事实相反的愿望",
        "grammar_point": "wish虚拟语气",
        "difficulty": 2,
    },
]


# ==================== 词汇管理器 ====================

class VocabularyManager:
    """词汇管理器"""

    def __init__(self, cet4_words=None, cet6_words=None):
        self.cet4_words = cet4_words or CET4_WORDS
        self.cet6_words = cet6_words or CET6_WORDS
        self.all_words = {**self.cet4_words, **self.cet6_words}

        # 按难度分类
        self.words_by_level = {
            "easy": [],      # level 1
            "medium": [],    # level 2
            "hard": [],      # level 3
            "expert": [],    # level 3+
            "master": [],    # 混合
        }
        self._categorize_words()

    def _categorize_words(self):
        """按难度分类词汇"""
        for word, data in self.all_words.items():
            level = data.get("level", 1)
            if level == 1:
                self.words_by_level["easy"].append(word)
            elif level == 2:
                self.words_by_level["medium"].append(word)
            else:
                self.words_by_level["hard"].append(word)

        # expert和master混合使用
        self.words_by_level["expert"] = self.words_by_level["hard"] + self.words_by_level["medium"]
        self.words_by_level["master"] = list(self.all_words.keys())

    def get_words_by_level(self, level, count=10):
        """获取指定难度的词汇"""
        words = self.words_by_level.get(level, self.words_by_level["medium"])
        return random.sample(words, min(count, len(words)))

    def get_random_word(self, level="medium"):
        """获取随机词汇"""
        words = self.words_by_level.get(level, self.words_by_level["medium"])
        return random.choice(words) if words else None

    def get_word_data(self, word):
        """获取词汇详情"""
        return self.all_words.get(word.lower())

    def _get_form_meaning(self, form, base_word, base_meaning):
        """根据形态变化推断释义"""
        form_lower = form.lower()

        # 提取基础释义（去掉词性标记）
        base_meaning_clean = base_meaning if base_meaning else ""
        for prefix in ["v. ", "n. ", "adj. ", "adv. ", "vt. ", "vi. "]:
            base_meaning_clean = base_meaning_clean.replace(prefix, "", 1)
        base_meaning_clean = base_meaning_clean.strip()

        # 根据后缀推断释义
        if form_lower.endswith("ed"):
            if "v." in (base_meaning or ""):
                return f"v. {base_meaning_clean}（过去式）"
            return "v. ...（过去式/过去分词）"

        elif form_lower.endswith("ing"):
            if "v." in (base_meaning or ""):
                return f"v. {base_meaning_clean}（进行时）"
            return "adj. 令人...的"

        elif form_lower.endswith("ly"):
            if "adj." in (base_meaning or ""):
                return f"adv. {base_meaning_clean}地"
            return "adv. ...地"

        elif form_lower.endswith("er") or form_lower.endswith("or"):
            if "v." in (base_meaning or ""):
                return f"n. {base_meaning_clean}者"
            return "n. ...者/物"

        elif form_lower.endswith("tion") or form_lower.endswith("sion"):
            if "v." in (base_meaning or ""):
                return f"n. {base_meaning_clean}"
            return "n. ...的动作/状态"

        elif form_lower.endswith("ment"):
            if "v." in (base_meaning or ""):
                return f"n. {base_meaning_clean}"
            return "n. ...的行为/结果"

        elif form_lower.endswith("ness"):
            if "adj." in (base_meaning or ""):
                return f"n. {base_meaning_clean}"
            return "n. ...的状态/性质"

        elif form_lower.endswith("ity"):
            return "n. ...的性质/状态"

        elif form_lower.endswith("ful"):
            if "n." in (base_meaning or ""):
                return f"adj. 充满{base_meaning_clean}的"
            return "adj. 充满...的"

        elif form_lower.endswith("less"):
            if "n." in (base_meaning or ""):
                return f"adj. 缺乏{base_meaning_clean}的"
            return "adj. 缺乏...的"

        elif form_lower.endswith("able") or form_lower.endswith("ible"):
            if "v." in (base_meaning or ""):
                return f"adj. 可{base_meaning_clean}的"
            return "adj. 可...的"

        elif form_lower.endswith("ous") or form_lower.endswith("ious"):
            return "adj. 具有...的"

        elif form_lower.endswith("ive"):
            if "v." in (base_meaning or ""):
                return f"adj. {base_meaning_clean}的"
            return "adj. ...的"

        elif form_lower.endswith("al"):
            if "n." in (base_meaning or ""):
                return f"adj. {base_meaning_clean}的"
            return "adj. ...的"

        elif form_lower.endswith("ist"):
            return "n. ...主义者/专家"

        elif form_lower.endswith("ant") or form_lower.endswith("ent"):
            if "v." in (base_meaning or ""):
                return f"n. {base_meaning_clean}者"
            return "n./adj. ..."

        elif form_lower.endswith("ance") or form_lower.endswith("ence"):
            return "n. ...的状态/性质"

        elif form_lower.endswith("cy"):
            return "n. ...的状态/性质"

        elif form_lower.endswith("dom"):
            return "n. ...的状态/领域"

        elif form_lower.endswith("ship"):
            return "n. ...的状态/关系"

        elif form_lower.endswith("hood"):
            return "n. ...的状态/时期"

        elif form_lower.endswith("ish"):
            return "adj. 稍微...的"

        elif form_lower.endswith("like"):
            return "adj. 像...的"

        elif form_lower.endswith("worthy"):
            return "adj. 值得...的"

        elif form_lower.endswith("ize") or form_lower.endswith("ise"):
            return "v. 使...化"

        elif form_lower.endswith("ify"):
            return "v. 使..."

        elif form_lower.endswith("en"):
            if len(form_lower) > 4:  # 避免太短的词
                return "v. 使变得..."
            return base_meaning if base_meaning else "..."

        # 如果无法识别后缀，返回基础释义
        return base_meaning if base_meaning else "..."

    def get_word_meaning(self, word):
        """获取词汇释义"""
        data = self.get_word_data(word)
        return data["meaning"] if data else None

    def get_meaning_options(self, correct_meaning, correct_word=None, count=4):
        """
        生成释义选择题选项

        Args:
            correct_meaning: 正确的释义
            correct_word: 正确的单词（用于排除）
            count: 选项数量（默认4个）

        Returns:
            list: 打乱后的选项列表，包含正确答案
        """
        # 收集其他单词的释义作为干扰项
        other_meanings = []
        for word, data in self.all_words.items():
            if word != correct_word:
                meaning = data.get("meaning", "")
                if meaning and meaning != correct_meaning:
                    other_meanings.append(meaning)

        # 随机选择干扰项
        import random
        wrong_count = count - 1
        if len(other_meanings) >= wrong_count:
            wrong_options = random.sample(other_meanings, wrong_count)
        else:
            wrong_options = other_meanings

        # 组合选项并打乱
        options = [correct_meaning] + wrong_options
        random.shuffle(options)

        return options

    def search_words(self, keyword, limit=10):
        """搜索词汇"""
        keyword = keyword.lower()
        results = []
        for word, data in self.all_words.items():
            if keyword in word.lower() or keyword in data["meaning"].lower():
                results.append((word, data))
                if len(results) >= limit:
                    break
        return results

    def get_battle_words(self, level, count=5):
        """获取战斗用词汇（用于Boss战）"""
        words = self.get_words_by_level(level, count)
        result = []
        for word in words:
            data = self.get_word_data(word)
            result.append({
                "word": word,
                "meaning": data["meaning"] if data else "",
                "forms": data.get("forms", []) if data else []
            })
        return result

    def get_quiz_question(self, quiz_type="en_to_cn", level="medium"):
        """
        获取选择题

        Args:
            quiz_type: 题目类型
                - "en_to_cn": 英文选中文
                - "cn_to_en": 中文选英文
                - "form": 单词形态选择
            level: 难度

        Returns:
            dict: 包含题目、选项、答案的字典
        """
        word = self.get_random_word(level)
        if not word:
            return None

        data = self.get_word_data(word)
        if not data:
            return None

        if quiz_type == "en_to_cn":
            # 英文选中文
            correct_answer = data["meaning"]
            # 生成干扰项
            other_words = random.sample(
                [w for w in self.all_words if w != word],
                min(3, len(self.all_words) - 1)
            )
            wrong_options = [self.all_words[w]["meaning"] for w in other_words]
            options = [correct_answer] + wrong_options
            random.shuffle(options)

            return {
                "type": "en_to_cn",
                "question": word,
                "options": options,
                "answer": correct_answer,
                "answer_index": options.index(correct_answer)
            }

        elif quiz_type == "cn_to_en":
            # 中文选英文
            correct_answer = word
            meaning = data["meaning"]
            # 生成干扰项
            other_words = random.sample(
                [w for w in self.all_words if w != word],
                min(3, len(self.all_words) - 1)
            )
            options = [word] + other_words
            random.shuffle(options)

            return {
                "type": "cn_to_en",
                "question": meaning,
                "options": options,
                "answer": correct_answer,
                "answer_index": options.index(correct_answer)
            }

        elif quiz_type == "form":
            # 单词形态选择
            forms = data.get("forms", [])
            if not forms:
                # 如果没有形态变化，改用其他题型
                return self.get_quiz_question("en_to_cn", level)

            base_word = word
            base_meaning = data["meaning"]
            correct_form = random.choice(forms)

            # 构建正确答案（带释义）
            correct_form_meaning = self._get_form_meaning(correct_form, base_word, base_meaning)
            correct_answer_display = f"{correct_form}  {correct_form_meaning}"

            # 生成干扰项（带释义）
            all_forms_with_meaning = []
            for w, d in self.all_words.items():
                for f in d.get("forms", []):
                    if f != correct_form:
                        form_meaning = self._get_form_meaning(f, w, d["meaning"])
                        all_forms_with_meaning.append((f, form_meaning))

            # 随机选择3个干扰项
            wrong_options_data = random.sample(all_forms_with_meaning, min(3, len(all_forms_with_meaning)))
            wrong_options_display = [f"{f}  {m}" for f, m in wrong_options_data]

            options = [correct_answer_display] + wrong_options_display
            random.shuffle(options)

            return {
                "type": "form",
                "question": f"{base_word} 的变形是?",
                "base_meaning": base_meaning,
                "options": options,
                "answer": correct_answer_display,
                "answer_word": correct_form,  # 用于学习模式
                "answer_index": options.index(correct_answer_display)
            }

        return None

    def get_cloze_question(self, difficulty=None):
        """获取完形填空题"""
        if difficulty:
            exercises = [e for e in CLOZE_EXERCISES if e["difficulty"] <= difficulty]
        else:
            exercises = CLOZE_EXERCISES

        if not exercises:
            exercises = CLOZE_EXERCISES

        return random.choice(exercises)


# ==================== 单词列表展示 ====================

def display_word_list(words, vocabulary_manager, columns=3):
    """展示单词列表"""
    lines = []
    for i in range(0, len(words), columns):
        row_words = words[i:i+columns]
        row = ""
        for word in row_words:
            data = vocabulary_manager.get_word_data(word)
            if data:
                row += f"  {c(word, DarkTheme.SOUL_BLUE):20}"
        if row:
            lines.append(row)
    return "\n".join(lines)


# 辅助导入
from ui import c, DarkTheme
