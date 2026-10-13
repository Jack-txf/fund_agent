const API_BASE = import.meta.env.VITE_API_BASE ?? ''

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options)

  if (response.status === 204) {
    return null
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new Error(data?.detail ?? `请求失败（${response.status}）`)
  }

  return data
}

function jsonOptions(method, body) {
  return {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  }
}

export const http = {
  get: (path) => request(path),
  post: (path, body) => request(path, jsonOptions('POST', body)),
  put: (path, body) => request(path, jsonOptions('PUT', body)),
  patch: (path, body) => request(path, jsonOptions('PATCH', body)),
  delete: (path) => request(path, { method: 'DELETE' })
}
