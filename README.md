# AI Trading Lab

<div align="center">

🚀 **开源 AI 量化交易平台**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [AI Agents](#-ai-agents) • [API 文档](#-api-文档) • [SKILL 开发](#-skill-开发)

</div>

---

## 📖 简介

AI Trading Lab 是一个基于 AI Agent 的开源量化交易平台，支持多市场数据获取、智能策略分析、历史回测和模拟交易。采用分层微服务架构，支持本地部署，数据完全私有。

## ✨ 功能特性

| 功能模块 | 描述 |
|---------|------|
| 📊 **多市场支持** | A股、美股、港股、加密货币、期货期权 |
| 🤖 **AI Agent 体系** | 6 大智能 Agent 协同工作 |
| 🧩 **SKILL 插件系统** | 可扩展的策略插件框架，支持上传下载评分 |
| 📈 **策略回测** | 历史数据回测、参数优化、收益分析 |
| 💰 **模拟交易** | 虚拟资金交易、持仓管理、风险控制 |
| ⚡ **实时监控** | 实时行情、大盘监控、交易信号 |
| 🔌 **本地部署** | Docker 一键启动，数据完全私有 |

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                          应用层 (Application)                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │  Web UI    │  │  Dashboard │  │  Trading   │  │  Skills    │    │
│  │  (React)   │  │  (监控大屏) │  │  (交易界面) │  │  (SKILL市场)│    │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │
├─────────────────────────────────────────────────────────────────────┤
│                        AI 引擎层 (AI Engine)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  Data    │ │ Analysis │ │ Backtest │ │ Trading  │ │  Risk    │  │
│  │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │ │  Agent   │  │
│  │ 数据采集  │ │ 技术分析  │ │ 策略回测  │ │ 交易执行  │ │ 风险管理  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                       SKILL 运行时层 (Runtime)                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │  Plugin    │  │    SDK     │  │  Executor  │  │Marketplace │    │
│  │  Engine    │  │  Framework │  │  执行引擎   │  │  插件市场   │    │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │
├─────────────────────────────────────────────────────────────────────┤
│                          数据层 (Data Layer)                         │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │
│  │  Market Data   │  │   User Data    │  │  Cache Layer   │        │
│  │  Gateway       │  │   Service      │  │  (Redis)       │        │
│  │  数据网关       │  │  用户数据服务   │  │  缓存层        │        │
│  └────────────────┘  └────────────────┘  └────────────────┘        │
├─────────────────────────────────────────────────────────────────────┤
│                       基础设施层 (Infrastructure)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  Redis   │ │ SQLite/  │ │  File    │ │ Monitoring│ │ Security │  │
│  │  Cache   │ │TimescaleDB│ │ Storage │ │  (日志)   │ │  (认证)   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## 🤖 AI Agents

| Agent | 功能 | 主要能力 |
|-------|------|----------|
| **Data Agent** | 数据采集智能体 | 实时行情获取、历史数据同步、监控列表管理、批量数据采集 |
| **Analysis Agent** | 行情分析智能体 | 技术指标计算（MA/EMA/RSI/MACD/布林带/ATR）、趋势分析、买卖信号生成、支撑阻力位识别 |
| **Backtest Agent** | 策略回测智能体 | 历史数据回测、策略验证、风险指标计算（最大回撤/夏普比率）、参数优化 |
| **Trading Agent** | 交易执行智能体 | 订单创建管理、交易执行（模拟）、持仓管理、账户余额管理 |
| **Risk Agent** | 风险管理智能体 | 综合风险评估、仓位大小检查、集中度分析、止损止盈设置 |

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Redis (可选，用于缓存)

### 方式一：Docker 部署（推荐）

```bash
# 克隆项目
git clone https://github.com/yourname/ai-trading-lab.git
cd ai-trading-lab

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

启动后访问：
- **前端**: http://localhost:3000
- **API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

### 方式二：本地开发

#### 1. 启动后端

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

#### 2. 启动前端

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
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── market.py      # 行情接口
│   │   │   ├── skill.py       # SKILL 接口
│   │   │   ├── agent.py       # Agent 接口
│   │   │   └── marketplace.py # SKILL 市场接口
│   │   ├── agent/             # AI Agents
│   │   │   ├── base.py        # Agent 基类
│   │   │   ├── data_agent.py  # 数据采集 Agent
│   │   │   ├── analysis_agent.py # 行情分析 Agent
│   │   │   ├── backtest_agent.py # 策略回测 Agent
│   │   │   ├── trading_agent.py  # 交易执行 Agent
│   │   │   └── risk_agent.py     # 风险管理 Agent
│   │   ├── skill/             # SKILL 框架
│   │   │   ├── base.py        # SKILL 基类
│   │   │   ├── registry.py    # 注册表
│   │   │   ├── executor.py    # 执行器
│   │   │   └── marketplace.py # 市场管理
│   │   ├── data/              # 数据层
│   │   │   ├── gateway.py     # 数据网关
│   │   │   └── sources/       # 数据源适配器
│   │   ├── core/              # 核心模块
│   │   │   ├── database.py    # 数据库连接
│   │   │   └── cache.py       # 缓存管理
│   │   └── main.py            # 应用入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # 前端服务
│   ├── src/
│   │   ├── pages/             # 页面组件
│   │   │   ├── Dashboard.tsx  # 大盘监控
│   │   │   ├── Backtest.tsx   # 策略回测
│   │   │   ├── Skills.tsx     # SKILL 市场
│   │   │   └── Portfolio.tsx  # 持仓管理
│   │   ├── components/        # 通用组件
│   │   ├── api/               # API 封装
│   │   └── App.tsx            # 应用入口
│   ├── package.json
│   └── Dockerfile
├── skills/                     # SKILL 插件库
│   ├── examples/              # 示例 SKILL
│   │   ├── stock_analysis/    # 股票分析
│   │   ├── simple_ma_strategy/ # 均线策略
│   │   └── rsi_strategy/      # RSI 策略
│   └── marketplace/           # 市场下载的 SKILL
├── docs/                       # 文档
│   └── plans/                 # 设计文档
├── docker-compose.yml
└── README.md
```

## 📖 API 文档

启动服务后访问 http://localhost:8000/docs 查看完整的 Swagger API 文档。

### 核心 API 接口

#### 行情接口

| 方法 | 接口 | 说明 |
|------|------|------|
| GET | `/api/market/search` | 搜索股票 |
| GET | `/api/market/quote/{symbol}` | 获取实时行情 |
| GET | `/api/market/history/{symbol}` | 获取历史 K 线 |

#### Agent 接口

| 方法 | 接口 | 说明 |
|------|------|------|
| POST | `/api/agent/data/fetch` | 获取实时行情数据 |
| POST | `/api/agent/data/history` | 获取历史数据 |
| POST | `/api/agent/analysis/technical` | 技术指标分析 |
| POST | `/api/agent/analysis/signal` | 买卖信号分析 |
| POST | `/api/agent/backtest/run` | 运行策略回测 |
| POST | `/api/agent/trading/order` | 创建交易订单 |
| GET | `/api/agent/trading/positions` | 获取持仓 |
| GET | `/api/agent/trading/account` | 获取账户信息 |
| POST | `/api/agent/risk/assess` | 综合风险评估 |

#### SKILL 接口

| 方法 | 接口 | 说明 |
|------|------|------|
| GET | `/api/skill/list` | 列出所有 SKILL |
| POST | `/api/skill/execute` | 执行 SKILL |
| GET | `/api/skill/marketplace/list` | SKILL 市场列表 |
| POST | `/api/skill/marketplace/upload` | 上传 SKILL |
| GET | `/api/skill/marketplace/{skill_id}/code` | 下载 SKILL |

## 🧩 SKILL 开发

### 创建自定义 SKILL

```python
# skills/my_strategy/__init__.py
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.skill.base import BaseSkill, SkillContext, SkillResult, SkillStatus

class MyStrategy(BaseSkill):
    """我的自定义策略"""

    @property
    def name(self) -> str:
        return "my_strategy"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "这是一个自定义策略示例"

    @property
    def category(self) -> str:
        return "trading"

    @property
    def params_schema(self) -> dict:
        return {
            "required": ["symbol"],
            "properties": {
                "symbol": {"type": "string", "description": "股票代码"},
                "period": {"type": "integer", "default": 14}
            }
        }

    async def execute(self, context: SkillContext) -> SkillResult:
        symbol = context.params["symbol"]
        period = context.params.get("period", 14)

        # 你的策略逻辑
        # ...

        return SkillResult(
            status=SkillStatus.SUCCESS,
            data={
                "symbol": symbol,
                "signal": "buy",
                "confidence": 0.85
            },
            message="分析完成，建议买入"
        )

# 导出 SKILL 实例
skill = MyStrategy()
```

### 执行 SKILL

```bash
# 通过 API 执行
curl -X POST http://localhost:8000/api/skill/execute \
  -H "Content-Type: application/json" \
  -d '{
    "skill_name": "my_strategy",
    "user_id": "user001",
    "params": {"symbol": "600519"}
  }'
```

## 🛠️ 技术栈

### 后端

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| FastAPI | 0.100+ | 高性能异步 Web 框架 |
| SQLAlchemy | 2.0+ | ORM |
| Redis | 7+ | 缓存 |
| AKShare | 1.10+ | A股数据源 |
| Pandas | 2.0+ | 数据处理 |

### 前端

| 技术 | 版本 | 说明 |
|------|------|------|
| React | 18+ | UI 框架 |
| TypeScript | 5+ | 类型安全 |
| Ant Design | 5+ | UI 组件库 |
| ECharts | 5+ | 图表库 |
| Axios | 1.6+ | HTTP 客户端 |
| Zustand | 4+ | 状态管理 |

## 📝 开发路线

- [x] **Phase 1: 核心框架**
  - [x] 数据层基础
  - [x] SKILL 框架
  - [x] Web UI 骨架
  - [x] Docker 部署

- [x] **Phase 2: AI 能力**
  - [x] Data Agent
  - [x] Analysis Agent
  - [x] Backtest Agent

- [x] **Phase 3: 交易能力**
  - [x] Trading Agent
  - [x] Risk Agent
  - [x] 模拟交易

- [x] **Phase 4: 生态建设**
  - [x] SKILL Marketplace
  - [x] 示例 SKILL
  - [x] 文档完善

## 🤝 贡献指南

欢迎贡献代码、提出问题或建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📜 License

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

<div align="center">

⚠️ **免责声明**：本项目仅供学习和研究使用，不构成任何投资建议。使用本平台进行任何投资行为，风险自担。

**Made with ❤️ by AI Trading Lab Team**

</div>