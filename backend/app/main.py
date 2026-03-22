"""
AI Trading Lab - FastAPI 主入口
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import DEBUG
from .api import api_router
from .core.cache import cache
from .skill.registry import registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("[App] 正在启动...")
    await cache.connect()
    print("[App] 缓存连接成功")

    # 注册内置 SKILL（如果有的话）
    # from skills.examples.stock_analysis.skill import StockAnalysisSkill
    # registry.register(StockAnalysisSkill())

    print(f"[App] 已注册 {registry.count()} 个 SKILL")

    yield

    # 关闭时
    print("[App] 正在关闭...")
    await cache.disconnect()
    print("[App] 已关闭")


# 创建应用
app = FastAPI(
    title="AI Trading Lab",
    description="AI量化交易平台 API",
    version="0.1.0",
    lifespan=lifespan,
    debug=DEBUG
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "AI Trading Lab",
        "version": "0.1.0",
        "docs": "/docs",
        "message": "Welcome to AI Trading Lab!"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "skills_count": registry.count()
    }


if __name__ == "__main__":
    import uvicorn
    from .config import API_HOST, API_PORT

    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG
    )