"""SKILL 相关 API 路由"""
from typing import Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..skill.base import SkillContext, SkillResult
from ..skill.registry import registry
from ..skill.executor import executor

router = APIRouter(prefix="/api/skill", tags=["skill"])


class ExecuteRequest(BaseModel):
    """执行请求"""
    skill_name: str = Field(..., description="SKILL 名称")
    user_id: str = Field(..., description="用户ID")
    params: dict = Field(default_factory=dict, description="执行参数")
    version: Optional[str] = Field(None, description="版本号")


class ExecuteResponse(BaseModel):
    """执行响应"""
    task_id: str = Field(..., description="任务ID")
    message: str = Field(..., description="消息")


@router.get("/list")
async def list_skills():
    """列出所有 SKILL"""
    skills = registry.list_all()
    return {
        "total": len(skills),
        "skills": skills
    }


@router.get("/{name}")
async def get_skill(name: str, version: Optional[str] = None):
    """
    获取 SKILL 详情

    - **name**: SKILL 名称
    - **version**: 版本号（可选）
    """
    skill = registry.get(name, version)
    if not skill:
        raise HTTPException(status_code=404, detail=f"SKILL 未找到: {name}")

    info = skill.to_dict()
    info["versions"] = registry.list_versions(name)
    return info


@router.post("/execute")
async def execute_skill(request: ExecuteRequest):
    """
    同步执行 SKILL

    等待执行完成后返回结果
    """
    context = SkillContext(
        user_id=request.user_id,
        params=request.params
    )

    result = await executor.execute(
        request.skill_name,
        context,
        request.version
    )

    return result.model_dump()


@router.post("/execute/async")
async def execute_skill_async(request: ExecuteRequest):
    """
    异步执行 SKILL

    返回任务ID，可通过 /result/{task_id} 查询结果
    """
    context = SkillContext(
        user_id=request.user_id,
        params=request.params
    )

    task_id = await executor.execute_async(
        request.skill_name,
        context,
        request.version
    )

    return {
        "task_id": task_id,
        "message": "任务已提交"
    }


@router.get("/result/{task_id}")
async def get_result(task_id: str):
    """
    获取异步执行结果

    - **task_id**: 任务ID
    """
    result = await executor.get_result(task_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"任务未找到: {task_id}")

    return result.model_dump()


@router.delete("/task/{task_id}")
async def cancel_task(task_id: str):
    """取消任务"""
    success = executor.cancel(task_id)
    if not success:
        raise HTTPException(status_code=400, detail="无法取消任务（可能已完成或不存在）")

    return {"message": "任务已取消"}