#!/usr/bin/env python3
"""
模拟数据生成器 — 生成典型币安用户数据用于演示
"""

from datetime import datetime, timezone, timedelta
import random


def generate_mock_user() -> dict:
    """生成一个典型的'有问题的交易者'模拟数据，用于演示"""

    # 模拟30天现货交易记录
    trades = []
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'BTCUSDT', 'BTCUSDT']  # BTC偏重
    for i in range(30):
        symbol = random.choice(symbols)
        pnl = random.choice([-320, -180, -95, -430, 85, 120, -210, 65, -380, 95])
        trades.append({
            "id": f"T{i:04d}",
            "symbol": symbol,
            "side": random.choice(["BUY", "SELL"]),
            "pnl": pnl,
            "buy_at_high": random.random() > 0.45,  # 55%概率追涨
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))).isoformat()
        })

    # 模拟合约交易记录（更多亏损，体现问题）
    futures_trades = []
    error_pool = [
        ["entry_timing", "stop_too_tight"],       # 插针止损
        ["entry_timing"],                          # 插针止损
        ["position_too_heavy", "revenge_trade"],   # 重仓+报复
        ["no_stop_loss", "hold_loss_too_long"],    # 不止损死扛
        ["revenge_trade"],                         # 报复交易
        ["direction_wrong"],                       # 方向错
        [],                                        # 正常交易
        [],                                        # 正常交易
    ]
    for i in range(47):
        pnl = random.choice([-850, -320, -180, -430, 210, 380, -95, 150, -670, 95])
        errors = random.choice(error_pool) if pnl < 0 else []
        futures_trades.append({
            "id": f"F{i:04d}",
            "symbol": "BTCUSDT",
            "side": random.choice(["LONG", "SHORT"]),
            "leverage": random.choice([5, 10, 10, 20, 10]),  # 偏高杠杆
            "pnl": pnl,
            "has_stop_loss": random.random() > 0.55,  # 45%没止损
            "errors": errors,
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))).isoformat()
        })

    return {
        "uid": "MOCK_88888888",
        "name": "模拟用户·小李",
        "join_date": "2023-06-15",
        "trades": trades,
        "futures_trades": futures_trades,
        "risk_preference": "medium",
        "lock_tolerance_days": 30,
        "assets": {
            "total_usdt": 12500,
            "BTC": 0.08,
            "ETH": 1.2,
            "BNB": 15,
            "USDT": 3500,
            "current_earn_config": {}  # 什么理财都没配，全放账户里
        },
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
