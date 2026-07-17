/**
 * Grid of question buttons. Each cell is marked answered / unanswered and the
 * current question is highlighted. `isAnswered(question)` returns a boolean.
 */
export default function QuestionNavigator({ questions, current, onJump, isAnswered }) {
  return (
    <div className="grid grid-cols-5 gap-2 sm:grid-cols-6">
      {questions.map((q, idx) => {
        const answered = isAnswered(q)
        const active = idx === current
        return (
          <button
            key={q.id}
            type="button"
            aria-label={`Question ${idx + 1}`}
            data-answered={answered ? 'true' : 'false'}
            onClick={() => onJump(idx)}
            className={[
              'h-9 w-9 rounded-md border text-sm font-medium transition',
              active ? 'ring-2 ring-brand-500 ring-offset-1' : '',
              answered
                ? 'border-emerald-300 bg-emerald-100 text-emerald-800'
                : 'border-slate-300 bg-white text-slate-600 hover:bg-slate-50',
            ].join(' ')}
          >
            {idx + 1}
          </button>
        )
      })}
    </div>
  )
}
