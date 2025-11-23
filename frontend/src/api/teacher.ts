import { api } from './index'
import type { TeacherChatRequest, TeacherChatResponse, ChatHistory } from '../types'

export async function sendTeacherMessage(data: TeacherChatRequest): Promise<TeacherChatResponse> {
  const response = await api.post<TeacherChatResponse>('/teacher/chat', data)
  return response.data
}

export async function getChatHistory(limit: number = 20): Promise<{ history: ChatHistory[] }> {
  const response = await api.get<{ history: ChatHistory[] }>('/teacher/history', {
    params: { limit },
  })
  return response.data
}
