#!/usr/bin/env python3
"""
报告生成器 — 汇总四大模块输出，生成完整成长报告
"""

from datetime import datetime, timezone


def generate_report(user_data: dict, results: dict) -> dict:
    mirror = results.get('mirror', {})
    yield_map = results.get('yield', {})
    coach = results.get('coach', {})
    socrates = results.get('socrates', {})

    name = user_data.get('name', '用户')
    # 兼容两种字段名
    trader_type = mirror.get('personality_type') or mirror.get('trader_type', '未知')
    grade = mirror.get('score', mirror.get('overall_grade', 'N/A'))
    weaknesses = mirror.get('suggestions', mirror.get('weaknesses', []))
    strengths = [mirror.get('personality_desc', '')] if mirror.get('personality_desc') else mirror.get('strengths', [])

    yield_gap = yield_map.get('yield_gap', 0)
    optimal_apy = yield_map.get('optimal_apy', 0)
    current_apy = yield_map.get('current_apy', 0)

    health = coach.get('health_verdict', coach.get('health_score', 'N/A'))
    top_errors = coach.get('top_error_patterns', [])

    today_q = socrates.get('today_scenario', '')
    core_q = socrates.get('core_question', '')

    summary = f"""
╔══════════════════════════════════════════╗
║     币安用户成长全栈Agent — 今日报告       ║
╚══════════════════════════════════════════╝

👤 用户：{name}
📅 生成时间：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}

🪞 【风险镜子】
交易者类型：{trader_type}
综合评级：{grade}
致命弱点：{' | '.join(weaknesses) if weaknesses else '暂无明显弱点'}
优势：{' | '.join(strengths) if strengths else '继续积累'}

🗺️ 【收益地图】
当前收益率：{current_apy}% APY
最优收益率：{optimal_apy}% APY
每年多赚：+${yield_gap:,.0f} USDT（同样的钱）

📊 【合约复盘】
合约健康评分：{health}
最高频错误：{top_errors[0]['error'] if top_errors else 'N/A'}（{top_errors[0].get('count', 0) if top_errors else 0}次）

🎓 【今日苏格拉底训练】
情景：{today_q[:80]}...
思考题：{core_q}

══════════════════════════════════════════
Built with OpenClaw | #AIBinance
""".strip()

    # 广场发布文本
    square_post = f"""用AI给自己的币安账户做了个全面体检 🔍

🪞 镜子照出来：我是「{trader_type}」
主要问题：{weaknesses[0] if weaknesses else '整体还不错'}

🗺️ 收益地图：我的钱一直白放着
同样{yield_map.get('total_assets_usdt', 0):,.0f}U，配置一下每年可以多赚${yield_gap:,.0f}

📊 合约复盘：最大问题是{top_errors[0]['error'] if top_errors else '仓位管理'}

🎓 今日训练题：
{core_q}

这个AI成长系统真的很有用，不是给你信号，是帮你认清自己
Built with OpenClaw 🦞 #AIBinance"""

    return {
        "user": name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "square_post": square_post,
        "mirror": mirror,
        "yield_map": yield_map,
        "coach": coach,
        "socrates": socrates
    }
