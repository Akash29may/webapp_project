import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../../api.js'
import { Spinner, ErrorBox, EmptyState, PageHeader } from '../../components/ui.jsx'
import { BarChart } from '../../components/Charts.jsx'

function buildDistribution(attempts) {
  // Bucket percentage scores into 0-20, 20-40, ... 80-100.
  const buckets = [0, 0, 0, 0, 0]
  const labels = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
  attempts.forEach((a) => {
    if (a.total > 0 && a.score != null) {
      const pct = (a.score / a.total) * 100
      let idx = Math.min(4, Math.floor(pct / 20))
      if (idx < 0) idx = 0
      buckets[idx] += 1
    }
  })
  return { labels, buckets }
}

export default function ExamResults() {
  const { id } = useParams()
  const results = useQuery({
    queryKey: ['exam-results', id],
    queryFn: async () => (await api.get(`/exams/${id}/results/`)).data,
  })

  if (results.isLoading) return <Spinner />
  if (results.isError) return <ErrorBox error={results.error} />

  const attempts = results.data.attempts || []
  const { labels, buckets } = buildDistribution(attempts)

  return (
    <div>
      <PageHeader
        title="Exam results"
        subtitle={`${attempts.length} attempt(s)`}
        actions={
          <Link to={`/t/exams/${id}`} className="btn-secondary">
            ← Exam editor
          </Link>
        }
      />

      {attempts.length ? (
        <>
          <div className="card mb-6">
            <h2 className="mb-3 font-semibold text-slate-800">Score distribution</h2>
            <BarChart labels={labels} values={buckets} label="Students" />
          </div>

          <div className="card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left text-slate-500">
                  <th className="py-2 pr-4">Student</th>
                  <th className="py-2 pr-4">Score</th>
                  <th className="py-2 pr-4">Status</th>
                  <th className="py-2 pr-4">Submitted</th>
                  <th className="py-2 pr-4">Focus warnings</th>
                </tr>
              </thead>
              <tbody>
                {attempts.map((a) => (
                  <tr key={a.id} className="border-b border-slate-100">
                    <td className="py-2 pr-4 font-medium text-slate-800">{a.student_name}</td>
                    <td className="py-2 pr-4">
                      {a.score ?? '—'} / {a.total}
                    </td>
                    <td className="py-2 pr-4">
                      <span className="badge bg-slate-100 text-slate-600">{a.status}</span>
                    </td>
                    <td className="py-2 pr-4 text-slate-500">
                      {a.submitted_at ? new Date(a.submitted_at).toLocaleString() : '—'}
                    </td>
                    <td className="py-2 pr-4">
                      {a.focus_warnings > 0 ? (
                        <span className="badge bg-red-100 text-red-700">{a.focus_warnings}</span>
                      ) : (
                        <span className="text-slate-400">0</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <EmptyState title="No attempts yet" hint="Results appear once students submit." />
      )}
    </div>
  )
}
