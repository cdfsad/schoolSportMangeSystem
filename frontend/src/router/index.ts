import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

declare module 'vue-router' {
  interface RouteMeta {
    public?: boolean
    roles?: string[]
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('@/views/Home.vue') },
      { path: 'places', name: 'place-list', component: () => import('@/views/PlaceList.vue') },
      {
        path: 'places/:id',
        name: 'place-detail',
        component: () => import('@/views/PlaceDetail.vue'),
        props: true,
      },
      {
        path: 'my-bookings',
        name: 'my-bookings',
        component: () => import('@/views/MyBookings.vue'),
      },
      { path: 'profile', name: 'profile', component: () => import('@/views/Profile.vue') },
      {
        path: 'notifications',
        name: 'notifications',
        component: () => import('@/views/Notifications.vue'),
      },
    ],
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { roles: ['admin'] },
    children: [
      {
        path: '',
        name: 'admin-dashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
      },
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('@/views/admin/Users.vue'),
      },
      {
        path: 'places',
        name: 'admin-places',
        component: () => import('@/views/admin/Places.vue'),
      },
      {
        path: 'campuses',
        name: 'admin-campuses',
        component: () => import('@/views/admin/Campuses.vue'),
      },
      {
        path: 'time-slots',
        name: 'admin-time-slots',
        component: () => import('@/views/admin/TimeSlots.vue'),
      },
      {
        path: 'bookings',
        name: 'admin-bookings',
        component: () => import('@/views/admin/Bookings.vue'),
      },
      {
        path: 'rules',
        name: 'admin-rules',
        component: () => import('@/views/admin/BookingRules.vue'),
      },
      {
        path: 'audit-logs',
        name: 'admin-audit-logs',
        component: () => import('@/views/admin/AuditLogs.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const userStore = useUserStore()

  // 已登录访问登录页 → 跳首页
  if (to.name === 'login' && userStore.token) {
    return { name: 'home' }
  }
  // 公开页直接放行
  if (to.meta.public) {
    return true
  }
  // 未登录 → 登录(带 redirect)
  if (!userStore.token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  // 深链竞态:有 token 但 user 未加载,先补拉(角色校验前置)
  if (!userStore.user) {
    try {
      await userStore.loadUserInfo()
    } catch {
      // loadUserInfo 失败(token 失效等)→ 请求拦截器已跳登录,此处兜底
      return { name: 'login', query: { redirect: to.fullPath } }
    }
  }
  // 角色校验(meta.roles 不含当前 role → 踢回首页)
  const roles = to.meta.roles
  if (roles && !roles.includes(userStore.user?.role || '')) {
    ElMessage.error('无权限访问该页面')
    return { name: 'home' }
  }
  return true
})

export default router
