import { http } from './client'

export const listHoldings = () => http.get('/api/holdings')
export const createHolding = (payload) => http.post('/api/holdings', payload)
export const updateHolding = (id, payload) => http.put(`/api/holdings/${id}`, payload)
export const deleteHolding = (id) => http.delete(`/api/holdings/${id}`)
