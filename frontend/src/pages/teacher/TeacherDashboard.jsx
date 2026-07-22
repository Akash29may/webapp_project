import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient, useQueries } from '@tanstack/react-query'
import api from '../../api.js'
import { Spinner, ErrorBox, EmptyState, PageHeader } from '../../components/ui.jsx'
import { BarChart, DoughnutChart } from '../../components/Charts.jsx'

export default function TeacherDashboard() {
  const qc = useQueryClient()
  const [showCourse, setShowCourse] = useState(false)
  const [showExam, setShowExam] = useState(false)

  const courses = useQuery({
    queryKey: ['courses'],
    queryFn: async () => (await api.get('/courses/')).data,
  })
  const exams = useQuery({
    queryKey: ['exams'],
    queryFn: async () => (await api.get('/exams/')).data,
  })

  const examList = exams.data || []

  // Fetch results for each exam to build charts.
  const resultQueries = useQueries({
    queries: examList.map((ex) => ({
      queryKey: ['exam-results', ex.id],
      queryFn: async () => (await api.get(`/exams/${ex.id}/results/`)).data,
      enabled: examList.length > 0,
    })),
  })

  const attemptCounts = examList.map((ex, i) => {
    const data = resultQueries[i]?.data
    return data?.attempts?.length || 0
  })
  const statusTotals = { submitted: 0, in_progress: 0, graded: 0 }
  resultQueries.forEach((rq) => {
    ;(rq.data?.attempts || []).forEach((a) => {
      const s = a.status || 'submitted'
      statusTotals[s] = (statusTotals[s] || 0) + 1
    })
  })

  if (courses.isLoading || exams.isLoading) return <Spinner />

  return (
    <div>
      <PageHeader
        title="Teacher dashboard"
        subtitle="Manage your courses and exams."
        actions={
          <>
            <button className="btn-secondary" onClick={() => setShowCourse((v) => !v)}>
              + New course
            </button>
            <button className="btn-primary" onClick={() => setShowExam((v) => !v)}>
              + New exam
            </button>
          </>
        }
      />

      {showCourse && (
        <CreateCourseForm
          onClose={() => setShowCourse(false)}
          onCreated={() => qc.invalidateQueries({ queryKey: ['courses'] })}
        />
      )}
      {showExam && (
        <CreateExamForm
          courses={courses.data || []}
          onClose={() => setShowExam(false)}
          onCreated={() => qc.invalidateQueries({ queryKey: ['exams'] })}
        />
      )}

      <div className="mt-4 grid gap-6 lg:grid-cols-2">
        <div className="card">
          <h2 className="mb-3 font-semibold text-slate-800">Attempts per exam</h2>
          {examList.length ? (
            <BarChart
              labels={examList.map((e) => e.title)}
              values={attemptCounts}
              label="Attempts"
            />
          ) : (
            <p className="text-sm text-slate-500">No exams yet.</p>
          )}
        </div>
        <div className="card">
          <h2 className="mb-3 font-semibold text-slate-800">Attempts by status</h2>
          {Object.values(statusTotals).some((v) => v > 0) ? (
            <div className="mx-auto max-w-xs">
              <DoughnutChart
                labels={Object.keys(statusTotals)}
                values={Object.values(statusTotals)}
              />
            </div>
          ) : (
            <p className="text-sm text-slate-500">No attempts recorded yet.</p>
          )}
        </div>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <section>
          <h2 className="mb-3 text-lg font-semibold text-slate-800">Courses</h2>
          {courses.isError && <ErrorBox error={courses.error} />}
          {courses.data?.length ? (
            <ul className="space-y-3">
              {courses.data.map((c) => (
                <li key={c.id} className="card flex items-center justify-between">
                  <div>
                    <p className="font-medium text-slate-800">{c.title}</p>
                    <p className="line-clamp-1 text-sm text-slate-500">{c.description}</p>
                  </div>
                  <Link to={`/t/courses/${c.id}`} className="btn-secondary">
                    Open
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState title="No courses yet" hint="Create your first course to add modules." />
          )}
        </section>

        <section>
          <h2 className="mb-3 text-lg font-semibold text-slate-800">Exams</h2>
          {exams.isError && <ErrorBox error={exams.error} />}
          {examList.length ? (
            <ul className="space-y-3">
              {examList.map((ex) => (
                <li key={ex.id} className="card flex items-center justify-between">
                  <div>
                    <p className="font-medium text-slate-800">{ex.title}</p>
                    <p className="text-sm text-slate-500">
                      {ex.duration_min} min ·{' '}
                      {ex.is_published ? (
                        <span className="badge bg-emerald-100 text-emerald-700">Published</span>
                      ) : (
                        <span className="badge bg-amber-100 text-amber-700">Draft</span>
                      )}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Link to={`/t/exams/${ex.id}`} className="btn-secondary">
                      Edit
                    </Link>
                    <Link to={`/t/exams/${ex.id}/results`} className="btn-secondary">
                      Results
                    </Link>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState title="No exams yet" hint="Create an exam and add questions." />
          )}
        </section>
      </div>
    </div>
  )
}

function CreateCourseForm({ onClose, onCreated }) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const m = useMutation({
    mutationFn: () => api.post('/courses/', { title, description }),
    onSuccess: () => {
      onCreated()
      onClose()
    },
  })
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        m.mutate()
      }}
      className="card mb-4 space-y-3"
    >
      <h3 className="font-semibold text-slate-800">New course</h3>
      <input
        className="input"
        placeholder="Course title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
      />
      <textarea
        className="input"
        placeholder="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      {m.isError && <ErrorBox error={m.error} />}
      <div className="flex gap-2">
        <button className="btn-primary" disabled={m.isPending}>
          Create
        </button>
        <button type="button" className="btn-secondary" onClick={onClose}>
          Cancel
        </button>
      </div>
    </form>
  )
}

function CreateExamForm({ courses, onClose, onCreated }) {
  const [title, setTitle] = useState('')
  const [duration, setDuration] = useState(30)
  const [course, setCourse] = useState('')
  const m = useMutation({
    mutationFn: () =>
      api.post('/exams/', {
        title,
        duration_min: Number(duration),
        ...(course ? { course: Number(course) } : {}),
      }),
    onSuccess: () => {
      onCreated()
      onClose()
    },
  })
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        m.mutate()
      }}
      className="card mb-4 space-y-3"
    >
      <h3 className="font-semibold text-slate-800">New exam</h3>
      <div className="grid gap-3 sm:grid-cols-3">
        <input
          className="input sm:col-span-2"
          placeholder="Exam title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <input
          className="input"
          type="number"
          min="1"
          placeholder="Duration (min)"
          value={duration}
          onChange={(e) => setDuration(e.target.value)}
          required
        />
      </div>
      <select className="input" value={course} onChange={(e) => setCourse(e.target.value)}>
        <option value="">No course</option>
        {courses.map((c) => (
          <option key={c.id} value={c.id}>
            {c.title}
          </option>
        ))}
      </select>
      {m.isError && <ErrorBox error={m.error} />}
      <div className="flex gap-2">
        <button className="btn-primary" disabled={m.isPending}>
          Create
        </button>
        <button type="button" className="btn-secondary" onClick={onClose}>
          Cancel
        </button>
      </div>
    </form>
  )
}
