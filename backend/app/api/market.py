"""行情相关 API 路由"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, HTTPException

from ..data.gateway import gateway

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/markets")
async def list_markets():
    """列出支持的市场"""
    return {
        "markets": gateway.list_markets(),
        "default": "cn"
    }


@router.get("/search")
async def search_stock(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    market: str = Query("cn", description="市场: cn/us/hk")
):
    """
    搜索股票

    - **keyword**: 股票代码或名称
    - **market**: 市场标识
    """
    try:
        results = await gateway.search(keyword, market)
        return {
            "keyword": keyword,
            "market": market,
            "total": len(results),
            "results": results
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/quote/{symbol}")
async def get_quote(
    symbol: str,
    market: str = Query("cn", description="市场: cn/us/hk")
):
    """
    获取实时行情

    - **symbol**: 股票代码
    - **market**: 市场标识
    """
    try:
        quote = await gateway.get_quote(symbol, market)
        if not quote:
            raise HTTPException(status_code=404, detail=f"未找到股票: {symbol}")
        return quote.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{symbol}")
async def get_history(
    symbol: str,
    start: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end: str = Query(..., description="结束日期 YYYY-MM-DD"),
    market: str = Query("cn", description="市场: cn/us/hk")
):
    """
    获取历史K线数据

    - **symbol**: 股票代码
    - **start**: 开始日期
    - **end**: 结束日期
    - **market**: 市场标识
    """
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，应为 YYYY-MM-DD")

    try:
        history = await gateway.get_history(symbol, start_dt, end_dt, market)
        return {
            "symbol": symbol,
            "market": market,
            "start": start,
            "end": end,
            "total": len(history),
            "data": [h.model_dump() for h in history]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))