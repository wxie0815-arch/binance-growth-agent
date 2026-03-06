#!/usr/bin/env python3
"""苏格拉底训练 - 针对交易弱点出情景题，AI反问引导改变思维"""

from datetime import datetime
import random

# 按弱点类型设计情景题库
SCENARIOS = {
    "no_stoploss": [
        {
            "scene": "你重仓做多BTC，开仓后跌了8%，此时你会？\nA. 加仓摊平成本\nB. 继续持仓等反弹\nC. 按计划止损出场",
            "wrong": ["A", "B"],
            "right": "C",
            "wrong_feedback": "❌ 错了。亏损时加仓或死扛，是让小亏变大亏的最快方式。",
            "socrates": "你为什么不愿意止损？是因为承认亏损让你很难受，还是你真的认为会反弹？",
            "insight": "止损不是认输，是保留下次翻盘的子弹。100U止损出场，和账号归零的区别就在这一刀。",
        },
        {
            "scene": "你开仓前没设止损，现在已经亏了15%，你会？\nA. 现在设止损\nB. 继续等，成本太高了\nC. 直接平仓认亏",
            "wrong": ["B"],
            "right": "A或C",
            "wrong_feedback": "❌ 错了。'成本太高'是沉没成本谬误，市场不管你的成本在哪里。",
            "socrates": "如果这15%不是亏损，而是你现在刚要开仓，你还会进这个方向吗？",
            "insight": "忘记你的开仓价，用现在的价格重新判断方向。答案变了，就该行动。",
        },
    ],
    "emotion_add": [
        {
            "scene": "你刚亏了200U，感觉市场要反转了，想立刻加倍开仓扳回来。你会？\nA. 立刻开仓，机会不等人\nB. 等至少1小时冷静期再做决定\nC. 看看止损再说",
            "wrong": ["A"],
            "right": "B",
            "wrong_feedback": "❌ 错了。刚亏完立刻想翻本，这不是机会，是情绪在驱动你。",
            "socrates": "你说'感觉要反转了'，这个感觉的依据是什么？是图表信号还是你不想认亏的心理？",
            "insight": "情绪化交易最大的特点：你觉得越确定，实际上越危险。强制冷静60分钟，保护你的账号。",
        },
    ],
    "over_leverage": [
        {
            "scene": "你判断BTC今天必涨，想用20倍杠杆放大收益。你会？\nA. 上20倍，判断准了收益最大化\nB. 用5倍，控制风险\nC. 用3倍，留足空间",
            "wrong": ["A"],
            "right": "B或C",
            "wrong_feedback": "❌ 错了。20倍杠杆只需要5%的波动就能让你爆仓，判断再准也扛不住短期波动。",
            "socrates": "你说'必涨'，如果市场先跌3%再涨呢？20倍杠杆下你还在场吗？",
            "insight": "高杠杆不是倍数收益，是把控制权交给市场。活下去才能等到你判断正确的那一天。",
        },
    ],
}

def get_scenario(weakness_type: str) -> dict:
    pool = SCENARIOS.get(weakness_type, SCENARIOS["no_stoploss"])
    return random.choice(pool)

def generate_training(weakness_type="no_stoploss", user_answer=None) -> str:
    scenario = get_scenario(weakness_type)
    lines = [
        f"🎓 苏格拉底训练",
        f"针对弱点：{weakness_type}",
        f"{'='*40}",
        f"",
        f"📌 情景题：",
        f"{scenario['scene']}",
        f"",
    ]
    if user_answer:
        if user_answer.upper() in scenario["wrong"]:
            lines += [
                scenario["wrong_feedback"],
                f"",
                f"🤔 苏格拉底反问：",
                f"{scenario['socrates']}",
                f"",
                f"💡 核心洞见：",
                f"{scenario['insight']}",
            ]
        else:
            lines += [
                f"✅ 答对了！",
                f"",
                f"💡 深入思考：",
                f"{scenario['insight']}",
                f"",
                f"🤔 进一步反问：",
                f"{scenario['socrates']}",
            ]
    else:
        lines.append("（等待用户回答...）")
    return "\n".join(lines)

if __name__ == "__main__":
    print(generate_training("over_leverage", user_answer="A"))
