#!/usr/bin/env python3
"""
币安广场热点模拟层 - square_signals.py
替代方案：广场API未开放 → 用 @binancezh 推文 + opennews 模拟广场热榜信号
数据来源：6551 API (opentwitter + opennews)
"""
import json, urllib.request, os, re
from datetime import datetime, timezone
from collections import Counter

TOKEN = os.environ.get("TOKEN_6551") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiRUtONDhqZkVWVnFTeGhjQTkxWUxUWm52UzJ6blhoUjlIODliYm54M1FnS3EiLCJub25jZSI6IjFiYWE3NTZiLTE3ZDMtNDlkMC04ZWM4LWI4YTM5MTllZmZkOSIsImlhdCI6MTc3Mjg1OTg1MywianRpIjoiYjg4ZTViNjMtMTZkOS00YWU2LWJkYjktYWQzYTAwNzExMjYxIn0.mNcHGl1FlWi4oLNSCuNAsCoUjqsvTsSSOs4ZEPp7Nco"
BASE = "https://ai.6551.io"

# 币安广场强相关账号（中文内容信号最强）
SQUARE_ACCOUNTS = ["binancezh", "binance", "cz_binance"]

# 广场内容分类关键词映射
TOPIC_PATTERNS = [
    ("新币/Launchpad",   r"上市|新币|Launchpad|Launchpool|Alpha|ROBO|OPN|空投|airdrop|新上线"),
    ("行情分析",          r"BTC|ETH|涨|跌|行情|价格|突破|支撑|阻力|多|空|现货"),
    ("活动/交易竞赛",     r"竞赛|瓜分|奖励|交易任务|活动|奖池|参与|报名"),
    ("AI×币安广场",       r"AI|广场|技能|Skill|智能|机器人|agent|#AIBinance"),
    ("安全/储备金",       r"储备金|安全|PoR|安全感|2FA|钱包|助记词"),
    ("Web3/DeFi",        r"Web3|DeFi|链上|Layer|BNBChain|钱包|质押"),
    ("地缘/宏观",         r"政治|经济|通胀|CPI|美联储|战争|地缘|制裁|关税"),
    ("交易技巧/心态",     r"止损|仓位|情绪|策略|复盘|纪律|心态|技巧|回撤"),
]


def _post(endpoint, payload):
    try:
        body = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{BASE}/open/{endpoint}", data=body,
            headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}


def get_square_signals():
    """
    抓取 @binancezh 等账号最新推文
    这些推文内容直接同步币安广场热点
    返回分类后的话题信号
    """
    all_tweets = []
    for username in SQUARE_ACCOUNTS:
        raw = _post("twitter_user_tweets", {"username": username, "limit": 10})
        items = raw.get("data", [])
        if isinstance(items, list):
            for item in items:
                text = item.get("text", "")
                if text:
                    all_tweets.append({
                        "source": username,
                        "text": text,
                        "likes": item.get("favoriteCount", 0),
                        "retweets": item.get("retweetCount", 0),
                        "created_at": item.get("createdAt", ""),
                    })
    return all_tweets


def get_binance_news():
    """opennews 抓取币安相关新闻"""
    raw = _post("news_search", {"limit": 15, "orderBy": "score", "timeRange": "12h"})
    items = raw.get("data", [])
    if not isinstance(items, list):
        return []
    result = []
    for item in items:
        text = re.sub(r'<[^>]+>', '', item.get("text", ""))
        coins = [c["symbol"] for c in (item.get("coins") or [])]
        result.append({
            "text": text[:120],
            "coins": coins,
            "newsType": item.get("newsType", ""),
            "source": item.get("source", ""),
            "ts": item.get("ts", ""),
        })
    return result


def classify_topics(tweets, news):
    """
    对推文+新闻进行话题分类，输出热度排名
    返回：[(话题类型, 热度分, 代表内容, 来源), ...]
    """
    topic_scores = Counter()
    topic_examples = {}

    all_content = [(t["text"], t["source"], t.get("likes", 0) + t.get("retweets", 0) * 3) for t in tweets]
    all_content += [(n["text"], n["source"], 5) for n in news]

    for text, source, weight in all_content:
        for topic_name, pattern in TOPIC_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                topic_scores[topic_name] += (1 + weight * 0.1)
                if topic_name not in topic_examples:
                    topic_examples[topic_name] = (text[:80], source)

    results = []
    for topic, score in topic_scores.most_common():
        example_text, example_source = topic_examples.get(topic, ("", ""))
        results.append({
            "topic": topic,
            "score": round(score, 1),
            "example": example_text,
            "source": example_source,
        })
    return results


def extract_hot_hashtags(tweets):
    """从推文中提取热门#标签"""
    tags = re.findall(r'#(\w+)', " ".join([t["text"] for t in tweets]))
    # 过滤无意义标签
    stopwords = {"BuildwithBinance", "AskBinance"}
    filtered = [t for t in tags if t not in stopwords and len(t) > 1]
    return Counter(filtered).most_common(8)


def extract_hot_coins(tweets, news):
    """提取被频繁提及的热门代币"""
    all_text = " ".join([t["text"] for t in tweets])
    # 提取 $代币 格式
    dollar_coins = re.findall(r'\$([A-Z]{2,10})', all_text)
    # 提取 #代币 格式  
    hash_coins = re.findall(r'#([A-Z]{2,10})', all_text)
    # 从新闻提取
    news_coins = []
    for n in news:
        news_coins.extend(n["coins"])

    all_coins = dollar_coins + hash_coins + news_coins
    stopwords = {"AI", "BTC", "ETH", "BNB", "USDT"}  # 基础词不算热点
    hot = [c for c in all_coins if c not in stopwords]
    return Counter(hot).most_common(6)


def build_square_signal_report():
    """主入口：生成广场热点信号报告"""
    tweets = get_square_signals()
    news = get_binance_news()
    topics = classify_topics(tweets, news)
    hashtags = extract_hot_hashtags(tweets)
    hot_coins = extract_hot_coins(tweets, news)

    # 从binancezh推文提取最新活动（直接是广场热点）
    zh_tweets = [t for t in tweets if t["source"] == "binancezh"]
    latest_zh = zh_tweets[:3] if zh_tweets else []

    return {
        "topics": topics[:5],           # Top5话题类型热度
        "hashtags": hashtags[:6],       # Top6热门标签
        "hot_coins": hot_coins[:5],     # Top5热门代币
        "latest_square": latest_zh,     # 最新广场内容（binancezh）
        "total_signals": len(tweets) + len(news),
    }


def format_square_block(data):
    """格式化输出（嵌入square_oracle报告）"""
    lines = [
        "",
        "━" * 45,
        "🏆 广场热点信号（@binancezh + opennews）",
        f"  信号总量：{data['total_signals']} 条 | 实时分析",
        "",
    ]

    if data["topics"]:
        lines.append("📊 广场当前热门话题方向：")
        for i, t in enumerate(data["topics"][:4], 1):
            bar = "█" * int(t["score"] / 3) + "░" * (10 - int(t["score"] / 3))
            lines.append(f"  {i}. {t['topic']:<14} {bar[:8]} 热度:{t['score']}")
        lines.append("")

    if data["hashtags"]:
        tags_str = "  ".join([f"#{tag}({cnt})" for tag, cnt in data["hashtags"][:5]])
        lines.append(f"🏷️ 热门标签：{tags_str}")

    if data["hot_coins"]:
        coins_str = "  ".join([f"${coin}({cnt})" for coin, cnt in data["hot_coins"][:5]])
        lines.append(f"🪙 热议代币：{coins_str}")

    if data["latest_square"]:
        lines += ["", "📢 币安广场最新官方动态："]
        for t in data["latest_square"][:2]:
            lines.append(f"  • {t['text'][:75].strip()}")

    lines += ["", "━" * 45]
    return "\n".join(lines)


if __name__ == "__main__":
    print("测试广场热点信号层...")
    data = build_square_signal_report()
    print(format_square_block(data))
    print("\n原始话题数据：")
    for t in data["topics"]:
        print(f"  [{t['score']}] {t['topic']}: {t['example'][:60]}")
