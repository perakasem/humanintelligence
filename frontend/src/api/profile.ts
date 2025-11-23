import { api } from './index'

export interface ProfileData {
  age: number | null
  gender: number | null
  year_in_school: number | null
  major: number | null
  preferred_payment_method: number | null
}

export interface ProfileResponse extends ProfileData {
  has_profile: boolean
}

export async function getProfile(): Promise<ProfileResponse> {
  const response = await api.get<ProfileResponse>('/profile')
  return response.data
}

export async function updateProfile(data: Partial<ProfileData>): Promise<ProfileResponse> {
  const response = await api.put<ProfileResponse>('/profile', data)
  return response.data
}
