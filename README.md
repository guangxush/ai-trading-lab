# AI Trading Lab

🚀 一个开源的 AI 量化交易平台，支持多市场数据获取、策略回测和智能交易建议。

## ✨ 特性

- 📊 **多市场支持**：A股、美股、港股、加密货币、期货期权
- 🧩 **SKILL 插件系统**：可扩展的策略插件框架，支持上传下载
- 🤖 **AI Agent 体系**：6 大智能 Agent 协同工作
- 📈 **策略回测**：历史数据回测和收益分析
- 💰 **模拟交易**：虚拟资金交易，风险可控
- 🔌 **本地部署**：Docker 一键启动，数据完全私有

## 🏗️ 架构

```
┌─────────────────────── 应用层 ─────────────────────────┐
│  Web UI    │  Chat Interface  │  API Gateway           │
├─────────────────── SKILL运行时层 ───────────────────────┤
│ Plugin Engine │ SDK Framework │ Strategy Executor       │
├─────────────────── AI引擎层 ──────────────────────────┤
│ Data Agent │ Analysis Agent │ Strategy Agent │ etc.    │
├─────────────────── 数据层 ────────────────────────────┤
│   Market Data Gateway   │   Cache Layer   │ DB         │
└──────────────────────────────────────────────────────┘
```

## 🤖 AI Agents

| Agent | 功能 |
|-------|------|
| **Data Agent** | 数据采集、监控列表、历史数据同步 |
| **Analysis Agent** | 技术指标（MA/RSI/MACD/布林带）、趋势分析、买卖信号 |
| **Backtest Agent** | 策略回测、参数优化、风险指标计算 |
| **Trading Agent** | 订单管理、交易执行、持仓管理 |
| **Risk Agent** | 风险评估、仓位控制、止损止盈 |

## 🚀 快速开始

### 方式一：Docker 部署（推荐）

```bash
# 克隆项目
git clone https://github.com/yourname/ai-trading-lab.git
cd ai-trading-lab

# 启动服务
docker-compose up -d

# 访问
# 前端: http://localhost:3000
# API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 方式二：本地开发

#### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 8000
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 📁 项目结构

```
ai-trading-lab/
├── backend/                # 后端服务 (FastAPI)
│   └── app/
│       ├── api/           # API 路由
│       ├── agent/         # AI Agents
│       ├── skill/         # SKILL 框架
│       └── data/          # 数据层
├── frontend/               # 前端服务 (React + TypeScript)
│   └── src/
│       ├── pages/         # 页面组件
│       └── api/           # API 封装
├── skills/                 # SKILL 插件库
│   └── examples/          # 示例 SKILL
└── docker-compose.yml
```

## 🧩 SKILL 开发

创建一个自定义 SKILL 非常简单：

```python
from app.skill.base import BaseSkill, SkillContext, SkillResult, SkillStatus

class MyStrategy(BaseSkill):
    @property
    def name(self) -> str:
        return "my_strategy"

    @property
    def version(self) -> str:
        return "1.0.0"

    async def execute(self, context: SkillContext) -> SkillResult:
        # 你的策略逻辑
        return SkillResult(
            status=SkillStatus.SUCCESS,
            data={"signal": "buy"}
        )
```

## 📖 API 文档

启动服务后访问 http://localhost:8000/docs 查看完整 API 文档。

### 主要接口

| 模块 | 接口 | 说明 |
|------|------|------|
| 行情 | `GET /api/market/search` | 搜索股票 |
| 行情 | `GET /api/market/quote/{symbol}` | 获取实时行情 |
| 分析 | `POST /api/agent/analysis/signal` | 买卖信号分析 |
| 回测 | `POST /api/agent/backtest/run` | 运行策略回测 |
| 交易 | `POST /api/agent/trading/order` | 创建交易订单 |
| 风险 | `POST /api/agent/risk/assess` | 综合风险评估 |
| 市场 | `GET /api/skill/marketplace/list` | SKILL 市场列表 |

## 🛠️ 技术栈

**后端**
- FastAPI - 高性能异步 Web 框架
- SQLAlchemy - ORM
- Redis - 缓存
- AKShare - A股数据源

**前端**
- React 18
- TypeScript
- Ant Design
- ECharts

## 📝 开发路线

- [x] Phase 1: 核心框架
- [x] Phase 2: AI 能力
- [x] Phase 3: 交易能力
- [x] Phase 4: 生态建设
  - [x] SKILL Marketplace
  - [x] 示例 SKILL
  - [x] 完善文档

## 🤝 贡献

欢迎贡献代码、提出问题或建议！

## 📜 License

MIT License

---

⚠️ **免责声明**：本项目仅供学习和研究使用，不构成任何投资建议。使用本平台进行任何投资行为，风险自担。