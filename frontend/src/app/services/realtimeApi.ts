const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export function wsBaseUrl(): string {
  if (API_BASE.startsWith('https://')) return API_BASE.replace('https://', 'wss://').replace(/\/api\/v1\/?$/, '')
  return API_BASE.replace('http://', 'ws://').replace(/\/api\/v1\/?$/, '')
}

export function wsUrl(path: string): string {
  const base = wsBaseUrl().replace(/\/$/, '')
  const suffix = path.startsWith('/') ? path : '/' + path
  return base + suffix
}
