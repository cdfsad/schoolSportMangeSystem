/** DRF PageNumberPagination 响应壳(PAGE_SIZE=20)。 */
export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
