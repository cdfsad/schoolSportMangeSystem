import request from './request'
import type { Paginated } from './types'

export interface TimeSlot {
  id: number
  campus: number
  start_time: string
  end_time: string
  is_active: boolean
  sort_order: number
}

export interface TimeSlotPayload {
  campus: number
  start_time: string
  end_time: string
  is_active?: boolean
  sort_order?: number
}

export function listTimeSlots(params?: { campus?: number; page?: number }) {
  return request.get('/time-slots/', { params }) as unknown as Promise<Paginated<TimeSlot>>
}

export function createTimeSlot(payload: TimeSlotPayload) {
  return request.post('/time-slots/', payload) as unknown as Promise<TimeSlot>
}

export function updateTimeSlot(id: number, payload: Partial<TimeSlotPayload>) {
  return request.patch(`/time-slots/${id}/`, payload) as unknown as Promise<TimeSlot>
}

export function deleteTimeSlot(id: number) {
  return request.delete(`/time-slots/${id}/`) as unknown as Promise<void>
}
