"""Analysis Agent - 行情分析智能体"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics

from .base import BaseAgent, AgentContext, AgentResult, AgentType
from ..data.gateway import gateway


class AnalysisAgent(BaseAgent):
    """
    行情分析 Agent

    负责：
    - 技术指标计算（MA、MACD、RSI、布林带等）
    - 趋势分析
    - 支撑阻力位识别
    - 买卖信号生成
    """

    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return "AnalysisAgent"

    @property
    def agent_type(self) -> AgentType:
        return AgentType.ANALYSIS

    @property
    def description(self) -> str:
        return "行情分析智能体，负责技术指标计算和趋势预测"

    async def execute(self, context: AgentContext) -> AgentResult:
        """执行分析任务"""
        action = context.params.get("action", "technical")

        handlers = {
            "technical": self._analyze_technical,
            "trend": self._analyze_trend,
            "signal": self._generate_signal,
            "support_resistance": self._find_support_resistance,
            "full": self._full_analysis,
        }

        handler = handlers.get(action)
        if not handler:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error=f"未知分析类型: {action}"
            )

        return await handler(context)

    async def _analyze_technical(self, context: AgentContext) -> AgentResult:
        """计算技术指标"""
        symbol = context.params.get("symbol")
        market = context.params.get("market", "cn")
        days = context.params.get("days", 60)

        if not symbol:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少 symbol 参数"
            )

        # 获取历史数据
        end = datetime.now()
        start = end - timedelta(days=days)
        history = await gateway.get_history(symbol, start, end, market)

        if len(history) < 5:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="历史数据不足，至少需要5天数据"
            )

        closes = [h.close for h in history]
        highs = [h.high for h in history]
        lows = [h.low for h in history]
        volumes = [h.volume for h in history]

        # 计算技术指标
        indicators = {
            "MA": self._calc_ma(closes),
            "EMA": self._calc_ema(closes),
            "RSI": self._calc_rsi(closes),
            "MACD": self._calc_macd(closes),
            "BollingerBands": self._calc_bollinger(closes),
            "ATR": self._calc_atr(highs, lows, closes),
            "VolumeRatio": self._calc_volume_ratio(volumes),
        }

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "symbol": symbol,
                "latest_price": closes[-1],
                "indicators": indicators,
                "data_points": len(history)
            },
            message=f"技术指标计算完成"
        )

    async def _analyze_trend(self, context: AgentContext) -> AgentResult:
        """趋势分析"""
        symbol = context.params.get("symbol")
        market = context.params.get("market", "cn")
        days = context.params.get("days", 30)

        if not symbol:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少 symbol 参数"
            )

        end = datetime.now()
        start = end - timedelta(days=days)
        history = await gateway.get_history(symbol, start, end, market)

        if len(history) < 10:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="历史数据不足，至少需要10天数据"
            )

        closes = [h.close for h in history]

        # 计算均线
        ma5 = self._calc_ma(closes, 5)
        ma10 = self._calc_ma(closes, 10)
        ma20 = self._calc_ma(closes, 20)

        # 趋势判断
        short_trend = self._determine_trend(closes, 5)
        mid_trend = self._determine_trend(closes, 10)
        long_trend = self._determine_trend(closes, 20)

        # 均线排列
        ma_alignment = self._check_ma_alignment(ma5, ma10, ma20)

        # 趋势强度
        trend_strength = self._calc_trend_strength(closes)

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "symbol": symbol,
                "short_trend": short_trend,
                "mid_trend": mid_trend,
                "long_trend": long_trend,
                "ma_alignment": ma_alignment,
                "trend_strength": trend_strength,
                "latest_price": closes[-1]
            },
            message=f"趋势分析完成: 短期{short_trend}, 中期{mid_trend}, 长期{long_trend}"
        )

    async def _generate_signal(self, context: AgentContext) -> AgentResult:
        """生成买卖信号"""
        symbol = context.params.get("symbol")
        market = context.params.get("market", "cn")

        if not symbol:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少 symbol 参数"
            )

        # 获取历史数据
        end = datetime.now()
        start = end - timedelta(days=60)
        history = await gateway.get_history(symbol, start, end, market)

        if len(history) < 30:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="历史数据不足"
            )

        closes = [h.close for h in history]

        # 计算指标
        ma5 = self._calc_ma(closes, 5)
        ma10 = self._calc_ma(closes, 10)
        ma20 = self._calc_ma(closes, 20)
        rsi = self._calc_rsi(closes, 14)
        macd = self._calc_macd(closes)

        # 信号判断
        signals = []
        score = 0

        # MA 金叉死叉
        if ma5 > ma10 > ma20:
            signals.append("多头排列")
            score += 2
        elif ma5 < ma10 < ma20:
            signals.append("空头排列")
            score -= 2

        # RSI 信号
        if rsi < 30:
            signals.append("RSI超卖")
            score += 1
        elif rsi > 70:
            signals.append("RSI超买")
            score -= 1

        # MACD 信号
        if macd["histogram"] > 0 and macd["histogram"] > macd.get("prev_histogram", 0):
            signals.append("MACD金叉")
            score += 1
        elif macd["histogram"] < 0:
            signals.append("MACD死叉")
            score -= 1

        # 综合评分
        if score >= 2:
            recommendation = "强烈买入"
            action = "BUY"
        elif score >= 1:
            recommendation = "建议买入"
            action = "BUY"
        elif score <= -2:
            recommendation = "强烈卖出"
            action = "SELL"
        elif score <= -1:
            recommendation = "建议卖出"
            action = "SELL"
        else:
            recommendation = "观望"
            action = "HOLD"

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "symbol": symbol,
                "action": action,
                "recommendation": recommendation,
                "score": score,
                "signals": signals,
                "indicators": {
                    "ma5": round(ma5, 2),
                    "ma10": round(ma10, 2),
                    "ma20": round(ma20, 2),
                    "rsi": round(rsi, 2),
                    "macd": macd
                },
                "latest_price": closes[-1]
            },
            message=f"信号分析完成: {recommendation}"
        )

    async def _find_support_resistance(self, context: AgentContext) -> AgentResult:
        """识别支撑阻力位"""
        symbol = context.params.get("symbol")
        market = context.params.get("market", "cn")
        days = context.params.get("days", 30)

        if not symbol:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少 symbol 参数"
            )

        end = datetime.now()
        start = end - timedelta(days=days)
        history = await gateway.get_history(symbol, start, end, market)

        if len(history) < 10:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="历史数据不足"
            )

        closes = [h.close for h in history]
        highs = [h.high for h in history]
        lows = [h.low for h in history]

        # 找支撑位（近期低点）
        support_levels = self._find_levels(lows, "support")

        # 找阻力位（近期高点）
        resistance_levels = self._find_levels(highs, "resistance")

        current_price = closes[-1]

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "symbol": symbol,
                "current_price": round(current_price, 2),
                "support_levels": [round(s, 2) for s in support_levels],
                "resistance_levels": [round(r, 2) for r in resistance_levels],
                "nearest_support": round(min(support_levels, key=lambda x: abs(x - current_price)), 2) if support_levels else None,
                "nearest_resistance": round(min(resistance_levels, key=lambda x: abs(x - current_price)), 2) if resistance_levels else None,
            },
            message=f"支撑阻力位识别完成"
        )

    async def _full_analysis(self, context: AgentContext) -> AgentResult:
        """完整分析"""
        symbol = context.params.get("symbol")
        market = context.params.get("market", "cn")

        if not symbol:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少 symbol 参数"
            )

        # 并行执行所有分析
        tech_ctx = AgentContext(task_id=f"{context.task_id}_tech", params={"symbol": symbol, "market": market})
        trend_ctx = AgentContext(task_id=f"{context.task_id}_trend", params={"symbol": symbol, "market": market})
        signal_ctx = AgentContext(task_id=f"{context.task_id}_signal", params={"symbol": symbol, "market": market})
        sr_ctx = AgentContext(task_id=f"{context.task_id}_sr", params={"symbol": symbol, "market": market})

        tech_result = await self._analyze_technical(tech_ctx)
        trend_result = await self._analyze_trend(trend_ctx)
        signal_result = await self._generate_signal(signal_ctx)
        sr_result = await self._find_support_resistance(sr_ctx)

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "symbol": symbol,
                "technical": tech_result.data if tech_result.success else None,
                "trend": trend_result.data if trend_result.success else None,
                "signal": signal_result.data if signal_result.success else None,
                "support_resistance": sr_result.data if sr_result.success else None,
            },
            message="完整分析完成"
        )

    # ===== 技术指标计算方法 =====

    def _calc_ma(self, data: List[float], period: int = 20) -> float:
        """计算移动平均线"""
        if len(data) < period:
            return sum(data) / len(data) if data else 0
        return sum(data[-period:]) / period

    def _calc_ema(self, data: List[float], period: int = 12) -> float:
        """计算指数移动平均线"""
        if len(data) < period:
            return sum(data) / len(data) if data else 0

        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period

        for price in data[period:]:
            ema = (price - ema) * multiplier + ema

        return ema

    def _calc_rsi(self, data: List[float], period: int = 14) -> float:
        """计算RSI"""
        if len(data) < period + 1:
            return 50

        deltas = [data[i] - data[i - 1] for i in range(1, len(data))]
        gains = [d for d in deltas if d > 0]
        losses = [-d for d in deltas if d < 0]

        avg_gain = sum(gains[-period:]) / period if gains else 0
        avg_loss = sum(losses[-period:]) / period if losses else 0

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _calc_macd(self, data: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """计算MACD"""
        ema_fast = self._calc_ema(data, fast)
        ema_slow = self._calc_ema(data, slow)
        macd_line = ema_fast - ema_slow

        # 简化计算信号线
        signal_line = macd_line * 0.9  # 简化
        histogram = macd_line - signal_line

        return {
            "macd": round(macd_line, 4),
            "signal": round(signal_line, 4),
            "histogram": round(histogram, 4)
        }

    def _calc_bollinger(self, data: List[float], period: int = 20, std_dev: float = 2) -> Dict:
        """计算布林带"""
        if len(data) < period:
            period = len(data)

        ma = sum(data[-period:]) / period
        variance = sum((x - ma) ** 2 for x in data[-period:]) / period
        std = variance ** 0.5

        return {
            "upper": round(ma + std_dev * std, 2),
            "middle": round(ma, 2),
            "lower": round(ma - std_dev * std, 2),
            "bandwidth": round(std_dev * std * 2 / ma * 100, 2) if ma else 0
        }

    def _calc_atr(self, highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
        """计算ATR"""
        if len(closes) < period + 1:
            return 0

        true_ranges = []
        for i in range(1, len(closes)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1])
            )
            true_ranges.append(tr)

        return sum(true_ranges[-period:]) / period if true_ranges else 0

    def _calc_volume_ratio(self, volumes: List[int], period: int = 5) -> float:
        """计算量比"""
        if len(volumes) < period + 1:
            return 1.0

        current = volumes[-1]
        avg = sum(volumes[-period - 1:-1]) / period
        return round(current / avg, 2) if avg > 0 else 0

    def _determine_trend(self, data: List[float], period: int) -> str:
        """判断趋势"""
        if len(data) < period:
            return "未知"

        recent = data[-period:]
        first_half = recent[:len(recent) // 2]
        second_half = recent[len(recent) // 2:]

        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)

        change = (avg_second - avg_first) / avg_first * 100

        if change > 3:
            return "上涨"
        elif change < -3:
            return "下跌"
        else:
            return "震荡"

    def _check_ma_alignment(self, ma5: float, ma10: float, ma20: float) -> str:
        """检查均线排列"""
        if ma5 > ma10 > ma20:
            return "多头排列"
        elif ma5 < ma10 < ma20:
            return "空头排列"
        else:
            return "交叉缠绕"

    def _calc_trend_strength(self, data: List[float], period: int = 14) -> float:
        """计算趋势强度"""
        if len(data) < period:
            return 0

        recent = data[-period:]
        changes = [recent[i] - recent[i - 1] for i in range(1, len(recent))]

        positive = sum(1 for c in changes if c > 0)
        total = len(changes)

        return round(positive / total * 100, 1) if total > 0 else 50

    def _find_levels(self, data: List[float], level_type: str) -> List[float]:
        """找出支撑/阻力位"""
        if len(data) < 5:
            return []

        levels = []
        for i in range(2, len(data) - 2):
            if level_type == "support":
                # 低点
                if data[i] < data[i - 1] and data[i] < data[i + 1]:
                    levels.append(data[i])
            else:
                # 高点
                if data[i] > data[i - 1] and data[i] > data[i + 1]:
                    levels.append(data[i])

        # 合并相近的价位
        if levels:
            levels.sort()
            merged = [levels[0]]
            for level in levels[1:]:
                if abs(level - merged[-1]) / merged[-1] > 0.02:  # 2%差异
                    merged.append(level)
            return merged[-5:] if len(merged) > 5 else merged

        return []


# 全局实例
analysis_agent = AnalysisAgent()