import request from './request'

export interface LoginPayload {
  username: string
  password: string
}

export interface LoginResult {
  access: string
  refresh: string
}

export interface UserInfo {
  id: number
  username: string
  first_name: string
  id_number: string
  role: string
  phone: string
  college: string
  date_joined: string
}

export function login(payload: LoginPayload) {
  return request.post('/auth/login/', payload) as unknown as Promise<LoginResult>
}

export function fetchMe() {
  return request.get('/auth/me/') as unknown as Promise<UserInfo>
}

export function logout(refresh: string) {
  return request.post('/auth/logout/', { refresh }) as unknown as Promise<{ detail: string }>
}
