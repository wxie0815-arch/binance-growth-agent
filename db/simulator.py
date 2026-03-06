#!/usr/bin/env python3
"""
模拟盘SQLite数据库 - 存储演示交易记录、PnL追踪
"""
import sqlite3, os, json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "simulator.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT DEFAULT (datetime('now')),
        symbol TEXT,
        side TEXT,
        price REAL,
        qty REAL,
        leverage INTEGER DEFAULT 1,
        pnl REAL DEFAULT 0,
        mode TEXT DEFAULT 'demo'
    );
    CREATE TABLE IF NOT EXISTS daily_report (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT UNIQUE,
        total_pnl REAL,
        win_rate REAL,
        trade_count INTEGER,
        summary TEXT
    );
    """)
    conn.commit()
    conn.close()

def insert_demo_trades():
    """插入Day1演示数据"""
    demo = [
        ("BTCUSDT","BUY",68500,0.02,1,0,"demo"),
        ("BTCUSDT","SELL",71200,0.02,1,54,"demo"),
        ("ETHUSDT","BUY",3800,0.5,1,0,"demo"),
        ("ETHUSDT","SELL",3650,0.5,1,-75,"demo"),
        ("BTCUSDT","BUY",69000,0.001,10,0,"demo"),
        ("BTCUSDT","SELL",70500,0.001,10,15,"demo"),
        ("BTCUSDT","SELL",70592,0.001,20,0,"demo"),  # 当前SHORT
    ]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for row in demo:
        c.execute("INSERT INTO trades (symbol,side,price,qty,leverage,pnl,mode) VALUES (?,?,?,?,?,?,?)", row)
    conn.commit()
    conn.close()
    print(f"✅ 插入 {len(demo)} 条演示交易记录")

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(pnl), AVG(pnl) FROM trades")
    total, sum_pnl, avg_pnl = c.fetchone()
    c.execute("SELECT COUNT(*) FROM trades WHERE pnl > 0")
    wins = c.fetchone()[0]
    conn.close()
    return {
        "total_trades": total or 0,
        "total_pnl": round(sum_pnl or 0, 2),
        "avg_pnl": round(avg_pnl or 0, 2),
        "win_rate": round((wins / total * 100) if total else 0, 1)
    }

if __name__ == "__main__":
    init_db()
    insert_demo_trades()
    stats = get_stats()
    print(f"📊 数据库统计: {json.dumps(stats, ensure_ascii=False)}")
