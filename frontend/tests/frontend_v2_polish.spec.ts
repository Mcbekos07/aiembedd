import { describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useRealtimeStore } from '../src/app/store/realtimeStore'

function withStore() {
  setActivePinia(createPinia())
  return useRealtimeStore()
}

describe('frontend v2 polish critical flows', () => {
  it('normalizes known websocket event type', () => {
    const store = withStore()
    const event = store.normalizeIncoming('ai', JSON.stringify({ event: 'task_finished', message: 'done' }))

    expect(event?.type).toBe('task_finished')
    expect(event?.payload.message).toBe('done')
  })

  it('falls back to channel-based type for unknown payload', () => {
    const store = withStore()
    const event = store.normalizeIncoming('logs', 'not-json')

    expect(event?.type).toBe('runtime_event')
  })

  it('marks UI stale when no events were received', () => {
    const store = withStore()
    store.markStaleIfNeeded(10)

    expect(store.staleUi).toBe(true)
  })
})
