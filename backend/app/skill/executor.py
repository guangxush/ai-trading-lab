"""SKILL 执行器"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional

from .base import BaseSkill, SkillContext, SkillResult, SkillStatus
from .registry import registry


class SkillExecutor:
    """
    SKILL 执行器

    负责 SKILL 的执行管理：
    - 同步/异步执行
    - 任务追踪
    - 超时控制
    """

    def __init__(self):
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._results: Dict[str, SkillResult] = {}

    async def execute(
        self,
        skill_name: str,
        context: SkillContext,
        version: Optional[str] = None,
        timeout: float = 300.0
    ) -> SkillResult:
        """
        执行 SKILL

        Args:
            skill_name: SKILL 名称
            context: 执行上下文
            version: 版本号
            timeout: 超时时间（秒）

        Returns:
            SkillResult
        """
        # 查找 SKILL
        skill = registry.get(skill_name, version)
        if not skill:
            return SkillResult(
                status=SkillStatus.FAILED,
                error=f"SKILL 未找到: {skill_name}"
            )

        # 参数校验
        if not skill.validate(context.params):
            return SkillResult(
                status=SkillStatus.FAILED,
                error="参数校验失败，缺少必要参数"
            )

        # 执行
        start_time = datetime.now()
        try:
            result = await asyncio.wait_for(
                skill.execute(context),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            return SkillResult(
                status=SkillStatus.FAILED,
                error=f"执行超时（>{timeout}秒）"
            )
        except Exception as e:
            return SkillResult(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    async def execute_async(
        self,
        skill_name: str,
        context: SkillContext,
        version: Optional[str] = None
    ) -> str:
        """
        异步执行 SKILL

        Args:
            skill_name: SKILL 名称
            context: 执行上下文
            version: 版本号

        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())

        async def _run():
            result = await self.execute(skill_name, context, version)
            self._results[task_id] = result
            return result

        task = asyncio.create_task(_run())
        self._running_tasks[task_id] = task

        return task_id

    async def get_result(self, task_id: str) -> Optional[SkillResult]:
        """
        获取异步执行结果

        Args:
            task_id: 任务ID

        Returns:
            SkillResult 或 None
        """
        # 如果已有结果，直接返回
        if task_id in self._results:
            return self._results[task_id]

        # 检查任务状态
        task = self._running_tasks.get(task_id)
        if not task:
            return SkillResult(
                status=SkillStatus.FAILED,
                error=f"任务未找到: {task_id}"
            )

        if not task.done():
            return SkillResult(status=SkillStatus.RUNNING)

        # 任务完成，获取结果
        try:
            result = task.result()
            self._results[task_id] = result
            return result
        except Exception as e:
            return SkillResult(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def cancel(self, task_id: str) -> bool:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功取消
        """
        task = self._running_tasks.get(task_id)
        if task and not task.done():
            task.cancel()
            return True
        return False

    def clear_completed(self):
        """清理已完成的任务"""
        completed = [
            tid for tid, task in self._running_tasks.items()
            if task.done()
        ]
        for tid in completed:
            del self._running_tasks[tid]


# 全局执行器实例
executor = SkillExecutor()