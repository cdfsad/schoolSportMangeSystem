import request from './request'
import type { Paginated } from './types'

export interface User {
  id: number
  username: string
  first_name: string
  id_number: string
  role: string
  phone: string
  college: string
  date_joined: string
}

export interface UserPayload {
  username?: string
  first_name?: string
  id_number?: string
  role?: string
  phone?: string
  college?: string
  password?: string
}

export function listUsers(params?: { page?: number; search?: string }) {
  return request.get('/users/', { params }) as unknown as Promise<Paginated<User>>
}

export function createUser(payload: UserPayload) {
  return request.post('/users/', payload) as unknown as Promise<User>
}

export function updateUser(id: number, payload: Partial<UserPayload>) {
  return request.patch(`/users/${id}/`, payload) as unknown as Promise<User>
}

export function deleteUser(id: number) {
  return request.delete(`/users/${id}/`) as unknown as Promise<void>
}

export function importUsers(file: File) {
  const form = new FormData()
  form.append('file', file)
  return request.post('/users/import/', form) as unknown as Promise<{
    success: number
    skipped: number
    error: string | null
  }>
}
