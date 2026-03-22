"""SKILL 注册表"""
from typing import Dict, List, Optional

from .base import BaseSkill


class SkillRegistry:
    """
    SKILL 注册表

    管理所有已注册的 SKILL，支持：
    - 注册/注销 SKILL
    - 按名称和版本查找
    - 列出所有 SKILL
    """

    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
        self._latest_versions: Dict[str, str] = {}

    def _make_key(self, name: str, version: str) -> str:
        """生成存储键"""
        return f"{name}@{version}"

    def register(self, skill: BaseSkill) -> None:
        """
        注册 SKILL

        Args:
            skill: SKILL 实例
        """
        key = self._make_key(skill.name, skill.version)
        self._skills[key] = skill

        # 更新最新版本记录
        current_latest = self._latest_versions.get(skill.name)
        if not current_latest or skill.version > current_latest:
            self._latest_versions[skill.name] = skill.version

        print(f"[Registry] 注册 SKILL: {key}")

    def unregister(self, name: str, version: str) -> bool:
        """
        注销 SKILL

        Args:
            name: SKILL 名称
            version: 版本号

        Returns:
            是否成功注销
        """
        key = self._make_key(name, version)
        if key in self._skills:
            del self._skills[key]

            # 如果是最新版本，需要更新
            if self._latest_versions.get(name) == version:
                del self._latest_versions[name]
                # 找到新的最新版本
                versions = [v for k, v in
                           [k.split("@") for k in self._skills if k.startswith(f"{name}@")]]
                if versions:
                    self._latest_versions[name] = max(versions)

            return True
        return False

    def get(self, name: str, version: Optional[str] = None) -> Optional[BaseSkill]:
        """
        获取 SKILL

        Args:
            name: SKILL 名称
            version: 版本号，为 None 时返回最新版本

        Returns:
            SKILL 实例或 None
        """
        if version:
            key = self._make_key(name, version)
            return self._skills.get(key)

        # 返回最新版本
        latest = self._latest_versions.get(name)
        if latest:
            return self._skills.get(self._make_key(name, latest))
        return None

    def list_all(self) -> List[Dict]:
        """列出所有 SKILL 基本信息列表"""
        seen = set()
        result = []
        for skill in self._skills.values():
            if skill.name not in seen:
                seen.add(skill.name)
                result.append(skill.to_dict())
        return result

    def list_versions(self, name: str) -> List[str]:
        """列出指定 SKILL 的所有版本"""
        versions = []
        for key in self._skills:
            if key.startswith(f"{name}@"):
                version = key.split("@")[1]
                versions.append(version)
        return sorted(versions)

    def count(self) -> int:
        """统计 SKILL 数量（按名称去重）"""
        return len(self._latest_versions)


# 全局注册表实例
registry = SkillRegistry()