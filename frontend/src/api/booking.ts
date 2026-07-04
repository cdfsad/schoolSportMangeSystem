import request from './request'
import type { Paginated } from './types'

export interface BookingUser {
  id: number
  username: string
  first_name: string
  id_number: string
  role: string
}

export interface BookingPlace {
  id: number
  name: string
  campus_name: string
  place_type: string
}

export interface Booking {
  id: number
  book_name: BookingUser
  place_name: BookingPlace
  campus: number
  campus_name: string
  people: string
  date: string
  time: string
  status: number
  status_display: string
  approver: { id: number; username: string; first_name: string } | null
  approved_at: string | null
  reject_reason: string
  created_at: string
}

export interface CreateBookingPayload {
  place: number
  date: string
  bkTime: string
  people: string
  campus?: string | number
}

// 学生端
export function listMyBookings(params?: { page?: number; status?: number }) {
  return request.get('/books/', { params }) as unknown as Promise<Paginated<Booking>>
}

export function createBooking(payload: CreateBookingPayload) {
  return request.post('/books/', payload) as unknown as Promise<Booking>
}

export function cancelBooking(id: number) {
  return request.post(`/books/${id}/cancel/`) as unknown as Promise<{ status: string }>
}

// 管理端:列出全部预约(可按 status/place/campus/date 过滤)
export function listAllBookings(params?: {
  page?: number
  status?: number
  place_name?: number
  campus?: number
  date?: string
}) {
  return request.get('/books/', { params }) as unknown as Promise<Paginated<Booking>>
}

export function approveBooking(id: number) {
  return request.post(`/books/${id}/approve/`) as unknown as Promise<Booking>
}

export function rejectBooking(id: number, reject_reason: string) {
  return request.post(`/books/${id}/reject/`, { reject_reason }) as unknown as Promise<Booking>
}

export function adminCancelBooking(id: number) {
  return request.delete(`/books/${id}/`) as unknown as Promise<void>
}
