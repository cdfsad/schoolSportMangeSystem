import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

const service: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

// 请求拦截:携带 JWT
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// 响应拦截:剥包到 data;统一错误处理
service.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail || error.response?.data || error.message
    if (status === 401) {
      // token 失效:清理 + 跳登录(简化版;P2c 可扩展 refresh 自动续期)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      if (window.location.pathname !== '/login') {
        ElMessage.error('登录已过期,请重新登录')
        window.location.href = '/login'
      }
    } else if (status === 403) {
      ElMessage.error('无权限访问')
    } else if (status && status >= 400) {
      const msg = typeof detail === 'string' ? detail : JSON.stringify(detail)
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  },
)

export default service
