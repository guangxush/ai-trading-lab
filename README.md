# AI Trading Lab

🚀 一个开源的 AI 量化交易平台，支持多市场数据获取、策略回测和智能交易建议。

## ✨ 特性

- 📊 **多市场支持**：A股、美股、港股、加密货币、期货期权
- 🧩 **SKILL 插件系统**：可扩展的策略插件框架
- 🤖 **AI 分析能力**：智能行情分析和交易建议
- 📈 **策略回测**：历史数据回测和收益分析
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
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心模块（数据库、缓存）
│   │   ├── data/          # 数据层（数据源、网关）
│   │   ├── skill/         # SKILL 框架
│   │   └── main.py        # 入口文件
│   └── requirements.txt
├── frontend/               # 前端服务 (React + TypeScript)
│   ├── src/
│   │   ├── pages/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   └── api/           # API 封装
│   └── package.json
├── skills/                 # SKILL 插件库
│   └── examples/          # 示例 SKILL
├── docs/                   # 文档
│   └── plans/             # 设计文档
└── docker-compose.yml      # Docker 编排
```

## 🧩 SKILL 开发

创建一个自定义 SKILL 非常简单：

```python
# skills/my_strategy/__init__.py
from app.skill.base import BaseSkill, SkillContext, SkillResult, SkillStatus

class MyStrategy(BaseSkill):
    @property
    def name(self) -> str:
        return "my_strategy"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "我的自定义策略"

    async def execute(self, context: SkillContext) -> SkillResult:
        # 你的策略逻辑
        return SkillResult(
            status=SkillStatus.SUCCESS,
            data={"result": "ok"}
        )
```

## 📖 API 文档

启动服务后访问 http://localhost:8000/docs 查看完整的 API 文档。

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/market/search` | GET | 搜索股票 |
| `/api/market/quote/{symbol}` | GET | 获取实时行情 |
| `/api/market/history/{symbol}` | GET | 获取历史K线 |
| `/api/skill/list` | GET | 列出所有 SKILL |
| `/api/skill/execute` | POST | 执行 SKILL |

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

## 📄 文档

- [设计文档](docs/plans/2026-03-22-ai-trading-platform-design.md)
- [Phase 1 实施计划](docs/plans/2026-03-22-implementation-plan-phase1.md)

## 📝 开发路线

- [x] Phase 1: 核心框架（当前）
  - [x] 数据层基础
  - [x] SKILL 框架
  - [x] Web UI 骨架
  - [x] Docker 部署
- [ ] Phase 2: AI 能力
  - [ ] Data Agent
  - [ ] Analysis Agent
  - [ ] Backtest Agent
- [ ] Phase 3: 交易能力
  - [ ] Trading Agent
  - [ ] Risk Agent
  - [ ] 模拟交易
- [ ] Phase 4: 生态建设
  - [ ] SKILL Marketplace
  - [ ] 社区运营

## 🤝 贡献

欢迎贡献代码、提出问题或建议！

## 📜 License

MIT License

---

⚠️ **免责声明**：本项目仅供学习和研究使用，不构成任何投资建议。使用本平台进行任何投资行为，风险自担。