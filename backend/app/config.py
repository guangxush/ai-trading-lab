"""配置管理"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# API 配置
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/data/trading.db")

# Redis 配置
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# 数据源配置
DATA_CACHE_TTL = int(os.getenv("DATA_CACHE_TTL", 60))  # 秒

# SKILL 配置
SKILL_DIR = Path(os.getenv("SKILL_DIR", BASE_DIR.parent / "skills"))