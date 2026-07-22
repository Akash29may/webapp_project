import { Link, Navigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext.jsx'

export default function Landing() {
  const { user } = useAuth()
  if (user) return <Navigate to={user.role === 'teacher' ? '/t' : '/s'} replace />

  return (
    <div className="mx-auto max-w-3xl py-12 text-center">
      <span className="badge bg-brand-100 text-brand-700">AI-powered assessments</span>
      <h1 className="mt-4 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl">
        Create, run and grade exams with <span className="text-brand-600">SmartExam AI</span>
      </h1>
      <p className="mx-auto mt-4 max-w-xl text-lg text-slate-600">
        Teachers generate questions from any source text, publish timed exams, and review
        results. Students take proctored exams with autosave and instant feedback.
      </p>
      <div className="mt-8 flex items-center justify-center gap-3">
        <Link to="/register" className="btn-primary px-6 py-3 text-base">
          Get started
        </Link>
        <Link to="/login" className="btn-secondary px-6 py-3 text-base">
          Log in
        </Link>
      </div>

      <div className="mt-14 grid gap-4 text-left sm:grid-cols-3">
        {[
          ['AI question generation', 'Turn lecture notes into MCQ & subjective drafts.'],
          ['Proctored runner', 'Server-synced timer, autosave, focus warnings.'],
          ['Insightful results', 'Score distribution charts and gap analysis.'],
        ].map(([t, d]) => (
          <div key={t} className="card">
            <h3 className="font-semibold text-slate-800">{t}</h3>
            <p className="mt-1 text-sm text-slate-500">{d}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
