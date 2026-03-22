"""简单均线策略 SKILL"""
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from datetime import datetime, timedelta
from typing import Dict, Any

from app.skill.base import BaseSkill, SkillContext, SkillResult, SkillStatus
from app.data.gateway import gateway


class SimpleMAStrategy(BaseSkill):
    """
    简单均线策略

    当短期均线上穿长期均线时买入，下穿时卖出。
    """

    @property
    def name(self) -> str:
        return "simple_ma_strategy"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "简单均线交叉策略：MA5上穿MA20买入，下穿卖出"

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
                "short_period": {
                    "type": "integer",
                    "default": 5,
                    "description": "短期均线周期"
                },
                "long_period": {
                    "type": "integer",
                    "default": 20,
                    "description": "长期均线周期"
                },
                "market": {
                    "type": "string",
                    "default": "cn",
                    "description": "市场"
                }
            }
        }

    async def execute(self, context: SkillContext) -> SkillResult:
        symbol = context.params["symbol"]
        short_period = context.params.get("short_period", 5)
        long_period = context.params.get("long_period", 20)
        market = context.params.get("market", "cn")

        # 获取历史数据
        end = datetime.now()
        start = end - timedelta(days=long_period * 2)

        history = await gateway.get_history(symbol, start, end, market)

        if len(history) < long_period:
            return SkillResult(
                status=SkillStatus.FAILED,
                error=f"历史数据不足，需要至少 {long_period} 天"
            )

        closes = [h.close for h in history]

        # 计算均线
        short_ma = sum(closes[-short_period:]) / short_period
        long_ma = sum(closes[-long_period:]) / long_period

        # 前一天的均线
        prev_short_ma = sum(closes[-short_period-1:-1]) / short_period
        prev_long_ma = sum(closes[-long_period-1:-1]) / long_period

        # 判断信号
        signal = "hold"
        if prev_short_ma <= prev_long_ma and short_ma > long_ma:
            signal = "buy"
            message = f"金叉信号：MA{short_period} 上穿 MA{long_period}，建议买入"
        elif prev_short_ma >= prev_long_ma and short_ma < long_ma:
            signal = "sell"
            message = f"死叉信号：MA{short_period} 下穿 MA{long_period}，建议卖出"
        else:
            message = "无信号：均线未形成交叉"

        return SkillResult(
            status=SkillStatus.SUCCESS,
            data={
                "symbol": symbol,
                "signal": signal,
                "short_ma": round(short_ma, 2),
                "long_ma": round(long_ma, 2),
                "latest_price": round(closes[-1], 2),
                "message": message
            },
            message=message
        )


skill = SimpleMAStrategy()