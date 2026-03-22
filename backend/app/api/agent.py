"""Agent 相关 API 路由"""
from typing import Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import uuid

from ..agent.base import AgentContext, AgentResult, AgentType
from ..agent.data_agent import data_agent
from ..agent.analysis_agent import analysis_agent
from ..agent.backtest_agent import backtest_agent
from ..agent.trading_agent import trading_agent
from ..agent.risk_agent import risk_agent

router = APIRouter(prefix="/api/agent", tags=["agent"])


class AgentExecuteRequest(BaseModel):
    """Agent 执行请求"""
    agent_type: str = Field(..., description="Agent 类型: data/analysis/backtest/trading/risk")
    action: str = Field(..., description="执行动作")
    params: dict = Field(default_factory=dict, description="执行参数")


class AgentExecuteResponse(BaseModel):
    """Agent 执行响应"""
    task_id: str
    success: bool
    data: Optional[dict] = None
    message: str = ""
    error: Optional[str] = None


# Agent 注册表
AGENTS = {
    "data": data_agent,
    "analysis": analysis_agent,
    "backtest": backtest_agent,
    "trading": trading_agent,
    "risk": risk_agent,
}


@router.get("/list")
async def list_agents():
    """列出所有 Agent"""
    return {
        "agents": [agent.to_dict() for agent in AGENTS.values()]
    }


@router.get("/{agent_type}")
async def get_agent_info(agent_type: str):
    """获取 Agent 详情"""
    if agent_type not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent 未找到: {agent_type}")

    agent = AGENTS[agent_type]
    return agent.to_dict()


@router.post("/execute")
async def execute_agent(request: AgentExecuteRequest):
    """
    执行 Agent 任务

    - **agent_type**: data/analysis/backtest
    - **action**: 具体操作
    - **params**: 参数
    """
    if request.agent_type not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent 未找到: {request.agent_type}")

    agent = AGENTS[request.agent_type]

    # 生成任务ID
    task_id = str(uuid.uuid4())

    # 构建上下文
    context = AgentContext(
        task_id=task_id,
        params={"action": request.action, **request.params}
    )

    # 执行
    result = await agent.run(context)

    return AgentExecuteResponse(
        task_id=result.task_id,
        success=result.success,
        data=result.data,
        message=result.message,
        error=result.error
    )


@router.post("/data/fetch")
async def data_fetch(
    symbol: str,
    market: str = "cn"
):
    """
    数据采集：获取实时行情

    - **symbol**: 股票代码
    - **market**: 市场
    """
    task_id = str(uuid.uuid4())
    context = AgentContext(
        task_id=task_id,
        params={"action": "fetch", "symbol": symbol, "market": market}
    )
    result = await data_agent.run(context)
    return result.model_dump()


@router.post("/data/history")
async def data_history(
    symbol: str,
    days: int = 30,
    market: str = "cn"
):
    """
    数据采集：获取历史数据

    - **symbol**: 股票代码
    - **days**: 天数
    - **market**: 市场
    """
    task_id = str(uuid.uuid4())
    context = AgentContext(
        task_id=task_id,
        params={"action": "history", "symbol": symbol, "days": days, "market": market}
    )
    result = await data_agent.run(context)
    return result.model_dump()


@router.post("/analysis/technical")
async def analysis_technical(
    symbol: str,
    market: str = "cn",
    days: int = 60
):
    """
    技术指标分析

    - **symbol**: 股票代码
    - **market**: 市场
    - **days**: 分析天数
    """
    task_id = str(uuid.uuid4())
    context = AgentContext(
        task_id=task_id,
        params={"action": "technical", "symbol": symbol, "market": market, "days": days}
    )
    result = await analysis_agent.run(context)
    return result.model_dump()


@router.post("/analysis/signal")
async def analysis_signal(
    symbol: str,
    market: str = "cn"
):
    """
    买卖信号分析

    - **symbol**: 股票代码
    - **market**: 市场
    """
    task_id = str(uuid.uuid4())
    context = AgentContext(
        task_id=task_id,
        params={"action": "signal", "symbol": symbol, "market": market}
    )
    result = await analysis_agent.run(context)
    return result.model_dump()


@router.post("/backtest/run")
async def backtest_run(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    initial_capital: float = 100000,
    strategy: str = "ma_cross",
    market: str = "cn"
):
    """
    运行回测

    - **symbol**: 股票代码
    - **start_date**: 开始日期 YYYY-MM-DD
    - **end_date**: 结束日期 YYYY-MM-DD
    - **initial_capital**: 初始资金
    - **strategy**: 策略名称
    - **market**: 市场
    """
    task_id = str(uuid.uuid4())
    context = AgentContext(
        task_id=task_id,
        params={
            "action": "run",
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": initial_capital,
            "strategy": strategy,
            "market": market
        }
    )
    result = await backtest_agent.run(context)
    return result.model_dump()


# ===== Trading Agent API =====

@router.post("/trading/order")
async def trading_create_order(
    symbol: str,
    side: str,  # buy/sell
    shares: int,
    order_type: str = "market",  # market/limit
    price: Optional[float] = None,
    market: str = "cn"
):
    """
    创建交易订单

    - **symbol**: 股票代码
    - **side**: 买卖方向 buy/sell
    - **shares**: 股数
    - **order_type**: 订单类型 market/limit
    - **price**: 限价单价格
    - **market**: 市场
    """
    task_id = str(uuid.uuid4())
    context = AgentContext(
        task_id=task_id,
        params={
            "action": "create_order",
            "symbol": symbol,
            "side": side,
            "shares": shares,
            "order_type": order_type,
            "price": price,
            "market": market
        }
    )
    result = await trading_agent.run(context)
    return result.model_dump()


@router.get("/trading/orders")
async def trading_get_orders(
    status: Optional[str] = None,
    symbol: Optional[str] = None
):
    """
    获取订单列表

    - **status**: 订单状态筛选
    - **symbol**: 股票代码筛选
    """
    task_id = str(uuid.uuid4())
    context = AgentContext(
        task_id=task_id,
        params={
            "action": "get_orders",
            "status": status,
            "symbol": symbol
        }
    )
    result = await trading_agent.run(context)
    return result.model_dump()


@router.get("/trading/positions")
async def trading_get_positions():
    """获取当前持仓"""
    task_id = str(uuid.uuid4())
    context = AgentContext(
        task_id=task_id,
        params={"action": "get_positions"}
    )
    result = await trading_agent.run(context)
    return result.model_dump()


@router.get("/trading/account")
async def trading_get_account():
    """获取账户信息"""
    task_id = str(uuid.uuid4())
    context = AgentContext(
        task_id=task_id,
        params={"action": "get_account"}
    )
    result = await trading_agent.run(context)
    return result.model_dump()


@router.get("/trading/history")
async def trading_get_history(limit: int = 50):
    """
    获取交易历史

    - **limit**: 返回条数
    """
    task_id = str(uuid.uuid4())
    context = AgentContext(
        task_id=task_id,
        params={"action": "get_trade_history", "limit": limit}
    )
    result = await trading_agent.run(context)
    return result.model_dump()


# ===== Risk Agent API =====

@router.post("/risk/assess")
async def risk_assess():
    """综合风险评估"""
    task_id = str(uuid.uuid4())
    context = AgentContext(
        task_id=task_id,
        params={"action": "assess"}
    )
    result = await risk_agent.run(context)
    return result.model_dump()


@router.post("/risk/check")
async def risk_check_position(
    symbol: str,
    shares: int,
    price: float,
    trade_action: str = "buy"
):
    """
    检查仓位风险

    - **symbol**: 股票代码
    - **shares**: 交易股数
    - **price**: 交易价格
    - **trade_action**: 交易类型 buy/sell
    """
    task_id = str(uuid.uuid4())
    context = AgentContext(
        task_id=task_id,
        params={
            "action": "position_check",
            "symbol": symbol,
            "shares": shares,
            "price": price,
            "trade_action": trade_action
        }
    )
    result = await risk_agent.run(context)
    return result.model_dump()


@router.get("/risk/config")
async def risk_get_config():
    """获取风控配置"""
    task_id = str(uuid.uuid4())
    context = AgentContext(
        task_id=task_id,
        params={"action": "get_config"}
    )
    result = await risk_agent.run(context)
    return result.model_dump()


@router.post("/risk/stop-loss")
async def risk_set_stop_loss(
    symbol: str,
    stop_loss_percent: float
):
    """
    设置止损

    - **symbol**: 股票代码
    - **stop_loss_percent**: 止损比例
    """
    task_id = str(uuid.uuid4())
    context = AgentContext(
        task_id=task_id,
        params={
            "action": "set_stop_loss",
            "symbol": symbol,
            "stop_loss_percent": stop_loss_percent
        }
    )
    result = await risk_agent.run(context)
    return result.model_dump()


@router.get("/risk/portfolio")
async def risk_portfolio_analysis():
    """投资组合风险分析"""
    task_id = str(uuid.uuid4())
    context = AgentContext(
        task_id=task_id,
        params={"action": "portfolio_analysis"}
    )
    result = await risk_agent.run(context)
    return result.model_dump()