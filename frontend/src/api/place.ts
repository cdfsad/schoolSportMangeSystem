import request from './request'

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
}

export interface Campus {
  id: number
  name: string
  code: string
  address: string
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface TimeSlot {
  id: number
  start_time: string
  end_time: string
  is_active: boolean
}

export function listPlaces(params?: { campus?: number; search?: string; page?: number }) {
  return request.get('/places/', { params }) as unknown as Promise<Paginated<Place>>
}

export function getPlace(id: number) {
  return request.get(`/places/${id}/`) as unknown as Promise<Place>
}

export function listTimeSlots(placeId: number) {
  return request.get(`/places/${placeId}/time-slots/`) as unknown as Promise<TimeSlot[]>
}

export function listCampuses() {
  return request.get('/campuses/') as unknown as Promise<Paginated<Campus>>
}
