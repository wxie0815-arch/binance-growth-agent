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
    parser.add_argument('--uid', type=str, help='币安UID（真实模式）')
    parser.add_argument('--module', type=str, choices=['mirror', 'yield', 'coach', 'socrates', 'all'], default='all')
    args = parser.parse_args()

    print("🚀 币安用户成长全栈Agent 启动")
    print("=" * 50)

    # 数据加载
    if args.demo:
        print("📊 演示模式 — 使用模拟数据")
        user_data = generate_mock_user()
    else:
        print(f"🔗 连接币安账户 UID: {args.uid}")
        user_data = {}  # 真实模式通过binance-pro-cn skill读取

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
