#!/usr/bin/env python3
"""
每日推送主程序 - 北京22:00自动运行
整合4个子Agent输出，生成并推送日报
"""
import sys, os, json
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "agents/risk-mirror"))
sys.path.insert(0, os.path.join(BASE, "agents/earn-map"))
sys.path.insert(0, os.path.join(BASE, "agents/contract-coach"))
sys.path.insert(0, os.path.join(BASE, "agents/challenge"))

from risk_mirror import generate_report as risk_report
from earn_map import generate_earn_map
from contract_coach import generate_coach_report
from challenge_generator import get_demo_content

# 尝试接入真实API
try:
    sys.path.insert(0, BASE)
    from agents.real_api import load_keys, get_spot_trades, get_futures_positions
    api_key, secret = load_keys()
    MODE = "live" if api_key else "demo"
except:
    MODE = "demo"

def build_daily_report():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"🦞 我的币安人生 · 每日成长报告",
        f"📅 {now} (北京时间)",
        f"模式: {'🔐 真实数据' if MODE == 'live' else '📊 演示模式'}",
        "=" * 40,
        "",
        risk_report(mode=MODE),
        "",
        generate_earn_map(trader_type="aggressive", total_idle_usdt=1000),
        "",
        generate_coach_report(mode=MODE),
        "",
        "=" * 40,
        "✅ 明日22:00继续推送",
    ]
    return "\n".join(lines)

if __name__ == "__main__":
    print(f"[daily_push] 模式={MODE}, 时间={datetime.now().isoformat()}")
    report = build_daily_report()
    print(report[:500] + "...\n[TRUNCATED]")

    # 保存到本地
    out_path = os.path.join(BASE, f"reports/report_{datetime.now().strftime('%Y%m%d')}.txt")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(report)
    print(f"✅ 报告已保存: {out_path}")
