"""SKILL Marketplace 模块"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import shutil

from ..config import SKILL_DIR
from .registry import registry


class SkillMeta(BaseModel):
    """SKILL 元数据"""
    id: str = Field(..., description="SKILL ID")
    name: str
    version: str
    description: str = ""
    author: str = "unknown"
    category: str = "general"
    tags: List[str] = Field(default_factory=list)
    params_schema: Dict = Field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""
    downloads: int = 0
    rating: float = 0.0
    rating_count: int = 0
    status: str = "active"  # active/draft/archived


class SkillRating(BaseModel):
    """SKILL 评分"""
    skill_id: str
    user_id: str
    score: int = Field(..., ge=1, le=5)
    comment: str = ""
    created_at: str = ""


class SkillUpload(BaseModel):
    """SKILL 上传请求"""
    name: str
    version: str
    description: str = ""
    author: str = ""
    category: str = "general"
    tags: List[str] = Field(default_factory=list)
    code: str = ""  # Python 代码


class MarketplaceManager:
    """
    SKILL 市场管理器

    负责：
    - SKILL 存储
    - SKILL 发现
    - 评分管理
    - 下载统计
    """

    def __init__(self):
        self._skill_dir = SKILL_DIR
        self._marketplace_dir = SKILL_DIR / "marketplace"
        self._ratings: Dict[str, List[SkillRating]] = {}
        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保目录存在"""
        self._skill_dir.mkdir(parents=True, exist_ok=True)
        self._marketplace_dir.mkdir(parents=True, exist_ok=True)

    def list_skills(
        self,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "downloads",
        limit: int = 20,
        offset: int = 0
    ) -> List[SkillMeta]:
        """列出市场中的 SKILL"""
        skills = []

        # 遍历 marketplace 目录
        if self._marketplace_dir.exists():
            for skill_dir in self._marketplace_dir.iterdir():
                if skill_dir.is_dir():
                    meta_file = skill_dir / "meta.json"
                    if meta_file.exists():
                        try:
                            with open(meta_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                skill = SkillMeta(**data)
                                skills.append(skill)
                        except Exception as e:
                            print(f"加载 SKILL 元数据失败: {skill_dir}: {e}")

        # 过滤
        if category:
            skills = [s for s in skills if s.category == category]
        if tag:
            skills = [s for s in skills if tag in s.tags]
        if search:
            search_lower = search.lower()
            skills = [
                s for s in skills
                if search_lower in s.name.lower()
                or search_lower in s.description.lower()
            ]

        # 排序
        if sort_by == "downloads":
            skills.sort(key=lambda x: x.downloads, reverse=True)
        elif sort_by == "rating":
            skills.sort(key=lambda x: x.rating, reverse=True)
        elif sort_by == "updated":
            skills.sort(key=lambda x: x.updated_at, reverse=True)

        # 分页
        return skills[offset:offset + limit]

    def get_skill(self, skill_id: str) -> Optional[SkillMeta]:
        """获取 SKILL 详情"""
        skill_dir = self._marketplace_dir / skill_id
        meta_file = skill_dir / "meta.json"

        if not meta_file.exists():
            return None

        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return SkillMeta(**data)
        except Exception as e:
            print(f"加载 SKILL 元数据失败: {e}")
            return None

    def upload_skill(self, upload: SkillUpload, user_id: str) -> SkillMeta:
        """上传 SKILL"""
        # 生成 SKILL ID
        skill_id = f"{upload.name}@{upload.version}".replace("/", "_")

        # 创建目录
        skill_dir = self._marketplace_dir / skill_id
        skill_dir.mkdir(parents=True, exist_ok=True)

        # 保存代码
        code_file = skill_dir / "skill.py"
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(upload.code)

        # 创建元数据
        now = datetime.now().isoformat()
        meta = SkillMeta(
            id=skill_id,
            name=upload.name,
            version=upload.version,
            description=upload.description,
            author=upload.author or user_id,
            category=upload.category,
            tags=upload.tags,
            created_at=now,
            updated_at=now,
        )

        # 保存元数据
        meta_file = skill_dir / "meta.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta.model_dump(), f, ensure_ascii=False, indent=2)

        return meta

    def download_skill(self, skill_id: str) -> Optional[str]:
        """下载 SKILL（返回代码）"""
        skill_dir = self._marketplace_dir / skill_id
        code_file = skill_dir / "skill.py"

        if not code_file.exists():
            return None

        # 增加下载计数
        self._increment_downloads(skill_id)

        with open(code_file, 'r', encoding='utf-8') as f:
            return f.read()

    def _increment_downloads(self, skill_id: str):
        """增加下载计数"""
        meta = self.get_skill(skill_id)
        if not meta:
            return

        meta.downloads += 1
        meta_file = self._marketplace_dir / skill_id / "meta.json"

        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta.model_dump(), f, ensure_ascii=False, indent=2)

    def rate_skill(
        self,
        skill_id: str,
        user_id: str,
        score: int,
        comment: str = ""
    ) -> SkillRating:
        """评分 SKILL"""
        now = datetime.now().isoformat()
        rating = SkillRating(
            skill_id=skill_id,
            user_id=user_id,
            score=score,
            comment=comment,
            created_at=now
        )

        # 存储评分
        if skill_id not in self._ratings:
            self._ratings[skill_id] = []
        self._ratings[skill_id].append(rating)

        # 更新平均评分
        self._update_rating(skill_id)

        return rating

    def _update_rating(self, skill_id: str):
        """更新平均评分"""
        ratings = self._ratings.get(skill_id, [])
        if not ratings:
            return

        avg_rating = sum(r.score for r in ratings) / len(ratings)

        meta = self.get_skill(skill_id)
        if not meta:
            return

        meta.rating = round(avg_rating, 1)
        meta.rating_count = len(ratings)

        meta_file = self._marketplace_dir / skill_id / "meta.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta.model_dump(), f, ensure_ascii=False, indent=2)

    def get_ratings(self, skill_id: str) -> List[SkillRating]:
        """获取 SKILL 的所有评分"""
        return self._ratings.get(skill_id, [])

    def get_categories(self) -> List[Dict]:
        """获取分类列表"""
        return [
            {"id": "analysis", "name": "技术分析", "description": "技术指标和趋势分析"},
            {"id": "backtest", "name": "策略回测", "description": "历史数据回测策略"},
            {"id": "trading", "name": "交易策略", "description": "自动交易和信号生成"},
            {"id": "risk", "name": "风险管理", "description": "仓位控制和风险评估"},
            {"id": "general", "name": "通用工具", "description": "其他通用功能"},
        ]

    def get_popular_tags(self, limit: int = 20) -> List[Dict]:
        """获取热门标签"""
        tag_counts: Dict[str, int] = {}

        skills = self.list_skills(limit=1000)
        for skill in skills:
            for tag in skill.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # 排序
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

        return [{"name": tag, "count": count} for tag, count in sorted_tags[:limit]]

    def get_stats(self) -> Dict:
        """获取市场统计"""
        skills = self.list_skills(limit=1000)

        return {
            "total_skills": len(skills),
            "total_downloads": sum(s.downloads for s in skills),
            "categories": len(self.get_categories()),
            "avg_rating": round(
                sum(s.rating for s in skills if s.rating > 0) / len([s for s in skills if s.rating > 0]),
                1
            ) if any(s.rating > 0 for s in skills) else 0,
        }


# 全局实例
marketplace = MarketplaceManager()