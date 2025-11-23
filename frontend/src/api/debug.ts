import { api } from './index'

export interface ClearUserDataResponse {
  message: string
  user_id: string
}

export async function clearUserData(): Promise<ClearUserDataResponse> {
  const response = await api.delete<ClearUserDataResponse>('/debug/clear-user-data')
  return response.data
}
