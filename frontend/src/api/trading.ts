import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || ''

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
})

// ===== 账户相关 =====

export interface AccountInfo {
  account_balance: number
  available_balance: number
  total_position_value: number
  total_assets: number
  position_count: number
  order_count: number
}

export const getAccount = async (): Promise<AccountInfo> => {
  const response = await api.get('/api/agent/trading/account')
  return response.data.data
}

// ===== 持仓相关 =====

export interface Position {
  symbol: string
  market: string
  shares: number
  avg_cost: number
  current_price: number
  market_value: number
  profit_loss: number
  profit_loss_percent: number
}

export interface PositionsResponse {
  positions: Position[]
  total_market_value: number
  total_profit_loss: number
  cash_balance: number
  total_assets: number
}

export const getPositions = async (): Promise<PositionsResponse> => {
  const response = await api.get('/api/agent/trading/positions')
  return response.data.data
}

// ===== 订单相关 =====

export interface Order {
  order_id: string
  symbol: string
  market: string
  side: string
  type: string
  shares: number
  price: number | null
  stop_price: number | null
  status: string
  filled_shares: number
  filled_price: number
  created_at: string
  updated_at: string
  message: string
}

export interface CreateOrderParams {
  symbol: string
  side: 'buy' | 'sell'
  shares: number
  order_type?: 'market' | 'limit'
  price?: number
  market?: string
}

export const createOrder = async (params: CreateOrderParams): Promise<Order> => {
  const response = await api.post('/api/agent/trading/order', null, { params })
  return response.data.data?.order
}

export const getOrders = async (status?: string, symbol?: string): Promise<Order[]> => {
  const response = await api.get('/api/agent/trading/orders', {
    params: { status, symbol }
  })
  return response.data.data?.orders || []
}

// ===== 交易历史 =====

export interface TradeHistory {
  timestamp: string
  order_id: string
  symbol: string
  side: string
  shares: number
  price: number
  amount: number
}

export const getTradeHistory = async (limit = 50): Promise<TradeHistory[]> => {
  const response = await api.get('/api/agent/trading/history', {
    params: { limit }
  })
  return response.data.data?.history || []
}

// ===== 风险管理 =====

export interface RiskAlert {
  risk_type: string
  level: string
  symbol: string | null
  message: string
  value: number
  threshold: number
  recommendation: string
}

export interface RiskAssessment {
  risk_level: string
  alerts: RiskAlert[]
  recommendations: string[]
}

export const assessRisk = async (): Promise<RiskAssessment> => {
  const response = await api.post('/api/agent/risk/assess')
  return response.data.data
}

export interface RiskConfig {
  max_position_percent: number
  max_single_loss_percent: number
  max_total_loss_percent: number
  max_concentration_percent: number
  stop_loss_percent: number
  take_profit_percent: number
}

export const getRiskConfig = async (): Promise<RiskConfig> => {
  const response = await api.get('/api/agent/risk/config')
  return response.data.data
}

export interface PortfolioAnalysis {
  total_value: number
  position_count: number
  total_profit: number
  total_profit_percent: number
  diversification_score: number
  largest_position: string
  best_performer: string
  worst_performer: string
}

export const analyzePortfolio = async (): Promise<PortfolioAnalysis> => {
  const response = await api.get('/api/agent/risk/portfolio')
  return response.data.data
}