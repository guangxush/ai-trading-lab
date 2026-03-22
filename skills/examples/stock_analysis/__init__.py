"""股票分析 SKILL"""
import sys
from pathlib import Path

# 添加后端路径
backend_path = Path(__file__).parent.parent.parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from datetime import datetime, timedelta

from app.skill.base import BaseSkill, SkillContext, SkillResult, SkillStatus
from app.data.gateway import gateway


class StockAnalysisSkill(BaseSkill):
    """
    股票分析 SKILL

    分析股票走势，提供简单的技术指标和买卖建议。
    """

    @property
    def name(self) -> str:
        return "stock_analysis"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "分析股票走势，计算MA均线，提供买卖建议"

    @property
    def author(self) -> str:
        return "ai-trading-lab"

    @property
    def category(self) -> str:
        return "analysis"

    @property
    def params_schema(self) -> dict:
        return {
            "required": ["symbol"],
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码，如 600519"
                },
                "days": {
                    "type": "integer",
                    "default": 30,
                    "description": "分析天数"
                },
                "market": {
                    "type": "string",
                    "default": "cn",
                    "description": "市场：cn/us/hk"
                }
            }
        }

    async def execute(self, context: SkillContext) -> SkillResult:
        symbol = context.params["symbol"]
        days = context.params.get("days", 30)
        market = context.params.get("market", "cn")

        # 获取历史数据
        end = datetime.now()
        start = end - timedelta(days=days * 2)  # 多获取一些数据用于计算均线

        try:
            history = await gateway.get_history(symbol, start, end, market)
        except ValueError as e:
            return SkillResult(
                status=SkillStatus.FAILED,
                error=str(e)
            )

        if not history:
            return SkillResult(
                status=SkillStatus.FAILED,
                error="无法获取历史数据，请检查股票代码"
            )

        # 取最近 days 天的数据
        history = history[-days:] if len(history) > days else history

        if len(history) < 5:
            return SkillResult(
                status=SkillStatus.FAILED,
                error="历史数据不足，至少需要5天的数据"
            )

        # 计算技术指标
        closes = [h.close for h in history]
        latest = history[-1]

        # 计算均线
        ma5 = sum(closes[-5:]) / 5
        ma10 = sum(closes[-10:]) / 10 if len(closes) >= 10 else ma5
        ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else ma10

        # 判断趋势
        if ma5 > ma10 > ma20:
            trend = "强势上涨"
            advice = "建议：可考虑持有或轻仓跟进"
        elif ma5 > ma10:
            trend = "震荡上涨"
            advice = "建议：可考虑持有，注意止损"
        elif ma5 < ma10 < ma20:
            trend = "弱势下跌"
            advice = "建议：建议观望或减仓"
        else:
            trend = "震荡整理"
            advice = "建议：等待方向明确"

        # 计算30天涨跌幅
        if len(closes) >= 2:
            change_30d = (closes[-1] - closes[0]) / closes[0] * 100
        else:
            change_30d = 0

        return SkillResult(
            status=SkillStatus.SUCCESS,
            data={
                "symbol": symbol,
                "market": market,
                "latest_price": round(latest.close, 2),
                "change_30d": round(change_30d, 2),
                "ma5": round(ma5, 2),
                "ma10": round(ma10, 2),
                "ma20": round(ma20, 2),
                "trend": trend,
                "advice": advice,
                "data_points": len(history),
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M")
            },
            message=f"分析完成: {symbol} 当前{trend}趋势"
        )


# 导出 SKILL 实例
skill = StockAnalysisSkill()