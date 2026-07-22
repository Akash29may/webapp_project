import { useCallback, useEffect, useRef } from 'react'

/**
 * Returns a debounced version of `fn`. Repeated calls within `delay` ms reset
 * the timer; only the last call runs. Also exposes `.flush()` and `.cancel()`.
 */
export function useDebouncedCallback(fn, delay = 600) {
  const timer = useRef(null)
  const lastArgs = useRef(null)
  const fnRef = useRef(fn)
  fnRef.current = fn

  const cancel = useCallback(() => {
    if (timer.current) {
      clearTimeout(timer.current)
      timer.current = null
    }
  }, [])

  const flush = useCallback(() => {
    if (timer.current) {
      clearTimeout(timer.current)
      timer.current = null
      if (lastArgs.current) fnRef.current(...lastArgs.current)
    }
  }, [])

  const debounced = useCallback(
    (...args) => {
      lastArgs.current = args
      cancel()
      timer.current = setTimeout(() => {
        timer.current = null
        fnRef.current(...args)
      }, delay)
    },
    [cancel, delay]
  )

  useEffect(() => cancel, [cancel])

  debounced.cancel = cancel
  debounced.flush = flush
  return debounced
}
