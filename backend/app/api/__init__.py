"""API 路由模块"""
from fastapi import APIRouter
from .market import router as market_router
from .skill import router as skill_router
from .agent import router as agent_router

api_router = APIRouter()
api_router.include_router(market_router)
api_router.include_router(skill_router)
api_router.include_router(agent_router)