import { reactive } from 'vue'

export const toasts = reactive([])

export function pushToast(message, type = 'success') {
  const id = Date.now() + Math.random()
  toasts.push({ id, message, type })
  window.setTimeout(() => {
    const index = toasts.findIndex((toast) => toast.id === id)
    if (index !== -1) {
      toasts.splice(index, 1)
    }
  }, 3200)
}
