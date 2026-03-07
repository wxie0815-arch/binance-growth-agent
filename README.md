# 🦞 我的币安人生
### 我的币安人生 | Powered by OpenClaw

> 用AI帮你照镜子、看地图、做复盘、练思维 —— 成为更好的币安交易者

[![GitHub stars](https://img.shields.io/github/stars/wxie0815-arch/binance-growth-agent?style=social)](https://github.com/wxie0815-arch/binance-growth-agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![#AIBinance](https://img.shields.io/badge/%23AIBinance-参赛作品-F0B90B)](https://www.binance.com/zh-CN/square)

---

## 📖 项目简介

我的币安人生，基于 [OpenClaw](https://openclaw.ai) 构建，帮助币安用户：
- 🪞 **照镜子**：分析你的交易历史，生成交易者人格报告
- 🗺️ **看地图**：实时对比币安生态收益产品，给出最优配置
- 📊 **做复盘**：逐笔拆解亏损原因，识别高频错误模式
- 🎓 **练思维**：苏格拉底式情景训练，改变交易思维
- 📅 **7日挑战**：每天在币安广场公开分享成长历程

---

## 🏗️ 架构

```
用户指令
    ↓
🦞 主Agent（入口调度）
    ↓           ↓           ↓           ↓
🪞 风险镜子  🗺️ 收益地图  📊 复盘教练  🎓 苏格拉底
(人格分析)  (收益优化)  (亏损拆解)  (思维训练)
    ↓           ↓           ↓           ↓
        汇总 → 每日22:00推送给用户
```

---

## ⚡ 快速开始

```bash
git clone https://github.com/wxie0815-arch/binance-growth-agent.git
cd binance-growth-agent

# 演示模式（无需API Key）
python3 main/orchestrator.py

# 实盘模式（需要币安只读API Key）
python3 main/orchestrator.py --mode live --api-key YOUR_KEY --api-secret YOUR_SECRET
```

---

## 🎯 5大功能

### 1. 🪞 交易者人格分析
- 读取现货+合约交易记录（binance-pro-cn）
- 输出风险偏好类型：保守 / 稳健 / 平衡 / 进取 / 激进
- 分别生成现货、合约两份详细分析报告

### 2. 🗺️ 个性化策略建议 + 收益地图
- 按风险偏好定制仓位管理、止损规则
- 实时对比 Earn / BNB Vault / Launchpool / 定期理财
- 一键展示「把闲置资金放哪里最划算」

### 3. 📊 每日交易追踪报告
- **模拟盘模式**：testnet.binance.vision（安全演示）
- **实盘模式**：用户提供只读API Key
- 每日自动生成策略执行报告 + 异常预警

### 4. 📅 7日币安广场挑战（可选）
- 用户自愿参与
- Agent每天生成当日内容，辅助发布到币安广场
- 带 `#AIBinance` 标签，格式统一

### 5. 📨 每日定时汇总
- 北京时间22:00自动推送
- 整合4个子Agent产出
- 明日重点提示

---

## 🧱 技术栈

- **框架**：[OpenClaw](https://openclaw.ai) AI Agent
- **数据来源**：
  - [Binance Skills Hub](https://github.com/binance/binance-skills-hub) 官方skill
  - 币安现货API / 合约API / Earn API
  - testnet.binance.vision（模拟盘）
- **子Agent通信**：agent_api 内部消息协议
- **语言**：Python 3.12+

---

## 👥 团队

| Agent | 负责模块 | 运行环境 |
|-------|---------|---------|
| 🥭 芒果 | 主Agent + 风险镜子 + 收益地图 + 7日挑战 | 18.179.6.146 |
| 🖤 邪修 | 合约复盘教练 + 苏格拉底训练 + 宏观分析 | 13.229.72.206 |

为 [@wuxie149](https://x.com/wuxie149) 构建 · 币安广场博主 & 交易员

---

## 📄 License

MIT License · 参赛作品，欢迎 Fork & Star ⭐

---

## 🎯 核心差异化

| 特点 | 说明 |
|------|------|
| 🤖 双Agent协作 | 邪修(分析层) + 芒果(输出层) 实时内部通信，全场唯一 |
| 📊 5步成长闭环 | 照镜子→看地图→做复盘→练思维→7日挑战，形成完整成长体系 |
| 🔮 广场流量预言机 | 预测今日热榜话题，AI选题助手 |
| 🛡️ Demo模式 | 无需API Key即可完整体验，30秒上手 |
| 🔗 官方Skills | 100% 调用币安7大官方技能 |

## 📹 演示视频

[![演示视频](https://img.shields.io/badge/▶_演示视频-哔哩哔哩-00A1D6)](https://github.com/wxie0815-arch/binance-growth-agent)

**系统实际运行输出（Demo模式）：**
```
🦞 我的币安人生 | Powered by OpenClaw
🪞 交易者人格：🚀 进取型（胜率50%，惯用杠杆12x）
🗺️ 收益地图：闲置1000U → 年化+106 USDT优化方案
📊 合约复盘：本周5笔，识别3个高频错误
🎓 苏格拉底训练：针对过度杠杆专项训练
📅 Day1广场内容：自动生成并带 #AIBinance 标签
```

## 🏆 参赛信息

- 比赛：[币安AI Agent创意大赛 #AIBinance](https://www.binance.com/zh-CN/square)
- 作者：XieXiu × 芒果
- GitHub：[wxie0815-arch/binance-growth-agent](https://github.com/wxie0815-arch/binance-growth-agent)
