#!/usr/bin/env python3
"""
接入币安测试网 - 真实模拟盘数据
生成真实K线、价格、模拟交易记录
"""

import urllib.request, json, time, hmac, hashlib
from datetime import datetime, timezone

TESTNET_BASE = "https://testnet.binance.vision"

def get_klines(symbol="BTCUSDT", interval="1h", limit=24):
    """获取真实K线数据"""
    url = f"{TESTNET_BASE}/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    with urllib.request.urlopen(url, timeout=10) as r:
        data = json.loads(r.read())
    return [{
        "time": datetime.fromtimestamp(k[0]/1000).strftime("%Y-%m-%d %H:%M"),
        "open": float(k[1]),
        "high": float(k[2]),
        "low":  float(k[3]),
        "close": float(k[4]),
        "volume": float(k[5]),
    } for k in data]

def get_ticker(symbol="BTCUSDT"):
    """获取当前价格和24h涨跌"""
    url = f"{TESTNET_BASE}/api/v3/ticker/24hr?symbol={symbol}"
    with urllib.request.urlopen(url, timeout=10) as r:
        d = json.loads(r.read())
    return {
        "symbol": symbol,
        "price": float(d["lastPrice"]),
        "change_pct": float(d["priceChangePercent"]),
        "high": float(d["highPrice"]),
        "low": float(d["lowPrice"]),
        "volume": float(d["volume"]),
    }

def get_real_earn_rates():
    """获取币安Earn真实利率（公开API）"""
    # 活期理财利率
    url = "https://www.binance.com/bapi/earn/v1/friendly/lending/daily/product/list?asset=USDT&status=PURCHASING&pageIndex=1&pageSize=5"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
        products = d.get("data", {}).get("list", [])
        rates = {}
        for p in products:
            rates[p.get("asset","?")] = {
                "apy": float(p.get("latestAnnualInterestRate", 0)) * 100,
                "name": p.get("productName", ""),
            }
        return rates
    except:
        return {"USDT": {"apy": 4.2, "name": "活期理财(默认值)"}}

def generate_daily_market_report():
    """生成每日市场报告（基于真实测试网数据）"""
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    lines = [
        f"📊 每日市场报告",
        f"数据来源：币安测试网（真实行情）",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} CST",
        f"{'='*40}",
        f"",
    ]
    for sym in symbols:
        try:
            t = get_ticker(sym)
            arrow = "🟢" if t["change_pct"] >= 0 else "🔴"
            lines.append(f"{arrow} {sym}: ${t['price']:,.2f} ({t['change_pct']:+.2f}%)")
            lines.append(f"   今日区间: ${t['low']:,.0f} - ${t['high']:,.0f}")
        except Exception as e:
            lines.append(f"⚠️ {sym}: 数据获取失败")
    
    lines += ["", f"{'='*40}"]
    
    # 简单趋势判断
    try:
        btc = get_ticker("BTCUSDT")
        if btc["change_pct"] > 2:
            signal = "🐂 今日BTC强势，合约多单注意止盈"
        elif btc["change_pct"] < -2:
            signal = "🐻 今日BTC走弱，注意风控，减少合约仓位"
        else:
            signal = "😐 今日BTC横盘，等待方向确认，轻仓观望"
        lines.append(f"💡 今日策略信号：{signal}")
    except:
        pass
    
    return "\n".join(lines)

if __name__ == "__main__":
    print(generate_daily_market_report())
    print("\n" + "="*40)
    print("Earn利率数据:")
    rates = get_real_earn_rates()
    for asset, info in rates.items():
        print(f"  {asset}: 年化 {info['apy']:.2f}% - {info['name']}")
