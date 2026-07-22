import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import QuestionNavigator from '../components/QuestionNavigator.jsx'
import { isQuestionAnswered } from '../pages/student/ExamRunner.jsx'

describe('QuestionNavigator', () => {
  const questions = [
    { id: 1, qtype: 'mcq' },
    { id: 2, qtype: 'subjective' },
    { id: 3, qtype: 'mcq' },
  ]
  const answers = {
    1: { selected_choice: 9 }, // answered
    2: { text_response: '' }, // not answered
    // 3 has no entry -> not answered
  }

  it('marks answered vs unanswered questions', () => {
    render(
      <QuestionNavigator
        questions={questions}
        current={0}
        onJump={() => {}}
        isAnswered={(q) => isQuestionAnswered(q, answers[q.id])}
      />
    )
    const buttons = screen.getAllByRole('button')
    expect(buttons).toHaveLength(3)
    expect(buttons[0]).toHaveAttribute('data-answered', 'true')
    expect(buttons[1]).toHaveAttribute('data-answered', 'false')
    expect(buttons[2]).toHaveAttribute('data-answered', 'false')
  })

  it('calls onJump with the clicked index', () => {
    const onJump = vi.fn()
    render(
      <QuestionNavigator
        questions={questions}
        current={0}
        onJump={onJump}
        isAnswered={() => false}
      />
    )
    fireEvent.click(screen.getByRole('button', { name: /question 3/i }))
    expect(onJump).toHaveBeenCalledWith(2)
  })
})
