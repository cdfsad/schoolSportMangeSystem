import request from './request'
import type { Paginated } from './types'

export interface Campus {
  id: number
  name: string
  code: string
  address: string
  is_active: boolean
  sort_order: number
}

export interface Place {
  id: number
  name: string
  campus: number
  campus_name: string
  people: string
  capacity: number
  place_type: string
  location: string
  use: number
  is_deleted: boolean
}

export interface TimeSlot {
  id: number
  start_time: string
  end_time: string
  is_active: boolean
}

export interface PlacePayload {
  name: string
  campus: number
  people?: string
  capacity?: number
  place_type?: string
  location?: string
  use?: number
}

// 学生端只读接口
export function listPlaces(params?: { campus?: number; search?: string; page?: number }) {
  return request.get('/places/', { params }) as unknown as Promise<Paginated<Place>>
}

export function getPlace(id: number) {
  return request.get(`/places/${id}/`) as unknown as Promise<Place>
}

export function listTimeSlots(placeId: number) {
  return request.get(`/places/${placeId}/time-slots/`) as unknown as Promise<TimeSlot[]>
}

export function listCampuses(params?: { page?: number }) {
  return request.get('/campuses/', { params }) as unknown as Promise<Paginated<Campus>>
}

// 管理端 CRUD
export function createPlace(payload: PlacePayload) {
  return request.post('/places/', payload) as unknown as Promise<Place>
}

export function updatePlace(id: number, payload: Partial<PlacePayload>) {
  return request.patch(`/places/${id}/`, payload) as unknown as Promise<Place>
}

export function deletePlace(id: number) {
  return request.delete(`/places/${id}/`) as unknown as Promise<void>
}
