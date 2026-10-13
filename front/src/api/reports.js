import { http } from './client'

export function listReports(threadId) {
  const query = threadId ? `?thread_id=${encodeURIComponent(threadId)}` : ''
  return http.get(`/api/reports${query}`)
}

export const updateReport = (id, payload) => http.patch(`/api/reports/${id}`, payload)
export const deleteReport = (id) => http.delete(`/api/reports/${id}`)
