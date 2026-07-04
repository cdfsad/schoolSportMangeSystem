import request from './request'
import type { Paginated } from './types'

export interface Notification {
  id: number
  type: string
  type_display: string
  title: string
  content: string
  is_read: boolean
  created_at: string
}

export function listNotifications(params?: { page?: number }) {
  return request.get('/notifications/', { params }) as unknown as Promise<Paginated<Notification>>
}

export function markAsRead(id: number) {
  return request.patch(`/notifications/${id}/`, { is_read: true }) as unknown as Promise<Notification>
}

export function markAllAsRead() {
  return request.post('/notifications/read-all/') as unknown as Promise<{ status: string }>
}

export function getUnreadCount() {
  return request.get('/notifications/unread-count/') as unknown as Promise<{ count: number }>
}
