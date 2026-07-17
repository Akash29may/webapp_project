import { createContext, useContext, useEffect } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import api, { ensureCsrf } from '../api.js'

const AuthContext = createContext(null)

async function fetchMe() {
  try {
    const { data } = await api.get('/auth/me/')
    return data
  } catch (err) {
    if (err?.response?.status === 403 || err?.response?.status === 401) {
      return null
    }
    throw err
  }
}

export function AuthProvider({ children }) {
  const queryClient = useQueryClient()

  // Make sure the CSRF cookie exists before any unsafe request.
  useEffect(() => {
    ensureCsrf().catch(() => {})
  }, [])

  const {
    data: user,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['me'],
    queryFn: fetchMe,
    staleTime: 60_000,
  })

  const value = {
    user: user || null,
    isLoading,
    isError,
    isAuthenticated: !!user,
    setUser: (u) => queryClient.setQueryData(['me'], u),
    refetchUser: () => queryClient.invalidateQueries({ queryKey: ['me'] }),
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider')
  return ctx
}
