"""SKILL 基类定义"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SkillStatus(str, Enum):
    """SKILL 执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class SkillContext(BaseModel):
    """SKILL 执行上下文"""
    user_id: str = Field(..., description="用户ID")
    params: Dict[str, Any] = Field(default_factory=dict, description="执行参数")
    market_data: Optional[Dict[str, Any]] = Field(default=None, description="市场数据")
    user_data: Optional[Dict[str, Any]] = Field(default=None, description="用户数据")


class SkillResult(BaseModel):
    """SKILL 执行结果"""
    status: SkillStatus = Field(..., description="执行状态")
    data: Optional[Dict[str, Any]] = Field(default=None, description="返回数据")
    message: Optional[str] = Field(default=None, description="消息")
    error: Optional[str] = Field(default=None, description="错误信息")


class BaseSkill(ABC):
    """
    SKILL 基类

    所有策略插件必须继承此类，并实现以下方法：
    - name: 技能名称
    - version: 版本号
    - execute: 执行入口
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """技能名称（唯一标识）"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """版本号（语义化版本）"""
        pass

    @property
    def description(self) -> str:
        """技能描述"""
        return ""

    @property
    def author(self) -> str:
        """作者"""
        return "unknown"

    @property
    def category(self) -> str:
        """分类: analysis/backtest/trading/risk"""
        return "general"

    @property
    def params_schema(self) -> Dict[str, Any]:
        """
        参数校验 schema

        格式:
        {
            "required": ["symbol"],
            "properties": {
                "symbol": {"type": "string", "description": "股票代码"},
                "days": {"type": "integer", "default": 30}
            }
        }
        """
        return {}

    @abstractmethod
    async def execute(self, context: SkillContext) -> SkillResult:
        """
        执行入口

        Args:
            context: 执行上下文

        Returns:
            SkillResult 执行结果
        """
        pass

    def validate(self, params: Dict[str, Any]) -> bool:
        """
        参数校验

        Args:
            params: 参数字典

        Returns:
            是否通过校验
        """
        required = self.params_schema.get("required", [])
        return all(k in params for k in required)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "category": self.category,
            "params_schema": self.params_schema
        }

    def __repr__(self) -> str:
        return f"<Skill {self.name} v{self.version}>"