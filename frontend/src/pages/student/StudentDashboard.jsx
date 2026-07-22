import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import api from '../../api.js'
import { Spinner, ErrorBox, EmptyState, PageHeader } from '../../components/ui.jsx'
import { BarChart } from '../../components/Charts.jsx'

export default function StudentDashboard() {
  const navigate = useNavigate()

  const exams = useQuery({
    queryKey: ['student-exams'],
    queryFn: async () => (await api.get('/student/exams/')).data,
  })

  const start = useMutation({
    mutationFn: async (examId) => {
      const { data } = await api.post(`/exams/${examId}/attempt/`)
      return { examId, ...data }
    },
    onSuccess: ({ examId }) => navigate(`/s/exams/${examId}/take`),
  })

  if (exams.isLoading) return <Spinner />
  if (exams.isError) return <ErrorBox error={exams.error} />

  const list = exams.data || []

  return (
    <div>
      <PageHeader title="Available exams" subtitle="Published exams you can attempt." />

      <div className="mb-6 card">
        <h2 className="mb-3 font-semibold text-slate-800">Marks available per exam</h2>
        {list.length ? (
          <BarChart
            labels={list.map((e) => e.title)}
            values={list.map((e) => e.total_marks || 0)}
            label="Total marks"
          />
        ) : (
          <p className="text-sm text-slate-500">No exams available.</p>
        )}
      </div>

      {list.length ? (
        <ul className="grid gap-4 sm:grid-cols-2">
          {list.map((ex) => (
            <li key={ex.id} className="card flex flex-col justify-between">
              <div>
                <h3 className="text-lg font-semibold text-slate-800">{ex.title}</h3>
                <p className="mt-1 text-sm text-slate-500">by {ex.teacher_name}</p>
                <div className="mt-3 flex flex-wrap gap-2 text-xs">
                  <span className="badge bg-slate-100 text-slate-600">
                    {ex.duration_min} min
                  </span>
                  <span className="badge bg-slate-100 text-slate-600">
                    {ex.question_count} questions
                  </span>
                  <span className="badge bg-slate-100 text-slate-600">
                    {ex.total_marks} marks
                  </span>
                </div>
              </div>
              {start.isError && start.variables === ex.id && (
                <div className="mt-3">
                  <ErrorBox error={start.error} />
                </div>
              )}
              <button
                className="btn-primary mt-4"
                onClick={() => start.mutate(ex.id)}
                disabled={start.isPending && start.variables === ex.id}
              >
                {start.isPending && start.variables === ex.id ? 'Starting…' : 'Start exam'}
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <EmptyState title="No exams available" hint="Check back when your teacher publishes one." />
      )}
    </div>
  )
}
