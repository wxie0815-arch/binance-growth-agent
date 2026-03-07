#!/usr/bin/env python3
"""
每日广场内容运营 - 自动生成今日内容方案
基于预言机热点 + 人格选题库 + 7日挑战计划
"""
import json, random
from datetime import datetime, timezone

# 今日是大赛Day4（2026-03-07）
TODAY_CHALLENGE_DAY = 4  # 练思维（苏格拉底训练）

ORACLE_HOT = [
    {"topic": "BTC突破趋势分析", "score": 94, "tags": "#BTC #AIBinance"},
    {"topic": "AI Agent实战分享", "score": 87, "tags": "#AIAgent #我的币安人生"},
    {"topic": "地缘风险与加密市场", "score": 81, "tags": "#宏观 #BTC"},
]

CHALLENGE_DAY4 = {
    "theme": "🎓 练思维",
    "title": "AI出了道题考我，我没答好，但想通了",
    "question": "你持有的BTC突然跌了15%，此时你会：\nA. 立刻止损，保住本金\nB. 加仓摊低成本\nC. 什么都不做，等反弹\nD. 看情况决定",
    "ai_reframe": "大多数人选A或B，但AI的反问是：「你选这个，是因为你有计划，还是因为你害怕？」\n真正的答案不是选项本身，而是你做决定前有没有想清楚止损线在哪。",
    "insight": "交易的本质不是预测对错，而是在任何情况下都有预案。",
    "tags": "#AIBinance #我的币安人生 #交易思维 #苏格拉底",
    "best_time": "北京22:00",
    "word_count": "≈300字",
    "cta": "你当时会选哪个？评论告诉我"
}

def generate_daily_plan():
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")

    plan = f"""
╔══════════════════════════════════════════════════════════════╗
║  📅 广场内容运营日报 {date_str}  (大赛 Day{TODAY_CHALLENGE_DAY})           ║
╚══════════════════════════════════════════════════════════════╝

🔮 预言机今日热点
{''.join([f"  Top{i+1}: {h['topic']} (热度:{h['score']}) {h['tags']}\\n" for i,h in enumerate(ORACLE_HOT)])}

📝 今日7日挑战发帖方案（Day{TODAY_CHALLENGE_DAY}）
─────────────────────────────────────────
主题：{CHALLENGE_DAY4['theme']}
标题：{CHALLENGE_DAY4['title']}
发布时间：{CHALLENGE_DAY4['best_time']}
字数：{CHALLENGE_DAY4['word_count']}
标签：{CHALLENGE_DAY4['tags']}
CTA：{CHALLENGE_DAY4['cta']}

文章大纲：
1. 开头（引子）：
   「AI今天给我出了一道题，我第一反应答了A，然后被反问破防了。」

2. 题目（直接放）：
   {CHALLENGE_DAY4['question']}

3. AI的反问（核心）：
   {CHALLENGE_DAY4['ai_reframe']}

4. 我的认知改变：
   {CHALLENGE_DAY4['insight']}

5. 结尾（CTA）：
   「明天Day5，AI帮我预测今天广场什么话题最热——它说对了吗？」

─────────────────────────────────────────
✅ 内容方案生成完毕，待无邪确认后发布
"""
    return plan

if __name__ == "__main__":
    plan = generate_daily_plan()
    print(plan)
    # 保存报告
    with open(f"/home/ubuntu/binance-growth-agent/reports/content_{datetime.now().strftime('%Y%m%d')}.txt", "w") as f:
        f.write(plan)
    print("✅ 已保存到 reports/")
