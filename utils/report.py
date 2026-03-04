#!/usr/bin/env python3
"""
报告生成器
整合四大子Agent结果，生成完整成长报告
"""

from datetime import datetime, timezone


def generate_report(user_data: dict, results: dict) -> dict:
    """整合所有子Agent结果生成完整报告"""

    now = datetime.now(timezone.utc)
    mirror = results.get('mirror', {})
    yield_r = results.get('yield', {})
    coach = results.get('coach', {})
    socrates = results.get('socrates', {})

    # 综合成长评分
    scores = []
    if mirror:
        scores.append(mirror.get('score', 50))
    if coach:
        scores.append(coach.get('health_score', 50))
    overall_score = round(sum(scores) / len(scores)) if scores else 50

    grade = "S" if overall_score >= 85 else \
            "A" if overall_score >= 70 else \
            "B" if overall_score >= 55 else \
            "C" if overall_score >= 40 else "D"

    # 每日Telegram推送摘要
    summary_lines = [
        f"📊 我的币安人生 · 今日报告",
        f"{'─' * 30}",
    ]

    if mirror:
        summary_lines += [
            f"🪞 交易者人格：{mirror.get('personality_icon','')} {mirror.get('personality_type','')}",
            f"   致命弱点：{mirror.get('fatal_weakness','')}",
        ]

    if yield_r:
        best = yield_r.get('best_option', {})
        summary_lines += [
            f"🗺️  收益地图：最优选项 {best.get('option','')}",
            f"   APY {best.get('apy',0)}% | 年收益约 ${best.get('annual_yield',0)}/千USDT",
        ]

    if coach:
        summary_lines += [
            f"📊 合约健康：{coach.get('health_verdict','')} {coach.get('health_score',0)}/100",
            f"   {coach.get('weekly_summary','')}",
        ]

    if socrates:
        summary_lines += [
            f"🎓 今日训练：{socrates.get('common_trap','')}",
            f"   {socrates.get('main_question','')}",
        ]

    summary_lines += [
        f"{'─' * 30}",
        f"🏆 综合成长评分：{overall_score}/100 ({grade}级)",
        f"💪 继续加油，你的币安人生正在改变",
    ]

    summary = "\n".join(summary_lines)

    # 广场文章草稿（7日挑战）
    square_post = _generate_square_post(mirror, coach, now)

    return {
        "generated_at": now.isoformat(),
        "overall_score": overall_score,
        "grade": grade,
        "summary": summary,
        "square_post": square_post,
        "modules": {
            "mirror": mirror,
            "yield": yield_r,
            "coach": coach,
            "socrates": socrates,
        }
    }


def _generate_square_post(mirror: dict, coach: dict, now: datetime) -> str:
    """生成广场7日挑战文章草稿"""

    personality = mirror.get('personality_type', '未知')
    weakness = mirror.get('fatal_weakness', '')
    health = coach.get('health_verdict', '')
    score = coach.get('health_score', 0)

    post = f"""AI帮我照了一面镜子，我看到了真实的自己

用了「我的币安人生」AI分析了过去3个月的交易记录

结论让我有点沉默：

我是【{personality}】

{weakness}

合约健康评分：{score}/100 {health}

最高频的错误我自己都知道，但就是改不掉
现在AI帮我盯着，每天复盘，每天一道思考题

这是第1天，14天后再来看看有没有变化

你也来测测你是什么交易者？

#AIBinance #我的币安人生 #币安广场 #交易成长"""

    return post
