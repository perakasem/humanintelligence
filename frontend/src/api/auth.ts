import { api } from './index'
import type { AuthResponse } from '../types'

export async function googleAuthCallback(credential: string): Promise<AuthResponse> {
  const response = await api.post<AuthResponse>('/auth/google/callback', {
    credential,
  })
  return response.data
}
