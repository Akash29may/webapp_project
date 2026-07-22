import { useEffect, useMemo, useRef, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import api from '../../api.js'
import { Spinner, ErrorBox } from '../../components/ui.jsx'
import QuestionNavigator from '../../components/QuestionNavigator.jsx'
import { useDebouncedCallback } from '../../hooks/useDebouncedCallback.js'

function fmt(total) {
  const s = Math.max(0, total)
  const m = Math.floor(s / 60)
  const sec = s % 60
  return `${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
}

/**
 * Server-synced countdown. Initialises from `initialSeconds`, ticks down every
 * second and calls `onExpire` exactly once when it reaches zero.
 */
export function ExamTimer({ initialSeconds, onExpire }) {
  const [remaining, setRemaining] = useState(initialSeconds)
  const expired = useRef(false)
  const onExpireRef = useRef(onExpire)
  onExpireRef.current = onExpire

  useEffect(() => {
    setRemaining(initialSeconds)
  }, [initialSeconds])

  useEffect(() => {
    const iv = setInterval(() => {
      setRemaining((r) => (r > 0 ? r - 1 : 0))
    }, 1000)
    return () => clearInterval(iv)
  }, [])

  useEffect(() => {
    if (remaining <= 0 && !expired.current) {
      expired.current = true
      onExpireRef.current?.()
    }
  }, [remaining])

  const low = remaining <= 60
  return (
    <div
      data-testid="exam-timer"
      className={`rounded-lg px-4 py-2 text-center font-mono text-lg font-bold ${
        low ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-700'
      }`}
    >
      {fmt(remaining)}
    </div>
  )
}

export function isQuestionAnswered(question, answer) {
  if (!answer) return false
  if (question.qtype === 'mcq') {
    return answer.selected_choice != null
  }
  return typeof answer.text_response === 'string' && answer.text_response.trim().length > 0
}

export default function ExamRunner() {
  const { id: examId } = useParams()
  const navigate = useNavigate()

  // Start or resume the attempt for this exam.
  const attemptStart = useQuery({
    queryKey: ['attempt-start', examId],
    queryFn: async () => (await api.post(`/exams/${examId}/attempt/`)).data,
    staleTime: Infinity,
    retry: false,
  })
  const attemptId = attemptStart.data?.attempt_id

  // Fetch the take state (questions + saved answers + seconds_remaining).
  const state = useQuery({
    queryKey: ['attempt', attemptId],
    queryFn: async () => (await api.get(`/attempts/${attemptId}/`)).data,
    enabled: !!attemptId,
    staleTime: Infinity,
    retry: false,
  })

  const [answers, setAnswers] = useState({})
  const [current, setCurrent] = useState(0)
  const [saveState, setSaveState] = useState('idle') // idle | saving | saved
  const [warning, setWarning] = useState(null)
  const submittedRef = useRef(false)

  // Seed local answers from server state once loaded (resume-after-refresh).
  useEffect(() => {
    if (state.data?.answers) {
      setAnswers(state.data.answers || {})
    }
  }, [state.data])

  const questions = state.data?.questions || []

  const saveAnswer = useMutation({
    mutationFn: (payload) => api.patch(`/attempts/${attemptId}/answer/`, payload),
    onMutate: () => setSaveState('saving'),
    onSuccess: () => setSaveState('saved'),
    onError: () => setSaveState('idle'),
  })

  const debouncedSave = useDebouncedCallback((payload) => saveAnswer.mutate(payload), 600)

  const submit = useMutation({
    mutationFn: () => api.post(`/attempts/${attemptId}/submit/`),
    onSuccess: () => {
      submittedRef.current = true
      navigate(`/s/attempts/${attemptId}/result`, { replace: true })
    },
  })

  const warn = useMutation({
    mutationFn: () => api.post(`/attempts/${attemptId}/warn/`),
  })

  // Anti-cheat: warn on focus loss / tab switch.
  useEffect(() => {
    if (!attemptId || state.data?.status !== 'in_progress') return
    const trigger = () => {
      if (submittedRef.current) return
      setWarning('You left the exam window. This has been recorded.')
      warn.mutate()
    }
    const onVisibility = () => {
      if (document.visibilityState === 'hidden') trigger()
    }
    window.addEventListener('blur', trigger)
    document.addEventListener('visibilitychange', onVisibility)
    return () => {
      window.removeEventListener('blur', trigger)
      document.removeEventListener('visibilitychange', onVisibility)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attemptId, state.data?.status])

  const onExpire = () => {
    if (!submittedRef.current && !submit.isPending) {
      debouncedSave.flush?.()
      submit.mutate()
    }
  }

  const setChoice = (question, choiceId) => {
    setAnswers((a) => ({ ...a, [question.id]: { ...a[question.id], selected_choice: choiceId } }))
    debouncedSave({ question_id: question.id, choice_id: choiceId })
  }
  const setText = (question, text) => {
    setAnswers((a) => ({ ...a, [question.id]: { ...a[question.id], text_response: text } }))
    debouncedSave({ question_id: question.id, text_response: text })
  }

  const answeredCount = useMemo(
    () => questions.filter((q) => isQuestionAnswered(q, answers[q.id])).length,
    [questions, answers]
  )

  if (attemptStart.isLoading || state.isLoading) return <Spinner label="Loading exam…" />
  if (attemptStart.isError) return <ErrorBox error={attemptStart.error} />
  if (state.isError) return <ErrorBox error={state.error} />

  // Already submitted -> go straight to review.
  if (state.data?.status && state.data.status !== 'in_progress') {
    return (
      <div className="mx-auto max-w-md p-8 text-center">
        <p className="text-slate-600">This attempt is {state.data.status}.</p>
        <button
          className="btn-primary mt-4"
          onClick={() => navigate(`/s/attempts/${attemptId}/result`, { replace: true })}
        >
          View result
        </button>
      </div>
    )
  }

  const q = questions[current]

  return (
    <div
      className="min-h-screen bg-slate-100 p-4 select-none"
      onCopy={(e) => e.preventDefault()}
      onCut={(e) => e.preventDefault()}
      onPaste={(e) => e.preventDefault()}
      onContextMenu={(e) => e.preventDefault()}
      data-testid="exam-wrapper"
    >
      {warning && (
        <div className="mx-auto mb-4 max-w-5xl rounded-md border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700">
          <div className="flex items-center justify-between">
            <span>⚠️ {warning}</span>
            <button className="font-medium underline" onClick={() => setWarning(null)}>
              Dismiss
            </button>
          </div>
        </div>
      )}

      <div className="mx-auto grid max-w-5xl gap-4 lg:grid-cols-[1fr_260px]">
        <div className="space-y-4">
          <div className="card">
            <div className="mb-4 flex items-center justify-between">
              <h1 className="text-lg font-bold text-slate-900">{state.data.exam_title}</h1>
              <span className="text-xs text-slate-500">
                {saveState === 'saving' && 'Saving…'}
                {saveState === 'saved' && <span className="text-emerald-600">✓ Saved</span>}
              </span>
            </div>

            {q ? (
              <div>
                <div className="mb-2 flex items-center gap-2">
                  <span className="badge bg-slate-100 text-slate-600">
                    Question {current + 1} of {questions.length}
                  </span>
                  <span className="badge bg-slate-100 text-slate-600">{q.marks} marks</span>
                </div>
                <p className="mb-4 whitespace-pre-wrap text-slate-800">{q.text}</p>

                {q.qtype === 'mcq' ? (
                  <div className="space-y-2">
                    {(q.choices || []).map((c) => (
                      <label
                        key={c.id}
                        className={`flex cursor-pointer items-center gap-3 rounded-md border p-3 ${
                          answers[q.id]?.selected_choice === c.id
                            ? 'border-brand-400 bg-brand-50'
                            : 'border-slate-200 hover:bg-slate-50'
                        }`}
                      >
                        <input
                          type="radio"
                          name={`q-${q.id}`}
                          checked={answers[q.id]?.selected_choice === c.id}
                          onChange={() => setChoice(q, c.id)}
                        />
                        <span>{c.text}</span>
                      </label>
                    ))}
                  </div>
                ) : (
                  <textarea
                    className="input"
                    rows={6}
                    placeholder="Type your answer…"
                    value={answers[q.id]?.text_response || ''}
                    onChange={(e) => setText(q, e.target.value)}
                  />
                )}

                <div className="mt-6 flex justify-between">
                  <button
                    className="btn-secondary"
                    disabled={current === 0}
                    onClick={() => setCurrent((c) => Math.max(0, c - 1))}
                  >
                    ← Previous
                  </button>
                  <button
                    className="btn-secondary"
                    disabled={current >= questions.length - 1}
                    onClick={() => setCurrent((c) => Math.min(questions.length - 1, c + 1))}
                  >
                    Next →
                  </button>
                </div>
              </div>
            ) : (
              <p className="text-slate-500">This exam has no questions.</p>
            )}
          </div>
        </div>

        <aside className="space-y-4">
          <div className="card">
            <p className="label">Time remaining</p>
            <ExamTimer initialSeconds={state.data.seconds_remaining ?? 0} onExpire={onExpire} />
          </div>

          <div className="card">
            <div className="mb-3 flex items-center justify-between">
              <p className="font-medium text-slate-700">Questions</p>
              <span className="text-xs text-slate-500">
                {answeredCount}/{questions.length}
              </span>
            </div>
            <QuestionNavigator
              questions={questions}
              current={current}
              onJump={setCurrent}
              isAnswered={(question) => isQuestionAnswered(question, answers[question.id])}
            />
            <button
              className="btn-primary mt-4 w-full"
              disabled={submit.isPending}
              onClick={() => {
                if (confirm('Submit your exam? You cannot change answers after this.')) {
                  debouncedSave.flush?.()
                  submit.mutate()
                }
              }}
            >
              {submit.isPending ? 'Submitting…' : 'Submit exam'}
            </button>
            {submit.isError && (
              <div className="mt-3">
                <ErrorBox error={submit.error} />
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}
