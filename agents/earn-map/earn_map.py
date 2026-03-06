#!/usr/bin/env python3
"""
收益地图 - 币安生态收益优化
根据用户风险偏好类型，给出最优资产配置建议
"""

import urllib.request, json
from datetime import datetime

# 模拟各产品当前收益率（实际可接入币安API）
EARN_PRODUCTS = {
    "flexible_usdt": {"name": "活期理财 USDT", "apy": 4.2, "liquidity": "随时存取", "risk": "极低", "min": 1},
    "bnb_vault":     {"name": "BNB Vault",      "apy": 8.5, "liquidity": "随时",     "risk": "低",   "min": 0.01},
    "launchpool_bnb":{"name": "Launchpool质押",  "apy": 12.4,"liquidity": "锁定期",   "risk": "低",   "min": 0.1},
    "fixed_30d":     {"name": "定期理财 30天",   "apy": 6.8, "liquidity": "锁定30天", "risk": "低",   "min": 100},
    "fixed_90d":     {"name": "定期理财 90天",   "apy": 9.1, "liquidity": "锁定90天", "risk": "低",   "min": 100},
    "simple_earn":   {"name": "简单赚币 ETH",    "apy": 5.3, "liquidity": "活期",     "risk": "低",   "min": 0.01},
}

# 按风险偏好推荐配置比例
ALLOCATION_TEMPLATES = {
    "conservative": [
        ("flexible_usdt", 0.6, "主仓稳健打底"),
        ("fixed_30d",     0.3, "短期定期增收"),
        ("simple_earn",   0.1, "ETH赚币"),
    ],
    "steady": [
        ("flexible_usdt", 0.4, "保持流动性"),
        ("bnb_vault",     0.3, "BNB复利"),
        ("fixed_30d",     0.2, "定期增收"),
        ("launchpool_bnb",0.1, "小仓参与Launchpool"),
    ],
    "balanced": [
        ("bnb_vault",     0.3, "BNB复利为主"),
        ("launchpool_bnb",0.3, "积极参与Launchpool"),
        ("flexible_usdt", 0.2, "保持流动性"),
        ("fixed_90d",     0.2, "90天定期锁仓"),
    ],
    "aggressive": [
        ("launchpool_bnb",0.5, "重仓Launchpool"),
        ("bnb_vault",     0.3, "BNB Vault复利"),
        ("fixed_90d",     0.2, "90天定期"),
    ],
    "radical": [
        ("launchpool_bnb",0.6, "全力参与Launchpool"),
        ("bnb_vault",     0.4, "BNB Vault"),
    ],
}

def generate_earn_map(trader_type="balanced", total_idle_usdt=1000):
    """生成收益地图报告"""
    
    template = ALLOCATION_TEMPLATES.get(trader_type, ALLOCATION_TEMPLATES["balanced"])
    
    # 计算各方案收益
    current_annual = 0  # 当前放着不动
    optimized_annual = sum(
        total_idle_usdt * ratio * EARN_PRODUCTS[pid]["apy"] / 100
        for pid, ratio, _ in template
    )
    
    lines = [
        f"🗺️ 收益地图报告",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"{'='*40}",
        f"",
        f"💰 你的闲置资产：{total_idle_usdt} USDT",
        f"📊 当前策略：现货钱包（年化 0%）",
        f"",
        f"🏆 最优配置方案（匹配你的风险偏好）",
        f"",
    ]
    
    for pid, ratio, note in template:
        prod = EARN_PRODUCTS[pid]
        amount = total_idle_usdt * ratio
        annual = amount * prod["apy"] / 100
        lines.append(f"  • {prod['name']}")
        lines.append(f"    配置：{int(ratio*100)}% = {amount:.0f} USDT | 年化 {prod['apy']}% | {note}")
        lines.append(f"    流动性：{prod['liquidity']} | 风险：{prod['risk']}")
        lines.append(f"    预计年收益：+{annual:.1f} USDT")
        lines.append("")
    
    daily_loss = optimized_annual / 365
    lines += [
        f"{'='*40}",
        f"📈 收益对比",
        f"  现在放着不动：  每年 +0 USDT",
        f"  优化配置之后：  每年 +{optimized_annual:.0f} USDT",
        f"  每天少赚：      {daily_loss:.1f} USDT 💸",
        f"",
        f"⚡ 建议立刻行动：把闲置资金存入BNB Vault或活期理财",
        f"下一步：开启每日交易报告追踪执行情况 📊",
    ]
    
    return "\n".join(lines)

if __name__ == "__main__":
    print(generate_earn_map(trader_type="aggressive", total_idle_usdt=1000))
