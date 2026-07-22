import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../api.js'
import { Spinner, ErrorBox, EmptyState, PageHeader } from '../../components/ui.jsx'

const DIFFICULTIES = ['easy', 'medium', 'hard']

export default function ExamEditor() {
  const { id } = useParams()
  const qc = useQueryClient()

  const exam = useQuery({
    queryKey: ['exam', id],
    queryFn: async () => (await api.get(`/exams/${id}/`)).data,
  })
  const invalidate = () => qc.invalidateQueries({ queryKey: ['exam', id] })

  if (exam.isLoading) return <Spinner />
  if (exam.isError) return <ErrorBox error={exam.error} />

  const data = exam.data
  const questions = data.questions || []

  return (
    <div>
      <PageHeader
        title="Exam editor"
        subtitle={data.title}
        actions={
          <div className="flex gap-2">
            <Link to={`/t/exams/${id}/results`} className="btn-secondary">
              Results
            </Link>
            <Link to="/t" className="btn-secondary">
              ← Dashboard
            </Link>
          </div>
        }
      />

      <ExamSettings exam={data} onSaved={invalidate} />

      <div className="mt-8 grid gap-8 lg:grid-cols-2">
        <section>
          <h2 className="mb-3 text-lg font-semibold text-slate-800">
            Questions ({questions.length})
          </h2>
          <div className="space-y-3">
            {questions.length ? (
              questions.map((q, i) => (
                <QuestionCard key={q.id} index={i} question={q} onChanged={invalidate} />
              ))
            ) : (
              <EmptyState title="No questions yet" hint="Add one manually or generate with AI." />
            )}
          </div>
          <AddQuestion examId={id} onAdded={invalidate} nextOrder={questions.length + 1} />
        </section>

        <section>
          <GeneratePanel examId={id} onSaved={invalidate} nextOrder={questions.length + 1} />
        </section>
      </div>
    </div>
  )
}

function ExamSettings({ exam, onSaved }) {
  const [title, setTitle] = useState(exam.title)
  const [duration, setDuration] = useState(exam.duration_min)

  const save = useMutation({
    mutationFn: (body) => api.patch(`/exams/${exam.id}/`, body),
    onSuccess: onSaved,
  })
  const togglePublish = useMutation({
    mutationFn: () => api.patch(`/exams/${exam.id}/`, { is_published: !exam.is_published }),
    onSuccess: onSaved,
  })

  return (
    <div className="card">
      <div className="flex flex-wrap items-end gap-4">
        <div className="flex-1">
          <label className="label">Title</label>
          <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div className="w-36">
          <label className="label">Duration (min)</label>
          <input
            className="input"
            type="number"
            min="1"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
          />
        </div>
        <button
          className="btn-primary"
          onClick={() => save.mutate({ title, duration_min: Number(duration) })}
          disabled={save.isPending}
        >
          Save
        </button>
        <button
          className={exam.is_published ? 'btn-secondary' : 'btn-primary'}
          onClick={() => togglePublish.mutate()}
          disabled={togglePublish.isPending}
        >
          {exam.is_published ? 'Unpublish' : 'Publish'}
        </button>
        <span
          className={`badge ${
            exam.is_published
              ? 'bg-emerald-100 text-emerald-700'
              : 'bg-amber-100 text-amber-700'
          }`}
        >
          {exam.is_published ? 'Published' : 'Draft'}
        </span>
      </div>
      {save.isError && <div className="mt-3"><ErrorBox error={save.error} /></div>}
    </div>
  )
}

function QuestionCard({ index, question, onChanged }) {
  const del = useMutation({
    mutationFn: () => api.delete(`/questions/${question.id}/`),
    onSuccess: onChanged,
  })
  return (
    <div className="card">
      <div className="flex items-start justify-between gap-3">
        <div>
          <span className="badge bg-slate-100 text-slate-600">
            {question.qtype === 'mcq' ? 'MCQ' : 'Subjective'} · {question.marks} marks ·{' '}
            {question.difficulty}
          </span>
          <p className="mt-2 font-medium text-slate-800">
            {index + 1}. {question.text}
          </p>
        </div>
        <button
          className="text-sm text-red-600 hover:underline"
          onClick={() => {
            if (confirm('Delete this question?')) del.mutate()
          }}
        >
          Delete
        </button>
      </div>
      {question.qtype === 'mcq' ? (
        <ul className="mt-2 space-y-1 text-sm">
          {(question.choices || []).map((c) => (
            <li
              key={c.id}
              className={c.is_correct ? 'font-medium text-emerald-700' : 'text-slate-600'}
            >
              {c.is_correct ? '✓ ' : '• '}
              {c.text}
            </li>
          ))}
        </ul>
      ) : (
        question.model_answer && (
          <p className="mt-2 rounded bg-slate-50 p-2 text-sm text-slate-600">
            <span className="font-medium">Model answer: </span>
            {question.model_answer}
          </p>
        )
      )}
    </div>
  )
}

/** Reusable question form used both for manual add and for editing AI drafts. */
export function QuestionForm({ initial, onSubmit, submitLabel = 'Add question', pending }) {
  const [qtype, setQtype] = useState(initial?.qtype || 'mcq')
  const [text, setText] = useState(initial?.text || '')
  const [marks, setMarks] = useState(initial?.marks ?? 1)
  const [difficulty, setDifficulty] = useState(initial?.difficulty || 'medium')
  const [modelAnswer, setModelAnswer] = useState(initial?.model_answer || '')
  const [choices, setChoices] = useState(
    initial?.choices?.length === 4
      ? initial.choices.map((c) => ({ text: c.text, is_correct: !!c.is_correct }))
      : [
          { text: '', is_correct: true },
          { text: '', is_correct: false },
          { text: '', is_correct: false },
          { text: '', is_correct: false },
        ]
  )
  const [err, setErr] = useState('')

  const setChoiceText = (i, v) =>
    setChoices((cs) => cs.map((c, idx) => (idx === i ? { ...c, text: v } : c)))
  const setCorrect = (i) =>
    setChoices((cs) => cs.map((c, idx) => ({ ...c, is_correct: idx === i })))

  const handle = (e) => {
    e.preventDefault()
    setErr('')
    const base = {
      qtype,
      text: text.trim(),
      marks: Number(marks),
      difficulty,
    }
    if (!base.text) return setErr('Question text is required.')
    if (qtype === 'mcq') {
      if (choices.some((c) => !c.text.trim())) return setErr('All 4 choices need text.')
      if (choices.filter((c) => c.is_correct).length !== 1)
        return setErr('Exactly one choice must be correct.')
      onSubmit({ ...base, choices: choices.map((c) => ({ text: c.text.trim(), is_correct: c.is_correct })) })
    } else {
      if (!modelAnswer.trim()) return setErr('Model answer is required for subjective questions.')
      onSubmit({ ...base, model_answer: modelAnswer.trim() })
    }
  }

  return (
    <form onSubmit={handle} className="space-y-3">
      <div className="flex gap-2">
        {['mcq', 'subjective'].map((t) => (
          <button
            type="button"
            key={t}
            onClick={() => setQtype(t)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium capitalize ${
              qtype === t ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-600'
            }`}
          >
            {t === 'mcq' ? 'MCQ' : 'Subjective'}
          </button>
        ))}
      </div>

      <textarea
        className="input"
        rows={2}
        placeholder="Question text"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="label">Marks</label>
          <input
            className="input"
            type="number"
            min="1"
            value={marks}
            onChange={(e) => setMarks(e.target.value)}
          />
        </div>
        <div>
          <label className="label">Difficulty</label>
          <select
            className="input"
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
          >
            {DIFFICULTIES.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>
      </div>

      {qtype === 'mcq' ? (
        <div className="space-y-2">
          <p className="label">Choices (select the correct one)</p>
          {choices.map((c, i) => (
            <div key={i} className="flex items-center gap-2">
              <input
                type="radio"
                name="correct-choice"
                checked={c.is_correct}
                onChange={() => setCorrect(i)}
                aria-label={`Mark choice ${i + 1} correct`}
              />
              <input
                className="input"
                placeholder={`Choice ${i + 1}`}
                value={c.text}
                onChange={(e) => setChoiceText(i, e.target.value)}
              />
            </div>
          ))}
        </div>
      ) : (
        <div>
          <label className="label">Model answer</label>
          <textarea
            className="input"
            rows={3}
            value={modelAnswer}
            onChange={(e) => setModelAnswer(e.target.value)}
          />
        </div>
      )}

      {err && <p className="text-sm text-red-600">{err}</p>}

      <button className="btn-primary" disabled={pending}>
        {submitLabel}
      </button>
    </form>
  )
}

function AddQuestion({ examId, onAdded, nextOrder }) {
  const [open, setOpen] = useState(false)
  const add = useMutation({
    mutationFn: (body) => api.post(`/exams/${examId}/questions/`, { ...body, order: nextOrder }),
    onSuccess: () => {
      setOpen(false)
      onAdded()
    },
  })

  if (!open)
    return (
      <button className="btn-secondary mt-4" onClick={() => setOpen(true)}>
        + Add question
      </button>
    )

  return (
    <div className="card mt-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold text-slate-800">New question</h3>
        <button className="text-sm text-slate-500 hover:underline" onClick={() => setOpen(false)}>
          Close
        </button>
      </div>
      {add.isError && <div className="mb-3"><ErrorBox error={add.error} /></div>}
      <QuestionForm onSubmit={(b) => add.mutate(b)} pending={add.isPending} />
    </div>
  )
}

function GeneratePanel({ examId, onSaved, nextOrder }) {
  const [sourceText, setSourceText] = useState('')
  const [count, setCount] = useState(5)
  const [difficulty, setDifficulty] = useState('medium')
  const [qtypes, setQtypes] = useState(['mcq'])
  const [drafts, setDrafts] = useState([])
  const orderRef = { current: nextOrder }

  const generate = useMutation({
    mutationFn: async () => {
      const { data } = await api.post(`/exams/${examId}/generate/`, {
        source_text: sourceText,
        count: Number(count),
        qtypes,
        difficulty,
      })
      return data.questions || []
    },
    onSuccess: (qs) => setDrafts(qs),
  })

  const toggleType = (t) =>
    setQtypes((prev) => (prev.includes(t) ? prev.filter((x) => x !== t) : [...prev, t]))

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-slate-800">Generate with AI</h2>
      <p className="mt-1 text-sm text-slate-500">
        Paste source material and generate draft questions to review before saving.
      </p>

      <div className="mt-4 space-y-3">
        <textarea
          className="input"
          rows={5}
          placeholder="Source text (lecture notes, article…)"
          value={sourceText}
          onChange={(e) => setSourceText(e.target.value)}
        />
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Count</label>
            <input
              className="input"
              type="number"
              min="1"
              max="20"
              value={count}
              onChange={(e) => setCount(e.target.value)}
            />
          </div>
          <div>
            <label className="label">Difficulty</label>
            <select
              className="input"
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
            >
              {DIFFICULTIES.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="flex gap-4">
          {['mcq', 'subjective'].map((t) => (
            <label key={t} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={qtypes.includes(t)}
                onChange={() => toggleType(t)}
              />
              {t === 'mcq' ? 'MCQ' : 'Subjective'}
            </label>
          ))}
        </div>
        <button
          className="btn-primary"
          onClick={() => generate.mutate()}
          disabled={generate.isPending || !sourceText.trim() || qtypes.length === 0}
        >
          {generate.isPending ? 'Generating…' : 'Generate drafts'}
        </button>
        {generate.isError && <ErrorBox error={generate.error} />}
      </div>

      {drafts.length > 0 && (
        <div className="mt-6 space-y-4">
          <h3 className="font-semibold text-slate-800">Review drafts ({drafts.length})</h3>
          {drafts.map((d, i) => (
            <DraftReview
              key={i}
              draft={d}
              examId={examId}
              order={orderRef.current + i}
              onSaved={() => {
                setDrafts((prev) => prev.filter((_, idx) => idx !== i))
                onSaved()
              }}
              onDiscard={() => setDrafts((prev) => prev.filter((_, idx) => idx !== i))}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function DraftReview({ draft, examId, order, onSaved, onDiscard }) {
  const save = useMutation({
    mutationFn: (body) => api.post(`/exams/${examId}/questions/`, { ...body, order }),
    onSuccess: onSaved,
  })
  return (
    <div className="rounded-lg border border-brand-200 bg-brand-50/40 p-4">
      <div className="mb-2 flex items-center justify-between">
        <span className="badge bg-brand-100 text-brand-700">AI draft</span>
        <button className="text-sm text-slate-500 hover:underline" onClick={onDiscard}>
          Discard
        </button>
      </div>
      {save.isError && <div className="mb-2"><ErrorBox error={save.error} /></div>}
      <QuestionForm
        initial={draft}
        onSubmit={(b) => save.mutate(b)}
        submitLabel="Accept & save"
        pending={save.isPending}
      />
    </div>
  )
}
