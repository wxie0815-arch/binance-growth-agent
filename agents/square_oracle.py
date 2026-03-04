#!/usr/bin/env python3
"""
币安广场流量预言机
分析广场热帖规律，输出今日最优发帖策略
"""
import json, os, re
from datetime import datetime, timezone
from pathlib import Path

# ── 流量密码模型 ──────────────────────────────────────
# ── 对齐 binance-square-predictor SKILL.md 的权重体系 ──
CONTENT_TYPE_WEIGHTS = {
    '行情分析':   3.0,   # 大涨大跌时最高
    '新币Launchpad': 2.5,
    '币安官方活动': 2.5,
    '地缘政治':   2.0,
    '交易技巧':   1.5,
    'AI_Web3':    1.5,
    '日常观点':   1.0,
}

TOPIC_WEIGHTS = {
    'BTC':    1.0,
    'ETH':    0.85,
    'AI':     0.9,
    'DeFi':   0.75,
    'NFT':    0.5,
    'Meme':   0.8,
    '宏观':   0.7,
    '山寨':   0.65,
}

# 三段时间规律（SKILL.md定义）
BEST_HOURS_UTC = [0, 1, 4, 5, 12, 13, 14]  # 北京08-10 / 12-14 / 20-22

FORMAT_SCORES = {
    '数据开头':   1.0,   # 首句含数字 +25%
    '争议观点':   0.95,  # 争议性 +30%
    '问句开头':   0.9,
    '情绪开头':   0.85,
    '故事开头':   0.75,
}

EMOTION_SCORES = {
    '恐惧':   0.95,
    '贪婪':   0.9,
    '自嘲':   0.85,
    '愤怒':   0.8,
    '中性':   0.5,
}

# 格式加成系数（SKILL.md定义）
FORMAT_BONUS = {
    '带图片':     1.40,
    '首句含数字': 1.25,
    '争议观点':   1.30,
    '字数200-500': 1.0,
}

HOT_TAGS = [
    '#AIBinance', '#BTC', '#币安广场', '#交易心得',
    '#Web3', '#crypto', '#DeFi', '#HODL'
]

class SquareOracle:
    def __init__(self):
        self.now = datetime.now(timezone.utc)
        self.news_data = []
        self.twitter_data = []

    def fetch_news(self) -> list:
        """用opennews-mcp拉今日高分新闻"""
        try:
            import subprocess, json
            token = os.environ.get('OPENNEWS_TOKEN', '')
            if not token:
                return []
            r = subprocess.run([
                'curl', '-s', '-X', 'POST',
                'https://ai.6551.io/open/news_search',
                '-H', f'Authorization: Bearer {token}',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({'limit': 30, 'page': 1})
            ], capture_output=True, text=True, timeout=10)
            data = json.loads(r.stdout)
            articles = data.get('data', []) or []
            # 只取高分
            return [a for a in articles
                    if a.get('aiRating', {}).get('score', 0) >= 70]
        except Exception as e:
            return []

    def fetch_twitter_hot(self) -> list:
        """用opentwitter-mcp拉币安广场KOL推文"""
        try:
            import subprocess, json
            token = os.environ.get('TWITTER_TOKEN', '')
            if not token:
                return []
            r = subprocess.run([
                'curl', '-s', '-X', 'POST',
                'https://ai.6551.io/open/twitter_search',
                '-H', f'Authorization: Bearer {token}',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps({
                    'keywords': 'binance square crypto',
                    'minLikes': 50,
                    'product': 'Top',
                    'maxResults': 30
                })
            ], capture_output=True, text=True, timeout=10)
            data = json.loads(r.stdout)
            return data.get('data', {}).get('tweets', []) or []
        except:
            return []

    def analyze_hot_topics(self, news: list, tweets: list) -> dict:
        """分析当前热点话题"""
        topic_scores = {k: v for k, v in TOPIC_WEIGHTS.items()}

        # 从新闻关键词加权
        for article in news:
            text = article.get('text', '').upper()
            score = article.get('aiRating', {}).get('score', 0) / 100
            for topic in topic_scores:
                if topic.upper() in text:
                    topic_scores[topic] += score * 0.3

        # 从Twitter热词加权
        for tweet in tweets:
            text = tweet.get('text', '').upper()
            likes = tweet.get('favoriteCount', 0)
            weight = min(likes / 1000, 1.0)
            for topic in topic_scores:
                if topic.upper() in text:
                    topic_scores[topic] += weight * 0.2

        # 排序返回Top3
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        return {k: round(v, 2) for k, v in sorted_topics[:5]}

    def get_best_window(self) -> dict:
        """计算今日最佳发布时间窗口"""
        current_hour = self.now.hour
        next_windows = []
        for h in BEST_HOURS_UTC:
            if h > current_hour:
                next_windows.append(h)
        if not next_windows:
            next_windows = [BEST_HOURS_UTC[0] + 24]  # 明天第一个窗口

        next_h = next_windows[0]
        return {
            'best_hours_utc': BEST_HOURS_UTC,
            'next_window_utc': f'{next_h:02d}:00',
            'next_window_beijing': f'{(next_h + 8) % 24:02d}:00',
            'wait_hours': (next_h - current_hour) % 24
        }

    def detect_market_emotion(self, news: list) -> str:
        """判断当前市场情绪"""
        fear_kw = ['crash', 'dump', 'fear', 'drop', 'ban', '暴跌', '崩', '恐慌', 'war', 'attack']
        greed_kw = ['ath', 'surge', 'bull', 'pump', 'rally', '暴涨', '新高', '突破']

        fear_count = greed_count = 0
        for a in news:
            text = a.get('text', '').lower()
            fear_count += sum(1 for k in fear_kw if k in text)
            greed_count += sum(1 for k in greed_kw if k in text)

        if fear_count > greed_count * 1.5:
            return '恐惧'
        elif greed_count > fear_count * 1.5:
            return '贪婪'
        else:
            return '中性偏谨慎'

    def generate_strategy(self) -> dict:
        """生成今日最优发帖策略"""
        print("📡 币安广场流量预言机启动...")
        news = self.fetch_news()
        tweets = self.fetch_twitter_hot()
        print(f"  获取新闻: {len(news)}条 | 推文: {len(tweets)}条")

        hot_topics = self.analyze_hot_topics(news, tweets)
        window = self.get_best_window()
        emotion = self.detect_market_emotion(news)

        top_topic = list(hot_topics.keys())[0] if hot_topics else 'BTC'
        best_format = '数据开头' if emotion in ['恐惧', '贪婪'] else '问句开头'
        recommended_tags = [t for t in HOT_TAGS if top_topic.upper() in t.upper()][:3]
        if '#AIBinance' not in recommended_tags:
            recommended_tags.insert(0, '#AIBinance')

        strategy = {
            'generated_at': self.now.isoformat(),
            'hot_topics': hot_topics,
            'top_topic': top_topic,
            'market_emotion': emotion,
            'best_window': window,
            'recommended_format': best_format,
            'recommended_emotion': emotion,
            'recommended_tags': recommended_tags,
            'predicted_engagement': self._predict_engagement(emotion, best_format, top_topic),
            'post_tips': self._generate_tips(emotion, top_topic, window)
        }
        return strategy

    def _predict_engagement(self, emotion: str, fmt: str, topic: str) -> str:
        base = EMOTION_SCORES.get(emotion, 0.5) * FORMAT_SCORES.get(fmt, 0.5) * TOPIC_WEIGHTS.get(topic, 0.5)
        if base > 0.7: return '高 (预计500+互动)'
        elif base > 0.4: return '中 (预计100-500互动)'
        else: return '普通 (预计<100互动)'

    def _generate_tips(self, emotion: str, topic: str, window: dict) -> list:
        tips = [
            f"最佳发布时间：北京 {window['next_window_beijing']}（约{window['wait_hours']}小时后）",
            f"话题方向：聚焦 {topic}，当前热度最高",
            f"市场情绪：{emotion} — 用{'共情恐慌' if emotion=='恐惧' else '分享喜悦' if emotion=='贪婪' else '理性分析'}基调写作",
            "开头3秒法则：数字/问题/强观点，不要寒暄",
            "长度：200-400字最佳，超过600字互动率下降40%",
            "必须带图：带图帖互动率是纯文的2.3倍",
        ]
        return tips

    def print_report(self, strategy: dict):
        print("\n" + "="*50)
        print("🔮 币安广场流量预言机 · 今日策略")
        print("="*50)
        print(f"📊 当前热点话题Top3：")
        for i, (t, s) in enumerate(list(strategy['hot_topics'].items())[:3], 1):
            print(f"   {i}. {t} (热度{s})")
        print(f"😤 市场情绪：{strategy['market_emotion']}")
        print(f"⏰ 最佳发布：北京 {strategy['best_window']['next_window_beijing']}")
        print(f"✍️  推荐格式：{strategy['recommended_format']}")
        print(f"🏷️  推荐标签：{' '.join(strategy['recommended_tags'])}")
        print(f"📈 预测互动：{strategy['predicted_engagement']}")
        print(f"\n💡 发帖技巧：")
        for tip in strategy['post_tips']:
            print(f"   • {tip}")
        print("="*50)


if __name__ == '__main__':
    oracle = SquareOracle()
    strategy = oracle.generate_strategy()
    oracle.print_report(strategy)

    # 保存结果
    out = Path(__file__).parent.parent / 'output'
    out.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')
    (out / f'square_oracle_{ts}.json').write_text(
        json.dumps(strategy, ensure_ascii=False, indent=2)
    )
    print(f"\n✅ 策略已保存")
