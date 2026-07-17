import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Mock the api module used by both Login and AuthContext.
vi.mock('../api.js', () => {
  return {
    default: { post: vi.fn(), get: vi.fn() },
    ensureCsrf: vi.fn().mockResolvedValue(undefined),
    getCookie: vi.fn(),
  }
})

import api from '../api.js'
import Login from '../pages/Login.jsx'
import { AuthProvider } from '../auth/AuthContext.jsx'

function renderLogin() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={['/login']}>
        <AuthProvider>
          <Login />
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('Login page', () => {
  beforeEach(() => {
    api.post.mockReset()
    api.get.mockReset()
    // /auth/me/ -> not logged in
    api.get.mockResolvedValue({ data: null })
  })

  it('renders the login form', () => {
    renderLogin()
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument()
  })

  it('calls the login mutation with credentials on submit', async () => {
    api.post.mockResolvedValue({
      data: { id: 1, username: 'alice', role: 'teacher', first_name: 'Alice' },
    })
    renderLogin()

    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: 'alice' } })
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'secret' } })
    fireEvent.click(screen.getByRole('button', { name: /log in/i }))

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/auth/login/', {
        username: 'alice',
        password: 'secret',
      })
    })
  })
})
