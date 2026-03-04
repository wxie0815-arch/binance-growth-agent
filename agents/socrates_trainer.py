#!/usr/bin/env python3
"""
🎓 苏格拉底训练Agent — 不给信号，只教你思考
"""

from datetime import datetime
import random


QUESTION_BANK = [
    {
        "scenario": "BTC刚刚突破前高，你的仓位显示盈利15%。此时市场情绪极度贪婪，各大KOL纷纷喊10万。",
        "question": "你现在最想做什么？为什么？",
        "weakness_target": "追涨杀跌型",
        "follow_ups": [
            "如果你选择继续持有，你的止盈在哪里？依据是什么？",
            "如果你选择加仓，这笔加仓的止损在哪里？",
            "贪婪指数极度贪婪时，历史上发生了什么？"
        ],
        "insight": "突破前高时往往是散户最兴奋的时刻，也是主力最容易分发的时刻。你的决策是被情绪驱动，还是被计划驱动？"
    },
    {
        "scenario": "你做空BTC，入场@72000，止损设在73500。现在价格到了73200，距离止损只差300刀，但你觉得行情马上要回落。",
        "question": "你会移动止损，还是坚持原计划？",
        "weakness_target": "止损恐惧型",
        "follow_ups": [
            "你觉得行情会回落的依据是什么？是数据还是感觉？",
            "如果你移了止损，上次你也这么做，结果怎样？",
            "止损被触发代表失败，还是代表你的计划在正常运作？"
        ],
        "insight": "移动止损是亏损扩大的头号原因。开仓前设的止损是理性时刻的判断，被触发时的冲动是情绪时刻的判断。你更信任哪个自己？"
    },
    {
        "scenario": "你刚刚爆了一笔大亏损，损失了5000U。你的账户还剩15000U，你现在情绪很差。",
        "question": "接下来你最可能做什么？",
        "weakness_target": "重仓赌博型",
        "follow_ups": [
            "如果你想立刻开仓'把亏损赚回来'，这个想法从哪里来？",
            "报复性交易和正常交易，在心理状态上有什么区别？",
            "历史上你在大亏之后立刻开的仓，结果通常如何？"
        ],
        "insight": "报复性交易是交易者最危险的状态。亏损后的冲动来自你的情绪，不是来自市场。市场不欠你的钱。"
    },
    {
        "scenario": "某山寨币过去3天涨了200%，你一直在旁边看。现在它回调了20%，你认为是上车机会。",
        "question": "你会买入吗？你的逻辑是什么？",
        "weakness_target": "追涨杀跌型",
        "follow_ups": [
            "你对这个项目的基本面了解多少？",
            "如果它再跌50%，你的应对预案是什么？",
            "你是因为'害怕错过'而买，还是因为'有明确判断'而买？"
        ],
        "insight": "所有人都在说'回调就是机会'，但没有人说清楚是哪个回调。FOMO（错过恐惧）是散户最大的敌人。"
    },
    {
        "scenario": "你用了10倍杠杆开了一笔合约，持仓占你总资金的50%。行情正在往你预期的方向走，但波动很大。",
        "question": "你觉得这笔仓位的风险合理吗？",
        "weakness_target": "重仓赌博型",
        "follow_ups": [
            "如果这笔仓位爆仓，对你的总资产影响是多少？",
            "你是否有能力在任何情况下承受这个损失？",
            "赢了你会怎么想？输了你会怎么想？两种情绪是否对称？"
        ],
        "insight": "仓位管理不是保守，是生存。活着才能等到好机会。每次all-in都是在赌自己不犯错，但市场会让每个人都犯错。"
    }
]


class SocratesTrainerAgent:
    def __init__(self, mirror_result: dict):
        self.trader_type = mirror_result.get('trader_type', '')
        self.weaknesses = mirror_result.get('weaknesses', [])

    def generate_question(self) -> dict:
        # 优先选择针对用户弱点的题目
        targeted = [q for q in QUESTION_BANK if q['weakness_target'] == self.trader_type]
        question = targeted[0] if targeted else random.choice(QUESTION_BANK)

        return {
            "today_scenario": question['scenario'],
            "core_question": question['question'],
            "follow_up_questions": question['follow_ups'],
            "insight": question['insight'],
            "weakness_targeted": self.trader_type,
            "instructions": "先认真思考，写下你的答案。不要直接看insight。",
            "training_tip": "每天一题，7天后你看市场的方式会不同",
            "generated_at": datetime.utcnow().isoformat()
        }
