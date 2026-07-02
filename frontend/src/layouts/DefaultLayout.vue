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
        </el-menu>
      </div>
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
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown, User } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 进入布局时若已登录但未加载用户信息,则补拉一次
if (userStore.token && !userStore.user) {
  userStore.loadUserInfo().catch(() => {})
}

async function handleLogout() {
  await userStore.logout()
  router.push('/login')
}
</script>
