import request from './request'

export interface Booking {
  id: number
  book_name: { id: number; username: string; first_name: string }
  place_name: { id: number; name: string }
  campus_name: string
  people: string
  date: string
  time: string
  status: number
  status_display: string
  created_at: string
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface CreateBookingPayload {
  place: number
  date: string
  bkTime: string
  people: string
  campus?: string | number
}

export function listMyBookings(params?: { page?: number; status?: number }) {
  return request.get('/books/', { params }) as unknown as Promise<Paginated<Booking>>
}

export function createBooking(payload: CreateBookingPayload) {
  return request.post('/books/', payload) as unknown as Promise<Booking>
}

export function cancelBooking(id: number) {
  return request.post(`/books/${id}/cancel/`) as unknown as Promise<{ status: string }>
}
