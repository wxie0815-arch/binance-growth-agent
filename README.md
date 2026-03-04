# 币安用户成长全栈Agent
> Built with OpenClaw | #AIBinance

一个专为币安用户打造的AI成长系统，帮你从"亏钱的交易者"成长为"懂自己的交易者"。

## 四大核心模块

### 🪞 风险镜子 (Risk Mirror)
分析你的交易历史，照出你是什么类型的交易者，找出致命弱点。

### 🗺️ 收益地图 (Yield Map)
实时对比币安全生态收益机会：现货/Earn/Launchpool/BNB Vault，告诉你同样的钱放哪最赚。

### 📊 合约复盘教练 (Futures Coach)
逐笔拆解每次亏损：方向错？时机差？止损太近？仓位太重？识别你的高频错误模式。

### 🎓 苏格拉底训练 (Socrates Trainer)
不给信号，只教你思考。针对你的弱点定制情景题，AI反问引导，改变交易思维。

## 系统架构

```
用户输入
    ↓
主Agent协调层（邪修 + Power 双Agent协作）
    ↓
┌─────────────────────────────────────┐
│  四大子Agent                         │
│  🪞 风险镜子Agent                    │
│  🗺️ 收益地图Agent                    │
│  📊 合约复盘教练Agent                │
│  🎓 苏格拉底训练Agent                │
└─────────────────────────────────────┘
    ↓
输出层
├── Telegram推送个人报告
└── 币安广场自动发布成长日记
```

## 使用的OpenClaw Skill
- `binance-pro-cn` — 币安完整API（交易/Earn/合约）
- `binance-pro` — 币安高级API
- `bn-square-skill` — 币安广场发布
- `binance-hunter` — Launchpad机会监控
- `binance-dca` — DCA策略对比
- `binance-spot-trader` — 现货数据

## 技术栈
- OpenClaw 多Agent协作框架
- Python 3.12
- 币安官方API
- 模拟数据演示

## 开发团队
- 邪修 (XieXiu) — 主Agent，框架/分析/图表
- Power — 子Agent，内容创作/广场发布

## 快速开始
```bash
cd binance-growth-agent
pip install -r requirements.txt
python3 main.py --demo  # 模拟数据演示模式
```

## License
MIT
