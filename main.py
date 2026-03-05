#!/usr/bin/env python3
"""
币安用户成长全栈Agent - 主入口
Built with OpenClaw | #AIBinance
"""

import argparse
import json
from datetime import datetime, timezone
from agents.risk_mirror import RiskMirrorAgent
from agents.yield_map import YieldMapAgent
from agents.futures_coach import FuturesCoachAgent
from agents.socrates_trainer import SocratesTrainerAgent
from utils.mock_data import generate_mock_user
from utils.report import generate_report


def main():
    parser = argparse.ArgumentParser(description='币安用户成长全栈Agent')
    parser.add_argument('--demo', action='store_true', help='使用模拟数据演示')
    parser.add_argument('--real', action='store_true', help='真实API模式（需配置 Binance Key）')
    parser.add_argument('--uid', type=str, help='币安UID（真实模式）')
    parser.add_argument('--module', type=str, choices=['mirror', 'yield', 'coach', 'socrates', 'all', 'paper'], default='all')
    parser.add_argument('--paper-open', nargs=4, metavar=('SYMBOL','SIDE','QTY','PRICE'), help='模拟盘开仓: BTCUSDT LONG 0.01 71000')
    parser.add_argument('--paper-close', nargs=2, metavar=('POS_ID','EXIT_PRICE'), help='模拟盘平仓: <pos_id> 73000')
    parser.add_argument('--paper-status', action='store_true', help='查看模拟盘状态')
    args = parser.parse_args()

    print("🚀 币安用户成长全栈Agent 启动")
    print("=" * 50)

    # ── 模拟盘快捷操作（不走全流程）──────────────────────────────
    if args.paper_open or args.paper_close or args.paper_status:
        from utils.paper_trader import PaperTrader
        pt = PaperTrader()
        if args.paper_status:
            pt.print_status()
        if args.paper_open:
            sym, side, qty, price = args.paper_open
            res = pt.open_position(sym, side, float(qty), float(price), leverage=10)
            print(json.dumps(res, ensure_ascii=False, indent=2))
        if args.paper_close:
            pos_id, exit_price = args.paper_close
            res = pt.close_position(pos_id, float(exit_price))
            print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    # ── 数据加载 ───────────────────────────────────────────────
    if args.real:
        print("🔗 真实API模式 — 接入 binance-pro-cn")
        from utils.real_api import get_account_summary
        account = get_account_summary()
        print(f"   数据来源: {account['source'].upper()} | "
              f"总资产: ${account['total_usdt_estimate']:,.2f} USDT | "
              f"BTC: ${account['prices'].get('BTCUSDT', 0):,.0f}")
        user_data = {"account": account, "mode": "real"}
    elif args.demo:
        print("📊 演示模式 — 使用模拟数据")
        user_data = generate_mock_user()
    else:
        print("ℹ️  未指定模式，使用演示模式（--real 接入真实API，--demo 明确指定演示）")
        user_data = generate_mock_user()

    results = {}

    # 模块执行
    if args.module in ('mirror', 'all'):
        print("\n🪞 风险镜子分析中...")
        mirror = RiskMirrorAgent(user_data)
        results['mirror'] = mirror.analyze()

    if args.module in ('yield', 'all'):
        print("\n🗺️  收益地图计算中...")
        yield_map = YieldMapAgent(user_data)
        results['yield'] = yield_map.calculate()

    if args.module in ('coach', 'all'):
        print("\n📊 合约复盘教练分析中...")
        coach = FuturesCoachAgent(user_data)
        results['coach'] = coach.review()

    if args.module in ('socrates', 'all'):
        print("\n🎓 苏格拉底训练题生成中...")
        socrates = SocratesTrainerAgent(results.get('mirror', {}))
        results['socrates'] = socrates.generate_question()

    # 生成报告
    print("\n📋 生成成长报告...")
    report = generate_report(user_data, results)

    # 输出
    output_path = f"output/report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 报告已生成: {output_path}")
    print("\n" + "=" * 50)
    print(report['summary'])


if __name__ == '__main__':
    main()
