import request from './request'
import type { Paginated } from './types'

export interface BookingRule {
  id: number
  place: number | null
  place_type: string
  advance_days: number
  daily_limit_per_user: number
  cancel_deadline_hours: number
  is_active: boolean
}

export interface RulePayload {
  place?: number | null
  place_type?: string
  advance_days?: number
  daily_limit_per_user?: number
  cancel_deadline_hours?: number
  is_active?: boolean
}

export function listRules(params?: { page?: number }) {
  return request.get('/booking-rules/', { params }) as unknown as Promise<Paginated<BookingRule>>
}

export function createRule(payload: RulePayload) {
  return request.post('/booking-rules/', payload) as unknown as Promise<BookingRule>
}

export function updateRule(id: number, payload: Partial<RulePayload>) {
  return request.patch(`/booking-rules/${id}/`, payload) as unknown as Promise<BookingRule>
}

export function deleteRule(id: number) {
  return request.delete(`/booking-rules/${id}/`) as unknown as Promise<void>
}
