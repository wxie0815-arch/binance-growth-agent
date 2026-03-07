#!/usr/bin/env python3
"""
Binance Skills 统一调用层
live模式下，所有数据通过官方skill接口获取
demo模式下，使用db/simulator.py的模拟数据
"""
import hmac, hashlib, time, json, os, urllib.request, urllib.parse
from datetime import datetime

CRED_PATH = os.path.expanduser("~/.openclaw/credentials/binance.json")

# ─── 认证 ───────────────────────────────────────────────

def load_keys():
    if os.path.exists(CRED_PATH):
        with open(CRED_PATH) as f:
            d = json.load(f)
        return d.get("apiKey") or d.get("api_key"), d.get("secretKey") or d.get("secret_key")
    return os.environ.get("BINANCE_API_KEY"), os.environ.get("BINANCE_SECRET")

def _sign(params: dict, secret: str) -> str:
    qs = urllib.parse.urlencode(params)
    return hmac.new(secret.encode(), qs.encode(), hashlib.sha256).hexdigest()

def _get(url: str, params: dict, api_key: str, secret: str) -> dict:
    params["timestamp"] = int(time.time() * 1000)
    params["signature"] = _sign(params, secret)
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={"X-MBX-APIKEY": api_key, "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

# ─── SKILL 1: binance-pro → 现货交易记录 ────────────────

def skill_get_spot_trades(symbol="BTCUSDT", limit=50):
    """
    调用 binance-pro skill
    接口: GET /api/v3/myTrades
    文档: SKILL.md - Account trade list
    """
    api_key, secret = load_keys()
    if not api_key:
        return None, "no_key"
    try:
        data = _get(
            "https://api.binance.com/api/v3/myTrades",
            {"symbol": symbol, "limit": limit},
            api_key, secret
        )
        trades = []
        for t in data:
            trades.append({
                "symbol":   t["symbol"],
                "side":     "BUY" if t["isBuyer"] else "SELL",
                "price":    float(t["price"]),
                "qty":      float(t["qty"]),
                "pnl":      float(t.get("realizedPnl", 0)),
                "time":     datetime.fromtimestamp(t["time"]/1000).strftime("%Y-%m-%d %H:%M"),
                "source":   "binance-pro/myTrades"  # skill来源标注
            })
        return trades, "ok"
    except Exception as e:
        return None, str(e)

# ─── SKILL 2: binance-pro → 合约持仓+交易记录 ────────────

def skill_get_futures_trades(symbol="BTCUSDT", limit=20):
    """
    调用 binance-pro skill
    接口: GET /fapi/v1/userTrades
    文档: SKILL.md - Futures section
    """
    api_key, secret = load_keys()
    if not api_key:
        return None, "no_key"
    try:
        data = _get(
            "https://fapi.binance.com/fapi/v1/userTrades",
            {"symbol": symbol, "limit": limit},
            api_key, secret
        )
        trades = []
        for t in data:
            trades.append({
                "symbol":   t["symbol"],
                "side":     t["side"],
                "price":    float(t["price"]),
                "qty":      float(t["qty"]),
                "pnl":      float(t.get("realizedPnl", 0)),
                "time":     datetime.fromtimestamp(t["time"]/1000).strftime("%Y-%m-%d %H:%M"),
                "source":   "binance-pro/fapi/userTrades"
            })
        return trades, "ok"
    except Exception as e:
        return None, str(e)

def skill_get_futures_positions():
    """
    调用 binance-pro skill
    接口: GET /fapi/v2/positionRisk
    文档: SKILL.md - Get All Futures Positions
    """
    api_key, secret = load_keys()
    if not api_key:
        return None, "no_key"
    try:
        data = _get(
            "https://fapi.binance.com/fapi/v2/positionRisk",
            {}, api_key, secret
        )
        positions = [p for p in data if float(p.get("positionAmt", 0)) != 0]
        return [{"symbol": p["symbol"],
                 "side": "LONG" if float(p["positionAmt"]) > 0 else "SHORT",
                 "size": abs(float(p["positionAmt"])),
                 "entry": float(p["entryPrice"]),
                 "pnl":   float(p["unRealizedProfit"]),
                 "leverage": int(p.get("leverage", 1)),
                 "source": "binance-pro/fapi/positionRisk"} for p in positions], "ok"
    except Exception as e:
        return None, str(e)

# ─── SKILL 3: binance-pro → Earn产品列表 ────────────────

def skill_get_earn_products():
    """
    调用 binance-pro skill
    接口: GET /sapi/v1/simple-earn/flexible/list
    文档: SKILL.md - Earn/Staking section
    """
    api_key, secret = load_keys()
    if not api_key:
        return None, "no_key"
    try:
        data = _get(
            "https://api.binance.com/sapi/v1/simple-earn/flexible/list",
            {"asset": "USDT", "size": 10},
            api_key, secret
        )
        products = []
        for p in data.get("rows", []):
            products.append({
                "name":    p.get("productName", ""),
                "asset":   p.get("asset", ""),
                "apy":     float(p.get("latestAnnualPercentageRate", 0)) * 100,
                "min":     float(p.get("minPurchaseAmount", 0)),
                "source":  "binance-pro/simple-earn/flexible"
            })
        return products, "ok"
    except Exception as e:
        return None, str(e)

# ─── SKILL 4: spot skill → 现货账户余额 ──────────────────

def skill_get_spot_balance():
    """
    调用 spot skill
    接口: GET /api/v3/account
    文档: spot/SKILL.md - Account information
    """
    api_key, secret = load_keys()
    if not api_key:
        return None, "no_key"
    try:
        data = _get("https://api.binance.com/api/v3/account", {}, api_key, secret)
        balances = [
            {"asset": b["asset"], "free": float(b["free"]), "locked": float(b["locked"]),
             "source": "spot/account"}
            for b in data.get("balances", [])
            if float(b["free"]) > 0 or float(b["locked"]) > 0
        ]
        return balances, "ok"
    except Exception as e:
        return None, str(e)

# ─── SKILL 5: 公开行情 (无需Key) ────────────────────────

def skill_get_realtime_price(symbol="BTCUSDT"):
    """
    调用 spot skill 公开接口
    接口: GET /api/v3/ticker/price
    """
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        with urllib.request.urlopen(url, timeout=8) as r:
            d = json.loads(r.read())
        return {"symbol": symbol, "price": float(d["price"]), "source": "spot/ticker/price"}, "ok"
    except Exception as e:
        return None, str(e)

def skill_get_top_movers(limit=10):
    """
    调用 spot skill 公开接口
    接口: GET /api/v3/ticker/24hr
    用于: square_oracle实时热点
    """
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        usdt = [d for d in data if d["symbol"].endswith("USDT") and float(d["quoteVolume"]) > 1e6]
        top = sorted(usdt, key=lambda x: float(x["quoteVolume"]), reverse=True)[:limit]
        return [{"symbol": t["symbol"].replace("USDT",""),
                 "change_pct": float(t["priceChangePercent"]),
                 "volume_usdt": float(t["quoteVolume"]),
                 "source": "spot/ticker/24hr"} for t in top], "ok"
    except Exception as e:
        return None, str(e)

# ─── SKILL 6: crypto-market-rank → 社交热度榜 ────────────

def skill_get_social_hype(chain_id="56", limit=10):
    """
    调用 crypto-market-rank skill
    接口: GET social/hype/rank/leaderboard
    文档: crypto-market-rank/SKILL.md - API 1
    无需API Key（公开接口）
    """
    try:
        url = (f"https://web3.binance.com/bapi/defi/v1/public/wallet-direct/"
               f"buw/wallet/market/token/pulse/social/hype/rank/leaderboard"
               f"?chainId={chain_id}&sentiment=All&socialLanguage=ALL&targetLanguage=en&timeRange=1")
        req = urllib.request.Request(url, headers={"Accept-Encoding": "identity", "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
        items = d.get("data", {}).get("leaderBoardList", [])[:limit]
        return [{"symbol":    i["metaInfo"]["symbol"],
                 "hype":      i["socialHypeInfo"]["socialHype"],
                 "sentiment": i["socialHypeInfo"]["sentiment"],
                 "summary":   i["socialHypeInfo"].get("socialSummaryBriefTranslated", ""),
                 "price_change": i.get("marketInfo", {}).get("priceChange", 0),
                 "source":    "crypto-market-rank/social-hype"} for i in items], "ok"
    except Exception as e:
        return None, str(e)

# ─── SKILL 7: crypto-market-rank → 趋势代币排行 ──────────

def skill_get_trending_tokens(rank_type=10, chain_id="56", limit=8):
    """
    调用 crypto-market-rank skill
    接口: POST unified/rank/list
    rankType: 10=Trending 11=TopSearch 20=Alpha 40=Stock
    文档: crypto-market-rank/SKILL.md - API 2
    无需API Key（公开接口）
    """
    try:
        url = ("https://web3.binance.com/bapi/defi/v1/public/wallet-direct/"
               "buw/wallet/market/token/pulse/unified/rank/list")
        body = json.dumps({"rankType": rank_type, "chainId": chain_id,
                           "page": 1, "size": limit}).encode()
        req = urllib.request.Request(url, data=body,
                                     headers={"Content-Type": "application/json",
                                              "Accept-Encoding": "identity"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
        items = d.get("data", {}).get("list", [])[:limit]
        return [{"symbol":      i.get("symbol", ""),
                 "price_change": i.get("priceChange24h", 0),
                 "volume":      i.get("volume24h", 0),
                 "rank_type":   rank_type,
                 "source":      "crypto-market-rank/unified-rank"} for i in items], "ok"
    except Exception as e:
        return None, str(e)

# ─── SKILL 8: trading-signal → 智能钱信号 ────────────────

def skill_get_smart_money_signals(chain_id="56", limit=5):
    """
    调用 trading-signal skill
    接口: POST signal/smart-money
    文档: trading-signal/SKILL.md
    无需API Key（公开接口）
    """
    try:
        url = ("https://web3.binance.com/bapi/defi/v1/public/wallet-direct/"
               "buw/wallet/web/signal/smart-money")
        body = json.dumps({"smartSignalType": "", "page": 1,
                           "pageSize": limit, "chainId": chain_id}).encode()
        req = urllib.request.Request(url, data=body,
                                     headers={"Content-Type": "application/json",
                                              "Accept-Encoding": "identity"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
        items = d.get("data", [])[:limit]
        return [{"ticker":    i.get("ticker", ""),
                 "direction": i.get("direction", ""),
                 "max_gain":  i.get("maxGain", "0"),
                 "exit_rate": i.get("exitRate", 0),
                 "status":    i.get("status", ""),
                 "smart_count": i.get("smartMoneyCount", 0),
                 "alert_price": i.get("alertPrice", "0"),
                 "current_price": i.get("currentPrice", "0"),
                 "source":    "trading-signal/smart-money"} for i in items], "ok"
    except Exception as e:
        return None, str(e)

def check_skill_status():
    api_key, secret = load_keys()
    status = {
        "has_key": bool(api_key),
        "key_preview": api_key[:8] + "..." if api_key else None,
        "skills_ready": {
            "binance-pro": bool(api_key),
            "spot": True,  # 公开接口无需key
        }
    }
    # 测试公开接口连通性
    price, err = skill_get_realtime_price("BTCUSDT")
    status["btc_price"] = price["price"] if price else f"error:{err}"
    # 测试top movers
    movers, err2 = skill_get_top_movers(3)
    status["top_movers"] = [m["symbol"] for m in movers] if movers else f"error:{err2}"
    return status

if __name__ == "__main__":
    print("=== Binance Skills 状态检查 ===")
    s = check_skill_status()
    print(json.dumps(s, indent=2, ensure_ascii=False))
