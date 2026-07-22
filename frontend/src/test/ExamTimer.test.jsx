import { describe, it, expect, vi, afterEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import { ExamTimer, isQuestionAnswered } from '../pages/student/ExamRunner.jsx'

describe('ExamTimer', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('counts down and auto-submits (calls onExpire once) at 0', () => {
    vi.useFakeTimers()
    const onExpire = vi.fn()
    render(<ExamTimer initialSeconds={3} onExpire={onExpire} />)

    expect(screen.getByTestId('exam-timer')).toHaveTextContent('00:03')

    act(() => {
      vi.advanceTimersByTime(1000)
    })
    expect(screen.getByTestId('exam-timer')).toHaveTextContent('00:02')
    expect(onExpire).not.toHaveBeenCalled()

    act(() => {
      vi.advanceTimersByTime(2000)
    })
    expect(screen.getByTestId('exam-timer')).toHaveTextContent('00:00')
    expect(onExpire).toHaveBeenCalledTimes(1)

    // Should not fire again if the timer keeps ticking.
    act(() => {
      vi.advanceTimersByTime(3000)
    })
    expect(onExpire).toHaveBeenCalledTimes(1)
  })
})

describe('isQuestionAnswered', () => {
  it('marks an MCQ answered only when a choice is selected', () => {
    const q = { id: 1, qtype: 'mcq' }
    expect(isQuestionAnswered(q, undefined)).toBe(false)
    expect(isQuestionAnswered(q, { selected_choice: null })).toBe(false)
    expect(isQuestionAnswered(q, { selected_choice: 42 })).toBe(true)
  })

  it('marks a subjective answered only with non-empty text', () => {
    const q = { id: 2, qtype: 'subjective' }
    expect(isQuestionAnswered(q, { text_response: '' })).toBe(false)
    expect(isQuestionAnswered(q, { text_response: '   ' })).toBe(false)
    expect(isQuestionAnswered(q, { text_response: 'my answer' })).toBe(true)
  })
})
