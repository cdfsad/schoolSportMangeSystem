import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import * as authApi from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('access_token') || '')
  const refreshToken = ref<string>(localStorage.getItem('refresh_token') || '')
  const user = ref<authApi.UserInfo | null>(null)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(payload: authApi.LoginPayload) {
    const data = await authApi.login(payload)
    token.value = data.access
    refreshToken.value = data.refresh
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    await loadUserInfo()
  }

  async function loadUserInfo() {
    user.value = await authApi.fetchMe()
    return user.value
  }

  async function logout() {
    try {
      if (refreshToken.value) {
        await authApi.logout(refreshToken.value)
      }
    } catch {
      // 忽略登出接口错误,本地一定清理
    } finally {
      token.value = ''
      refreshToken.value = ''
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  return { token, refreshToken, user, isAdmin, login, loadUserInfo, logout }
})
