import { apiClient } from './apiClient'

export const deviceApi = {
  list: () => apiClient<{ usb_scan: Array<Record<string, string>>; usb_parser: Array<Record<string, string>>; ports: string[] }>('/devices'),
  dependencies: () => apiClient<{ items: Array<Record<string, string>> }>('/dependencies/check'),
  toolchains: () => apiClient<{ items: string[] }>('/toolchains'),
  toolchainsDetect: () => apiClient<{ items: Array<Record<string, string>> }>('/toolchains/detect'),
  environment: () => apiClient<{ paths: Record<string, string> }>('/environment'),
}
