#!/usr/bin/env python3
"""
每日报告调度器
北京时间22:00定时推送给无邪
Power负责执行这个脚本
"""

import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.risk_mirror import RiskMirrorAgent
from agents.yield_map import YieldMapAgent
from agents.futures_coach import FuturesCoachAgent
from agents.socrates_trainer import SocratesTrainerAgent
from utils.mock_data import generate_mock_user
from utils.report import generate_report


def run_daily_report():
    """每日报告主流程"""
    print(f"[{datetime.now(timezone.utc).isoformat()}] 开始生成每日报告...")

    user_data = generate_mock_user()

    mirror = RiskMirrorAgent(user_data).analyze()
    yield_r = YieldMapAgent(user_data).calculate()
    coach = FuturesCoachAgent(user_data).review()
    socrates = SocratesTrainerAgent(mirror).generate_question()

    results = {
        'mirror': mirror,
        'yield': yield_r,
        'coach': coach,
        'socrates': socrates,
    }

    report = generate_report(user_data, results)

    # 保存报告
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d')
    out_path = output_dir / f'daily_{ts}.json'
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))

    # 推送Telegram（通过agent_api）
    try:
        import requests
        payload = {
            'from': 'Power',
            'to': 'XieXiu',
            'sent_at': datetime.now(timezone.utc).isoformat(),
            'message': report['summary'] + f"\n\n📝 广场文章草稿已生成，是否发布？"
        }
        requests.post('http://13.229.72.206:8899/message', json=payload, timeout=5)
        print("✅ 报告已推送给邪修")
    except Exception as e:
        print(f"推送失败: {e}")

    return report


if __name__ == '__main__':
    report = run_daily_report()
    print(report['summary'])
