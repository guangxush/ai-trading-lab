"""Trading Agent - 交易执行智能体"""
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field
import uuid

from .base import BaseAgent, AgentContext, AgentResult, AgentType
from ..data.gateway import gateway


class OrderType(str, Enum):
    """订单类型"""
    MARKET = "market"       # 市价单
    LIMIT = "limit"         # 限价单
    STOP = "stop"           # 止损单
    STOP_LIMIT = "stop_limit"  # 止损限价单


class OrderSide(str, Enum):
    """买卖方向"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = "pending"     # 待提交
    SUBMITTED = "submitted" # 已提交
    FILLED = "filled"       # 已成交
    PARTIAL = "partial"     # 部分成交
    CANCELLED = "cancelled" # 已取消
    REJECTED = "rejected"   # 已拒绝


@dataclass
class Order:
    """订单"""
    order_id: str
    symbol: str
    market: str
    side: OrderSide
    order_type: OrderType
    shares: int
    price: Optional[float] = None  # 限价单价格
    stop_price: Optional[float] = None  # 止损价
    status: OrderStatus = OrderStatus.PENDING
    filled_shares: int = 0
    filled_price: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    message: str = ""


@dataclass
class Position:
    """持仓"""
    symbol: str
    market: str
    shares: int
    avg_cost: float
    current_price: float = 0.0
    market_value: float = 0.0
    profit_loss: float = 0.0
    profit_loss_percent: float = 0.0

    def update_price(self, current_price: float):
        """更新当前价格和盈亏"""
        self.current_price = current_price
        self.market_value = self.shares * current_price
        self.profit_loss = (current_price - self.avg_cost) * self.shares
        self.profit_loss_percent = (current_price - self.avg_cost) / self.avg_cost * 100 if self.avg_cost > 0 else 0


class TradingAgent(BaseAgent):
    """
    交易执行 Agent

    负责：
    - 订单创建和管理
    - 交易执行（模拟）
    - 成交确认
    - 持仓管理
    """

    def __init__(self):
        super().__init__()
        self._orders: Dict[str, Order] = {}
        self._positions: Dict[str, Position] = {}
        self._account_balance: float = 1000000.0  # 初始资金100万
        self._available_balance: float = 1000000.0
        self._trade_history: List[Dict] = []

    @property
    def name(self) -> str:
        return "TradingAgent"

    @property
    def agent_type(self) -> AgentType:
        return AgentType.TRADING

    @property
    def description(self) -> str:
        return "交易执行智能体，负责订单管理和交易执行"

    async def execute(self, context: AgentContext) -> AgentResult:
        """执行交易任务"""
        action = context.params.get("action", "create_order")

        handlers = {
            "create_order": self._create_order,
            "cancel_order": self._cancel_order,
            "get_orders": self._get_orders,
            "get_positions": self._get_positions,
            "get_account": self._get_account,
            "execute_pending": self._execute_pending_orders,
            "get_trade_history": self._get_trade_history,
            "update_balance": self._update_balance,
        }

        handler = handlers.get(action)
        if not handler:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error=f"未知交易操作: {action}"
            )

        return await handler(context)

    async def _create_order(self, context: AgentContext) -> AgentResult:
        """创建订单"""
        symbol = context.params.get("symbol")
        market = context.params.get("market", "cn")
        side = context.params.get("side", "buy")
        shares = context.params.get("shares")
        order_type = context.params.get("order_type", "market")
        price = context.params.get("price")
        stop_price = context.params.get("stop_price")

        if not symbol or not shares:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="缺少必要参数: symbol, shares"
            )

        # 验证订单
        validation = self._validate_order(symbol, market, side, shares, price)
        if not validation["valid"]:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error=validation["message"]
            )

        # 创建订单
        order = Order(
            order_id=str(uuid.uuid4()),
            symbol=symbol,
            market=market,
            side=OrderSide(side),
            order_type=OrderType(order_type),
            shares=int(shares),
            price=float(price) if price else None,
            stop_price=float(stop_price) if stop_price else None,
            status=OrderStatus.PENDING,
        )

        self._orders[order.order_id] = order

        # 立即执行市价单
        if order.order_type == OrderType.MARKET:
            result = await self._execute_order(order)
            return AgentResult(
                task_id=context.task_id,
                success=result["success"],
                data={"order": self._order_to_dict(order), "execution": result},
                message=result["message"]
            )

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={"order": self._order_to_dict(order)},
            message=f"订单已创建: {order.order_id}"
        )

    def _validate_order(
        self,
        symbol: str,
        market: str,
        side: str,
        shares: int,
        price: Optional[float]
    ) -> Dict:
        """验证订单"""
        # 验证股数
        if shares <= 0:
            return {"valid": False, "message": "股数必须大于0"}

        # 验证买入：检查可用资金
        if side == "buy":
            # 获取当前价格估算
            estimated_cost = shares * (price or 100)  # 默认估计价格
            if estimated_cost > self._available_balance:
                return {
                    "valid": False,
                    "message": f"可用资金不足，需要 {estimated_cost:.2f}，可用 {self._available_balance:.2f}"
                }

        # 验证卖出：检查持仓
        if side == "sell":
            position_key = f"{market}:{symbol}"
            position = self._positions.get(position_key)
            if not position or position.shares < shares:
                available = position.shares if position else 0
                return {
                    "valid": False,
                    "message": f"持仓不足，需要 {shares} 股，可用 {available} 股"
                }

        return {"valid": True, "message": "验证通过"}

    async def _execute_order(self, order: Order) -> Dict:
        """执行订单"""
        # 获取当前价格
        quote = await gateway.get_quote(order.symbol, order.market)
        if not quote:
            order.status = OrderStatus.REJECTED
            order.message = "无法获取行情数据"
            return {"success": False, "message": order.message}

        execute_price = quote.price
        if order.order_type == OrderType.LIMIT and order.price:
            # 限价单检查价格
            if order.side == OrderSide.BUY and quote.price > order.price:
                return {"success": False, "message": "当前价格高于限价，无法成交"}
            if order.side == OrderSide.SELL and quote.price < order.price:
                return {"success": False, "message": "当前价格低于限价，无法成交"}
            execute_price = order.price

        # 更新订单状态
        order.status = OrderStatus.FILLED
        order.filled_shares = order.shares
        order.filled_price = execute_price
        order.updated_at = datetime.now()
        order.message = f"全部成交，成交价 {execute_price:.2f}"

        # 更新持仓和资金
        self._update_position_and_balance(order, execute_price)

        # 记录交易历史
        self._trade_history.append({
            "timestamp": datetime.now().isoformat(),
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side.value,
            "shares": order.shares,
            "price": execute_price,
            "amount": order.shares * execute_price
        })

        return {
            "success": True,
            "message": order.message,
            "filled_price": execute_price,
            "filled_shares": order.shares
        }

    def _update_position_and_balance(self, order: Order, execute_price: float):
        """更新持仓和资金"""
        position_key = f"{order.market}:{order.symbol}"
        trade_amount = order.shares * execute_price

        if order.side == OrderSide.BUY:
            # 买入：减少资金，增加持仓
            self._available_balance -= trade_amount
            self._account_balance -= trade_amount

            if position_key in self._positions:
                # 加仓
                position = self._positions[position_key]
                total_cost = position.avg_cost * position.shares + trade_amount
                position.shares += order.shares
                position.avg_cost = total_cost / position.shares
            else:
                # 新建仓位
                self._positions[position_key] = Position(
                    symbol=order.symbol,
                    market=order.market,
                    shares=order.shares,
                    avg_cost=execute_price,
                    current_price=execute_price
                )
        else:
            # 卖出：增加资金，减少持仓
            self._available_balance += trade_amount
            self._account_balance += trade_amount

            if position_key in self._positions:
                position = self._positions[position_key]
                position.shares -= order.shares
                if position.shares == 0:
                    del self._positions[position_key]

    async def _cancel_order(self, context: AgentContext) -> AgentResult:
        """取消订单"""
        order_id = context.params.get("order_id")

        if not order_id or order_id not in self._orders:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error="订单不存在"
            )

        order = self._orders[order_id]
        if order.status not in [OrderStatus.PENDING, OrderStatus.SUBMITTED]:
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error=f"订单状态为 {order.status.value}，无法取消"
            )

        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now()
        order.message = "订单已取消"

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={"order": self._order_to_dict(order)},
            message="订单已取消"
        )

    async def _get_orders(self, context: AgentContext) -> AgentResult:
        """获取订单列表"""
        status = context.params.get("status")
        symbol = context.params.get("symbol")

        orders = []
        for order in self._orders.values():
            if status and order.status.value != status:
                continue
            if symbol and order.symbol != symbol:
                continue
            orders.append(self._order_to_dict(order))

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "total": len(orders),
                "orders": orders
            },
            message=f"共 {len(orders)} 个订单"
        )

    async def _get_positions(self, context: AgentContext) -> AgentResult:
        """获取持仓"""
        positions = []
        total_market_value = 0
        total_profit_loss = 0

        for position in self._positions.values():
            # 更新当前价格
            quote = await gateway.get_quote(position.symbol, position.market)
            if quote:
                position.update_price(quote.price)

            positions.append({
                "symbol": position.symbol,
                "market": position.market,
                "shares": position.shares,
                "avg_cost": round(position.avg_cost, 2),
                "current_price": round(position.current_price, 2),
                "market_value": round(position.market_value, 2),
                "profit_loss": round(position.profit_loss, 2),
                "profit_loss_percent": round(position.profit_loss_percent, 2),
            })

            total_market_value += position.market_value
            total_profit_loss += position.profit_loss

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "positions": positions,
                "total_market_value": round(total_market_value, 2),
                "total_profit_loss": round(total_profit_loss, 2),
                "cash_balance": round(self._available_balance, 2),
                "total_assets": round(total_market_value + self._available_balance, 2),
            }
        )

    async def _get_account(self, context: AgentContext) -> AgentResult:
        """获取账户信息"""
        # 计算总资产
        total_position_value = sum(p.market_value for p in self._positions.values())
        total_assets = self._available_balance + total_position_value

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "account_balance": round(self._account_balance, 2),
                "available_balance": round(self._available_balance, 2),
                "total_position_value": round(total_position_value, 2),
                "total_assets": round(total_assets, 2),
                "position_count": len(self._positions),
                "order_count": len(self._orders),
            }
        )

    async def _execute_pending_orders(self, context: AgentContext) -> AgentResult:
        """执行挂单"""
        executed = []
        failed = []

        for order in self._orders.values():
            if order.status == OrderStatus.PENDING:
                if order.order_type in [OrderType.MARKET, OrderType.LIMIT]:
                    result = await self._execute_order(order)
                    if result["success"]:
                        executed.append({
                            "order_id": order.order_id,
                            "symbol": order.symbol,
                            "filled_price": result["filled_price"]
                        })
                    else:
                        failed.append({
                            "order_id": order.order_id,
                            "error": result["message"]
                        })

        return AgentResult(
            task_id=context.task_id,
            success=len(failed) == 0,
            data={
                "executed": executed,
                "failed": failed,
            },
            message=f"执行 {len(executed)} 个订单，{len(failed)} 个失败"
        )

    async def _get_trade_history(self, context: AgentContext) -> AgentResult:
        """获取交易历史"""
        limit = context.params.get("limit", 50)
        history = self._trade_history[-limit:]

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "total": len(self._trade_history),
                "history": history
            }
        )

    async def _update_balance(self, context: AgentContext) -> AgentResult:
        """更新账户余额（用于初始化）"""
        amount = context.params.get("amount")
        if amount:
            self._account_balance = float(amount)
            self._available_balance = float(amount)

        return AgentResult(
            task_id=context.task_id,
            success=True,
            data={
                "account_balance": self._account_balance,
                "available_balance": self._available_balance
            },
            message="账户余额已更新"
        )

    def _order_to_dict(self, order: Order) -> Dict:
        """订单转字典"""
        return {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "market": order.market,
            "side": order.side.value,
            "type": order.order_type.value,
            "shares": order.shares,
            "price": order.price,
            "stop_price": order.stop_price,
            "status": order.status.value,
            "filled_shares": order.filled_shares,
            "filled_price": order.filled_price,
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat(),
            "message": order.message,
        }


# 全局实例
trading_agent = TradingAgent()