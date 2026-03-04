#!/usr/bin/env python3
"""
🗺️ 收益地图Agent
- binance-pro-cn 读取Earn/余额
- binance-dca DCA策略对比
- binance-hunter Launchpad机会监控
"""

import random
from datetime import datetime, timezone


class YieldMapAgent:
    """收益地图：同样的钱放哪里收益最高"""

    def __init__(self, user_data: dict):
        self.user_data = user_data

    def _mock_binance_earn_data(self) -> dict:
        """
        模拟 binance-pro-cn Earn API 数据结构
        真实调用: GET /sapi/v1/simple-earn/flexible/list + locked/list
        """
        return {
            "flexible": [
                {"asset": "USDT", "apy": round(random.uniform(3.5, 5.2), 2), "minAmount": 1, "locked": False},
                {"asset": "BTC",  "apy": round(random.uniform(0.5, 1.8), 2), "minAmount": 0.001, "locked": False},
                {"asset": "ETH",  "apy": round(random.uniform(1.2, 2.5), 2), "minAmount": 0.01, "locked": False},
                {"asset": "BNB",  "apy": round(random.uniform(1.5, 3.0), 2), "minAmount": 0.1, "locked": False},
            ],
            "locked": [
                {"asset": "USDT", "apy": round(random.uniform(6.0, 9.5), 2), "duration": 30, "locked": True},
                {"asset": "USDT", "apy": round(random.uniform(8.0, 12.0), 2), "duration": 90, "locked": True},
                {"asset": "BNB",  "apy": round(random.uniform(4.0, 7.0), 2), "duration": 60, "locked": True},
            ],
            "bnb_vault": {"apy": round(random.uniform(2.8, 4.5), 2), "asset": "BNB"},
        }

    def _mock_launchpool_data(self) -> list:
        """
        模拟 binance-hunter Launchpad/Launchpool 数据
        """
        return [
            {
                "project": "SampleProject A",
                "stakeAsset": "BNB",
                "estimatedApy": round(random.uniform(15, 40), 1),
                "endDate": "2026-03-15",
                "status": "active",
                "totalStaked": f"{random.randint(5000000, 20000000)} BNB"
            },
            {
                "project": "SampleProject B",
                "stakeAsset": "FDUSD",
                "estimatedApy": round(random.uniform(10, 25), 1),
                "endDate": "2026-03-20",
                "status": "active",
                "totalStaked": f"{random.randint(100000000, 500000000)} FDUSD"
            }
        ]

    def _mock_dca_comparison(self) -> dict:
        """
        模拟 binance-dca DCA策略收益对比
        """
        return {
            "btc_dca_1y_return": round(random.uniform(25, 65), 1),
            "eth_dca_1y_return": round(random.uniform(15, 45), 1),
            "bnb_dca_1y_return": round(random.uniform(20, 55), 1),
            "vs_hold": "DCA在震荡市场中平均优于持有约12-18%",
        }

    def calculate(self) -> dict:
        """计算最优收益配置"""
        print("  → 调用 binance-pro-cn 读取Earn产品数据...")
        earn_data = self._mock_binance_earn_data()

        print("  → 调用 binance-hunter 获取Launchpool机会...")
        launchpool = self._mock_launchpool_data()

        print("  → 调用 binance-dca 计算DCA策略对比...")
        dca = self._mock_dca_comparison()

        # 假设用户有 1000 USDT 可配置
        capital = 1000

        # 构建收益地图
        yield_map = [
            {
                "option": "活期理财 (USDT Flexible)",
                "apy": earn_data["flexible"][0]["apy"],
                "annual_yield": round(capital * earn_data["flexible"][0]["apy"] / 100, 2),
                "liquidity": "随时可取",
                "risk": "极低",
                "skill": "binance-pro-cn"
            },
            {
                "option": f"定期理财 90天 (USDT Locked)",
                "apy": earn_data["locked"][1]["apy"],
                "annual_yield": round(capital * earn_data["locked"][1]["apy"] / 100, 2),
                "liquidity": "锁定90天",
                "risk": "低",
                "skill": "binance-pro-cn"
            },
            {
                "option": f"BNB Vault",
                "apy": earn_data["bnb_vault"]["apy"],
                "annual_yield": round(capital * earn_data["bnb_vault"]["apy"] / 100, 2),
                "liquidity": "灵活",
                "risk": "低（需持有BNB）",
                "skill": "binance-pro-cn"
            },
            {
                "option": f"Launchpool: {launchpool[0]['project']}",
                "apy": launchpool[0]["estimatedApy"],
                "annual_yield": round(capital * launchpool[0]["estimatedApy"] / 100 / 12, 2),
                "liquidity": f"截止 {launchpool[0]['endDate']}",
                "risk": "中（需质押BNB）",
                "skill": "binance-hunter"
            },
            {
                "option": "BTC DCA定投",
                "apy": dca["btc_dca_1y_return"],
                "annual_yield": round(capital * dca["btc_dca_1y_return"] / 100, 2),
                "liquidity": "随时可终止",
                "risk": "中高（市场波动）",
                "skill": "binance-dca"
            },
        ]

        # 排序：按年化收益率从高到低
        yield_map.sort(key=lambda x: x["apy"], reverse=True)
        best = yield_map[0]

        print(f"  ✅ 最优选项: {best['option']} | APY {best['apy']}%")
        return {
            "capital_assumed": capital,
            "yield_map": yield_map,
            "best_option": best,
            "recommendation": f"当前最优：{best['option']}，预计年化 {best['apy']}%，每千USDT年收益约 ${best['annual_yield']}",
            "launchpool_active": launchpool,
            "dca_insight": dca["vs_hold"],
        }
