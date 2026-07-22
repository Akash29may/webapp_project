import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import api from '../api.js'
import { useAuth } from '../auth/AuthContext.jsx'
import { ErrorBox } from '../components/ui.jsx'

const emptyForm = {
  username: '',
  password: '',
  password2: '',
  first_name: '',
  last_name: '',
  email: '',
  contact_no: '',
  department: '',
  designation: '',
  university: '',
}

export default function Register() {
  const [role, setRole] = useState('teacher')
  const [form, setForm] = useState(emptyForm)
  const { setUser } = useAuth()
  const navigate = useNavigate()

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const register = useMutation({
    mutationFn: async () => {
      const payload = { role, ...form }
      if (role === 'teacher') {
        delete payload.university
      } else {
        delete payload.designation
      }
      const { data } = await api.post('/auth/register/', payload)
      return data
    },
    onSuccess: (user) => {
      setUser(user)
      navigate(user.role === 'teacher' ? '/t' : '/s', { replace: true })
    },
  })

  const onSubmit = (e) => {
    e.preventDefault()
    register.mutate()
  }

  return (
    <div className="mx-auto max-w-2xl py-8">
      <div className="card">
        <h1 className="text-xl font-bold text-slate-900">Create your account</h1>

        <div className="mt-4 inline-flex rounded-lg border border-slate-200 bg-slate-100 p-1">
          {['teacher', 'student'].map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => setRole(r)}
              className={[
                'rounded-md px-4 py-1.5 text-sm font-medium capitalize transition',
                role === r ? 'bg-white text-brand-700 shadow' : 'text-slate-500',
              ].join(' ')}
            >
              {r}
            </button>
          ))}
        </div>

        <form onSubmit={onSubmit} className="mt-6 grid gap-4 sm:grid-cols-2">
          <Field label="First name" value={form.first_name} onChange={set('first_name')} required />
          <Field label="Last name" value={form.last_name} onChange={set('last_name')} required />
          <Field label="Username" value={form.username} onChange={set('username')} required />
          <Field
            label="Email"
            type="email"
            value={form.email}
            onChange={set('email')}
            required
          />
          <Field label="Contact no" value={form.contact_no} onChange={set('contact_no')} required />
          <Field label="Department" value={form.department} onChange={set('department')} required />

          {role === 'teacher' ? (
            <Field
              label="Designation"
              value={form.designation}
              onChange={set('designation')}
            />
          ) : (
            <Field
              label="University"
              value={form.university}
              onChange={set('university')}
              required
            />
          )}

          <Field
            label="Password"
            type="password"
            value={form.password}
            onChange={set('password')}
            required
          />
          <Field
            label="Confirm password"
            type="password"
            value={form.password2}
            onChange={set('password2')}
            required
          />

          {register.isError && (
            <div className="sm:col-span-2">
              <ErrorBox error={register.error} />
            </div>
          )}

          <div className="sm:col-span-2">
            <button type="submit" className="btn-primary w-full" disabled={register.isPending}>
              {register.isPending ? 'Creating…' : 'Create account'}
            </button>
          </div>
        </form>

        <p className="mt-4 text-center text-sm text-slate-500">
          Already registered?{' '}
          <Link to="/login" className="font-medium text-brand-600 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  )
}

function Field({ label, value, onChange, type = 'text', required }) {
  return (
    <div>
      <label className="label">{label}</label>
      <input
        className="input"
        type={type}
        value={value}
        onChange={onChange}
        required={required}
      />
    </div>
  )
}
