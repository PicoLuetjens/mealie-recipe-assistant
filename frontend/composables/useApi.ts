import type { Health, LoginResponse, MealieCreateResponse, RecipeDraft, User, UserCreate, UserUpdate } from '~/types/api'

export function useApi() {
  const config = useRuntimeConfig()
  const token = useState<string | null>('token', () => null)
  const user = useState<User | null>('user', () => null)
  async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers)
    if (token.value) headers.set('Authorization', `Bearer ${token.value}`)
    if (options.body && !(options.body instanceof FormData)) headers.set('Content-Type', 'application/json')
    try { return await $fetch<T>(`${config.public.apiBase}${path}`, { ...options, headers }) }
    catch (error: unknown) { const message = error instanceof Error ? error.message : 'Unbekannter API-Fehler'; throw new Error(message) }
  }
  async function login(email: string, password: string) { const data = await request<LoginResponse>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }); token.value = data.access_token; user.value = data.user }
  async function logout() { token.value = null; user.value = null }
  return { token, user, health: () => request<Health>('/health'), login, logout, me: () => request<User>('/auth/me'), users: () => request<User[]>('/users'), createUser: (body: UserCreate) => request<User>('/users', { method: 'POST', body: JSON.stringify(body) }), updateUser: (id: number, body: UserUpdate) => request<User>(`/users/${id}`, { method: 'PATCH', body: JSON.stringify(body) }), generate: (message: string, servings: number) => request<RecipeDraft>('/recipes/generate', { method: 'POST', body: JSON.stringify({ message, servings }) }), transcribe: (audio: Blob) => { const form = new FormData(); form.append('audio', audio, 'aufnahme.webm'); return request<{ text: string }>('/recipes/transcribe', { method: 'POST', body: form }) }, publish: (recipe: RecipeDraft, withImage: boolean) => request<MealieCreateResponse>(`/recipes/publish?with_image=${withImage}`, { method: 'POST', body: JSON.stringify(recipe) }) }
}

