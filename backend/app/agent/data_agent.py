"""Data Agent - 数据采集智能体"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import json

from .base import BaseAgent, AgentContext, AgentResult, AgentType
from ..data.gateway import gateway
from ..data.sources.base import StockQuote, MarketData
from ..core.cache import cache


class DataAgent(BaseAgent):
    """
    数据采集 Agent

    负责：
    - 实时行情数据采集
    - 历史K线数据同步
    - 数据缓存管理
    - 数据清洗和预处理
    """

    def __init__(self):
        super().__init__()
        self._watch_list: Dict[str, Set[str]] = {}  # market -> symbols
        self._last_update: Dict[str, datetime] = {}

    @property
    def name(self) -> str:
        return "DataAgent"

    @property
    def agent_type(self) -> AgentType:
        return AgentType.DATA

    @property
    def description(self) -> str:
        return "数据采集智能体，负责实时行情和历史数据的采集与同步"

    async def execute(self, context: AgentContext) -> AgentResult:
        """执行数据采集任务"""
        action = context.params.get("action", "fetch")

        handlers = {
            "fetch": self._fetch_quote,
            "history": self._fetch_history,
            "watch": self._add_to_watch,
            "unwatch": self._remove_from_watch,
            "sync": self._sync_watch_list,
            "batch": self._batch_fetch,
        }

        handler = handlers.get(action)
        if not handler:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error=f"未知操作: {action}",
                message="不支持的采集操作"
            )

        return await handler(context)

    async def _fetch_quote(self, context: AgentContext) -> AgentResult:
        """获取实时行情"""
        symbol = context.params.get("symbol")
        market = context.params.get("market", "cn")

        if not symbol:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少 symbol 参数",
                message="请提供股票代码"
            )

        quote = await gateway.get_quote(symbol, market)
        if not quote:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error=f"无法获取 {symbol} 的行情数据",
                message="数据获取失败"
            )

        # 缓存数据
        cache_key = f"quote:{market}:{symbol}"
        await cache.set(cache_key, quote.model_dump())

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data=quote.model_dump(),
            message=f"成功获取 {symbol} 行情数据",
            metrics={"data_source": gateway.get_source(market).name if gateway.get_source(market) else "unknown"}
        )

    async def _fetch_history(self, context: AgentContext) -> AgentResult:
        """获取历史数据"""
        symbol = context.params.get("symbol")
        market = context.params.get("market", "cn")
        days = context.params.get("days", 30)

        if not symbol:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少 symbol 参数",
                message="请提供股票代码"
            )

        end = datetime.now()
        start = end - timedelta(days=days)

        history = await gateway.get_history(symbol, start, end, market)

        if not history:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error=f"无法获取 {symbol} 的历史数据",
                message="历史数据获取失败"
            )

        # 缓存历史数据
        cache_key = f"history:{market}:{symbol}:{days}d"
        await cache.set(cache_key, [h.model_dump() for h in history], ttl=3600)

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "symbol": symbol,
                "market": market,
                "total": len(history),
                "data": [h.model_dump() for h in history]
            },
            message=f"成功获取 {symbol} 最近 {len(history)} 天的历史数据",
            metrics={"data_points": len(history), "days": days}
        )

    async def _add_to_watch(self, context: AgentContext) -> AgentResult:
        """添加到监控列表"""
        symbol = context.params.get("symbol")
        market = context.params.get("market", "cn")

        if not symbol:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少 symbol 参数"
            )

        if market not in self._watch_list:
            self._watch_list[market] = set()

        self._watch_list[market].add(symbol)

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "symbol": symbol,
                "market": market,
                "watch_list": {k: list(v) for k, v in self._watch_list.items()}
            },
            message=f"已将 {symbol} 添加到监控列表"
        )

    async def _remove_from_watch(self, context: AgentContext) -> AgentResult:
        """从监控列表移除"""
        symbol = context.params.get("symbol")
        market = context.params.get("market", "cn")

        if market in self._watch_list and symbol in self._watch_list[market]:
            self._watch_list[market].remove(symbol)
            return AgentResult(
                task_id=context.task_id,
                success=True,
                message=f"已将 {symbol} 从监控列表移除"
            )

        return AgentResult(
            task_id=context.task_id,
            success=False,
            error=f"{symbol} 不在监控列表中"
        )

    async def _sync_watch_list(self, context: AgentContext) -> AgentResult:
        """同步监控列表中的所有数据"""
        results = []
        errors = []

        for market, symbols in self._watch_list.items():
            for symbol in symbols:
                try:
                    quote = await gateway.get_quote(symbol, market)
                    if quote:
                        cache_key = f"quote:{market}:{symbol}"
                        await cache.set(cache_key, quote.model_dump())
                        results.append({
                            "symbol": symbol,
                            "market": market,
                            "price": quote.price,
                            "change_percent": quote.change_percent
                        })
                except Exception as e:
                    errors.append({"symbol": symbol, "market": market, "error": str(e)})

        return AgentResult(
            task_id=context.task_id,
            success=len(errors) == 0,
            data={
                "updated": results,
                "errors": errors,
                "total_updated": len(results),
                "total_errors": len(errors)
            },
            message=f"同步完成: {len(results)} 成功, {len(errors)} 失败"
        )

    async def _batch_fetch(self, context: AgentContext) -> AgentResult:
        """批量获取数据"""
        symbols = context.params.get("symbols", [])
        market = context.params.get("market", "cn")

        if not symbols:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少 symbols 参数"
            )

        results = []
        errors = []

        for symbol in symbols:
            try:
                quote = await gateway.get_quote(symbol, market)
                if quote:
                    results.append(quote.model_dump())
            except Exception as e:
                errors.append({"symbol": symbol, "error": str(e)})

        return AgentResult(
            task_id=context.task_id,
            success=len(errors) == 0,
            data={
                "quotes": results,
                "errors": errors,
                "total": len(results)
            },
            message=f"批量获取完成: {len(results)} 成功, {len(errors)} 失败"
        )

    def get_watch_list(self) -> Dict[str, List[str]]:
        """获取当前监控列表"""
        return {k: list(v) for k, v in self._watch_list.items()}


# 全局实例
data_agent = DataAgent()