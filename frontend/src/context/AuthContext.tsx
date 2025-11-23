import { createContext, useState, useEffect, useCallback } from 'react'
import type { User } from '../types'
import { googleAuthCallback } from '../api'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  isNewUser: boolean
  login: (credential: string) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isNewUser, setIsNewUser] = useState(false)

  // Load user from localStorage on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user')
    const token = localStorage.getItem('auth_token')

    if (storedUser && token) {
      setUser(JSON.parse(storedUser))
    }
    setIsLoading(false)
  }, [])

  const login = useCallback(async (credential: string) => {
    try {
      setIsLoading(true)
      const response = await googleAuthCallback(credential)

      // Store auth data
      localStorage.setItem('auth_token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))

      setUser(response.user)
      setIsNewUser(response.is_new_user)
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
    setUser(null)
    setIsNewUser(false)
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        isNewUser,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
