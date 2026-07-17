import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'

// Control the auth state directly.
let mockAuth = { user: null, isLoading: false }
vi.mock('../auth/AuthContext.jsx', () => ({
  useAuth: () => mockAuth,
}))

import RequireRole from '../auth/RequireRole.jsx'

function renderAt(entry) {
  return render(
    <MemoryRouter initialEntries={[entry]}>
      <Routes>
        <Route
          path="/t"
          element={
            <RequireRole role="teacher">
              <div>teacher area</div>
            </RequireRole>
          }
        />
        <Route path="/login" element={<div>login page</div>} />
        <Route path="/s" element={<div>student dashboard</div>} />
      </Routes>
    </MemoryRouter>
  )
}

describe('RequireRole', () => {
  it('redirects unauthenticated users to /login', () => {
    mockAuth = { user: null, isLoading: false }
    renderAt('/t')
    expect(screen.getByText('login page')).toBeInTheDocument()
    expect(screen.queryByText('teacher area')).not.toBeInTheDocument()
  })

  it('redirects wrong-role users to their own dashboard', () => {
    mockAuth = { user: { id: 1, role: 'student' }, isLoading: false }
    renderAt('/t')
    expect(screen.getByText('student dashboard')).toBeInTheDocument()
    expect(screen.queryByText('teacher area')).not.toBeInTheDocument()
  })

  it('renders children for the correct role', () => {
    mockAuth = { user: { id: 1, role: 'teacher' }, isLoading: false }
    renderAt('/t')
    expect(screen.getByText('teacher area')).toBeInTheDocument()
  })
})
