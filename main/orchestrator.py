#!/usr/bin/env python3
"""
主Agent调度器 - 统一入口，分发给4个子Agent，汇总输出
每日22:00自动推送汇总报告
"""

import sys, os
from datetime import datetime

# 子Agent路径
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "../agents/risk-mirror"))
sys.path.insert(0, os.path.join(BASE, "../agents/earn-map"))
sys.path.insert(0, os.path.join(BASE, "../agents/contract-coach"))
sys.path.insert(0, os.path.join(BASE, "../agents/socrates"))
sys.path.insert(0, os.path.join(BASE, "../agents/challenge"))

from risk_mirror import generate_report as risk_report
from earn_map import generate_earn_map
from contract_coach import generate_coach_report
from socrates import generate_training
from challenge_generator import get_demo_content

def run_full_analysis(mode="demo", api_key=None, api_secret=None,
                      challenge_day=None, trader_type="aggressive"):
    """
    主入口：运行完整分析流程
    mode: "demo"（模拟盘演示）或 "live"（真实API）
    challenge_day: None=不开启7日挑战，1-7=当天挑战
    """
    print(f"\n{'🦞'*20}")
    print(f"  我的币安人生")
    print(f"  Powered by OpenClaw · Power × XieXiu")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')} CST")
    print(f"{'🦞'*20}\n")

    # ① 风险镜子
    print("=" * 50)
    print(risk_report(mode=mode, api_key=api_key, api_secret=api_secret))

    # ② 收益地图
    print("\n" + "=" * 50)
    print(generate_earn_map(trader_type=trader_type, total_idle_usdt=1000))

    # ③ 合约复盘
    print("\n" + "=" * 50)
    print(generate_coach_report(mode=mode))

    # ④ 苏格拉底训练
    print("\n" + "=" * 50)
    print(generate_training("over_leverage"))

    # ⑤ 7日挑战（可选）
    if challenge_day:
        print("\n" + "=" * 50)
        print(f"📅 今天是7日挑战 Day{challenge_day}")
        print(get_demo_content(challenge_day))

    # 汇总
    print(f"\n{'='*50}")
    print(f"✅ 今日成长报告生成完毕")
    print(f"明日22:00将自动推送下一份报告")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    # 演示：全流程 + Day1挑战
    run_full_analysis(mode="demo", challenge_day=1, trader_type="aggressive")
