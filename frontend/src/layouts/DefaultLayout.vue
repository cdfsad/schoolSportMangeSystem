<template>
  <el-container style="height: 100vh">
    <el-header
      style="
        background: #fff;
        border-bottom: 1px solid #e6e6e6;
        display: flex;
        align-items: center;
        justify-content: space-between;
      "
    >
      <div style="display: flex; align-items: center; gap: 32px">
        <h3 style="margin: 0; color: #409eff; white-space: nowrap">高校体育场馆管理系统</h3>
        <el-menu
          mode="horizontal"
          :router="true"
          :default-active="route.path"
          style="border: none"
        >
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/places">场地</el-menu-item>
          <el-menu-item index="/my-bookings">我的预约</el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/admin">管理后台</el-menu-item>
        </el-menu>
      </div>
      <div style="display: flex; align-items: center; gap: 16px">
        <el-badge
          :value="unreadCount"
          :hidden="unreadCount === 0"
          :max="99"
          class="bell-badge"
        >
          <el-icon :size="20" style="cursor: pointer" @click="router.push('/notifications')">
            <Bell />
          </el-icon>
        </el-badge>
        <el-dropdown>
        <span style="cursor: pointer; display: flex; align-items: center; gap: 6px">
          <el-icon><User /></el-icon>
          {{ userStore.user?.first_name || userStore.user?.username || '用户' }}
          <el-icon><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="router.push('/profile')">个人中心</el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      </div>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown, Bell, User } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getUnreadCount } from '@/api/notification'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const unreadCount = ref(0)
let pollTimer: ReturnType<typeof setInterval> | null = null

// 进入布局时若已登录但未加载用户信息,则补拉一次
if (userStore.token && !userStore.user) {
  userStore.loadUserInfo().catch(() => {})
}

async function loadUnread() {
  if (!userStore.token) return
  try {
    const data = await getUnreadCount()
    unreadCount.value = data.count
  } catch {
    // 401 等由拦截器处理
  }
}

onMounted(() => {
  loadUnread()
  pollTimer = setInterval(loadUnread, 30000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

async function handleLogout() {
  await userStore.logout()
  router.push('/login')
}
</script>
