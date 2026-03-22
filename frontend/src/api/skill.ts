import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || ''

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
})

export interface SkillInfo {
  name: string
  version: string
  description: string
  author: string
  category: string
  params_schema?: Record<string, unknown>
  versions?: string[]
}

export interface SkillListResponse {
  total: number
  skills: SkillInfo[]
}

export interface ExecuteResult {
  status: 'pending' | 'running' | 'success' | 'failed'
  data?: Record<string, unknown>
  message?: string
  error?: string
}

export interface ExecuteRequest {
  skill_name: string
  user_id: string
  params: Record<string, unknown>
  version?: string
}

/**
 * 获取 SKILL 列表
 */
export const listSkills = async (): Promise<SkillListResponse> => {
  const response = await api.get('/api/skill/list')
  return response.data
}

/**
 * 获取 SKILL 详情
 */
export const getSkillDetail = async (
  name: string,
  version?: string
): Promise<SkillInfo> => {
  const response = await api.get(`/api/skill/${name}`, {
    params: version ? { version } : {},
  })
  return response.data
}

/**
 * 执行 SKILL
 */
export const executeSkill = async (
  request: ExecuteRequest
): Promise<ExecuteResult> => {
  const response = await api.post('/api/skill/execute', request)
  return response.data
}

/**
 * 异步执行 SKILL
 */
export const executeSkillAsync = async (
  request: ExecuteRequest
): Promise<{ task_id: string; message: string }> => {
  const response = await api.post('/api/skill/execute/async', request)
  return response.data
}

/**
 * 获取异步执行结果
 */
export const getAsyncResult = async (
  taskId: string
): Promise<ExecuteResult> => {
  const response = await api.get(`/api/skill/result/${taskId}`)
  return response.data
}