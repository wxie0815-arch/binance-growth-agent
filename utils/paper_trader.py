#!/usr/bin/env python3
"""
模拟盘交易引擎 — SQLite 持久化
支持：下单 / 持仓查询 / PnL统计 / 历史记录
"""

import sqlite3
import time
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


DB_PATH = Path(__file__).parent.parent / "data" / "paper_trading.db"


class PaperTrader:
    """模拟盘交易引擎"""

    INITIAL_BALANCE = 10_000.0  # 初始 USDT

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # ─── DB 初始化 ────────────────────────────────────────────────

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS account (
                    id       INTEGER PRIMARY KEY,
                    balance  REAL NOT NULL DEFAULT 10000.0,
                    created  TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS orders (
                    order_id    TEXT PRIMARY KEY,
                    symbol      TEXT NOT NULL,
                    side        TEXT NOT NULL,
                    order_type  TEXT NOT NULL DEFAULT 'MARKET',
                    qty         REAL NOT NULL,
                    price       REAL NOT NULL,
                    leverage    INTEGER NOT NULL DEFAULT 1,
                    margin_used REAL NOT NULL DEFAULT 0,
                    status      TEXT NOT NULL DEFAULT 'FILLED',
                    pnl         REAL,
                    time        TEXT NOT NULL,
                    close_time  TEXT,
                    note        TEXT
                );

                CREATE TABLE IF NOT EXISTS positions (
                    pos_id      TEXT PRIMARY KEY,
                    symbol      TEXT NOT NULL,
                    side        TEXT NOT NULL,
                    qty         REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    leverage    INTEGER NOT NULL DEFAULT 1,
                    margin_used REAL NOT NULL,
                    open_time   TEXT NOT NULL,
                    stop_loss   REAL,
                    take_profit REAL
                );

                CREATE TABLE IF NOT EXISTS pnl_history (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol      TEXT NOT NULL,
                    side        TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price  REAL NOT NULL,
                    qty         REAL NOT NULL,
                    leverage    INTEGER NOT NULL,
                    pnl_usdt    REAL NOT NULL,
                    pnl_pct     REAL NOT NULL,
                    close_time  TEXT NOT NULL
                );
            """)
            # 初始化账户（只做一次）
            cur = conn.execute("SELECT COUNT(*) FROM account")
            if cur.fetchone()[0] == 0:
                conn.execute(
                    "INSERT INTO account (balance, created) VALUES (?, ?)",
                    (self.INITIAL_BALANCE, datetime.now(timezone.utc).isoformat())
                )

    # ─── 账户 ────────────────────────────────────────────────────

    def get_balance(self) -> float:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT balance FROM account WHERE id=1").fetchone()
            return row[0] if row else self.INITIAL_BALANCE

    def _update_balance(self, delta: float, conn: sqlite3.Connection):
        conn.execute("UPDATE account SET balance = balance + ? WHERE id=1", (delta,))

    # ─── 开仓 ────────────────────────────────────────────────────

    def open_position(
        self,
        symbol: str,
        side: str,          # "LONG" | "SHORT"
        qty: float,
        price: float,
        leverage: int = 1,
        stop_loss: float = None,
        take_profit: float = None,
        note: str = None,
    ) -> dict:
        """开仓并记录"""
        side = side.upper()
        if side not in ("LONG", "SHORT"):
            return {"error": "side 必须是 LONG 或 SHORT"}

        margin_used = (qty * price) / leverage
        balance = self.get_balance()

        if margin_used > balance:
            return {"error": f"余额不足: 需要 ${margin_used:.2f}，当前 ${balance:.2f}"}

        pos_id   = str(uuid.uuid4())[:8]
        order_id = str(uuid.uuid4())[:8]
        now      = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            # 冻结保证金
            self._update_balance(-margin_used, conn)

            # 写入持仓
            conn.execute("""
                INSERT INTO positions
                  (pos_id, symbol, side, qty, entry_price, leverage, margin_used, open_time, stop_loss, take_profit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (pos_id, symbol, side, qty, price, leverage, margin_used, now, stop_loss, take_profit))

            # 写入订单
            conn.execute("""
                INSERT INTO orders
                  (order_id, symbol, side, qty, price, leverage, margin_used, time, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (order_id, symbol, side, qty, price, leverage, margin_used, now, note))

        print(f"  [paper] ✅ 开仓 {side} {symbol} x{leverage} 数量:{qty} 价格:${price:,.2f} 保证金:${margin_used:.2f}")
        return {
            "pos_id": pos_id,
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "entry_price": price,
            "leverage": leverage,
            "margin_used": round(margin_used, 4),
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "status": "FILLED",
            "time": now,
        }

    # ─── 平仓 ────────────────────────────────────────────────────

    def close_position(self, pos_id: str, exit_price: float) -> dict:
        """平仓并计算 PnL"""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("""
                SELECT pos_id, symbol, side, qty, entry_price, leverage, margin_used
                FROM positions WHERE pos_id=?
            """, (pos_id,)).fetchone()

            if not row:
                return {"error": f"持仓 {pos_id} 不存在"}

            _, symbol, side, qty, entry_price, leverage, margin_used = row
            now = datetime.now(timezone.utc).isoformat()

            # 计算 PnL
            if side == "LONG":
                pnl_usdt = (exit_price - entry_price) * qty
            else:  # SHORT
                pnl_usdt = (entry_price - exit_price) * qty

            pnl_pct = (pnl_usdt / margin_used) * 100

            # 归还保证金 + PnL
            self._update_balance(margin_used + pnl_usdt, conn)

            # 删除持仓
            conn.execute("DELETE FROM positions WHERE pos_id=?", (pos_id,))

            # 记录 PnL 历史
            conn.execute("""
                INSERT INTO pnl_history
                  (symbol, side, entry_price, exit_price, qty, leverage, pnl_usdt, pnl_pct, close_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (symbol, side, entry_price, exit_price, qty, leverage,
                  round(pnl_usdt, 4), round(pnl_pct, 2), now))

            # 更新订单状态
            conn.execute("""
                UPDATE orders SET pnl=?, close_time=?, status='CLOSED'
                WHERE symbol=? AND close_time IS NULL
                ORDER BY ROWID DESC LIMIT 1
            """, (round(pnl_usdt, 4), now, symbol))

        print(f"  [paper] {'✅' if pnl_usdt >= 0 else '❌'} 平仓 {side} {symbol} "
              f"盈亏: ${pnl_usdt:+.2f} ({pnl_pct:+.1f}%)")
        return {
            "pos_id": pos_id,
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "qty": qty,
            "leverage": leverage,
            "pnl_usdt": round(pnl_usdt, 4),
            "pnl_pct": round(pnl_pct, 2),
            "close_time": now,
        }

    # ─── 查询 ────────────────────────────────────────────────────

    def get_positions(self) -> list:
        """当前所有持仓"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM positions ORDER BY open_time DESC").fetchall()
            return [dict(r) for r in rows]

    def get_pnl_summary(self) -> dict:
        """PnL 汇总统计"""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM pnl_history").fetchall()

        if not rows:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "win_rate": 0.0,
                "total_pnl_usdt": 0.0,
                "balance": round(self.get_balance(), 2),
                "return_pct": round((self.get_balance() - self.INITIAL_BALANCE) / self.INITIAL_BALANCE * 100, 2),
            }

        total_pnl  = sum(r[7] for r in rows)   # pnl_usdt
        wins       = sum(1 for r in rows if r[7] > 0)
        win_rate   = wins / len(rows) * 100

        return {
            "total_trades": len(rows),
            "winning_trades": wins,
            "win_rate": round(win_rate, 1),
            "total_pnl_usdt": round(total_pnl, 2),
            "balance": round(self.get_balance(), 2),
            "return_pct": round((self.get_balance() - self.INITIAL_BALANCE) / self.INITIAL_BALANCE * 100, 2),
        }

    def get_order_history(self, limit: int = 20) -> list:
        """订单历史"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM orders ORDER BY time DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def reset(self):
        """重置模拟盘（回到初始状态）"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                DELETE FROM orders;
                DELETE FROM positions;
                DELETE FROM pnl_history;
                UPDATE account SET balance=10000.0 WHERE id=1;
            """)
        print("  [paper] 🔄 模拟盘已重置，余额恢复 $10,000")

    def print_status(self):
        """打印当前状态"""
        summary = self.get_pnl_summary()
        positions = self.get_positions()
        print("\n" + "=" * 45)
        print("📊 模拟盘状态")
        print("=" * 45)
        print(f"  账户余额:  ${summary['balance']:>10,.2f} USDT")
        print(f"  总收益率:  {summary['return_pct']:>+.2f}%")
        print(f"  总盈亏:    ${summary['total_pnl_usdt']:>+.2f} USDT")
        print(f"  交易次数:  {summary['total_trades']}")
        print(f"  胜率:      {summary['win_rate']:.1f}%")
        print(f"  当前持仓:  {len(positions)} 笔")
        for p in positions:
            print(f"    [{p['pos_id']}] {p['side']} {p['symbol']} "
                  f"x{p['leverage']} 数量:{p['qty']} 均价:${p['entry_price']:,.2f}")
        print("=" * 45)


# ─── 命令行快速测试 ───────────────────────────────────────────────

if __name__ == "__main__":
    pt = PaperTrader()
    print("=== 模拟盘测试 ===")
    pt.print_status()

    # 开一笔 BTC Long
    r1 = pt.open_position("BTCUSDT", "LONG", qty=0.01, price=71000, leverage=10,
                           stop_loss=68000, take_profit=75000, note="测试开仓")
    print(f"开仓结果: {r1}")

    # 模拟价格上涨平仓
    r2 = pt.close_position(r1["pos_id"], exit_price=73500)
    print(f"平仓结果: {r2}")

    pt.print_status()
