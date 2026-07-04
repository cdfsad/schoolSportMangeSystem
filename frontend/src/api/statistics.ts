import request from './request'

export interface Statistics {
  legend: string[]
  series: number[]
}

export function getStatistics() {
  return request.get('/statistics/') as unknown as Promise<Statistics>
}
