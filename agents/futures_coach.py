#!/usr/bin/env python3
"""
📊 合约复盘教练Agent
- binance-pro 读取合约交易历史
- binance-spot-trader 现货对比
- 逐笔拆解亏损，识别高频错误模式
"""

import random
from datetime import datetime, timezone


class FuturesCoachAgent:
    """合约复盘教练：每笔亏损背后的真正原因"""

    ERROR_PATTERNS = {
        "direction_wrong": {
            "name": "方向判断错误",
            "desc": "趋势判断失误，做多时遇到下跌或做空时遇到上涨",
            "fix": "加强趋势分析，至少看3个时间周期确认方向再入场"
        },
        "entry_timing_bad": {
            "name": "入场时机太差",
            "desc": "方向对但入场位置在极端高/低点，被插针扫出",
            "fix": "等待回调或突破确认再入场，不要追市"
        },
        "stop_too_tight": {
            "name": "止损设置太近",
            "desc": "止损位在正常波动范围内，频繁被市场正常波动触发",
            "fix": "把止损设在关键支撑/阻力位外，而非固定百分比"
        },
        "position_too_heavy": {
            "name": "仓位过重",
            "desc": "单笔仓位过大，微小波动就造成巨大亏损",
            "fix": "单笔仓位不超过总资金的5%，用凯利公式计算最优仓位"
        },
        "no_stop_loss": {
            "name": "不设止损死扛",
            "desc": "没有止损计划，亏损后靠等待解套，越套越深",
            "fix": "任何仓位开仓同时设好止损，这是铁律"
        },
    }

    def __init__(self, user_data: dict):
        self.user_data = user_data

    def _mock_futures_history(self) -> list:
        """
        模拟 binance-pro 合约历史数据
        真实调用: GET /fapi/v1/userTrades + /fapi/v1/income
        """
        trades = []
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        error_types = list(self.ERROR_PATTERNS.keys())

        for i in range(20):
            symbol = random.choice(symbols)
            is_long = random.choice([True, False])
            pnl = random.uniform(-200, 300) if random.random() > 0.45 else random.uniform(-500, -50)
            error = random.choice(error_types) if pnl < 0 else None

            price_map = {"BTCUSDT": 71000, "ETHUSDT": 3200, "BNBUSDT": 600}
            entry_price = price_map[symbol] * random.uniform(0.95, 1.05)
            leverage = random.choice([5, 10, 20])

            trades.append({
                "symbol": symbol,
                "side": "LONG" if is_long else "SHORT",
                "entry_price": round(entry_price, 2),
                "exit_price": round(entry_price * (1 + pnl / 10000), 2),
                "leverage": leverage,
                "pnl_usdt": round(pnl, 2),
                "pnl_pct": round(pnl / 1000 * 100, 2),
                "duration_hours": random.randint(1, 48),
                "error_type": error,
                "time": datetime.now(timezone.utc).isoformat(),
                # binance-spot-trader 对比：同期现货持有收益
                "spot_hold_pnl": round(random.uniform(-50, 100), 2),
            })

        return trades

    def _analyze_errors(self, trades: list) -> dict:
        """统计高频错误模式"""
        losing_trades = [t for t in trades if t["pnl_usdt"] < 0]
        error_counts = {}

        for t in losing_trades:
            err = t.get("error_type")
            if err:
                error_counts[err] = error_counts.get(err, 0) + 1

        # 排序找最高频错误
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)

        total_pnl = sum(t["pnl_usdt"] for t in trades)
        total_loss = sum(t["pnl_usdt"] for t in trades if t["pnl_usdt"] < 0)
        total_profit = sum(t["pnl_usdt"] for t in trades if t["pnl_usdt"] > 0)
        win_rate = len([t for t in trades if t["pnl_usdt"] > 0]) / len(trades) * 100

        # 合约 vs 现货对比
        spot_total = sum(t["spot_hold_pnl"] for t in trades)

        return {
            "total_trades": len(trades),
            "losing_trades": len(losing_trades),
            "win_rate": round(win_rate, 1),
            "total_pnl": round(total_pnl, 2),
            "total_loss": round(total_loss, 2),
            "total_profit": round(total_profit, 2),
            "top_errors": sorted_errors[:3],
            "vs_spot_pnl": round(total_pnl - spot_total, 2),
            "vs_spot_better": total_pnl > spot_total,
        }

    def review(self) -> dict:
        """执行合约复盘分析"""
        print("  → 调用 binance-pro 读取合约交易历史...")
        trades = self._mock_futures_history()

        print("  → 调用 binance-spot-trader 获取现货对比数据...")
        analysis = self._analyze_errors(trades)

        # 生成高频错误报告
        error_report = []
        for err_type, count in analysis["top_errors"]:
            pattern = self.ERROR_PATTERNS[err_type]
            error_report.append({
                "error": pattern["name"],
                "count": count,
                "desc": pattern["desc"],
                "fix": pattern["fix"],
            })

        # 周健康报告
        health_score = min(100, max(0, int(
            analysis["win_rate"] * 0.4 +
            (50 if analysis["vs_spot_better"] else 20) +
            (30 if analysis["total_pnl"] > 0 else 0)
        )))

        verdict = "🔴 需要大幅改进" if health_score < 40 else \
                  "🟡 有进步空间" if health_score < 70 else \
                  "🟢 状态不错"

        print(f"  ✅ 合约健康分: {health_score}/100 {verdict}")
        print(f"  ✅ 高频错误: {error_report[0]['error'] if error_report else '暂无'}")

        return {
            "analysis": analysis,
            "top_error_patterns": error_report,
            "health_score": health_score,
            "health_verdict": verdict,
            "weekly_summary": f"本周{analysis['total_trades']}笔合约，"
                              f"胜率{analysis['win_rate']}%，"
                              f"净盈亏${analysis['total_pnl']}，"
                              f"{'跑赢' if analysis['vs_spot_better'] else '跑输'}现货持有",
            "recent_trades": trades[-5:],  # 最近5笔
        }
