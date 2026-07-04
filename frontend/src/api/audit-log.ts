import request from './request'
import type { Paginated } from './types'

export interface AuditLog {
  id: number
  user: number | null
  username: string
  action: string
  target_model: string
  target_id: string
  detail: Record<string, unknown>
  ip: string | null
  created_at: string
}

export function listAuditLogs(params?: {
  page?: number
  action?: string
  target_model?: string
  user?: number
}) {
  return request.get('/audit-logs/', { params }) as unknown as Promise<Paginated<AuditLog>>
}
