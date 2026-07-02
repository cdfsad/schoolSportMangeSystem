import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

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
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const userStore = useUserStore()
  // 未登录访问受保护页 → 跳登录(带 redirect)
  if (!to.meta.public && !userStore.token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  // 已登录访问登录页 → 跳首页
  if (to.name === 'login' && userStore.token) {
    return { name: 'home' }
  }
})

export default router
