import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../../api.js'
import { Spinner, ErrorBox, PageHeader } from '../../components/ui.jsx'

export default function AttemptResult() {
  const { id } = useParams()
  const result = useQuery({
    queryKey: ['attempt-result', id],
    queryFn: async () => (await api.get(`/attempts/${id}/result/`)).data,
  })

  if (result.isLoading) return <Spinner />
  if (result.isError) return <ErrorBox error={result.error} />

  const data = result.data
  const pct = data.total ? Math.round((data.score / data.total) * 100) : 0

  return (
    <div>
      <PageHeader
        title="Your result"
        actions={
          <Link to="/s" className="btn-secondary">
            ← Dashboard
          </Link>
        }
      />

      <div className="card mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm text-slate-500">Score</p>
          <p className="text-3xl font-bold text-slate-900">
            {data.score} <span className="text-lg text-slate-400">/ {data.total}</span>
          </p>
        </div>
        <div className="text-right">
          <span className="badge bg-slate-100 text-slate-600">{data.status}</span>
          <p className="mt-1 text-2xl font-bold text-brand-600">{pct}%</p>
        </div>
      </div>

      {data.gap_analysis && (
        <div className="card mb-6 border-brand-200 bg-brand-50/40">
          <h2 className="mb-1 font-semibold text-brand-800">Gap analysis</h2>
          <p className="whitespace-pre-wrap text-sm text-slate-700">{data.gap_analysis}</p>
        </div>
      )}

      <div className="space-y-4">
        {(data.questions || []).map((q, i) => {
          const correct = q.qtype === 'mcq' && q.your_choice != null && q.your_choice === q.correct_choice
          return (
            <div key={q.id} className="card">
              <div className="flex items-start justify-between gap-3">
                <p className="font-medium text-slate-800">
                  {i + 1}. {q.text}
                </p>
                <span
                  className={`badge shrink-0 ${
                    q.qtype === 'mcq'
                      ? correct
                        ? 'bg-emerald-100 text-emerald-700'
                        : 'bg-red-100 text-red-700'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {q.awarded_marks ?? 0} / {q.marks}
                </span>
              </div>

              {q.qtype === 'mcq' ? (
                <div className="mt-3 space-y-1 text-sm">
                  <p>
                    <span className="text-slate-500">Your answer: </span>
                    <span className={correct ? 'text-emerald-700' : 'text-red-700'}>
                      {q.your_text ?? q.your_choice ?? '—'}
                    </span>
                  </p>
                  {!correct && (
                    <p>
                      <span className="text-slate-500">Correct answer: </span>
                      <span className="text-emerald-700">{q.correct_choice_text ?? q.correct_choice ?? '—'}</span>
                    </p>
                  )}
                </div>
              ) : (
                <div className="mt-3 space-y-2 text-sm">
                  <div>
                    <p className="text-slate-500">Your answer:</p>
                    <p className="whitespace-pre-wrap rounded bg-slate-50 p-2 text-slate-700">
                      {q.your_text || '—'}
                    </p>
                  </div>
                  {q.model_answer && (
                    <div>
                      <p className="text-slate-500">Model answer:</p>
                      <p className="whitespace-pre-wrap rounded bg-emerald-50 p-2 text-slate-700">
                        {q.model_answer}
                      </p>
                    </div>
                  )}
                  {q.ai_rationale && (
                    <div>
                      <p className="text-slate-500">AI rationale:</p>
                      <p className="whitespace-pre-wrap rounded bg-brand-50 p-2 text-slate-700">
                        {q.ai_rationale}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
