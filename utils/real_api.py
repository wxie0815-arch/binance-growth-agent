#!/usr/bin/env python3
"""
真实API接入层 — binance-pro-cn skill 封装
使用 Binance 官方 REST API（HMAC-SHA256签名）
无真实 Key 时自动降级 mock 数据
"""

import os
import hmac
import hashlib
import time
import json
import requests
from pathlib import Path
from datetime import datetime, timezone

# ─── API Key 读取优先级 ───────────────────────────────────────────
# 1. 环境变量
# 2. ~/.openclaw/credentials/binance.json
# 3. 降级 mock

def _load_credentials():
    api_key    = os.environ.get("BINANCE_API_KEY", "")
    secret_key = os.environ.get("BINANCE_SECRET", "")
    if api_key and secret_key:
        return api_key, secret_key

    cred_path = Path.home() / ".openclaw" / "credentials" / "binance.json"
    if cred_path.exists():
        try:
            creds = json.loads(cred_path.read_text())
            return creds.get("apiKey", ""), creds.get("secretKey", "")
        except Exception:
            pass

    return "", ""

_API_KEY, _SECRET_KEY = _load_credentials()

BASE_SPOT    = "https://api.binance.com"
BASE_FUTURES = "https://fapi.binance.com"
TIMEOUT      = 8


def _sign(params_str: str, secret: str) -> str:
    return hmac.new(secret.encode(), params_str.encode(), hashlib.sha256).hexdigest()


def _get(url: str, params_str: str) -> dict | list | None:
    """带签名的 GET 请求"""
    ts = int(time.time() * 1000)
    full_params = f"{params_str}&timestamp={ts}" if params_str else f"timestamp={ts}"
    sig = _sign(full_params, _SECRET_KEY)
    full_url = f"{url}?{full_params}&signature={sig}"
    try:
        r = requests.get(full_url, headers={"X-MBX-APIKEY": _API_KEY}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  [real_api] ⚠️  请求失败: {e}")
        return None


# ─── 公开接口（无需签名） ─────────────────────────────────────────

def get_price(symbol: str = "BTCUSDT") -> float:
    """获取最新价格"""
    try:
        r = requests.get(
            f"{BASE_SPOT}/api/v3/ticker/price",
            params={"symbol": symbol}, timeout=TIMEOUT
        )
        return float(r.json()["price"])
    except Exception:
        return 0.0


def get_prices(symbols: list[str] = None) -> dict:
    """批量获取价格"""
    if not symbols:
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"]
    result = {}
    for s in symbols:
        result[s] = get_price(s)
    return result


# ─── 账户接口（需签名） ──────────────────────────────────────────

def get_spot_balance() -> dict:
    """现货账户余额（过滤零余额）"""
    if not (_API_KEY and _SECRET_KEY):
        print("  [real_api] 无真实 Key，返回 mock 余额")
        return _mock_spot_balance()

    data = _get(f"{BASE_SPOT}/api/v3/account", "")
    if data and "balances" in data:
        balances = {
            b["asset"]: {
                "free": float(b["free"]),
                "locked": float(b["locked"])
            }
            for b in data["balances"]
            if float(b["free"]) > 0 or float(b["locked"]) > 0
        }
        return {"source": "real", "balances": balances, "time": datetime.now(timezone.utc).isoformat()}
    return _mock_spot_balance()


def get_futures_balance() -> dict:
    """合约账户余额"""
    if not (_API_KEY and _SECRET_KEY):
        return _mock_futures_balance()

    data = _get(f"{BASE_FUTURES}/fapi/v2/balance", "")
    if data:
        items = [d for d in data if float(d.get("balance", 0)) > 0]
        return {"source": "real", "balances": items, "time": datetime.now(timezone.utc).isoformat()}
    return _mock_futures_balance()


def get_futures_positions() -> list:
    """合约当前持仓（过滤零仓）"""
    if not (_API_KEY and _SECRET_KEY):
        return _mock_positions()

    data = _get(f"{BASE_FUTURES}/fapi/v2/positionRisk", "")
    if data:
        positions = [p for p in data if float(p.get("positionAmt", 0)) != 0]
        for p in positions:
            p["source"] = "real"
        return positions
    return _mock_positions()


def get_spot_trade_history(symbol: str = "BTCUSDT", limit: int = 50) -> list:
    """现货交易历史"""
    if not (_API_KEY and _SECRET_KEY):
        return _mock_trade_history()

    data = _get(f"{BASE_SPOT}/api/v3/myTrades", f"symbol={symbol}&limit={limit}")
    if data and isinstance(data, list):
        return [{"source": "real", **t} for t in data]
    return _mock_trade_history()


def get_futures_trade_history(symbol: str = "BTCUSDT", limit: int = 50) -> list:
    """合约交易历史"""
    if not (_API_KEY and _SECRET_KEY):
        return _mock_trade_history()

    data = _get(f"{BASE_FUTURES}/fapi/v1/userTrades", f"symbol={symbol}&limit={limit}")
    if data and isinstance(data, list):
        return [{"source": "real", **t} for t in data]
    return _mock_trade_history()


def get_account_summary() -> dict:
    """全账户汇总（现货 + 合约 + 实时价格）"""
    print("  [real_api] 拉取账户汇总...")
    spot    = get_spot_balance()
    futures = get_futures_balance()
    prices  = get_prices()
    positons = get_futures_positions()

    # 估算现货 USDT 价值
    spot_usdt = 0.0
    for asset, bal in spot.get("balances", {}).items():
        free = bal["free"]
        if asset == "USDT":
            spot_usdt += free
        else:
            sym = f"{asset}USDT"
            if sym in prices:
                spot_usdt += free * prices[sym]

    # 合约保证金
    futures_usdt = sum(
        float(b.get("availableBalance", 0))
        for b in futures.get("balances", [])
        if b.get("asset") == "USDT"
    )

    source = spot.get("source", "mock")

    return {
        "source": source,
        "spot_usdt_value": round(spot_usdt, 2),
        "futures_usdt_balance": round(futures_usdt, 2),
        "total_usdt_estimate": round(spot_usdt + futures_usdt, 2),
        "open_positions": len(positons),
        "prices": prices,
        "time": datetime.now(timezone.utc).isoformat(),
    }


# ─── Mock 降级数据 ───────────────────────────────────────────────

def _mock_spot_balance() -> dict:
    return {
        "source": "mock",
        "balances": {
            "USDT": {"free": 5230.5,  "locked": 0.0},
            "BTC":  {"free": 0.12,    "locked": 0.0},
            "ETH":  {"free": 1.5,     "locked": 0.0},
            "BNB":  {"free": 8.3,     "locked": 0.0},
        },
        "time": datetime.now(timezone.utc).isoformat(),
    }


def _mock_futures_balance() -> dict:
    return {
        "source": "mock",
        "balances": [
            {"asset": "USDT", "balance": "3000.00", "availableBalance": "2800.00"},
        ],
        "time": datetime.now(timezone.utc).isoformat(),
    }


def _mock_positions() -> list:
    return [
        {
            "source": "mock",
            "symbol": "BTCUSDT",
            "positionAmt": "0.01",
            "entryPrice": "71500.0",
            "unRealizedProfit": "123.5",
            "leverage": "10",
            "marginType": "isolated",
        }
    ]


def _mock_trade_history() -> list:
    import random
    trades = []
    symbols_prices = {"BTCUSDT": 71000, "ETHUSDT": 3200, "BNBUSDT": 600}
    for i in range(10):
        sym = random.choice(list(symbols_prices.keys()))
        side = random.choice(["BUY", "SELL"])
        price = symbols_prices[sym] * random.uniform(0.97, 1.03)
        qty   = round(random.uniform(0.001, 0.05), 4)
        trades.append({
            "source": "mock",
            "symbol": sym,
            "side": side,
            "price": round(price, 2),
            "qty": qty,
            "quoteQty": round(price * qty, 4),
            "commission": round(price * qty * 0.001, 4),
            "commissionAsset": "USDT",
            "time": int(time.time() * 1000) - i * 3600000,
        })
    return trades


if __name__ == "__main__":
    print("=== Real API 测试 ===")
    print(f"API Key 配置: {'✅ 已配置' if _API_KEY else '⚠️  未配置（使用mock）'}")
    print(f"BTC 最新价格: ${get_price('BTCUSDT'):,.2f}")
    summary = get_account_summary()
    print(f"账户数据来源: {summary['source']}")
    print(f"现货估值: ${summary['spot_usdt_value']:,.2f} USDT")
    print(f"合约余额: ${summary['futures_usdt_balance']:,.2f} USDT")
    print(f"总估值:   ${summary['total_usdt_estimate']:,.2f} USDT")
    print(f"持仓数:   {summary['open_positions']}")
