import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import api from '../api.js'
import { useAuth } from '../auth/AuthContext.jsx'
import { ErrorBox } from '../components/ui.jsx'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const { setUser } = useAuth()
  const navigate = useNavigate()

  const login = useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/auth/login/', { username, password })
      return data
    },
    onSuccess: (user) => {
      setUser(user)
      navigate(user.role === 'teacher' ? '/t' : '/s', { replace: true })
    },
  })

  const onSubmit = (e) => {
    e.preventDefault()
    login.mutate()
  }

  return (
    <div className="mx-auto max-w-md py-8">
      <div className="card">
        <h1 className="text-xl font-bold text-slate-900">Log in</h1>
        <p className="mt-1 text-sm text-slate-500">Welcome back to SmartExam AI.</p>

        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <div>
            <label className="label" htmlFor="username">
              Username
            </label>
            <input
              id="username"
              name="username"
              className="input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
            />
          </div>
          <div>
            <label className="label" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>

          {login.isError && <ErrorBox error={login.error} />}

          <button type="submit" className="btn-primary w-full" disabled={login.isPending}>
            {login.isPending ? 'Signing in…' : 'Log in'}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-slate-500">
          No account?{' '}
          <Link to="/register" className="font-medium text-brand-600 hover:underline">
            Register
          </Link>
        </p>
      </div>
    </div>
  )
}
