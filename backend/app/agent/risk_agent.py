"""Risk Agent - 风险管理智能体"""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .base import BaseAgent, AgentContext, AgentResult, AgentType
from .trading_agent import trading_agent
from ..data.gateway import gateway


class RiskLevel(str, Enum):
    """风险等级"""
    LOW = "low"           # 低风险
    MEDIUM = "medium"     # 中等风险
    HIGH = "high"         # 高风险
    CRITICAL = "critical" # 危险


class RiskType(str, Enum):
    """风险类型"""
    POSITION_SIZE = "position_size"     # 仓位风险
    CONCENTRATION = "concentration"     # 集中度风险
    DRAWDOWN = "drawdown"               # 回撤风险
    VOLATILITY = "volatility"           # 波动风险
    LIQUIDITY = "liquidity"             # 流动性风险
    LEVERAGE = "leverage"               # 杠杆风险


@dataclass
class RiskAlert:
    """风险预警"""
    risk_type: RiskType
    level: RiskLevel
    symbol: Optional[str]
    message: str
    value: float
    threshold: float
    timestamp: datetime
    recommendation: str


class RiskAgent(BaseAgent):
    """
    风险管理 Agent

    负责：
    - 仓位风险评估
    - 止损止盈设置
    - 风险预警
    - 投资组合风险分析
    """

    def __init__(self):
        super().__init__()
        # 风控参数
        self._max_position_percent = 20.0      # 单只股票最大仓位比例
        self._max_single_loss_percent = 5.0    # 单笔最大亏损比例
        self._max_total_loss_percent = 15.0    # 总仓位最大亏损比例
        self._max_concentration_percent = 40.0 # 单行业最大集中度
        self._stop_loss_percent = 8.0          # 止损比例
        self._take_profit_percent = 20.0       # 止盈比例

        # 预警记录
        self._alerts: List[RiskAlert] = []

    @property
    def name(self) -> str:
        return "RiskAgent"

    @property
    def agent_type(self) -> AgentType:
        return AgentType.RISK

    @property
    def description(self) -> str:
        return "风险管理智能体，负责仓位控制和风险评估"

    async def execute(self, context: AgentContext) -> AgentResult:
        """执行风险任务"""
        action = context.params.get("action", "assess")

        handlers = {
            "assess": self._assess_risk,
            "position_check": self._check_position_risk,
            "set_stop_loss": self._set_stop_loss,
            "set_take_profit": self._set_take_profit,
            "check_concentration": self._check_concentration,
            "get_alerts": self._get_alerts,
            "get_config": self._get_risk_config,
            "set_config": self._set_risk_config,
            "portfolio_analysis": self._portfolio_analysis,
        }

        handler = handlers.get(action)
        if not handler:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error=f"未知风险操作: {action}"
            )

        return await handler(context)

    async def _assess_risk(self, context: AgentContext) -> AgentResult:
        """综合风险评估"""
        # 获取当前持仓
        positions_result = await trading_agent._get_positions(context)
        positions = positions_result.data.get("positions", [])
        total_assets = positions_result.data.get("total_assets", 0)

        if not positions:
            return AgentResult(
                task_id=context.task_id,
                success=True,
                data={
                    "risk_level": RiskLevel.LOW.value,
                    "message": "当前无持仓",
                    "alerts": [],
                },
                message="风险评估完成：无持仓"
            )

        alerts = []

        # 1. 检查仓位风险
        position_alerts = self._check_position_sizes(positions, total_assets)
        alerts.extend(position_alerts)

        # 2. 检查集中度风险
        concentration_alerts = await self._analyze_concentration(positions, total_assets)
        alerts.extend(concentration_alerts)

        # 3. 检查盈亏风险
        pnl_alerts = self._check_profit_loss(positions)
        alerts.extend(pnl_alerts)

        # 4. 确定整体风险等级
        overall_risk = self._determine_overall_risk(alerts)

        # 生成建议
        recommendations = self._generate_recommendations(alerts)

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "risk_level": overall_risk.value,
                "alerts": [self._alert_to_dict(a) for a in alerts],
                "alert_count": len(alerts),
                "recommendations": recommendations,
                "positions_analyzed": len(positions),
            },
            message=f"风险评估完成，发现 {len(alerts)} 个风险点"
        )

    def _check_position_sizes(
        self,
        positions: List[Dict],
        total_assets: float
    ) -> List[RiskAlert]:
        """检查仓位大小"""
        alerts = []

        for position in positions:
            position_percent = (position["market_value"] / total_assets) * 100

            if position_percent > self._max_position_percent:
                alerts.append(RiskAlert(
                    risk_type=RiskType.POSITION_SIZE,
                    level=RiskLevel.HIGH if position_percent > self._max_position_percent * 1.5 else RiskLevel.MEDIUM,
                    symbol=position["symbol"],
                    message=f"仓位过大: {position['symbol']} 占比 {position_percent:.1f}%",
                    value=position_percent,
                    threshold=self._max_position_percent,
                    timestamp=datetime.now(),
                    recommendation=f"建议减仓至 {self._max_position_percent}% 以下"
                ))

        return alerts

    async def _analyze_concentration(
        self,
        positions: List[Dict],
        total_assets: float
    ) -> List[RiskAlert]:
        """分析集中度风险"""
        alerts = []

        # 简化版：检查前三大持仓集中度
        sorted_positions = sorted(positions, key=lambda x: x["market_value"], reverse=True)
        top3_value = sum(p["market_value"] for p in sorted_positions[:3])
        top3_percent = (top3_value / total_assets) * 100 if total_assets > 0 else 0

        if top3_percent > self._max_concentration_percent:
            alerts.append(RiskAlert(
                risk_type=RiskType.CONCENTRATION,
                level=RiskLevel.MEDIUM,
                symbol=None,
                message=f"持仓集中度过高: 前3大持仓占比 {top3_percent:.1f}%",
                value=top3_percent,
                threshold=self._max_concentration_percent,
                timestamp=datetime.now(),
                recommendation="建议分散投资，降低集中度"
            ))

        return alerts

    def _check_profit_loss(self, positions: List[Dict]) -> List[RiskAlert]:
        """检查盈亏风险"""
        alerts = []

        for position in positions:
            # 止损检查
            if position["profit_loss_percent"] <= -self._stop_loss_percent:
                alerts.append(RiskAlert(
                    risk_type=RiskType.DRAWDOWN,
                    level=RiskLevel.CRITICAL if position["profit_loss_percent"] <= -self._stop_loss_percent * 1.5 else RiskLevel.HIGH,
                    symbol=position["symbol"],
                    message=f"触发止损线: {position['symbol']} 亏损 {abs(position['profit_loss_percent']):.1f}%",
                    value=position["profit_loss_percent"],
                    threshold=-self._stop_loss_percent,
                    timestamp=datetime.now(),
                    recommendation="建议立即止损卖出"
                ))

            # 止盈检查
            if position["profit_loss_percent"] >= self._take_profit_percent:
                alerts.append(RiskAlert(
                    risk_type=RiskType.DRAWDOWN,
                    level=RiskLevel.LOW,
                    symbol=position["symbol"],
                    message=f"达到止盈线: {position['symbol']} 盈利 {position['profit_loss_percent']:.1f}%",
                    value=position["profit_loss_percent"],
                    threshold=self._take_profit_percent,
                    timestamp=datetime.now(),
                    recommendation="考虑部分止盈锁定收益"
                ))

        return alerts

    async def _check_position_risk(self, context: AgentContext) -> AgentResult:
        """检查单只股票仓位风险"""
        symbol = context.params.get("symbol")
        shares = context.params.get("shares")
        price = context.params.get("price")
        action = context.params.get("trade_action", "buy")

        if not all([symbol, shares, price]):
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少必要参数"
            )

        # 获取当前账户信息
        account = await trading_agent._get_account(context)
        total_assets = account.data.get("total_assets", 0)

        trade_value = shares * price
        position_percent = (trade_value / total_assets) * 100

        # 风险评估
        risks = []
        if action == "buy":
            if position_percent > self._max_position_percent:
                risks.append({
                    "type": "position_size",
                    "level": "high",
                    "message": f"仓位占比 {position_percent:.1f}% 超过上限 {self._max_position_percent}%",
                    "recommendation": f"建议减少购买数量"
                })

            if trade_value > account.data.get("available_balance", 0):
                risks.append({
                    "type": "liquidity",
                    "level": "critical",
                    "message": "可用资金不足",
                    "recommendation": "请减少购买数量或补充资金"
                })

        # 计算最大可购买数量
        max_shares = int((total_assets * self._max_position_percent / 100) / price)
        affordable_shares = int(account.data.get("available_balance", 0) / price)

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "symbol": symbol,
                "trade_value": round(trade_value, 2),
                "position_percent": round(position_percent, 2),
                "risks": risks,
                "risk_level": self._calculate_risk_level_from_risks(risks),
                "suggestions": {
                    "max_shares": min(max_shares, affordable_shares),
                    "max_trade_value": round(min(max_shares, affordable_shares) * price, 2),
                },
            },
            message=f"风险评估完成，发现 {len(risks)} 个风险点"
        )

    def _calculate_risk_level_from_risks(self, risks: List[Dict]) -> str:
        """根据风险列表计算整体风险等级"""
        if not risks:
            return RiskLevel.LOW.value

        levels = [r["level"] for r in risks]
        if "critical" in levels:
            return RiskLevel.CRITICAL.value
        elif "high" in levels:
            return RiskLevel.HIGH.value
        elif "medium" in levels:
            return RiskLevel.MEDIUM.value
        else:
            return RiskLevel.LOW.value

    async def _set_stop_loss(self, context: AgentContext) -> AgentResult:
        """设置止损"""
        symbol = context.params.get("symbol")
        stop_loss_percent = context.params.get("stop_loss_percent")

        if not symbol or stop_loss_percent is None:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少参数: symbol, stop_loss_percent"
            )

        # 简化版：返回止损价计算
        positions = await trading_agent._get_positions(context)
        position = next(
            (p for p in positions.data.get("positions", []) if p["symbol"] == symbol),
            None
        )

        if not position:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error=f"未找到持仓: {symbol}"
            )

        stop_price = position["avg_cost"] * (1 - stop_loss_percent / 100)

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "symbol": symbol,
                "avg_cost": position["avg_cost"],
                "stop_loss_percent": stop_loss_percent,
                "stop_price": round(stop_price, 2),
            },
            message=f"止损设置成功，止损价: {stop_price:.2f}"
        )

    async def _set_take_profit(self, context: AgentContext) -> AgentResult:
        """设置止盈"""
        symbol = context.params.get("symbol")
        take_profit_percent = context.params.get("take_profit_percent")

        if not symbol or take_profit_percent is None:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少参数: symbol, take_profit_percent"
            )

        positions = await trading_agent._get_positions(context)
        position = next(
            (p for p in positions.data.get("positions", []) if p["symbol"] == symbol),
            None
        )

        if not position:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error=f"未找到持仓: {symbol}"
            )

        take_profit_price = position["avg_cost"] * (1 + take_profit_percent / 100)

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "symbol": symbol,
                "avg_cost": position["avg_cost"],
                "take_profit_percent": take_profit_percent,
                "take_profit_price": round(take_profit_price, 2),
            },
            message=f"止盈设置成功，止盈价: {take_profit_price:.2f}"
        )

    async def _check_concentration(self, context: AgentContext) -> AgentResult:
        """检查集中度"""
        positions_result = await trading_agent._get_positions(context)
        positions = positions_result.data.get("positions", [])
        total_assets = positions_result.data.get("total_assets", 0)

        # 计算集中度指标
        top1_percent = 0
        top3_percent = 0
        top5_percent = 0

        if positions:
            sorted_positions = sorted(positions, key=lambda x: x["market_value"], reverse=True)
            top1_percent = (sorted_positions[0]["market_value"] / total_assets) * 100 if total_assets > 0 else 0
            top3_percent = (sum(p["market_value"] for p in sorted_positions[:3]) / total_assets) * 100 if total_assets > 0 else 0
            top5_percent = (sum(p["market_value"] for p in sorted_positions[:5]) / total_assets) * 100 if total_assets > 0 else 0

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "position_count": len(positions),
                "top1_percent": round(top1_percent, 2),
                "top3_percent": round(top3_percent, 2),
                "top5_percent": round(top5_percent, 2),
                "threshold": self._max_concentration_percent,
                "is_concentrated": top3_percent > self._max_concentration_percent,
            },
            message="集中度分析完成"
        )

    async def _get_alerts(self, context: AgentContext) -> AgentResult:
        """获取风险预警"""
        limit = context.params.get("limit", 20)
        level = context.params.get("level")

        alerts = self._alerts
        if level:
            alerts = [a for a in alerts if a.level.value == level]

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "total": len(alerts),
                "alerts": [self._alert_to_dict(a) for a in alerts[-limit:]],
            }
        )

    async def _get_risk_config(self, context: AgentContext) -> AgentResult:
        """获取风控配置"""
        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "max_position_percent": self._max_position_percent,
                "max_single_loss_percent": self._max_single_loss_percent,
                "max_total_loss_percent": self._max_total_loss_percent,
                "max_concentration_percent": self._max_concentration_percent,
                "stop_loss_percent": self._stop_loss_percent,
                "take_profit_percent": self._take_profit_percent,
            }
        )

    async def _set_risk_config(self, context: AgentContext) -> AgentResult:
        """设置风控配置"""
        if "max_position_percent" in context.params:
            self._max_position_percent = float(context.params["max_position_percent"])
        if "max_single_loss_percent" in context.params:
            self._max_single_loss_percent = float(context.params["max_single_loss_percent"])
        if "stop_loss_percent" in context.params:
            self._stop_loss_percent = float(context.params["stop_loss_percent"])
        if "take_profit_percent" in context.params:
            self._take_profit_percent = float(context.params["take_profit_percent"])

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data=await self._get_risk_config(context).then(lambda r: r.data),
            message="风控配置已更新"
        )

    async def _portfolio_analysis(self, context: AgentContext) -> AgentResult:
        """投资组合风险分析"""
        positions_result = await trading_agent._get_positions(context)
        positions = positions_result.data.get("positions", [])

        if not positions:
            return AgentResult(
                task_id=context.task_id,
                success=True,
                data={
                    "total_value": 0,
                    "position_count": 0,
                    "analysis": "无持仓",
                },
                message="投资组合为空"
            )

        # 计算组合指标
        total_value = sum(p["market_value"] for p in positions)
        total_profit = sum(p["profit_loss"] for p in positions)
        total_profit_percent = (total_profit / (total_value - total_profit)) * 100 if total_value > total_profit else 0

        # 风险分散度
        position_values = [p["market_value"] for p in positions]
        avg_position = sum(position_values) / len(position_values)
        variance = sum((v - avg_position) ** 2 for v in position_values) / len(position_values)
        diversification_score = 100 - (variance ** 0.5 / total_value * 100) if total_value > 0 else 0

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "total_value": round(total_value, 2),
                "position_count": len(positions),
                "total_profit": round(total_profit, 2),
                "total_profit_percent": round(total_profit_percent, 2),
                "diversification_score": round(diversification_score, 1),
                "largest_position": max(positions, key=lambda x: x["market_value"])["symbol"],
                "best_performer": max(positions, key=lambda x: x["profit_loss_percent"])["symbol"],
                "worst_performer": min(positions, key=lambda x: x["profit_loss_percent"])["symbol"],
            },
            message="投资组合分析完成"
        )

    def _determine_overall_risk(self, alerts: List[RiskAlert]) -> RiskLevel:
        """确定整体风险等级"""
        if not alerts:
            return RiskLevel.LOW

        levels = [a.level for a in alerts]
        if RiskLevel.CRITICAL in levels:
            return RiskLevel.CRITICAL
        elif RiskLevel.HIGH in levels:
            return RiskLevel.HIGH
        elif RiskLevel.MEDIUM in levels:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_recommendations(self, alerts: List[RiskAlert]) -> List[str]:
        """生成风险建议"""
        recommendations = []
        for alert in alerts:
            if alert.recommendation:
                recommendations.append(f"[{alert.level.value.upper()}] {alert.recommendation}")

        if not recommendations:
            recommendations.append("当前风险水平良好，继续保持")

        return recommendations

    def _alert_to_dict(self, alert: RiskAlert) -> Dict:
        """预警转字典"""
        return {
            "risk_type": alert.risk_type.value,
            "level": alert.level.value,
            "symbol": alert.symbol,
            "message": alert.message,
            "value": round(alert.value, 2),
            "threshold": round(alert.threshold, 2),
            "timestamp": alert.timestamp.isoformat(),
            "recommendation": alert.recommendation,
        }


# 全局实例
risk_agent = RiskAgent()