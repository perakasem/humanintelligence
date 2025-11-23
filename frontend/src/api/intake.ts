import { api } from './index'
import type { IntakeRequest, IntakeResponse } from '../types'

export async function submitIntake(data: IntakeRequest): Promise<IntakeResponse> {
  const response = await api.post<IntakeResponse>('/intake', data)
  return response.data
}
