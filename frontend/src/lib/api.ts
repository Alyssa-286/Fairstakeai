const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

const buildUrl = (path: string) => `${API_BASE}${path}`

export async function postJson<T>(path: string, body: Record<string, unknown>): Promise<T> {
  const response = await fetch(buildUrl(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    throw new Error((await response.text()) || 'Request failed')
  }
  return response.json()
}

export async function postFormData<T>(path: string, formData: FormData): Promise<T> {
  const response = await fetch(buildUrl(path), {
    method: 'POST',
    body: formData,
  })
  if (!response.ok) {
    throw new Error((await response.text()) || 'Upload failed')
  }
  return response.json()
}




