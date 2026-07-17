import { describe, it, expect, beforeEach } from 'vitest'
import api, { getCookie } from '../api.js'

// A stub adapter that resolves with the (post-interceptor) request config so we
// can inspect the headers axios computed.
function installEchoAdapter() {
  api.defaults.adapter = async (config) => ({
    data: config,
    status: 200,
    statusText: 'OK',
    headers: {},
    config,
  })
}

function setCookie(value) {
  Object.defineProperty(document, 'cookie', {
    configurable: true,
    get: () => value,
  })
}

describe('api CSRF interceptor', () => {
  beforeEach(() => {
    installEchoAdapter()
  })

  it('reads a cookie value by name', () => {
    setCookie('foo=1; csrftoken=abc123; bar=2')
    expect(getCookie('csrftoken')).toBe('abc123')
    expect(getCookie('missing')).toBeNull()
  })

  it('attaches X-CSRFToken header on POST from the csrftoken cookie', async () => {
    setCookie('csrftoken=tok-POST')
    const res = await api.post('/thing/', { a: 1 })
    expect(res.data.headers['X-CSRFToken']).toBe('tok-POST')
  })

  it('attaches X-CSRFToken on PATCH and DELETE too', async () => {
    setCookie('csrftoken=tok-UNSAFE')
    const patched = await api.patch('/thing/1/', { a: 1 })
    const deleted = await api.delete('/thing/1/')
    expect(patched.data.headers['X-CSRFToken']).toBe('tok-UNSAFE')
    expect(deleted.data.headers['X-CSRFToken']).toBe('tok-UNSAFE')
  })

  it('does NOT attach X-CSRFToken on GET (safe method)', async () => {
    setCookie('csrftoken=tok-GET')
    const res = await api.get('/thing/')
    expect(res.data.headers['X-CSRFToken']).toBeUndefined()
  })
})
