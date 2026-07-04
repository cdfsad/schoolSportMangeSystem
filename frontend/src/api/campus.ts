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

export interface CampusPayload {
  name: string
  code: string
  address?: string
  is_active?: boolean
  sort_order?: number
}

// listCampuses 复用 place.ts 的同名导出(单一来源),供 campus 页用
export { listCampuses } from './place'

export function createCampus(payload: CampusPayload) {
  return request.post('/campuses/', payload) as unknown as Promise<Campus>
}

export function updateCampus(id: number, payload: Partial<CampusPayload>) {
  return request.patch(`/campuses/${id}/`, payload) as unknown as Promise<Campus>
}

export function deleteCampus(id: number) {
  return request.delete(`/campuses/${id}/`) as unknown as Promise<void>
}
