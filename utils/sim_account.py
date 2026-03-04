#!/usr/bin/env python3
"""模拟盘账户 — SQLite持久化"""
import sqlite3, json, time
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).parent.parent / 'data' / 'sim_account.db'
DB_PATH.parent.mkdir(exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 10000.0,
            updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT, side TEXT, price REAL,
            qty REAL, pnl REAL, strategy TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS daily_stats (
            date TEXT PRIMARY KEY,
            start_balance REAL, end_balance REAL,
            trade_count INTEGER, win_count INTEGER, pnl REAL
        );
    ''')
    # 初始化账户
    if not conn.execute('SELECT 1 FROM account').fetchone():
        conn.execute("INSERT INTO account VALUES (1, 10000.0, ?)", 
                    (datetime.now(timezone.utc).isoformat(),))
    conn.commit()
    conn.close()

def get_balance() -> float:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    bal = conn.execute('SELECT balance FROM account WHERE id=1').fetchone()[0]
    conn.close()
    return bal

def record_trade(symbol, side, price, qty, pnl, strategy=''):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'INSERT INTO trades (symbol,side,price,qty,pnl,strategy,created_at) VALUES (?,?,?,?,?,?,?)',
        (symbol, side, price, qty, pnl, strategy, datetime.now(timezone.utc).isoformat())
    )
    conn.execute('UPDATE account SET balance=balance+?, updated_at=? WHERE id=1',
                (pnl, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()

def get_stats(days=7) -> dict:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    trades = conn.execute(
        'SELECT * FROM trades ORDER BY created_at DESC LIMIT 100'
    ).fetchall()
    balance = get_balance()
    total_pnl = sum(t[5] for t in trades)
    wins = sum(1 for t in trades if t[5] > 0)
    conn.close()
    return {
        'balance': balance,
        'total_pnl': total_pnl,
        'trade_count': len(trades),
        'win_rate': wins/len(trades) if trades else 0,
        'recent_trades': trades[:10]
    }

if __name__ == '__main__':
    init_db()
    print(f"模拟账户余额: ${get_balance():,.2f}")
    print(f"统计: {get_stats()}")
