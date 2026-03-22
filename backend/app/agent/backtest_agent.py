"""Backtest Agent - 策略回测智能体"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from .base import BaseAgent, AgentContext, AgentResult, AgentType
from ..data.gateway import gateway


class SignalType(str, Enum):
    """信号类型"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Trade:
    """交易记录"""
    date: datetime
    signal: SignalType
    price: float
    shares: int
    value: float


@dataclass
class Position:
    """持仓"""
    symbol: str
    shares: int
    avg_cost: float
    current_value: float


class BacktestAgent(BaseAgent):
    """
    回测 Agent

    负责：
    - 策略回测执行
    - 收益计算
    - 风险指标计算
    - 回测报告生成
    """

    def __init__(self):
        super().__init__()
        self._strategies: Dict[str, Callable] = {}

    @property
    def name(self) -> str:
        return "BacktestAgent"

    @property
    def agent_type(self) -> AgentType:
        return AgentType.BACKTEST

    @property
    def description(self) -> str:
        return "策略回测智能体，负责历史数据回测和性能评估"

    def register_strategy(self, name: str, strategy_func: Callable):
        """注册策略函数"""
        self._strategies[name] = strategy_func

    async def execute(self, context: AgentContext) -> AgentResult:
        """执行回测任务"""
        action = context.params.get("action", "run")

        handlers = {
            "run": self._run_backtest,
            "report": self._generate_report,
            "optimize": self._optimize_params,
            "compare": self._compare_strategies,
        }

        handler = handlers.get(action)
        if not handler:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error=f"未知回测操作: {action}"
            )

        return await handler(context)

    async def _run_backtest(self, context: AgentContext) -> AgentResult:
        """运行回测"""
        symbol = context.params.get("symbol")
        market = context.params.get("market", "cn")
        start_date = context.params.get("start_date")
        end_date = context.params.get("end_date")
        initial_capital = context.params.get("initial_capital", 100000)
        strategy_name = context.params.get("strategy", "ma_cross")
        params = context.params.get("params", {})

        if not symbol:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少 symbol 参数"
            )

        # 获取历史数据
        if start_date and end_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end = datetime.now()
            start = end - timedelta(days=365)

        history = await gateway.get_history(symbol, start, end, market)

        if len(history) < 30:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="历史数据不足，至少需要30天"
            )

        # 运行回测
        result = self._execute_backtest(
            history=history,
            initial_capital=initial_capital,
            strategy_name=strategy_name,
            params=params
        )

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data=result,
            message=f"回测完成: 总收益率 {result['total_return']:.2f}%"
        )

    def _execute_backtest(
        self,
        history: List,
        initial_capital: float,
        strategy_name: str,
        params: Dict
    ) -> Dict:
        """执行回测逻辑"""
        closes = [h.close for h in history]
        dates = [h.timestamp for h in history]

        # 初始化
        capital = initial_capital
        position = 0
        trades: List[Dict] = []
        portfolio_values: List[Dict] = []

        # 简单策略：MA金叉死叉
        if strategy_name == "ma_cross":
            short_period = params.get("short_period", 5)
            long_period = params.get("long_period", 20)

            for i in range(long_period, len(closes)):
                short_ma = sum(closes[i - short_period:i]) / short_period
                long_ma = sum(closes[i - long_period:i]) / long_period

                price = closes[i]
                date = dates[i]

                # 买入信号：短期均线上穿长期均线
                if short_ma > long_ma and position == 0:
                    shares = int(capital / price)
                    if shares > 0:
                        position = shares
                        capital -= shares * price
                        trades.append({
                            "date": date.strftime("%Y-%m-%d"),
                            "type": "BUY",
                            "price": round(price, 2),
                            "shares": shares,
                            "value": round(shares * price, 2)
                        })

                # 卖出信号：短期均线下穿长期均线
                elif short_ma < long_ma and position > 0:
                    capital += position * price
                    trades.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "type": "SELL",
                        "price": round(price, 2),
                        "shares": position,
                        "value": round(position * price, 2)
                    })
                    position = 0

                # 记录持仓市值
                portfolio_value = capital + position * price
                portfolio_values.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "value": round(portfolio_value, 2)
                })

        # 计算最终市值
        final_capital = capital + position * closes[-1]
        total_return = (final_capital - initial_capital) / initial_capital * 100

        # 计算风险指标
        risk_metrics = self._calculate_risk_metrics(portfolio_values, initial_capital)

        # 计算交易统计
        trade_stats = self._calculate_trade_stats(trades)

        return {
            "symbol": history[0].symbol if history else "unknown",
            "initial_capital": initial_capital,
            "final_capital": round(final_capital, 2),
            "total_return": round(total_return, 2),
            "total_trades": len(trades),
            "win_rate": trade_stats["win_rate"],
            "max_drawdown": risk_metrics["max_drawdown"],
            "sharpe_ratio": risk_metrics["sharpe_ratio"],
            "trades": trades,
            "portfolio_values": portfolio_values[-30:],  # 最近30天
            "risk_metrics": risk_metrics,
            "trade_stats": trade_stats,
        }

    def _calculate_risk_metrics(
        self,
        portfolio_values: List[Dict],
        initial_capital: float
    ) -> Dict:
        """计算风险指标"""
        if not portfolio_values:
            return {"max_drawdown": 0, "sharpe_ratio": 0, "volatility": 0}

        values = [v["value"] for v in portfolio_values]

        # 最大回撤
        peak = initial_capital
        max_drawdown = 0
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # 日收益率
        returns = []
        for i in range(1, len(values)):
            daily_return = (values[i] - values[i - 1]) / values[i - 1]
            returns.append(daily_return)

        # 波动率（年化）
        if returns:
            volatility = (sum(r ** 2 for r in returns) / len(returns)) ** 0.5 * (252 ** 0.5)
        else:
            volatility = 0

        # 夏普比率（简化计算，假设无风险利率为3%）
        if returns and volatility > 0:
            avg_return = sum(returns) / len(returns) * 252
            sharpe_ratio = (avg_return - 0.03) / volatility
        else:
            sharpe_ratio = 0

        return {
            "max_drawdown": round(max_drawdown * 100, 2),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "volatility": round(volatility * 100, 2),
        }

    def _calculate_trade_stats(self, trades: List[Dict]) -> Dict:
        """计算交易统计"""
        if not trades:
            return {"win_rate": 0, "total_profit": 0, "total_loss": 0}

        profits = []
        buy_trades = [t for t in trades if t["type"] == "BUY"]

        # 配对买卖计算盈亏
        for i, buy in enumerate(buy_trades):
            # 找对应的卖出
            for j, trade in enumerate(trades):
                if trade["type"] == "SELL" and trades.index(buy) < j:
                    profit = (trade["price"] - buy["price"]) * buy["shares"]
                    profits.append(profit)
                    break

        if not profits:
            return {"win_rate": 0, "total_profit": 0, "total_loss": 0}

        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p < 0]

        return {
            "win_rate": round(len(wins) / len(profits) * 100, 1) if profits else 0,
            "total_profit": round(sum(wins), 2),
            "total_loss": round(sum(losses), 2),
            "avg_profit": round(sum(profits) / len(profits), 2) if profits else 0,
        }

    async def _generate_report(self, context: AgentContext) -> AgentResult:
        """生成回测报告"""
        # 获取回测结果
        backtest_result = context.params.get("backtest_result")

        if not backtest_result:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少回测结果数据"
            )

        # 生成报告
        report = self._format_report(backtest_result)

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={"report": report},
            message="回测报告生成完成"
        )

    def _format_report(self, result: Dict) -> str:
        """格式化报告"""
        lines = [
            "=" * 50,
            "策略回测报告",
            "=" * 50,
            "",
            f"股票代码: {result.get('symbol', 'N/A')}",
            f"初始资金: ¥{result.get('initial_capital', 0):,.2f}",
            f"最终资金: ¥{result.get('final_capital', 0):,.2f}",
            f"总收益率: {result.get('total_return', 0):.2f}%",
            "",
            "-" * 50,
            "风险指标",
            "-" * 50,
            f"最大回撤: {result.get('max_drawdown', 0):.2f}%",
            f"夏普比率: {result.get('sharpe_ratio', 0):.2f}",
            f"年化波动率: {result.get('risk_metrics', {}).get('volatility', 0):.2f}%",
            "",
            "-" * 50,
            "交易统计",
            "-" * 50,
            f"总交易次数: {result.get('total_trades', 0)}",
            f"胜率: {result.get('win_rate', 0):.1f}%",
            "",
            "=" * 50,
        ]
        return "\n".join(lines)

    async def _optimize_params(self, context: AgentContext) -> AgentResult:
        """参数优化"""
        symbol = context.params.get("symbol")
        market = context.params.get("market", "cn")
        param_ranges = context.params.get("param_ranges", {})

        if not symbol or not param_ranges:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少必要参数"
            )

        # 获取历史数据
        end = datetime.now()
        start = end - timedelta(days=365)
        history = await gateway.get_history(symbol, start, end, market)

        if len(history) < 30:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="历史数据不足"
            )

        # 简单网格搜索
        best_params = {}
        best_return = -float("inf")
        results = []

        # 简单优化：遍历均线周期
        if "short_period" in param_ranges and "long_period" in param_ranges:
            short_range = param_ranges["short_period"]
            long_range = param_ranges["long_period"]

            for short in range(short_range[0], short_range[1] + 1, short_range[2]):
                for long in range(long_range[0], long_range[1] + 1, long_range[2]):
                    if short >= long:
                        continue

                    result = self._execute_backtest(
                        history=history,
                        initial_capital=100000,
                        strategy_name="ma_cross",
                        params={"short_period": short, "long_period": long}
                    )

                    results.append({
                        "params": {"short_period": short, "long_period": long},
                        "return": result["total_return"]
                    })

                    if result["total_return"] > best_return:
                        best_return = result["total_return"]
                        best_params = {"short_period": short, "long_period": long}

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "best_params": best_params,
                "best_return": round(best_return, 2),
                "all_results": sorted(results, key=lambda x: x["return"], reverse=True)[:10]
            },
            message=f"参数优化完成，最佳收益率: {best_return:.2f}%"
        )

    async def _compare_strategies(self, context: AgentContext) -> AgentResult:
        """比较不同策略"""
        symbol = context.params.get("symbol")
        market = context.params.get("market", "cn")
        strategies = context.params.get("strategies", ["ma_cross"])

        if not symbol:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少 symbol 参数"
            )

        # 获取历史数据
        end = datetime.now()
        start = end - timedelta(days=365)
        history = await gateway.get_history(symbol, start, end, market)

        if len(history) < 30:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="历史数据不足"
            )

        # 运行各策略回测
        comparison = []
        for strategy_name in strategies:
            result = self._execute_backtest(
                history=history,
                initial_capital=100000,
                strategy_name=strategy_name,
                params={}
            )
            comparison.append({
                "strategy": strategy_name,
                "total_return": result["total_return"],
                "max_drawdown": result["max_drawdown"],
                "sharpe_ratio": result["sharpe_ratio"],
                "win_rate": result["win_rate"]
            })

        # 按收益率排序
        comparison.sort(key=lambda x: x["total_return"], reverse=True)

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={"comparison": comparison},
            message="策略比较完成"
        )


# 全局实例
backtest_agent = BacktestAgent()