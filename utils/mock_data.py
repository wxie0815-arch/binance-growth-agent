#!/usr/bin/env python3
"""
模拟数据生成器
根据真实币安API结构生成演示用模拟用户数据
"""

import random
from datetime import datetime, timezone, timedelta


def generate_mock_user() -> dict:
    """生成一个典型币安用户的模拟数据"""

    now = datetime.now(timezone.utc)

    # 模拟用户基本信息
    user = {
        "uid": "88888888",
        "nickname": "示例用户",
        "created_at": (now - timedelta(days=random.randint(180, 730))).isoformat(),
        "spot": _generate_spot_data(now),
        "futures": _generate_futures_data(now),
        "earn": _generate_earn_data(),
        "assets": _generate_assets(),
    }
    return user


def _generate_spot_data(now: datetime) -> dict:
    """模拟现货交易数据（符合binance-pro-cn API结构）"""
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "DOGEUSDT"]
    trades = []

    for i in range(40):
        symbol = random.choice(symbols)
        price_base = {"BTCUSDT": 70000, "ETHUSDT": 3200,
                      "BNBUSDT": 600, "SOLUSDT": 175, "DOGEUSDT": 0.20}
        price = price_base[symbol] * random.uniform(0.92, 1.08)
        qty = random.uniform(0.001, 0.05) if "BTC" in symbol else random.uniform(0.1, 5.0)
        is_buyer = random.choice([True, False])

        # 注入常见错误模式
        entry_timing = random.choices(
            ["高点追入", "正常区间", "低点布局"],
            weights=[0.45, 0.35, 0.20]
        )[0]

        trades.append({
            "symbol": symbol,
            "id": 200000 + i,
            "price": round(price, 4),
            "qty": round(qty, 6),
            "quoteQty": round(price * qty, 2),
            "commission": round(price * qty * 0.001, 6),
            "commissionAsset": "BNB",
            "time": int((now - timedelta(hours=i * random.randint(6, 48))).timestamp() * 1000),
            "isBuyer": is_buyer,
            "pnl": round(random.uniform(-120, 180) if random.random() > 0.45
                         else random.uniform(-250, -30), 2),
            "entry_timing": entry_timing,
            "hold_hours": random.randint(1, 96),
            "stop_loss_triggered": random.random() > 0.55,
        })

    return {
        "trades": trades,
        "total_volume_usdt": round(sum(t["quoteQty"] for t in trades), 2),
        "total_commission_bnb": round(sum(t["commission"] for t in trades), 6),
    }


def _generate_futures_data(now: datetime) -> dict:
    """模拟合约交易数据（符合binance-pro API结构）"""
    trades = []
    error_types = [
        "direction_wrong", "entry_timing_bad",
        "stop_too_tight", "position_too_heavy", "no_stop_loss"
    ]

    for i in range(25):
        is_long = random.choice([True, False])
        leverage = random.choice([5, 10, 20, 50])
        entry = 70000 * random.uniform(0.90, 1.10)
        pnl = (random.uniform(-300, 400) if random.random() > 0.42
               else random.uniform(-600, -50))

        trades.append({
            "symbol": "BTCUSDT",
            "side": "LONG" if is_long else "SHORT",
            "entry_price": round(entry, 2),
            "exit_price": round(entry * (1 + pnl / 5000), 2),
            "leverage": leverage,
            "margin_usdt": round(abs(pnl) * random.uniform(3, 8), 2),
            "pnl_usdt": round(pnl, 2),
            "pnl_pct": round(pnl / 1000 * 100, 2),
            "duration_hours": random.randint(1, 72),
            "error_type": random.choice(error_types) if pnl < 0 else None,
            "time": int((now - timedelta(hours=i * random.randint(8, 48))).timestamp() * 1000),
            "spot_equivalent_pnl": round(pnl * random.uniform(0.3, 0.7), 2),
        })

    return {"trades": trades}


def _generate_earn_data() -> dict:
    """模拟Earn配置数据"""
    return {
        "flexible": [
            {"asset": "USDT", "amount": round(random.uniform(500, 3000), 2), "apy": 4.2},
            {"asset": "BNB", "amount": round(random.uniform(1, 10), 4), "apy": 2.1},
        ],
        "locked": [
            {"asset": "USDT", "amount": round(random.uniform(1000, 5000), 2),
             "apy": 8.5, "duration_days": 90, "days_remaining": random.randint(10, 80)},
        ],
        "bnb_vault": {"amount": round(random.uniform(0.5, 5), 4), "apy": 3.8},
    }


def _generate_assets() -> dict:
    """模拟资产配置"""
    return {
        "spot_usdt_value": round(random.uniform(2000, 15000), 2),
        "futures_margin": round(random.uniform(500, 3000), 2),
        "earn_total_usdt": round(random.uniform(1500, 8000), 2),
        "total_usdt": 0,  # 由上面三项求和
    }
