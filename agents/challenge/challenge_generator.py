#!/usr/bin/env python3
"""
7日广场挑战 - 每日内容生成器
用户自愿开启，Agent辅助生成每天广场发布内容
"""

from datetime import datetime

CHALLENGE_TEMPLATES = {
    1: {
        "title": "Day1：AI帮我照了一面镜子",
        "template": """🦞 #AIBinance 7日成长挑战 · Day1

今天用OpenClaw的AI Agent分析了我过去的交易记录，结果让我有点意外——

AI告诉我：我是「{trader_type}」类型的交易者

现货分析：
• 胜率：{win_rate}%
• 平均持仓：{hold_days}天
• 交易风格：{spot_style}

合约分析：
• 惯用杠杆：{avg_leverage}x
• 致命弱点：{weakness}

说实话，这些数据摆出来有点扎心 😅

但知道了弱点才能改，接下来7天我会用AI来优化策略，每天同步进展。

你也来照照镜子？→ 评论区留言

#币安广场 #AI交易 #OpenClaw"""
    },
    2: {
        "title": "Day2：发现我的钱一直放错地方了",
        "template": """🦞 #AIBinance 7日成长挑战 · Day2

AI今天帮我算了一笔账，算完我沉默了……

我有{idle_amount} USDT一直躺在现货钱包里
年化收益：0%

AI给出的最优配置：
{allocation_summary}

综合年化：{total_apy}%
每年多赚：+{annual_gain} USDT
每天少赚：{daily_loss} USDT 💸

就这么白白躺着……已经把钱存进去了

你的闲置资金放哪里？

#币安广场 #理财 #BeMore"""
    },
    3: {
        "title": "Day3：AI拆解了我最惨的一笔亏损",
        "template": """🦞 #AIBinance 7日成长挑战 · Day3

把最痛的一笔交易交给AI分析……

那次亏损：{worst_loss} USDT

AI的诊断：
❌ 问题1：{issue_1}
❌ 问题2：{issue_2}
❌ 问题3：{issue_3}

每一条都说到心坎里了

AI给的改进方案：
✅ {fix_1}
✅ {fix_2}

今天开始执行，明天反馈结果

你有没有一笔亏损反复想起来？

#币安广场 #交易复盘 #成长"""
    },
    4: {
        "title": "Day4：按AI策略执行的第一天",
        "template": """🦞 #AIBinance 7日成长挑战 · Day4

按照AI优化后的策略实操了一天

今日执行情况：
📊 模拟盘战绩：{sim_pnl} USDT
✅ 止损纪律：执行{stop_loss_rate}%
🎯 入场条件：严格按信号开仓

最大的改变：不再因为"感觉"开仓了
等信号，等条件，再动

和之前对比，心态稳了很多

明天继续

#币安广场 #量化思维 #AIBinance"""
    },
    5: {
        "title": "Day5：AI出了道题，我答错了",
        "template": """🦞 #AIBinance 7日成长挑战 · Day5

今天AI给我出了个情景题：

「{scenario}」

你会怎么选？

我的答案：{my_answer}
AI说：❌ 错了

正确思路：{correct_thinking}

这种问法真的能暴露思维盲区
感觉比直接告诉我答案更有效

你来答一下这道题？评论区见

#币安广场 #交易思维 #AIBinance"""
    },
    6: {
        "title": "Day6：模拟盘 vs 实盘对比",
        "template": """🦞 #AIBinance 7日成长挑战 · Day6

经过5天的AI策略优化，来看看数据对比：

模拟盘（AI策略）：
• 累计收益：+{sim_total_pnl} USDT
• 胜率：{sim_win_rate}%
• 最大回撤：{sim_drawdown}%

参考旧习惯（估算）：
• 累计收益：{old_pnl} USDT
• 胜率：{old_win_rate}%

差距：{diff} USDT

明天是最后一天，再照一次镜子看成长

#币安广场 #数据说话 #AIBinance"""
    },
    7: {
        "title": "Day7：7天后再照一次镜子",
        "template": """🦞 #AIBinance 7日成长挑战 · Day7 完结✅

7天前 vs 现在：

交易者类型：{old_type} → {new_tendency}
止损执行率：{old_sl}% → {new_sl}%
情绪化交易：{old_emotion}次 → {new_emotion}次
模拟盘累计：+{total_sim_pnl} USDT

改变不是一夜之间的
但7天能让你看清方向

感谢 @binancezh 这次比赛的机会
感谢 OpenClaw 让AI成为交易搭档

你也来试试？

#AIBinance #OpenClaw #币安广场 #7日挑战"""
    },
}

def generate_day_content(day: int, user_data: dict) -> str:
    """生成指定天的广场内容"""
    if day not in CHALLENGE_TEMPLATES:
        return "无效的天数"
    
    template = CHALLENGE_TEMPLATES[day]
    try:
        content = template["template"].format(**user_data)
    except KeyError:
        content = template["template"]  # 数据不足时返回原始模板
    
    return f"📝 {template['title']}\n\n{content}"

def get_demo_content(day: int) -> str:
    """用演示数据生成内容"""
    demo_data = {
        "trader_type": "🚀 进取型",
        "win_rate": "50.0",
        "hold_days": "3.2",
        "spot_style": "分散持仓，短线偏多",
        "avg_leverage": "12",
        "weakness": "情绪化交易，止损纪律差",
        "idle_amount": "1000",
        "allocation_summary": "  Launchpool 50% + BNB Vault 30% + 定期理财 20%",
        "total_apy": "10.8",
        "annual_gain": "108",
        "daily_loss": "0.3",
        "worst_loss": "850",
        "issue_1": "20倍杠杆开仓，风控完全失效",
        "issue_2": "没有设置止损，任由亏损扩大",
        "issue_3": "情绪化追跌加仓，越套越深",
        "fix_1": "杠杆上限调整为5倍",
        "fix_2": "每笔交易必须先设止损再开仓",
        "sim_pnl": "+127",
        "stop_loss_rate": "100",
        "scenario": "BTC突然暴跌8%，你的多单已亏损15%，此时你会？A.加仓摊平 B.止损出场 C.持仓等待",
        "my_answer": "C.持仓等待",
        "correct_thinking": "B.止损出场。趋势改变时，持仓等待会让亏损继续扩大，止损保留子弹才是正解。",
        "sim_total_pnl": "+340",
        "sim_win_rate": "68",
        "sim_drawdown": "4.2",
        "old_pnl": "-180",
        "old_win_rate": "45",
        "diff": "520",
        "old_type": "🚀 进取型（高危）",
        "new_tendency": "🎯 平衡型（改善中）",
        "old_sl": "20",
        "new_sl": "95",
        "old_emotion": "12",
        "new_emotion": "2",
        "total_sim_pnl": "+340",
    }
    return get_demo_content_with_data(day, demo_data)

def get_demo_content_with_data(day: int, data: dict) -> str:
    return generate_day_content(day, data)

if __name__ == "__main__":
    for day in range(1, 8):
        print(f"\n{'='*50}")
        print(get_demo_content(day))
