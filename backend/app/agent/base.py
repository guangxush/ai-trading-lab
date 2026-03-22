"""Agent 基类定义"""
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent 状态"""
    IDLE = "idle"           # 空闲
    RUNNING = "running"     # 运行中
    PAUSED = "paused"       # 暂停
    ERROR = "error"         # 错误


class AgentType(str, Enum):
    """Agent 类型"""
    DATA = "data"           # 数据采集
    ANALYSIS = "analysis"   # 行情分析
    STRATEGY = "strategy"   # 策略生成
    TRADING = "trading"     # 交易执行
    RISK = "risk"           # 风险管理
    BACKTEST = "backtest"   # 回测验证


class AgentContext(BaseModel):
    """Agent 执行上下文"""
    task_id: str = Field(..., description="任务ID")
    user_id: Optional[str] = Field(default=None, description="用户ID")
    params: Dict[str, Any] = Field(default_factory=dict, description="执行参数")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class AgentResult(BaseModel):
    """Agent 执行结果"""
    task_id: str = Field(..., description="任务ID")
    success: bool = Field(..., description="是否成功")
    data: Optional[Dict[str, Any]] = Field(default=None, description="返回数据")
    message: str = Field(default="", description="消息")
    error: Optional[str] = Field(default=None, description="错误信息")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="执行指标")
    completed_at: datetime = Field(default_factory=datetime.now, description="完成时间")


class BaseAgent(ABC):
    """
    Agent 基类

    所有 AI Agent 必须继承此类，实现以下核心功能：
    - 任务执行入口
    - 状态管理
    - 错误处理
    """

    def __init__(self):
        self._status = AgentStatus.IDLE
        self._current_task: Optional[AgentContext] = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent 名称"""
        pass

    @property
    @abstractmethod
    def agent_type(self) -> AgentType:
        """Agent 类型"""
        pass

    @property
    def description(self) -> str:
        """Agent 描述"""
        return ""

    @property
    def version(self) -> str:
        """版本号"""
        return "1.0.0"

    @property
    def status(self) -> AgentStatus:
        """当前状态"""
        return self._status

    @property
    def current_task(self) -> Optional[AgentContext]:
        """当前任务"""
        return self._current_task

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        执行任务

        Args:
            context: 执行上下文

        Returns:
            AgentResult 执行结果
        """
        pass

    async def run(self, context: AgentContext) -> AgentResult:
        """
        运行 Agent（带状态管理）

        Args:
            context: 执行上下文

        Returns:
            AgentResult 执行结果
        """
        self._status = AgentStatus.RUNNING
        self._current_task = context

        try:
            result = await self.execute(context)
            self._status = AgentStatus.IDLE
            return result
        except Exception as e:
            self._status = AgentStatus.ERROR
            return AgentResult(
                task_id=context.task_id,
                success=False,
                error=str(e),
                message="执行失败"
            )
        finally:
            self._current_task = None

    def pause(self):
        """暂停 Agent"""
        if self._status == AgentStatus.RUNNING:
            self._status = AgentStatus.PAUSED

    def resume(self):
        """恢复 Agent"""
        if self._status == AgentStatus.PAUSED:
            self._status = AgentStatus.RUNNING

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "type": self.agent_type.value,
            "description": self.description,
            "version": self.version,
            "status": self.status.value,
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name} [{self.status.value}]>"