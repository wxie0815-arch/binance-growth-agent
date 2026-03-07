#!/usr/bin/env python3
"""
主Agent调度器 - 统一入口，分发给4个子Agent，汇总输出
每日22:00自动推送汇总报告

Skills调用声明：
  demo模式: 使用db/simulator.py模拟数据
  live模式:
    - binance-pro skill → 现货交易记录 (myTrades)
    - binance-pro skill → 合约交易记录 (fapi/userTrades)
    - binance-pro skill → 合约持仓     (fapi/positionRisk)
    - binance-pro skill → Earn产品列表  (simple-earn/flexible)
    - spot skill        → 账户余额      (account)
    - spot skill        → 实时价格      (ticker/price, ticker/24hr)
"""

import sys, os, argparse
from datetime import datetime

# 子Agent路径
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "../agents/risk-mirror"))
sys.path.insert(0, os.path.join(BASE, "../agents/earn-map"))
sys.path.insert(0, os.path.join(BASE, "../agents/contract-coach"))
sys.path.insert(0, os.path.join(BASE, "../agents/socrates"))
sys.path.insert(0, os.path.join(BASE, "../agents/challenge"))
sys.path.insert(0, os.path.join(BASE, "../agents"))

from risk_mirror import generate_report as risk_report
from earn_map import generate_earn_map
from contract_coach import generate_coach_report
from socrates import generate_training
from challenge_generator import get_demo_content

def run_full_analysis(mode="demo", api_key=None, api_secret=None,
                      challenge_day=None, trader_type="aggressive"):
    """
    主入口：运行完整分析流程
    mode: "demo"（模拟盘演示）或 "live"（真实API，调用官方skills）
    challenge_day: None=不开启7日挑战，1-7=当天挑战
    """
    print(f"\n{'🦞'*20}")
    print(f"  我的币安人生")
    print(f"  Powered by OpenClaw · XieXiu × 芒果")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')} CST")
    print(f"  模式: {'🔐 live（真实skill调用）' if mode=='live' else '📊 demo（模拟盘）'}")
    print(f"{'🦞'*20}\n")

    # live模式先做skill连通性检查
    if mode == "live":
        from binance_skills import check_skill_status
        status = check_skill_status()
        if not status["has_key"]:
            print("⚠️  未检测到API Key，自动降级为demo模式")
            print("   配置方式: ~/.openclaw/credentials/binance.json")
            print("   格式: {\"apiKey\": \"...\", \"secretKey\": \"...\"}\n")
            mode = "demo"
        else:
            print(f"✅ binance-pro skill 已连接 | Key: {status['key_preview']}")
            print(f"✅ spot skill 公开接口 | BTC: ${status.get('btc_price','N/A')}")
            print(f"✅ 热门代币: {', '.join(status.get('top_movers',[]))[:50]}\n")

    # ① 风险镜子 → binance-pro/myTrades + fapi/userTrades
    print("=" * 50)
    print(risk_report(mode=mode, api_key=api_key, api_secret=api_secret))

    # ② 收益地图 → binance-pro/simple-earn/flexible
    print("\n" + "=" * 50)
    print(generate_earn_map(trader_type=trader_type, total_idle_usdt=1000, mode=mode))

    # ③ 合约复盘 → binance-pro/fapi/userTrades
    print("\n" + "=" * 50)
    print(generate_coach_report(mode=mode))

    # ④ 苏格拉底训练（逻辑推理，无需API）
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
    parser = argparse.ArgumentParser(description="我的币安人生 - 主调度器")
    parser.add_argument("--mode", choices=["demo", "live"], default="demo")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--api-secret", default=None)
    parser.add_argument("--day", type=int, default=1)
    parser.add_argument("--trader-type", default="aggressive")
    args = parser.parse_args()

    run_full_analysis(
        mode=args.mode,
        api_key=args.api_key,
        api_secret=args.api_secret,
        challenge_day=args.day,
        trader_type=args.trader_type
    )
