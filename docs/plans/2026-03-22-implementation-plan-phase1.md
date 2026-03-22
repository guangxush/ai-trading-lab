# AI量化交易平台 - Phase 1 实施计划

## 目标

搭建核心框架，包括项目结构、数据层基础、SKILL 基础框架和 Web UI 骨架。

## 项目结构

```
ai-trading-lab/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py          # 配置管理
│   │   ├── api/               # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── market.py      # 行情接口
│   │   │   ├── skill.py       # SKILL 接口
│   │   │   └── user.py        # 用户接口
│   │   ├── core/              # 核心模块
│   │   │   ├── __init__.py
│   │   │   ├── database.py    # 数据库连接
│   │   │   └── cache.py       # 缓存管理
│   │   ├── data/              # 数据层
│   │   │   ├── __init__.py
│   │   │   ├── gateway.py     # 数据网关
│   │   │   ├── sources/       # 数据源适配器
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py    # 基类
│   │   │   │   ├── akshare.py # A股数据源
│   │   │   │   └── yfinance.py# 美股数据源
│   │   │   └── models.py      # 数据模型
│   │   ├── skill/             # SKILL 框架
│   │   │   ├── __init__.py
│   │   │   ├── base.py        # SKILL 基类
│   │   │   ├── executor.py    # 执行引擎
│   │   │   ├── loader.py      # 加载器
│   │   │   └── registry.py    # 注册表
│   │   ├── agent/             # AI Agent（Phase 2）
│   │   └── models/            # 数据库模型
│   │       ├── __init__.py
│   │       ├── user.py
│   │       └── skill.py
│   ├── tests/                 # 测试
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # 前端服务
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx  # 大盘监控
│   │   │   ├── Backtest.tsx   # 策略回测
│   │   │   └── Skills.tsx     # SKILL市场
│   │   ├── components/
│   │   │   ├── Layout.tsx
│   │   │   ├── Chart.tsx
│   │   │   └── StockCard.tsx
│   │   ├── api/               # API 调用
│   │   └── stores/            # 状态管理
│   ├── package.json
│   └── Dockerfile
├── skills/                     # 内置 SKILL 库
│   └── examples/
│       ├── stock_analysis/
│       └── simple_backtest/
├── docker-compose.yml          # 本地部署配置
├── README.md
└── docs/
    └── plans/
```

## Task 1: 项目初始化

### 1.1 创建基础目录结构

```bash
mkdir -p backend/app/{api,core,data/sources,skill,agent,models}
mkdir -p backend/tests
mkdir -p frontend/src/{pages,components,api,stores}
mkdir -p skills/examples
```

### 1.2 后端依赖

```txt
# backend/requirements.txt
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
python-dotenv>=1.0.0
akshare>=1.10.0
yfinance>=0.2.0
redis>=4.5.0
sqlalchemy>=2.0.0
aiosqlite>=0.19.0
pandas>=2.0.0
numpy>=1.24.0
pytest>=7.4.0
httpx>=0.24.0
```

### 1.3 前端依赖

```json
// frontend/package.json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.14.0",
    "antd": "^5.8.0",
    "echarts": "^5.4.0",
    "echarts-for-react": "^3.0.0",
    "axios": "^1.4.0",
    "zustand": "^4.3.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "vite": "^4.4.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0"
  }
}
```

## Task 2: 数据层实现

### 2.1 数据源基类

```python
# backend/app/data/sources/base.py
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class StockQuote(BaseModel):
    """股票行情数据模型"""
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime

class MarketData(BaseModel):
    """市场数据模型"""
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: datetime

class BaseDataSource(ABC):
    """数据源基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """数据源名称"""
        pass

    @abstractmethod
    async def get_quote(self, symbol: str) -> Optional[StockQuote]:
        """获取实时行情"""
        pass

    @abstractmethod
    async def get_history(
        self,
        symbol: str,
        start: datetime,
        end: datetime
    ) -> List[MarketData]:
        """获取历史数据"""
        pass

    @abstractmethod
    async def search(self, keyword: str) -> List[dict]:
        """搜索股票"""
        pass
```

### 2.2 AKShare 适配器

```python
# backend/app/data/sources/akshare.py
import akshare as ak
from datetime import datetime
from typing import List, Optional
from .base import BaseDataSource, StockQuote, MarketData

class AKShareSource(BaseDataSource):
    """AKShare 数据源 - A股"""

    @property
    def name(self) -> str:
        return "akshare"

    async def get_quote(self, symbol: str) -> Optional[StockQuote]:
        """获取A股实时行情"""
        try:
            df = ak.stock_zh_a_spot_em()
            row = df[df['代码'] == symbol].iloc[0]
            return StockQuote(
                symbol=symbol,
                name=row['名称'],
                price=float(row['最新价']),
                change=float(row['涨跌额']),
                change_percent=float(row['涨跌幅']),
                volume=int(row['成交量']),
                timestamp=datetime.now()
            )
        except Exception as e:
            print(f"获取行情失败: {e}")
            return None

    async def get_history(
        self,
        symbol: str,
        start: datetime,
        end: datetime
    ) -> List[MarketData]:
        """获取A股历史数据"""
        try:
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start.strftime("%Y%m%d"),
                end_date=end.strftime("%Y%m%d"),
                adjust="qfq"
            )
            return [
                MarketData(
                    symbol=symbol,
                    open=row['开盘'],
                    high=row['最高'],
                    low=row['最低'],
                    close=row['收盘'],
                    volume=row['成交量'],
                    timestamp=row['日期']
                )
                for _, row in df.iterrows()
            ]
        except Exception as e:
            print(f"获取历史数据失败: {e}")
            return []

    async def search(self, keyword: str) -> List[dict]:
        """搜索A股"""
        try:
            df = ak.stock_zh_a_spot_em()
            matched = df[
                df['名称'].str.contains(keyword) |
                df['代码'].str.contains(keyword)
            ]
            return [
                {"symbol": row['代码'], "name": row['名称']}
                for _, row in matched.head(20).iterrows()
            ]
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
```

### 2.3 数据网关

```python
# backend/app/data/gateway.py
from typing import Dict, Optional, List
from datetime import datetime
from .sources.base import BaseDataSource, StockQuote, MarketData
from .sources.akshare import AKShareSource
# from .sources.yfinance import YFinanceSource  # Phase 1 后续添加

class MarketDataGateway:
    """市场数据网关 - 统一数据访问"""

    def __init__(self):
        self._sources: Dict[str, BaseDataSource] = {}
        self._register_sources()

    def _register_sources(self):
        """注册数据源"""
        self._sources["cn"] = AKShareSource()  # A股
        # self._sources["us"] = YFinanceSource()  # 美股

    def get_source(self, market: str) -> Optional[BaseDataSource]:
        """获取指定市场的数据源"""
        return self._sources.get(market)

    async def get_quote(self, symbol: str, market: str = "cn") -> Optional[StockQuote]:
        """获取实时行情"""
        source = self.get_source(market)
        if not source:
            raise ValueError(f"不支持的市场: {market}")
        return await source.get_quote(symbol)

    async def get_history(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        market: str = "cn"
    ) -> List[MarketData]:
        """获取历史数据"""
        source = self.get_source(market)
        if not source:
            raise ValueError(f"不支持的市场: {market}")
        return await source.get_history(symbol, start, end)

    async def search(self, keyword: str, market: str = "cn") -> List[dict]:
        """搜索股票"""
        source = self.get_source(market)
        if not source:
            raise ValueError(f"不支持的市场: {market}")
        return await source.search(keyword)

# 全局实例
gateway = MarketDataGateway()
```

## Task 3: SKILL 基础框架

### 3.1 SKILL 基类

```python
# backend/app/skill/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel
from enum import Enum

class SkillStatus(str, Enum):
    """SKILL 执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

class SkillContext(BaseModel):
    """SKILL 执行上下文"""
    user_id: str
    params: Dict[str, Any]
    market_data: Optional[Dict] = None
    user_data: Optional[Dict] = None

class SkillResult(BaseModel):
    """SKILL 执行结果"""
    status: SkillStatus
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None

class BaseSkill(ABC):
    """SKILL 基类 - 所有策略插件必须继承"""

    @property
    @abstractmethod
    def name(self) -> str:
        """技能名称"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """版本号"""
        pass

    @property
    def description(self) -> str:
        """技能描述"""
        return ""

    @property
    def author(self) -> str:
        """作者"""
        return "unknown"

    @property
    def params_schema(self) -> Dict[str, Any]:
        """参数校验 schema"""
        return {}

    @abstractmethod
    async def execute(self, context: SkillContext) -> SkillResult:
        """执行入口"""
        pass

    def validate(self, params: Dict[str, Any]) -> bool:
        """参数校验"""
        # 简单实现，后续可用 jsonschema 增强
        required = self.params_schema.get("required", [])
        return all(k in params for k in required)

    def __repr__(self) -> str:
        return f"<Skill {self.name} v{self.version}>"
```

### 3.2 SKILL 注册表

```python
# backend/app/skill/registry.py
from typing import Dict, List, Optional, Type
from .base import BaseSkill

class SkillRegistry:
    """SKILL 注册表"""

    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill) -> None:
        """注册 SKILL"""
        key = f"{skill.name}@{skill.version}"
        self._skills[key] = skill
        print(f"注册 SKILL: {key}")

    def unregister(self, name: str, version: str) -> None:
        """注销 SKILL"""
        key = f"{name}@{version}"
        if key in self._skills:
            del self._skills[key]

    def get(self, name: str, version: Optional[str] = None) -> Optional[BaseSkill]:
        """获取 SKILL"""
        if version:
            return self._skills.get(f"{name}@{version}")
        # 返回最新版本
        versions = [k for k in self._skills if k.startswith(f"{name}@")]
        if not versions:
            return None
        latest = sorted(versions)[-1]
        return self._skills[latest]

    def list_all(self) -> List[Dict]:
        """列出所有 SKILL"""
        return [
            {
                "name": skill.name,
                "version": skill.version,
                "description": skill.description,
                "author": skill.author
            }
            for skill in self._skills.values()
        ]

# 全局注册表
registry = SkillRegistry()
```

### 3.3 SKILL 执行器

```python
# backend/app/skill/executor.py
import asyncio
from typing import Dict, Any
from .base import BaseSkill, SkillContext, SkillResult, SkillStatus
from .registry import registry

class SkillExecutor:
    """SKILL 执行器"""

    def __init__(self):
        self._running_tasks: Dict[str, asyncio.Task] = {}

    async def execute(
        self,
        skill_name: str,
        context: SkillContext,
        version: str = None
    ) -> SkillResult:
        """执行 SKILL"""
        skill = registry.get(skill_name, version)
        if not skill:
            return SkillResult(
                status=SkillStatus.FAILED,
                error=f"SKILL 未找到: {skill_name}"
            )

        # 参数校验
        if not skill.validate(context.params):
            return SkillResult(
                status=SkillStatus.FAILED,
                error="参数校验失败"
            )

        try:
            result = await skill.execute(context)
            return result
        except Exception as e:
            return SkillResult(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    async def execute_async(
        self,
        skill_name: str,
        context: SkillContext,
        version: str = None
    ) -> str:
        """异步执行 SKILL，返回任务 ID"""
        task_id = f"{skill_name}_{context.user_id}_{asyncio.get_event_loop().time()}"

        async def _run():
            return await self.execute(skill_name, context, version)

        task = asyncio.create_task(_run())
        self._running_tasks[task_id] = task
        return task_id

    async def get_result(self, task_id: str) -> SkillResult:
        """获取异步执行结果"""
        task = self._running_tasks.get(task_id)
        if not task:
            return SkillResult(
                status=SkillStatus.FAILED,
                error=f"任务未找到: {task_id}"
            )

        if not task.done():
            return SkillResult(status=SkillStatus.RUNNING)

        return task.result()

# 全局执行器
executor = SkillExecutor()
```

### 3.4 示例 SKILL

```python
# skills/examples/stock_analysis/skill.py
from backend.app.skill.base import BaseSkill, SkillContext, SkillResult, SkillStatus
from backend.app.data.gateway import gateway

class StockAnalysisSkill(BaseSkill):
    """股票分析 SKILL"""

    @property
    def name(self) -> str:
        return "stock_analysis"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "分析股票走势，提供买入/卖出建议"

    @property
    def author(self) -> str:
        return "ai-trading-lab"

    @property
    def params_schema(self) -> dict:
        return {
            "required": ["symbol"],
            "properties": {
                "symbol": {"type": "string", "description": "股票代码"},
                "days": {"type": "integer", "default": 30, "description": "分析天数"}
            }
        }

    async def execute(self, context: SkillContext) -> SkillResult:
        symbol = context.params["symbol"]
        days = context.params.get("days", 30)

        # 获取历史数据
        from datetime import datetime, timedelta
        end = datetime.now()
        start = end - timedelta(days=days)

        history = await gateway.get_history(symbol, start, end)

        if not history:
            return SkillResult(
                status=SkillStatus.FAILED,
                error="无法获取历史数据"
            )

        # 简单技术分析
        closes = [h.close for h in history]
        ma5 = sum(closes[-5:]) / 5 if len(closes) >= 5 else 0
        ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else 0

        trend = "上涨" if ma5 > ma20 else "下跌"
        advice = "建议买入" if ma5 > ma20 else "建议观望"

        return SkillResult(
            status=SkillStatus.SUCCESS,
            data={
                "symbol": symbol,
                "latest_price": closes[-1],
                "ma5": ma5,
                "ma20": ma20,
                "trend": trend,
                "advice": advice
            },
            message=f"分析完成: {symbol} 当前{trend}趋势，{advice}"
        )
```

## Task 4: Web UI 基础框架

### 4.1 主布局

```tsx
// frontend/src/components/Layout.tsx
import React from 'react';
import { Layout, Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';

const { Header, Sider, Content } = Layout;

export const MainLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { key: '/', label: '大盘监控' },
    { key: '/backtest', label: '策略回测' },
    { key: '/skills', label: 'SKILL市场' },
    { key: '/portfolio', label: '持仓管理' },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={200} theme="dark">
        <div style={{ height: 64, color: '#fff', textAlign: 'center', lineHeight: '64px' }}>
          AI Trading Lab
        </div>
        <Menu
          theme="dark"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px' }} />
        <Content style={{ margin: 24, background: '#fff', padding: 24, borderRadius: 8 }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};
```

### 4.2 大盘监控页面

```tsx
// frontend/src/pages/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Input, List } from 'antd';
import { StockCard } from '../components/StockCard';
import { searchStock } from '../api/market';

export const Dashboard: React.FC = () => {
  const [keyword, setKeyword] = useState('');
  const [stocks, setStocks] = useState<any[]>([]);

  const handleSearch = async (value: string) => {
    if (!value) return;
    const results = await searchStock(value);
    setStocks(results);
  };

  return (
    <div>
      <h2>大盘监控</h2>
      <Input.Search
        placeholder="搜索股票代码或名称"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        onSearch={handleSearch}
        style={{ marginBottom: 24 }}
      />
      <Row gutter={[16, 16]}>
        {stocks.map((stock) => (
          <Col key={stock.symbol} span={6}>
            <StockCard symbol={stock.symbol} name={stock.name} />
          </Col>
        ))}
      </Row>
    </div>
  );
};
```

### 4.3 API 封装

```typescript
// frontend/src/api/market.ts
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export const searchStock = async (keyword: string, market = 'cn') => {
  const response = await axios.get(`${API_BASE}/api/market/search`, {
    params: { keyword, market }
  });
  return response.data;
};

export const getQuote = async (symbol: string, market = 'cn') => {
  const response = await axios.get(`${API_BASE}/api/market/quote/${symbol}`, {
    params: { market }
  });
  return response.data;
};

export const getHistory = async (
  symbol: string,
  startDate: string,
  endDate: string,
  market = 'cn'
) => {
  const response = await axios.get(`${API_BASE}/api/market/history/${symbol}`, {
    params: { start: startDate, end: endDate, market }
  });
  return response.data;
};
```

## Task 5: API 路由

### 5.1 行情接口

```python
# backend/app/api/market.py
from fastapi import APIRouter, Query
from datetime import datetime
from ..data.gateway import gateway

router = APIRouter(prefix="/api/market", tags=["market"])

@router.get("/search")
async def search(
    keyword: str = Query(..., description="搜索关键词"),
    market: str = Query("cn", description="市场: cn/us/hk")
):
    """搜索股票"""
    results = await gateway.search(keyword, market)
    return results

@router.get("/quote/{symbol}")
async def get_quote(
    symbol: str,
    market: str = Query("cn", description="市场")
):
    """获取实时行情"""
    quote = await gateway.get_quote(symbol, market)
    if not quote:
        return {"error": "未找到股票"}
    return quote.model_dump()

@router.get("/history/{symbol}")
async def get_history(
    symbol: str,
    start: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end: str = Query(..., description="结束日期 YYYY-MM-DD"),
    market: str = Query("cn", description="市场")
):
    """获取历史数据"""
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d")
    history = await gateway.get_history(symbol, start_dt, end_dt, market)
    return [h.model_dump() for h in history]
```

### 5.2 SKILL 接口

```python
# backend/app/api/skill.py
from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from ..skill.base import SkillContext
from ..skill.registry import registry
from ..skill.executor import executor

router = APIRouter(prefix="/api/skill", tags=["skill"])

class ExecuteRequest(BaseModel):
    skill_name: str
    user_id: str
    params: dict
    version: Optional[str] = None

@router.get("/list")
async def list_skills():
    """列出所有 SKILL"""
    return registry.list_all()

@router.post("/execute")
async def execute_skill(request: ExecuteRequest):
    """执行 SKILL"""
    context = SkillContext(
        user_id=request.user_id,
        params=request.params
    )
    result = await executor.execute(
        request.skill_name,
        context,
        request.version
    )
    return result.model_dump()

@router.get("/{name}")
async def get_skill(name: str, version: Optional[str] = None):
    """获取 SKILL 详情"""
    skill = registry.get(name, version)
    if not skill:
        raise HTTPException(404, "SKILL 未找到")
    return {
        "name": skill.name,
        "version": skill.version,
        "description": skill.description,
        "author": skill.author,
        "params_schema": skill.params_schema
    }
```

### 5.3 主入口

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import market, skill
from .skill.registry import registry
# 导入示例 SKILL
# from skills.examples.stock_analysis.skill import StockAnalysisSkill

app = FastAPI(
    title="AI Trading Lab",
    description="AI量化交易平台",
    version="0.1.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(market.router)
app.include_router(skill.router)

# 注册内置 SKILL
# registry.register(StockAnalysisSkill())

@app.get("/")
async def root():
    return {"message": "AI Trading Lab API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Task 6: Docker 部署配置

### 6.1 docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./backend:/app
      - ./skills:/app/skills:ro

  web:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - api

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### 6.2 后端 Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6.3 前端 Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 时间规划

| Week | Tasks |
|------|-------|
| Week 1 | 项目初始化、目录结构、后端基础框架 |
| Week 2 | 数据层实现（AKShare 适配器、数据网关） |
| Week 3 | SKILL 框架实现（基类、注册表、执行器） |
| Week 4 | Web UI 框架、Docker 部署、集成测试 |

## 验收标准

1. **数据层**：能够获取 A 股实时行情和历史数据
2. **SKILL框架**：能够注册、加载、执行自定义 SKILL
3. **Web UI**：能够搜索股票、查看行情、调用 SKILL
4. **部署**：`docker-compose up` 一键启动全部服务

## 下一步

Phase 1 完成后，进入 Phase 2：AI 能力实现
- Data Agent：自动化数据采集和清洗
- Analysis Agent：行情分析和趋势预测
- Backtest Agent：策略回测引擎