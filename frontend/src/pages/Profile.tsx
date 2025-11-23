import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getProfile, updateProfile } from '../api'
import {
  GENDER_OPTIONS,
  YEAR_OPTIONS,
  MAJOR_OPTIONS,
  PAYMENT_OPTIONS,
} from '../types'

export default function Profile() {
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
    year_in_school: '',
    major: '',
    preferred_payment_method: '',
  })

  const { data, isLoading, error } = useQuery({
    queryKey: ['profile'],
    queryFn: getProfile,
  })

  const mutation = useMutation({
    mutationFn: updateProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] })
      setIsEditing(false)
    },
  })

  useEffect(() => {
    if (data) {
      setFormData({
        age: data.age?.toString() || '',
        gender: data.gender?.toString() || '',
        year_in_school: data.year_in_school?.toString() || '',
        major: data.major?.toString() || '',
        preferred_payment_method: data.preferred_payment_method?.toString() || '',
      })
    }
  }, [data])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate({
      age: formData.age ? parseInt(formData.age) : null,
      gender: formData.gender ? parseInt(formData.gender) : null,
      year_in_school: formData.year_in_school ? parseInt(formData.year_in_school) : null,
      major: formData.major ? parseInt(formData.major) : null,
      preferred_payment_method: formData.preferred_payment_method ? parseInt(formData.preferred_payment_method) : null,
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load profile data.</p>
      </div>
    )
  }

  const getLabel = (value: number | null, options: { value: string; label: string }[]) => {
    if (value === null) return 'Not set'
    const option = options.find(o => o.value === value.toString())
    return option?.label || 'Unknown'
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Your Profile</h1>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="btn btn-primary"
          >
            Edit Profile
          </button>
        )}
      </div>

      {isEditing ? (
        <form onSubmit={handleSubmit} className="card space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Age
            </label>
            <input
              type="number"
              min="16"
              max="100"
              value={formData.age}
              onChange={(e) => setFormData({ ...formData, age: e.target.value })}
              className="input"
              placeholder="Enter your age"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Gender
            </label>
            <select
              value={formData.gender}
              onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
              className="input"
            >
              <option value="">Select...</option>
              {GENDER_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Year in School
            </label>
            <select
              value={formData.year_in_school}
              onChange={(e) => setFormData({ ...formData, year_in_school: e.target.value })}
              className="input"
            >
              <option value="">Select...</option>
              {YEAR_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Major
            </label>
            <select
              value={formData.major}
              onChange={(e) => setFormData({ ...formData, major: e.target.value })}
              className="input"
            >
              <option value="">Select...</option>
              {MAJOR_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Preferred Payment Method
            </label>
            <select
              value={formData.preferred_payment_method}
              onChange={(e) => setFormData({ ...formData, preferred_payment_method: e.target.value })}
              className="input"
            >
              <option value="">Select...</option>
              {PAYMENT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex gap-3 justify-end pt-4">
            <button
              type="button"
              onClick={() => setIsEditing(false)}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="btn btn-primary disabled:opacity-50"
            >
              {mutation.isPending ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      ) : (
        <div className="card space-y-4">
          <div className="flex justify-between py-3 border-b border-gray-100">
            <span className="text-gray-600">Age</span>
            <span className="font-medium text-gray-900">
              {data?.age || 'Not set'}
            </span>
          </div>
          <div className="flex justify-between py-3 border-b border-gray-100">
            <span className="text-gray-600">Gender</span>
            <span className="font-medium text-gray-900">
              {getLabel(data?.gender ?? null, GENDER_OPTIONS)}
            </span>
          </div>
          <div className="flex justify-between py-3 border-b border-gray-100">
            <span className="text-gray-600">Year in School</span>
            <span className="font-medium text-gray-900">
              {getLabel(data?.year_in_school ?? null, YEAR_OPTIONS)}
            </span>
          </div>
          <div className="flex justify-between py-3 border-b border-gray-100">
            <span className="text-gray-600">Major</span>
            <span className="font-medium text-gray-900">
              {getLabel(data?.major ?? null, MAJOR_OPTIONS)}
            </span>
          </div>
          <div className="flex justify-between py-3">
            <span className="text-gray-600">Preferred Payment</span>
            <span className="font-medium text-gray-900">
              {getLabel(data?.preferred_payment_method ?? null, PAYMENT_OPTIONS)}
            </span>
          </div>
        </div>
      )}

      <p className="text-sm text-gray-500">
        These fields are only collected during your initial onboarding. Weekly check-ins will only ask about your current financial situation.
      </p>
    </div>
  )
}
