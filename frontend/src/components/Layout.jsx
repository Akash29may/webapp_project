import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import api from '../api.js'
import { useAuth } from '../auth/AuthContext.jsx'

export default function Layout() {
  const { user, setUser } = useAuth()
  const navigate = useNavigate()

  const logout = useMutation({
    mutationFn: () => api.post('/auth/logout/'),
    onSuccess: () => {
      setUser(null)
      navigate('/login')
    },
  })

  const homePath = user ? (user.role === 'teacher' ? '/t' : '/s') : '/'

  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <Link to={homePath} className="flex items-center gap-2 font-bold text-brand-700">
            <span className="grid h-8 w-8 place-items-center rounded-lg bg-brand-600 text-white">
              S
            </span>
            SmartExam AI
          </Link>
          <nav className="flex items-center gap-3 text-sm">
            {user ? (
              <>
                {user.role === 'teacher' && (
                  <NavLink to="/t" className="text-slate-600 hover:text-brand-700">
                    Dashboard
                  </NavLink>
                )}
                {user.role === 'student' && (
                  <NavLink to="/s" className="text-slate-600 hover:text-brand-700">
                    Dashboard
                  </NavLink>
                )}
                <span className="hidden text-slate-500 sm:inline">
                  {user.first_name || user.username}{' '}
                  <span className="badge bg-slate-100 text-slate-600">{user.role}</span>
                </span>
                <button
                  className="btn-secondary"
                  onClick={() => logout.mutate()}
                  disabled={logout.isPending}
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login" className="text-slate-600 hover:text-brand-700">
                  Login
                </NavLink>
                <Link to="/register" className="btn-primary">
                  Sign up
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6">
        <Outlet />
      </main>

      <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-400">
        SmartExam AI — built with React + Vite
      </footer>
    </div>
  )
}
