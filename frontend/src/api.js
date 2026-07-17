import axios from 'axios'

/**
 * Read a cookie value by name. Used to pull the Django `csrftoken` cookie.
 */
export function getCookie(name) {
  const match = document.cookie.match(
    new RegExp('(?:^|; )' + name.replace(/([.$?*|{}()[\]\\/+^])/g, '\\$1') + '=([^;]*)')
  )
  return match ? decodeURIComponent(match[1]) : null
}

const UNSAFE_METHODS = ['post', 'put', 'patch', 'delete']

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
})

// Attach the CSRF token from the csrftoken cookie on unsafe methods.
api.interceptors.request.use((config) => {
  const method = (config.method || 'get').toLowerCase()
  if (UNSAFE_METHODS.includes(method)) {
    const token = getCookie('csrftoken')
    if (token) {
      config.headers = config.headers || {}
      config.headers['X-CSRFToken'] = token
    }
  }
  return config
})

/**
 * Ensure the csrftoken cookie is set. Call once on app load.
 */
export async function ensureCsrf() {
  await api.get('/auth/csrf/')
}

export default api
