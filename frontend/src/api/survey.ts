import { api } from './index'

export interface ConversationMessage {
  role: 'assistant' | 'user'
  content: string
  field?: string
}

export interface NextQuestionRequest {
  conversation: ConversationMessage[]
  collected_fields: string[]
}

export interface NextQuestionResponse {
  field: string | null
  question: string | null
  context: string | null
  is_complete: boolean
  suggested_type: string | null
  options: string[] | null
  progress: number
}

export async function getNextQuestion(data: NextQuestionRequest): Promise<NextQuestionResponse> {
  const response = await api.post<NextQuestionResponse>('/survey/next-question', data)
  return response.data
}
