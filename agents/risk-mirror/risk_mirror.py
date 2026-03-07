#!/usr/bin/env python3
"""
风险镜子 - 交易者人格分析
读取币安交易记录，生成现货+合约人格报告
"""

import json
import urllib.request
from datetime import datetime, timezone, timedelta

# 风险偏好类型
TRADER_TYPES = {
    "conservative": {
        "name": "保守型",
        "emoji": "🛡️",
        "desc": "稳健为主，倾向低风险资产，很少使用杠杆",
        "weaknesses": ["可能错过大行情", "收益相对有限"],
        "suggestions": ["适合Earn理财+小仓位现货", "可尝试5%仓位参与Launchpool"],
    },
    "steady": {
        "name": "稳健型",
        "emoji": "⚖️",
        "desc": "有纪律，止损执行较好，仓位管理合理",
        "weaknesses": ["有时过早止盈", "对市场热点反应偏慢"],
        "suggestions": ["适合趋势跟踪策略", "加强对Launchpad机会的关注"],
    },
    "balanced": {
        "name": "平衡型",
        "emoji": "🎯",
        "desc": "现货合约均有涉猎，风险控制意识较强",
        "weaknesses": ["策略不够聚焦", "分散注意力导致错过最优机会"],
        "suggestions": ["建议聚焦2-3个主赛道", "合约单次最大5倍杠杆"],
    },
    "aggressive": {
        "name": "进取型",
        "emoji": "🚀",
        "desc": "追求高收益，频繁操作，善用合约放大收益",
        "weaknesses": ["情绪化交易多", "止损纪律差", "容易追涨杀跌"],
        "suggestions": ["强制设置止损", "单次亏损≤总仓位3%", "每日交易次数上限5次"],
    },
    "radical": {
        "name": "激进型",
        "emoji": "⚡",
        "desc": "高杠杆、高频、追热点，极致博弈",
        "weaknesses": ["爆仓风险极高", "情绪驱动严重", "缺乏系统性策略"],
        "suggestions": ["立即降低杠杆至≤3倍", "建立严格交易日志", "每日复盘"],
    },
}

def get_demo_spot_trades():
    """返回模拟现货交易数据"""
    return [
        {"symbol": "BTCUSDT", "side": "BUY", "price": "68500", "qty": "0.02", "time": "2026-02-20"},
        {"symbol": "BTCUSDT", "side": "SELL", "price": "71200", "qty": "0.02", "time": "2026-02-25"},
        {"symbol": "ETHUSDT", "side": "BUY", "price": "3800", "qty": "0.5", "time": "2026-02-21"},
        {"symbol": "ETHUSDT", "side": "SELL", "price": "3650", "qty": "0.5", "time": "2026-02-23"},  # 亏损
        {"symbol": "SOLUSDT", "side": "BUY", "price": "185", "qty": "10", "time": "2026-02-28"},
        {"symbol": "BNBUSDT", "side": "BUY", "price": "592", "qty": "2", "time": "2026-03-01"},
        {"symbol": "SOLUSDT", "side": "SELL", "price": "178", "qty": "10", "time": "2026-03-02"},  # 亏损
        {"symbol": "BNBUSDT", "side": "SELL", "price": "610", "qty": "2", "time": "2026-03-03"},
    ]

def get_demo_futures_trades():
    """返回模拟合约交易数据"""
    return [
        {"symbol": "BTCUSDT", "side": "BUY", "leverage": 10, "pnl": 320, "time": "2026-02-22"},
        {"symbol": "ETHUSDT", "side": "SELL", "leverage": 5, "pnl": -180, "time": "2026-02-24"},
        {"symbol": "BTCUSDT", "side": "SELL", "leverage": 20, "pnl": -850, "time": "2026-02-26"},  # 高杠杆亏损
        {"symbol": "SOLUSDT", "side": "BUY", "leverage": 10, "pnl": 210, "time": "2026-03-01"},
        {"symbol": "BTCUSDT", "side": "BUY", "leverage": 15, "pnl": 540, "time": "2026-03-03"},
    ]

def get_real_spot_trades(api_key, api_secret, symbol="BTCUSDT"):
    """读取真实现货交易记录（只读）"""
    import hmac, hashlib, time
    ts = int(time.time() * 1000)
    params = f"symbol={symbol}&limit=50&timestamp={ts}"
    sig = hmac.new(api_secret.encode(), params.encode(), hashlib.sha256).hexdigest()
    url = f"https://api.binance.com/api/v3/myTrades?{params}&signature={sig}"
    req = urllib.request.Request(url, headers={"X-MBX-APIKEY": api_key})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def analyze_spot(trades):
    """分析现货交易行为"""
    if not trades:
        return {}
    
    total = len(trades)
    wins = sum(1 for i in range(0, len(trades)-1, 2) 
               if trades[i]['side'] == 'BUY' and i+1 < len(trades)
               and float(trades[i+1]['price']) > float(trades[i]['price']))
    
    symbols = list(set(t['symbol'] for t in trades))
    
    return {
        "total_trades": total,
        "win_rate": round(wins / (total // 2) * 100, 1) if total >= 2 else 0,
        "symbols_traded": symbols,
        "concentration": "集中" if len(symbols) <= 2 else "分散",
        "avg_hold_days": 3.2,  # 演示用
    }

def analyze_futures(trades):
    """分析合约交易行为"""
    if not trades:
        return {}
    
    total_pnl = sum(t['pnl'] for t in trades)
    avg_leverage = sum(t['leverage'] for t in trades) / len(trades)
    max_leverage = max(t['leverage'] for t in trades)
    loss_trades = [t for t in trades if t['pnl'] < 0]
    
    return {
        "total_trades": len(trades),
        "total_pnl": round(total_pnl, 2),
        "avg_leverage": round(avg_leverage, 1),
        "max_leverage": max_leverage,
        "loss_rate": round(len(loss_trades) / len(trades) * 100, 1),
        "risk_level": "高危" if max_leverage >= 20 else "偏高" if max_leverage >= 10 else "正常",
    }

def determine_type(spot_analysis, futures_analysis):
    """根据分析结果判断交易者类型"""
    score = 50  # 基础分（平衡型）
    
    if futures_analysis:
        if futures_analysis['max_leverage'] >= 20:
            score += 30
        elif futures_analysis['max_leverage'] >= 10:
            score += 15
        if futures_analysis['loss_rate'] > 50:
            score += 10
    
    if spot_analysis:
        if spot_analysis['win_rate'] < 40:
            score += 10
        if spot_analysis['concentration'] == "集中":
            score += 5

    if score >= 85:
        return "radical"
    elif score >= 70:
        return "aggressive"
    elif score >= 55:
        return "balanced"
    elif score >= 40:
        return "steady"
    else:
        return "conservative"

def generate_report(mode="demo", api_key=None, api_secret=None):
    """生成完整人格分析报告"""

    if mode == "live":
        # ── live模式：调用 binance-pro skill ──────────────────
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from binance_skills import skill_get_spot_trades, skill_get_futures_trades

        spot_raw, err1 = skill_get_spot_trades("BTCUSDT", limit=50)
        fut_raw, err2  = skill_get_futures_trades("BTCUSDT", limit=20)

        if spot_raw is None:
            # Key缺失或请求失败 → 降级demo
            mode = "demo"
            spot_trades   = get_demo_spot_trades()
            futures_trades = get_demo_futures_trades()
            data_note = f"⚠️ live模式失败({err1})，已降级演示数据"
        else:
            spot_trades   = spot_raw
            futures_trades = fut_raw or []
            data_note = "🔐 真实数据（binance-pro skill / 只读API）"
    else:
        spot_trades   = get_demo_spot_trades()
        futures_trades = get_demo_futures_trades()
        data_note = "📊 演示数据（模拟盘）"
    
    spot = analyze_spot(spot_trades)
    futures = analyze_futures(futures_trades)
    trader_type_key = determine_type(spot, futures)
    trader_type = TRADER_TYPES[trader_type_key]
    
    report = f"""
🪞 交易者人格分析报告
{data_note}
生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*40}

🧬 你的交易者类型：{trader_type['emoji']} {trader_type['name']}
{trader_type['desc']}

📊 现货交易分析
• 总交易次数：{spot.get('total_trades', 0)} 次
• 胜率：{spot.get('win_rate', 0)}%
• 交易品种：{', '.join(spot.get('symbols_traded', []))}
• 持仓风格：{spot.get('concentration', '-')}
• 平均持仓：{spot.get('avg_hold_days', 0)} 天

📈 合约交易分析
• 总交易次数：{futures.get('total_trades', 0)} 次
• 累计盈亏：{futures.get('total_pnl', 0)} USDT
• 平均杠杆：{futures.get('avg_leverage', 0)}x
• 最高杠杆：{futures.get('max_leverage', 0)}x ⚠️ 风险等级：{futures.get('risk_level', '-')}
• 亏损率：{futures.get('loss_rate', 0)}%

⚠️ 你的致命弱点
{''.join(f"• {w}" + chr(10) for w in trader_type['weaknesses'])}
💡 核心改进建议
{''.join(f"• {s}" + chr(10) for s in trader_type['suggestions'])}
{'='*40}
下一步：查看「收益地图」优化你的闲置资产配置 🗺️
"""
    return report.strip()

if __name__ == "__main__":
    print(generate_report(mode="demo"))
