#!/usr/bin/env python3
"""
每日推送主程序 - 北京22:00自动运行
整合所有子Agent输出，生成并推送日报

Skills调用声明：
  - binance-pro skill     → 交易记录/Earn产品（live模式）
  - spot skill            → 实时价格/行情
  - crypto-market-rank   → 社交热度榜
  - trading-signal       → 智能钱信号
  - square-oracle        → 今日广场选题推荐
"""
import sys, os, json
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "agents/risk-mirror"))
sys.path.insert(0, os.path.join(BASE, "agents/earn-map"))
sys.path.insert(0, os.path.join(BASE, "agents/contract-coach"))
sys.path.insert(0, os.path.join(BASE, "agents/challenge"))
sys.path.insert(0, os.path.join(BASE, "agents"))

from risk_mirror import generate_report as risk_report
from earn_map import generate_earn_map
from contract_coach import generate_coach_report
from challenge_generator import get_demo_content
from binance_skills import check_skill_status, skill_get_smart_money_signals, skill_get_social_hype

# 检测模式
status = check_skill_status()
MODE = "live" if status["has_key"] else "demo"

def get_smart_money_section():
    """trading-signal skill - 智能钱信号板块"""
    signals, err = skill_get_smart_money_signals("56", limit=3)
    if not signals:
        return ""
    lines = ["", "💰 智能钱信号（trading-signal skill）", "─" * 35]
    for s in signals:
        status_emoji = "🟢" if s["status"] == "active" else "⚪"
        lines.append(f"{status_emoji} {s['ticker']} {s['direction'].upper()} "
                     f"| 最大涨幅:{s['max_gain']}% | 退出率:{s['exit_rate']}%")
    return "\n".join(lines)

def get_social_section():
    """crypto-market-rank skill - 今日社交热度"""
    hype, err = skill_get_social_hype("56", limit=5)
    if not hype:
        return ""
    lines = ["", "🔥 今日社交热度（crypto-market-rank skill）", "─" * 35]
    for h in hype[:5]:
        lines.append(f"  #{h['symbol']}  热度:{h['hype']:,}  {h.get('sentiment','')}")
    return "\n".join(lines)

def build_daily_report(challenge_day=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"🦞 我的币安人生 · 每日成长报告",
        f"📅 {now} (北京时间)",
        f"模式: {'🔐 live（binance-pro skill）' if MODE == 'live' else '📊 演示模式'}",
        "=" * 40,
        "",
        # ① 风险镜子 → binance-pro skill
        risk_report(mode=MODE),
        "",
        # ② 收益地图 → binance-pro/simple-earn
        generate_earn_map(trader_type="aggressive", total_idle_usdt=1000, mode=MODE),
        "",
        # ③ 合约复盘 → binance-pro/fapi
        generate_coach_report(mode=MODE),
        "",
        # ④ 智能钱信号 → trading-signal skill
        get_smart_money_section(),
        "",
        # ⑤ 社交热度 → crypto-market-rank skill
        get_social_section(),
        "",
        "=" * 40,
        "✅ 明日22:00继续推送",
    ]

    # ⑥ 7日挑战板块（可选）
    if challenge_day:
        lines += ["", f"📅 7日挑战 Day{challenge_day}", get_demo_content(challenge_day)]

    return "\n".join(str(l) for l in lines)

if __name__ == "__main__":
    from datetime import date
    day_of_challenge = (date.today() - date(2026, 3, 4)).days + 1
    day_of_challenge = max(1, min(7, day_of_challenge))

    print(f"[daily_push] 模式={MODE} | 挑战Day={day_of_challenge} | {datetime.now().isoformat()}")
    report = build_daily_report(challenge_day=day_of_challenge)
    print(report[:600] + "\n...[TRUNCATED]")

    out_path = os.path.join(BASE, f"reports/report_{datetime.now().strftime('%Y%m%d')}.txt")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(report)
    print(f"✅ 报告已保存: {out_path}")
