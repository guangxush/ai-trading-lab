import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || ''

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
})

export interface SearchResult {
  symbol: string
  name: string
  market: string
}

export interface SearchResponse {
  keyword: string
  market: string
  total: number
  results: SearchResult[]
}

export interface QuoteData {
  symbol: string
  name: string
  price: number
  change: number
  change_percent: number
  volume: number
  timestamp: string
}

export interface HistoryData {
  symbol: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  timestamp: string
}

export interface HistoryResponse {
  symbol: string
  market: string
  start: string
  end: string
  total: number
  data: HistoryData[]
}

/**
 * 搜索股票
 */
export const searchStock = async (
  keyword: string,
  market = 'cn'
): Promise<SearchResponse> => {
  const response = await api.get('/api/market/search', {
    params: { keyword, market },
  })
  return response.data
}

/**
 * 获取实时行情
 */
export const getQuote = async (
  symbol: string,
  market = 'cn'
): Promise<QuoteData | null> => {
  try {
    const response = await api.get(`/api/market/quote/${symbol}`, {
      params: { market },
    })
    return response.data
  } catch (error) {
    console.error('获取行情失败:', error)
    return null
  }
}

/**
 * 获取历史K线数据
 */
export const getHistory = async (
  symbol: string,
  startDate: string,
  endDate: string,
  market = 'cn'
): Promise<HistoryResponse> => {
  const response = await api.get(`/api/market/history/${symbol}`, {
    params: {
      start: startDate,
      end: endDate,
      market,
    },
  })
  return response.data
}

/**
 * 获取支持的市场列表
 */
export const getMarkets = async (): Promise<{
  markets: string[]
  default: string
}> => {
  const response = await api.get('/api/market/markets')
  return response.data
}