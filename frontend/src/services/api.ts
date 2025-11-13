import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface AdCapture {
  id: number
  uuid: string
  keyword: string
  location?: string
  device_type?: string
  advertiser_domain?: string
  advertiser_name?: string
  display_url?: string
  final_url?: string
  landing_page_url?: string
  ad_position?: number
  is_top_ad: boolean
  captured_at: string
  created_at: string
  source?: string
  headlines: AdHeadline[]
  descriptions: AdDescription[]
  extensions: AdExtension[]
}

export interface AdHeadline {
  id: number
  headline_text: string
  position?: number
  character_count?: number
}

export interface AdDescription {
  id: number
  description_text: string
  position?: number
  character_count?: number
}

export interface AdExtension {
  id: number
  extension_type: string
  extension_text?: string
  extension_url?: string
}

export interface Keyword {
  id: number
  keyword_text: string
  location?: string
  device_type?: string
  is_active: boolean
  check_interval_hours: number
  last_checked_at?: string
  last_check_status?: string
  created_at: string
  notes?: string
  tags?: string[]
  total_checks: number
  total_ads_found: number
}

export interface Analysis {
  id: number
  analysis_type: string
  keywords?: string[]
  competitors?: string[]
  summary?: string
  total_ads_analyzed?: number
  total_headlines_analyzed?: number
  total_descriptions_analyzed?: number
  created_at: string
  completed_at?: string
  status: string
  insights: AnalysisInsight[]
}

export interface AnalysisInsight {
  id: number
  insight_type: string
  category: string
  title: string
  description: string
  examples?: any[]
  metrics?: Record<string, any>
  priority: string
  confidence_score?: number
  recommendations?: string[]
}

export interface ChatSession {
  id: number
  session_name?: string
  context_keywords?: string[]
  is_active: boolean
  created_at: string
  total_messages: number
  messages: ChatMessage[]
}

export interface ChatMessage {
  id: number
  session_id: number
  role: string
  content: string
  created_at: string
}

// API Functions

// Ads
export const searchAds = async (params: {
  keyword?: string
  location?: string
  device_type?: string
  advertiser?: string
  limit?: number
  offset?: number
}) => {
  const { data } = await api.get('/ads/', { params })
  return data
}

export const getAdStats = async () => {
  const { data } = await api.get('/ads/stats/overview')
  return data
}

export const captureAd = async (adData: any) => {
  const { data } = await api.post('/ads/capture', adData)
  return data
}

// Keywords
export const getKeywords = async (activeOnly = true) => {
  const { data } = await api.get('/keywords/', { params: { active_only: activeOnly } })
  return data
}

export const createKeyword = async (keywordData: {
  keyword_text: string
  location?: string
  device_type?: string
  check_interval_hours?: number
  notes?: string
}) => {
  const { data } = await api.post('/keywords/', keywordData)
  return data
}

export const updateKeyword = async (id: number, keywordData: Partial<Keyword>) => {
  const { data } = await api.put(`/keywords/${id}`, keywordData)
  return data
}

export const deleteKeyword = async (id: number) => {
  const { data } = await api.delete(`/keywords/${id}`)
  return data
}

// Analysis
export const createAnalysis = async (analysisData: {
  analysis_type: string
  keywords?: string[]
  competitors?: string[]
  date_from?: string
  date_to?: string
}) => {
  const { data } = await api.post('/analysis/', analysisData)
  return data
}

export const getAnalysis = async (id: number) => {
  const { data } = await api.get(`/analysis/${id}`)
  return data
}

// Chat
export const sendChatMessage = async (messageData: {
  session_id?: number
  message: string
  context_keywords?: string[]
}) => {
  const { data } = await api.post('/chat/message', messageData)
  return data
}

export const getChatSessions = async () => {
  const { data } = await api.get('/chat/sessions')
  return data
}

export const getChatSession = async (id: number) => {
  const { data } = await api.get(`/chat/sessions/${id}`)
  return data
}

export const createChatSession = async (sessionData: {
  session_name?: string
  context_keywords?: string[]
}) => {
  const { data } = await api.post('/chat/sessions', sessionData)
  return data
}
