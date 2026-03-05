# 🦞 我的币安人生 | My Binance Life

> OpenClaw × Binance 7大官方Skills 打造的专属交易人生导师
> 
> 帮你照镜子、看地图、改思维、冲热榜，真正"少亏多赚、成长可见"！

---

## 🏆 比赛亮点（一眼定胜负）

| 亮点 | 说明 |
|------|------|
| 🔗 **真实 Binance API 接入** | `--real` 模式直连账户，非演示数据 |
| 🤖 **双Agent协作架构** | 邪修（分析层）× Power（输出层）实时分工 |
| 📊 **7大官方Skills深度整合** | binance-pro-cn / trading-signal / meme-rush 等 |
| 🔄 **五步成长闭环** | 照镜子→看地图→做复盘→练思维→广场传播 |
| 🎮 **模拟盘 SQLite 持久化** | 零风险练习，本地记录每笔交易 |
| 📣 **无邪 54,500+ 粉丝背书** | 在真实广场验证过的流量策略 |
| 📅 **7日成长挑战** | 每天AI定制任务 + 广场爆款话题预测 |

---

## 核心理念

不再是冷冰冰的工具，而是你 **24小时贴身交易人生导师** ——
它懂你的交易历史、懂币安全生态、懂人性弱点，还会陪你一起在Square公开成长！

---

## 五大核心功能

### 🪞 照镜子 — 交易人格报告
输入钱包地址 → 一键分析全部交易历史，生成专属《交易者人格报告》。

你是"激进猎手""保守守护者"还是"情绪过山车"？

> 调用：`binance-pro-cn` + `query-address-info`

### 🗺️ 看地图 — 最优收益配置
实时对比币安所有 Earn、Launchpool、Simple Earn、Staking 等产品，秒出最优配置建议 + 预期年化 + 风险评分。

> 调用：`spot` + `crypto-market-rank`

### 📊 做复盘 — 亏损模式分析
逐笔拆解每一笔亏损/盈利，自动识别高频错误模式（追高、扛单、FOMO、过早止盈……），给出避坑金句。

> 调用：`trading-signal` + `binance-pro-cn`

### 🎓 练思维 — 苏格拉底训练
苏格拉底式情景训练：「如果你现在看到SOL暴涨30%，你会怎么做？」AI模拟10种结果，帮你重塑交易心智。

> 调用：`trading-signal` + `crypto-market-rank`

### 📅 7日成长挑战 — 广场成长闭环
每天AI给你定制任务 + 最佳发帖话题，自动生成文案。同时嵌入 **广场流量预言机**：用三维数据（热度、互动、历史转化）预测今日Top5热榜话题，让你的分享直接冲流量！

7天后生成《我的币安成长档案》，可永久存证分享。

> 调用：`meme-rush` + `query-token-info` + `bn-square-skill`

---

## 系统架构

```
用户 → 五大功能模块 → 广场流量预言机 → 输出层
                                        ├── Telegram推送
                                        ├── 广场文章生成
                                        ├── 成长档案
                                        └── 冲榜加速

双Agent协作：
  邪修 (XieXiu) — 分析层 · 人格识别 · 策略生成
  Power          — 输出层 · 数据采集 · 广场发布
  通信：agent_api :8899
```

---

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/wxie0815-arch/binance-growth-agent.git
cd binance-growth-agent
pip install -r requirements.txt
```

### 演示模式（无需 API Key）

```bash
python3 main.py --demo
```

### 真实 API 模式

**第一步**：配置 Binance API Key

```bash
mkdir -p ~/.openclaw/credentials
cat > ~/.openclaw/credentials/binance.json << 'EOF'
{
  "apiKey": "YOUR_BINANCE_API_KEY",
  "secretKey": "YOUR_BINANCE_SECRET_KEY"
}
EOF
```

或使用环境变量：

```bash
export BINANCE_API_KEY="your_api_key"
export BINANCE_SECRET="your_secret_key"
```

**第二步**：启动真实模式

```bash
python3 main.py --real
```

输出示例：
```
🔗 真实API模式 — 接入 binance-pro-cn
   数据来源: REAL | 总资产: $15,230.50 USDT | BTC: $71,450
```

### 模拟盘操作

```bash
# 查看账户状态（初始 $10,000 USDT）
python3 main.py --paper-status

# 开仓：BTC Long 10倍杠杆
python3 main.py --paper-open BTCUSDT LONG 0.01 71000

# 平仓
python3 main.py --paper-close <pos_id> 73500
```

### 单模块运行

```bash
python3 main.py --demo --module mirror    # 🪞 照镜子
python3 main.py --demo --module yield     # 🗺️ 收益地图
python3 main.py --demo --module coach     # 📊 合约复盘
python3 main.py --demo --module socrates  # 🎓 苏格拉底训练
```

---

## 📸 演示截图

### 账户连接（真实 API）
```
🔗 真实API模式 — 接入 binance-pro-cn
   数据来源: REAL | 总资产: $15,230.50 USDT
   BTC: $71,450 | ETH: $3,182 | BNB: $618
```
*↑ 截图占位：真实API连接输出*

### 合约复盘报告
```
📊 合约健康分: 72/100 🟢 状态不错
   最高频错误: 仓位过重 (5次)
   合约 vs 现货: +$320 跑赢现货持有
```
*↑ 截图占位：合约复盘报告输出*

### 模拟盘状态
```
📊 模拟盘状态
   账户余额:  $10,312.50 USDT
   总收益率:  +3.12%
   胜率:      68.0%
   当前持仓:  1 笔
```
*↑ 截图占位：模拟盘状态展示*

---

## 使用的 Binance 官方 Skills（7个）

| Skill | 功能 |
|-------|------|
| `binance-pro-cn` | 币安完整API（交易/Earn/合约） |
| `spot` | 现货行情数据 |
| `trading-signal` | 交易信号分析 |
| `crypto-market-rank` | 市场排名洞察 |
| `query-token-info` | 代币信息查询 |
| `query-address-info` | 钱包地址分析 |
| `meme-rush` | Meme币热度追踪 |

**扩展 Skills：**

| Skill | 功能 |
|-------|------|
| `bn-square-skill` | 广场发帖/图片/草稿 |
| `binance-hunter` | AI市场分析 + 杠杆交易 |
| `binance-dca` | DCA定投策略 |

---

## 广场流量预言机

| 模式 | 说明 |
|------|------|
| **模式1** | 交易人格 + 历史发帖风格 → 今日3个专属选题推荐 |
| **模式2** | 专属选题 + 当日热点 → 完整文章生成 + 配图方案 |

5种人格精准匹配：过度交易型 / 保守守护型 / FOMO追涨型 / 数据分析型 / 佛系持有型

---

## 为什么这个Agent能赢？

- **真痛点**：99%的用户最想解决的不是「预测价格」，而是「我为什么老亏」和「钱放哪里最赚」
- **强生态闭环**：从交易成长 → Square晒成长 → 带来真实流量
- **高传播性**：人格报告、7日挑战、流量预测机，天生自带病毒属性
- **双Agent协作**：邪修+Power 实时通信，分析层+输出层完美分工
- **真实验证**：无邪 Binance Square 54,500+ 粉丝账号验证过的内容策略

---

## 技术栈

- **框架**：OpenClaw 多Agent协作
- **语言**：Python 3.12
- **数据库**：SQLite（模拟盘持久化）
- **API**：币安官方 7大Skills + 扩展Skills
- **签名**：HMAC-SHA256 标准 Binance 签名方案

---

## 演示视频脚本

[📄 完整演示脚本](docs/demo_script.md) — 包含6段流程、旁白文案、5个截图时机说明

---

## 相关项目

- [广场流量预言机](https://github.com/wxie0815-arch/binance-square-oracle) — 独立的广场话题预测引擎
- [PR #27](https://github.com/binance/binance-skills-hub/pull/27) — 贡献 trader-growth-analysis skill 到官方 Skills Hub

---

## License

MIT

---

> 用AI把「币安人生」过成传奇，从今天开始！
> 
> **#AIBinance #我的币安人生**
> 
> _无邪 × 邪修AI工作室 | Binance Square @WuXie | 54,500+ 关注_
