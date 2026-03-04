#!/usr/bin/env python3
"""
🎓 苏格拉底训练Agent
- crypto-market-rank 获取行情数据
- trading-signal 生成情景题
- 针对用户弱点定制训练，AI反问引导改变思维
"""

import random
from datetime import datetime, timezone


class SocratesTrainerAgent:
    """苏格拉底训练：不给答案，只教你思考"""

    # 针对不同人格类型的训练场景库
    SCENARIOS = {
        "追涨杀跌型": [
            {
                "scene": "BTC刚刚在1小时内暴涨8%，Twitter上全是FOMO情绪，你的朋友说'这波不上车就亏大了'",
                "market_context": "BTC日线强势，但RSI已超买80，成交量放大3倍",
                "question": "你现在最想做什么操作？为什么？",
                "followups": [
                    "如果这是一个假突破，你的止损在哪？",
                    "追进去的胜率历史上是多少？",
                    "等回调再买会损失多少机会？损失多少又能接受？"
                ],
                "trap": "FOMO追涨"
            },
            {
                "scene": "你持有的ETH跌了15%，红色K线一根接一根，社群里开始有人喊'要归零了'",
                "market_context": "ETH跌至关键支撑位，成交量萎缩，大盘整体下跌",
                "question": "你现在的第一反应是什么？止损还是补仓还是观望？",
                "followups": [
                    "你当初买的逻辑还成立吗？",
                    "这次下跌是市场结构破坏还是正常回调？",
                    "如果再跌15%，你的底线是什么？"
                ],
                "trap": "恐慌止损"
            }
        ],
        "重仓赌徒型": [
            {
                "scene": "你看好一个信号，想把账户70%的资金压进去，感觉'这次稳了'",
                "market_context": "信号胜率历史55%，盈亏比1.5:1",
                "question": "70%仓位，这个决定的依据是什么？",
                "followups": [
                    "如果这笔亏了，下一笔你还能正常交易吗？",
                    "凯利公式算出的最优仓位是多少？",
                    "你上次'感觉稳了'的结果是什么？"
                ],
                "trap": "过度集中仓位"
            }
        ],
        "止损混乱型": [
            {
                "scene": "你开了一笔多单，设了1%的止损，结果被插针扫了，价格又回来了",
                "market_context": "BTC 4小时震荡行情，ATR平均波幅2.5%",
                "question": "这次止损是对的还是错的？",
                "followups": [
                    "1%止损和当前市场波幅的关系是什么？",
                    "止损位应该基于什么来设定？",
                    "宁愿被扫还是拿着不动，你的逻辑是什么？"
                ],
                "trap": "止损太近"
            }
        ],
        "过度交易型": [
            {
                "scene": "今天已经交易了8次，账户微亏，但你发现了一个新信号想再开一笔",
                "market_context": "今日手续费已消耗$23，净亏损$15",
                "question": "第9笔交易，你的开仓理由是什么？",
                "followups": [
                    "如果今天一笔都不交易，结果会更好吗？",
                    "手续费成本你算进去了吗？",
                    "这个信号和前8次有什么本质不同？"
                ],
                "trap": "手痒过度交易"
            }
        ],
        "纪律交易型": [
            {
                "scene": "你的策略给出信号，但你觉得宏观环境不对，想跳过这次",
                "market_context": "策略历史胜率63%，你已跳过3次信号，其中2次是盈利的",
                "question": "用直觉覆盖系统信号，这是进步还是退步？",
                "followups": [
                    "你的宏观判断有多少次是准确的？",
                    "如果每次都能自由覆盖，策略还有意义吗？",
                    "怎么区分'有依据的跳过'和'情绪化跳过'？"
                ],
                "trap": "过度主观干预系统"
            }
        ]
    }

    def __init__(self, mirror_result: dict):
        self.mirror_result = mirror_result
        self.personality_type = mirror_result.get("personality_type", "止损混乱型")

    def _get_market_context(self) -> dict:
        """
        模拟 crypto-market-rank + trading-signal 数据
        真实调用: crypto-market-rank获取涨跌幅榜, trading-signal获取当前信号
        """
        cryptos = ["BTC", "ETH", "BNB", "SOL", "DOGE"]
        rankings = []
        for i, c in enumerate(cryptos):
            change = random.uniform(-8, 12)
            rankings.append({
                "rank": i + 1,
                "symbol": c,
                "change_24h": round(change, 2),
                "trend": "上涨" if change > 0 else "下跌"
            })

        # trading-signal 当前信号
        signal = {
            "symbol": "BTCUSDT",
            "direction": random.choice(["LONG", "SHORT", "NEUTRAL"]),
            "strength": random.choice(["强", "中", "弱"]),
            "rsi": round(random.uniform(30, 75), 1),
            "trend": random.choice(["上升趋势", "下降趋势", "震荡"]),
        }

        return {"rankings": rankings, "signal": signal}

    def generate_question(self) -> dict:
        """生成今日苏格拉底训练题"""
        print(f"  → 调用 crypto-market-rank 获取行情数据...")
        market = self._get_market_context()

        print(f"  → 调用 trading-signal 生成情景题...")
        scenarios = self.SCENARIOS.get(self.personality_type,
                                       self.SCENARIOS["止损混乱型"])
        scenario = random.choice(scenarios)

        # 根据当前行情动态调整情景
        top_mover = max(market["rankings"], key=lambda x: abs(x["change_24h"]))
        signal = market["signal"]

        result = {
            "personality_type": self.personality_type,
            "scenario": scenario["scene"],
            "market_context": f"{scenario['market_context']} | 今日{top_mover['symbol']} {top_mover['change_24h']:+.1f}% | 当前{signal['symbol']}信号:{signal['direction']}({signal['strength']})",
            "main_question": scenario["question"],
            "followup_questions": scenario["followups"],
            "common_trap": scenario["trap"],
            "hint": "💡 先回答主问题，AI会根据你的回答追问",
            "format": "今日训练",
            "market_snapshot": market,
        }

        print(f"  ✅ 训练场景: {scenario['trap']} | 针对: {self.personality_type}")
        return result
