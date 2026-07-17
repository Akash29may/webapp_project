import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext.jsx'

/**
 * Route guard. Redirects unauthenticated users to /login and users with the
 * wrong role to their own dashboard.
 */
export default function RequireRole({ role, children }) {
  const { user, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center text-slate-500">
        Loading…
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  if (role && user.role !== role) {
    const dest = user.role === 'teacher' ? '/t' : '/s'
    return <Navigate to={dest} replace />
  }

  return children
}
