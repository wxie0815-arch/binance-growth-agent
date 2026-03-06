#!/usr/bin/env python3
"""合约复盘教练 - 逐笔拆解亏损，识别高频错误"""

from datetime import datetime

ERROR_PATTERNS = {
    "no_stoploss":    "未设置止损，亏损超10%仍持仓",
    "emotion_add":    "亏损后30分钟内情绪加仓",
    "over_leverage":  "杠杆超过10倍，风险过大",
    "chase_high":     "追涨追高开多",
    "panic_short":    "恐慌杀跌开空",
}

def analyze_contract_trades(trades: list) -> dict:
    errors = []
    total_pnl = 0
    wins, losses = 0, 0

    for i, t in enumerate(trades):
        pnl = t.get("pnl", 0)
        total_pnl += pnl
        if pnl > 0:
            wins += 1
        else:
            losses += 1
            # 检测错误模式
            if t.get("leverage", 1) > 10:
                errors.append(("over_leverage", t))
            if t.get("no_stoploss", False):
                errors.append(("no_stoploss", t))
            if t.get("emotion_add", False):
                errors.append(("emotion_add", t))

    # 统计高频错误
    error_counts = {}
    for etype, _ in errors:
        error_counts[etype] = error_counts.get(etype, 0) + 1

    return {
        "total": len(trades),
        "wins": wins,
        "losses": losses,
        "total_pnl": round(total_pnl, 2),
        "win_rate": round(wins / len(trades) * 100, 1) if trades else 0,
        "errors": error_counts,
        "worst_trade": min(trades, key=lambda x: x.get("pnl", 0)) if trades else None,
    }

def generate_coach_report(trades=None, mode="demo") -> str:
    if mode == "demo" or not trades:
        trades = [
            {"symbol": "BTCUSDT", "pnl": 320,  "leverage": 10, "no_stoploss": False, "emotion_add": False},
            {"symbol": "ETHUSDT", "pnl": -180, "leverage": 5,  "no_stoploss": False, "emotion_add": True},
            {"symbol": "BTCUSDT", "pnl": -850, "leverage": 20, "no_stoploss": True,  "emotion_add": True},
            {"symbol": "SOLUSDT", "pnl": 210,  "leverage": 10, "no_stoploss": False, "emotion_add": False},
            {"symbol": "BTCUSDT", "pnl": 540,  "leverage": 15, "no_stoploss": False, "emotion_add": False},
        ]

    r = analyze_contract_trades(trades)
    worst = r["worst_trade"]

    lines = [
        f"📊 合约复盘报告",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"{'='*40}",
        f"",
        f"本周交易：{r['total']}笔 | 盈利：{r['wins']}笔 | 亏损：{r['losses']}笔",
        f"胜率：{r['win_rate']}% | 总盈亏：{r['total_pnl']} USDT",
        f"",
        f"❌ 高频错误：",
    ]
    if r["errors"]:
        for etype, cnt in sorted(r["errors"].items(), key=lambda x: -x[1]):
            lines.append(f"  • {ERROR_PATTERNS[etype]} × {cnt}次")
    else:
        lines.append("  本周无明显错误，继续保持！")

    if worst:
        lines += [
            f"",
            f"💀 最惨一笔：{worst['symbol']} 亏损 {worst['pnl']} USDT",
            f"   杠杆：{worst.get('leverage',1)}x | 无止损：{'是' if worst.get('no_stoploss') else '否'}",
        ]

    lines += [
        f"",
        f"🔧 本周改进重点：",
        f"  1. 杠杆上限调整为5倍",
        f"  2. 每笔交易先设止损再开仓",
        f"  3. 亏损后冷静60分钟再操作",
        f"",
        f"{'='*40}",
        f"下一步：开启苏格拉底训练，针对弱点改变思维 🎓",
    ]
    return "\n".join(lines)

if __name__ == "__main__":
    print(generate_coach_report(mode="demo"))
