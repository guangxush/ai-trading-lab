"""SKILL Marketplace API 路由"""
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..skill.marketplace import marketplace, SkillMeta, SkillUpload, SkillRating

router = APIRouter(prefix="/api/skill/marketplace", tags=["skill-marketplace"])


class SkillListResponse(BaseModel):
    """SKILL 列表响应"""
    total: int
    skills: List[SkillMeta]
    categories: List[dict]
    popular_tags: List[dict]


class UploadRequest(BaseModel):
    """上传请求"""
    name: str = Field(..., min_length=1, max_length=50)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    description: str = Field(default="", max_length=500)
    author: str = Field(default="")
    category: str = Field(default="general")
    tags: List[str] = Field(default_factory=list)
    code: str = Field(..., min_length=1)


class RatingRequest(BaseModel):
    """评分请求"""
    skill_id: str
    score: int = Field(..., ge=1, le=5)
    comment: str = Field(default="", max_length=200)


@router.get("/list")
async def list_skills(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("downloads", enum=["downloads", "rating", "updated"]),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    列出市场中的 SKILL

    - **category**: 分类筛选
    - **tag**: 标签筛选
    - **search**: 搜索关键词
    - **sort_by**: 排序方式
    - **limit**: 返回数量
    - **offset**: 偏移量
    """
    skills = marketplace.list_skills(
        category=category,
        tag=tag,
        search=search,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )

    return {
        "total": len(skills),
        "skills": [s.model_dump() for s in skills],
        "categories": marketplace.get_categories(),
        "popular_tags": marketplace.get_popular_tags(),
    }


@router.get("/stats")
async def get_stats():
    """获取市场统计"""
    return marketplace.get_stats()


@router.get("/categories")
async def get_categories():
    """获取分类列表"""
    return marketplace.get_categories()


@router.get("/tags")
async def get_tags(limit: int = 20):
    """获取热门标签"""
    return marketplace.get_popular_tags(limit)


@router.get("/{skill_id}")
async def get_skill(skill_id: str):
    """获取 SKILL 详情"""
    skill = marketplace.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="SKILL 未找到")

    return skill.model_dump()


@router.get("/{skill_id}/code")
async def get_skill_code(skill_id: str):
    """获取 SKILL 代码"""
    code = marketplace.download_skill(skill_id)
    if not code:
        raise HTTPException(status_code=404, detail="SKILL 代码未找到")

    return {
        "skill_id": skill_id,
        "code": code
    }


@router.post("/upload")
async def upload_skill(request: UploadRequest, user_id: str = "anonymous"):
    """
    上传 SKILL

    - **name**: SKILL 名称
    - **version**: 版本号 (语义化版本)
    - **description**: 描述
    - **category**: 分类
    - **tags**: 标签列表
    - **code**: Python 代码
    """
    # 验证代码基本格式
    if "class" not in request.code or "BaseSkill" not in request.code:
        raise HTTPException(status_code=400, detail="代码必须包含继承 BaseSkill 的类")

    upload = SkillUpload(**request.model_dump())
    skill = marketplace.upload_skill(upload, user_id)

    return {
        "success": True,
        "skill": skill.model_dump(),
        "message": "SKILL 上传成功"
    }


@router.post("/{skill_id}/rate")
async def rate_skill(skill_id: str, request: RatingRequest, user_id: str = "anonymous"):
    """
    评分 SKILL

    - **score**: 评分 (1-5)
    - **comment**: 评论
    """
    # 检查 SKILL 是否存在
    skill = marketplace.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="SKILL 未找到")

    rating = marketplace.rate_skill(
        skill_id=skill_id,
        user_id=user_id,
        score=request.score,
        comment=request.comment
    )

    return {
        "success": True,
        "rating": rating.model_dump(),
        "message": "评分成功"
    }


@router.get("/{skill_id}/ratings")
async def get_ratings(skill_id: str):
    """获取 SKILL 的所有评分"""
    ratings = marketplace.get_ratings(skill_id)

    return {
        "total": len(ratings),
        "ratings": [r.model_dump() for r in ratings]
    }