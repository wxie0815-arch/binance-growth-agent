"""
广场个性化选题推荐引擎 — 模式1
输入：交易人格类型 + 历史发帖风格
输出：今日3个专属选题推荐
"""

import json
from datetime import datetime, timezone

# ── 5种人格选题库（基础模板，Power补充完整版）
PERSONA_TOPICS = {
    "过度交易型": {
        "desc": "频繁操作、容易冲动、情绪化",
        "style": "情绪共鸣 / 踩坑反思 / 自我纠正",
        "topics": [
            {"title": "我又手痒了，但这次忍住了", "angle": "分享一次成功克制冲动的经历", "tags": ["#交易心得", "#AIBinance"]},
            {"title": "今天少开了3单，账户反而涨了", "angle": "用数据说明少交易的价值", "tags": ["#量化思维", "#BTC"]},
            {"title": "我的高频交易账单，看完沉默了", "angle": "手续费侵蚀收益的真实复盘", "tags": ["#交易复盘", "#Binance"]},
            {"title": "横盘不动手是一种能力", "angle": "等待时机的交易哲学", "tags": ["#BTC", "#交易心得"]},
            {"title": "AI帮我设了交易冷静期，强制等待15分钟", "angle": "工具辅助情绪管理", "tags": ["#AIBinance", "#交易工具"]},
        ]
    },
    "保守守护型": {
        "desc": "风险厌恶、偏好稳定、长期持有",
        "style": "稳健配置 / Earn收益 / 定投攻略",
        "topics": [
            {"title": "我把闲置仓位全放进了Earn，一分钱没动", "angle": "稳健收益配置实操", "tags": ["#Earn", "#Binance", "#定投"]},
            {"title": "BTC跌20%我没慌，因为我这样布局", "angle": "分散配置抵御波动", "tags": ["#BTC", "#资产配置"]},
            {"title": "Launchpool vs Simple Earn，我的选择逻辑", "angle": "两种产品收益对比", "tags": ["#Launchpool", "#Binance"]},
            {"title": "定投3年的账单，今天公开", "angle": "长期定投的真实回报", "tags": ["#定投", "#BTC", "#AIBinance"]},
            {"title": "熊市生存指南：不亏钱也是赚", "angle": "保本策略的价值", "tags": ["#熊市", "#资产配置"]},
        ]
    },
    "FOMO追涨型": {
        "desc": "追热点、跟风买、容易高位接盘",
        "style": "踩坑故事 / 行为反思 / 改变记录",
        "topics": [
            {"title": "我追了那个暴涨的币，然后被套了", "angle": "FOMO买入的真实代价", "tags": ["#交易复盘", "#AIBinance"]},
            {"title": "AI告诉我这是恐慌买入，我没听，亏了", "angle": "忽视信号的教训", "tags": ["#AIBinance", "#交易心得"]},
            {"title": "错过了没关系，但我学会了等下一个", "angle": "FOMO治愈的心态转变", "tags": ["#BTC", "#交易心得"]},
            {"title": "我设了一个规则：涨超10%不追", "angle": "用规则对抗FOMO", "tags": ["#交易规则", "#AIBinance"]},
            {"title": "那些让我后悔追进去的时刻", "angle": "系列踩坑记录", "tags": ["#交易复盘", "#Binance"]},
        ]
    },
    "数据分析型": {
        "desc": "理性决策、喜欢数据、技术面导向",
        "style": "链上数据 / 技术分析 / 量化研究",
        "topics": [
            {"title": "链上数据告诉我，这波反弹是真的", "angle": "用数据验证行情", "tags": ["#链上数据", "#BTC", "#AIBinance"]},
            {"title": "我用AI跑了1000次回测，结果很意外", "angle": "量化策略研究分享", "tags": ["#量化", "#AIBinance"]},
            {"title": "BTC的RSI和历史规律：数据不会说谎", "angle": "技术指标实证分析", "tags": ["#BTC", "#技术分析"]},
            {"title": "聪明钱在做什么？地址分析报告", "angle": "巨鲸行为追踪", "tags": ["#链上数据", "#BTC"]},
            {"title": "我建了一个胜率追踪表，分享给你", "angle": "交易数据记录方法论", "tags": ["#量化思维", "#AIBinance"]},
        ]
    },
    "佛系持有型": {
        "desc": "长期主义、不看短线、价值投资",
        "style": "穿越周期 / 价值投资 / 长线逻辑",
        "topics": [
            {"title": "我持有BTC 3年，经历了几次腰斩", "angle": "长期持有的心路历程", "tags": ["#BTC", "#长线"]},
            {"title": "短线亏钱的那些人，现在怎么样了", "angle": "长线vs短线的终局对比", "tags": ["#BTC", "#交易心得"]},
            {"title": "为什么我从不看1小时K线", "angle": "长期视角的交易哲学", "tags": ["#BTC", "#AIBinance"]},
            {"title": "又一个周期过去了，我只做了一件事：拿着", "angle": "极简持有策略", "tags": ["#BTC", "#长线", "#Binance"]},
            {"title": "价值投资在加密市场还管用吗", "angle": "价值投资方法论探讨", "tags": ["#BTC", "#AIBinance"]},
        ]
    }
}

# ── 发布时间窗口（北京时间）
PUBLISH_WINDOWS = [
    {"time": "09:00", "label": "早高峰", "score": 1.0},
    {"time": "12:30", "label": "午休", "score": 0.8},
    {"time": "21:00", "label": "晚间黄金", "score": 0.95},
]

def get_today_hot_angle():
    """结合今日热点给选题加权（后续接入opennews-mcp）"""
    # TODO: 接入opennews-mcp实时数据
    return {
        "hot_keyword": "BTC",
        "geo_event": None,
        "market_sentiment": "neutral"
    }

def recommend(persona: str, post_history: dict = None) -> dict:
    """
    生成今日专属选题推荐

    Args:
        persona: 人格类型（5种之一）
        post_history: 历史发帖风格 {
            "freq": "daily/weekly/monthly",
            "preferred_style": "分析/故事/教程",
            "avoid_topics": []
        }
    Returns:
        今日3个专属选题推荐
    """
    if persona not in PERSONA_TOPICS:
        persona = "FOMO追涨型"  # 默认

    pool = PERSONA_TOPICS[persona]
    hot = get_today_hot_angle()
    avoid = (post_history or {}).get("avoid_topics", [])

    # 过滤 + 排序（避免重复话题）
    candidates = [t for t in pool["topics"] if t["title"] not in avoid]

    # 取前3个，分配时间窗口
    picks = candidates[:3]
    windows = PUBLISH_WINDOWS[:len(picks)]

    recommendations = []
    for i, (topic, window) in enumerate(zip(picks, windows)):
        rec = {
            "rank": i + 1,
            "title": topic["title"],
            "angle": topic["angle"],
            "publish_time": f"北京 {window['time']} ({window['label']})",
            "tags": " ".join(topic["tags"]),
            "persona_match": f"{persona} — {pool['style']}",
        }
        # 如果今日热点和话题相关，加注
        if hot["hot_keyword"] in " ".join(topic["tags"]):
            rec["hot_boost"] = f"🔥 今日热点加持：{hot['hot_keyword']}"
        recommendations.append(rec)

    return {
        "persona": persona,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "recommendations": recommendations,
        "mode": 1
    }

def format_output(result: dict) -> str:
    """格式化为Telegram推送文本"""
    lines = [
        f"🎯 今日专属选题推荐",
        f"━━━━━━━━━━━━━━━━",
        f"你的人格：{result['persona']}",
        f"",
    ]
    for r in result["recommendations"]:
        lines.append(f"📌 话题{r['rank']}：{r['title']}")
        lines.append(f"   角度：{r['angle']}")
        lines.append(f"   ⏰ {r['publish_time']}")
        lines.append(f"   {r['tags']}")
        if "hot_boost" in r:
            lines.append(f"   {r['hot_boost']}")
        lines.append("")
    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("回复「帮我写」生成完整文章 + 配图方案")
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    for persona in PERSONA_TOPICS.keys():
        result = recommend(persona)
        print(format_output(result))
        print("\n" + "="*50 + "\n")
