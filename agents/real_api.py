#!/usr/bin/env python3
"""
真实币安API接入层 - 替换mock数据
需要: ~/.openclaw/credentials/binance.json
"""
import json, hmac, hashlib, time, os
import urllib.request, urllib.parse

CRED_PATH = os.path.expanduser("~/.openclaw/credentials/binance.json")

def load_keys():
    if os.path.exists(CRED_PATH):
        with open(CRED_PATH) as f:
            cred = json.load(f)
            return cred.get("apiKey"), cred.get("secretKey")
    api_key = os.environ.get("BINANCE_API_KEY")
    secret  = os.environ.get("BINANCE_SECRET")
    return api_key, secret

def sign(params: dict, secret: str) -> str:
    query = urllib.parse.urlencode(params)
    return hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()

def get_spot_trades(symbol="BTCUSDT", limit=50):
    api_key, secret = load_keys()
    if not api_key:
        return None, "NO_API_KEY"
    params = {"symbol": symbol, "limit": limit, "timestamp": int(time.time()*1000)}
    params["signature"] = sign(params, secret)
    url = "https://api.binance.com/api/v3/myTrades?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"X-MBX-APIKEY": api_key})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()), None
    except Exception as e:
        return None, str(e)

def get_futures_positions():
    api_key, secret = load_keys()
    if not api_key:
        return None, "NO_API_KEY"
    params = {"timestamp": int(time.time()*1000)}
    params["signature"] = sign(params, secret)
    url = "https://fapi.binance.com/fapi/v2/positionRisk?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"X-MBX-APIKEY": api_key})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            return [p for p in data if float(p.get("positionAmt","0")) != 0], None
    except Exception as e:
        return None, str(e)

def get_futures_trades(symbol="BTCUSDT", limit=20):
    api_key, secret = load_keys()
    if not api_key:
        return None, "NO_API_KEY"
    params = {"symbol": symbol, "limit": limit, "timestamp": int(time.time()*1000)}
    params["signature"] = sign(params, secret)
    url = "https://fapi.binance.com/fapi/v1/userTrades?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"X-MBX-APIKEY": api_key})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()), None
    except Exception as e:
        return None, str(e)

def get_earn_products():
    """获取Earn活期产品列表（公开接口）"""
    url = "https://api.binance.com/sapi/v1/simple-earn/flexible/list?asset=USDT&size=5"
    api_key, secret = load_keys()
    headers = {"X-MBX-APIKEY": api_key} if api_key else {}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()), None
    except Exception as e:
        return None, str(e)

def check_api_status():
    api_key, secret = load_keys()
    status = {
        "has_key": bool(api_key),
        "key_preview": api_key[:8] + "..." if api_key else None,
        "source": "credentials_file" if os.path.exists(CRED_PATH) else "env_var"
    }
    return status

if __name__ == "__main__":
    s = check_api_status()
    print(f"API状态: {json.dumps(s, ensure_ascii=False, indent=2)}")
    if s["has_key"]:
        trades, err = get_spot_trades("BTCUSDT", 5)
        if err:
            print(f"❌ 现货交易记录: {err}")
        else:
            print(f"✅ 现货交易记录: 获取 {len(trades)} 条")
