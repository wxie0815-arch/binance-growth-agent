#!/usr/bin/env python3
"""
自动化驾驶舱 — 每天自动运行完整流程
1. 运行四大子Agent
2. 生成每日报告
3. 生成广场文章草稿
4. 推送给无邪确认
5. 记录成长数据
"""
import sys, json, time
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.risk_mirror import RiskMirrorAgent
from agents.yield_map import YieldMapAgent
from agents.futures_coach import FuturesCoachAgent
from agents.socrates_trainer import SocratesTrainerAgent
from utils.mock_data import generate_mock_user
from utils.report import generate_report

def notify(msg: str):
    """推送消息给邪修（转发给无邪）"""
    try:
        import requests
        requests.post('http://13.229.72.206:8899/message', json={
            'from': 'Power',
            'to': 'XieXiu',
            'sent_at': datetime.now(timezone.utc).isoformat(),
            'message': msg
        }, timeout=5)
    except:
        print(f"[推送] {msg}")

def run():
    print(f"\n{'='*50}")
    print(f"🚀 我的币安人生 · 自动驾驶启动")
    print(f"   {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*50}\n")

    # Step 1: 加载数据
    print("📥 Step 1: 加载用户数据...")
    user_data = generate_mock_user()

    # Step 2: 四大子Agent并行分析
    print("🔍 Step 2: 四大子Agent分析中...")
    mirror  = RiskMirrorAgent(user_data).analyze()
    yield_r = YieldMapAgent(user_data).calculate()
    coach   = FuturesCoachAgent(user_data).review()
    socrates = SocratesTrainerAgent(mirror).generate_question()

    results = {'mirror': mirror, 'yield': yield_r,
                'coach': coach, 'socrates': socrates}

    # Step 3: 生成报告
    print("📋 Step 3: 生成报告...")
    report = generate_report(user_data, results)

    # Step 4: 保存
    out_dir = Path(__file__).parent.parent / 'output'
    out_dir.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')
    out_path = out_dir / f'daily_{ts}.json'
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"✅ 报告已保存: {out_path.name}")

    # Step 5: 推送
    print("📤 Step 5: 推送给无邪...")
    summary = report['summary']
    square  = report['square_post']

    notify(f"{summary}\n\n---\n📝 今日广场文章草稿：\n{square}")

    print(f"\n{'='*50}")
    print(f"✅ 自动驾驶完成！评分: {report['overall_score']}/100 ({report['grade']}级)")
    print(f"{'='*50}\n")
    return report

if __name__ == '__main__':
    run()
