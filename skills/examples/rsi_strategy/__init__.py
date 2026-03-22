"""RSI 超买超卖策略 SKILL"""
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from datetime import datetime, timedelta

from app.skill.base import BaseSkill, SkillContext, SkillResult, SkillStatus
from app.data.gateway import gateway


class RSIStrategy(BaseSkill):
    """
    RSI 策略

    RSI < 30 超卖区间，买入信号
    RSI > 70 超买区间，卖出信号
    """

    @property
    def name(self) -> str:
        return "rsi_strategy"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "RSI超买超卖策略：RSI<30买入，RSI>70卖出"

    @property
    def author(self) -> str:
        return "ai-trading-lab"

    @property
    def category(self) -> str:
        return "trading"

    @property
    def params_schema(self) -> dict:
        return {
            "required": ["symbol"],
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码"
                },
                "period": {
                    "type": "integer",
                    "default": 14,
                    "description": "RSI周期"
                },
                "oversold": {
                    "type": "number",
                    "default": 30,
                    "description": "超卖阈值"
                },
                "overbought": {
                    "type": "number",
                    "default": 70,
                    "description": "超买阈值"
                },
                "market": {
                    "type": "string",
                    "default": "cn",
                    "description": "市场"
                }
            }
        }

    def _calc_rsi(self, closes: list, period: int) -> float:
        """计算 RSI"""
        if len(closes) < period + 1:
            return 50

        deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
        gains = [d for d in deltas if d > 0]
        losses = [-d for d in deltas if d < 0]

        avg_gain = sum(gains[-period:]) / period if gains else 0
        avg_loss = sum(losses[-period:]) / period if losses else 0

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    async def execute(self, context: SkillContext) -> SkillResult:
        symbol = context.params["symbol"]
        period = context.params.get("period", 14)
        oversold = context.params.get("oversold", 30)
        overbought = context.params.get("overbought", 70)
        market = context.params.get("market", "cn")

        # 获取历史数据
        end = datetime.now()
        start = end - timedelta(days=period * 3)

        history = await gateway.get_history(symbol, start, end, market)

        if len(history) < period + 1:
            return SkillResult(
                status=SkillStatus.FAILED,
                error=f"历史数据不足"
            )

        closes = [h.close for h in history]

        # 计算 RSI
        rsi = self._calc_rsi(closes, period)

        # 判断信号
        if rsi < oversold:
            signal = "buy"
            message = f"超卖信号：RSI={rsi:.1f} < {oversold}，建议买入"
        elif rsi > overbought:
            signal = "sell"
            message = f"超买信号：RSI={rsi:.1f} > {overbought}，建议卖出"
        else:
            signal = "hold"
            message = f"RSI={rsi:.1f}，处于正常区间"

        return SkillResult(
            status=SkillStatus.SUCCESS,
            data={
                "symbol": symbol,
                "signal": signal,
                "rsi": round(rsi, 2),
                "latest_price": round(closes[-1], 2),
                "oversold_threshold": oversold,
                "overbought_threshold": overbought
            },
            message=message
        )


skill = RSIStrategy()