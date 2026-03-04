#!/usr/bin/env python3
"""
真实API接入层 — binance-pro-cn skill调用封装
在没有真实Key时自动降级到mock数据
"""
import os, json, time
from pathlib import Path

SKILL_DIR = Path('/home/ubuntu/.openclaw/workspace/skills/binance-pro-cn')

def call_skill(action: str, params: dict = {}) -> dict:
    """调用binance-pro-cn skill，失败时降级mock"""
    try:
        import subprocess
        cmd = ['python3', '-c', f'''
import sys
sys.path.insert(0, "{SKILL_DIR}")
# skill调用占位，等真实key配置后替换
print("{{}}")
''']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        data = json.loads(result.stdout.strip() or '{}')
        if data:
            return {'source': 'real', 'data': data}
    except Exception as e:
        pass
    # 降级mock
    from utils.mock_data import generate_mock_user
    return {'source': 'mock', 'data': generate_mock_user()}

def get_spot_trades(api_key: str = '', api_secret: str = '', symbol: str = 'BTCUSDT', limit: int = 100) -> list:
    """读取现货交易历史"""
    if api_key and api_secret:
        try:
            import hmac, hashlib, requests
            from datetime import datetime, timezone
            ts = int(time.time() * 1000)
            params_str = f'symbol={symbol}&limit={limit}&timestamp={ts}'
            sig = hmac.new(api_secret.encode(), params_str.encode(), hashlib.sha256).hexdigest()
            r = requests.get(
                f'https://api.binance.com/api/v3/myTrades?{params_str}&signature={sig}',
                headers={'X-MBX-APIKEY': api_key}, timeout=5
            )
            return r.json()
        except Exception as e:
            print(f'[real API] {e}, 降级mock')
    # mock数据
    from utils.mock_data import generate_mock_user
    return generate_mock_user()['spot_trades']

def get_futures_trades(api_key: str = '', api_secret: str = '', symbol: str = 'BTCUSDT') -> list:
    """读取合约交易历史"""
    if api_key and api_secret:
        try:
            import hmac, hashlib, requests
            ts = int(time.time() * 1000)
            params_str = f'symbol={symbol}&timestamp={ts}'
            sig = hmac.new(api_secret.encode(), params_str.encode(), hashlib.sha256).hexdigest()
            r = requests.get(
                f'https://fapi.binance.com/fapi/v1/userTrades?{params_str}&signature={sig}',
                headers={'X-MBX-APIKEY': api_key}, timeout=5
            )
            return r.json()
        except Exception as e:
            print(f'[real API] {e}, 降级mock')
    from utils.mock_data import generate_mock_user
    return generate_mock_user()['futures_trades']

def get_btc_price() -> float:
    """获取BTC实时价格"""
    try:
        import requests
        r = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=5)
        return float(r.json()['price'])
    except:
        return 73000.0
