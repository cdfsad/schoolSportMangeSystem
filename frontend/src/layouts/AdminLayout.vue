<template>
  <el-container style="height: 100vh">
    <el-aside width="220px" style="background: #304156">
      <div class="logo">场馆管理后台</div>
      <el-menu
        :default-active="route.path"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/admin">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/places">
          <el-icon><Location /></el-icon>
          <span>场地管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/campuses">
          <el-icon><School /></el-icon>
          <span>校区管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/time-slots">
          <el-icon><Clock /></el-icon>
          <span>时段管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/bookings">
          <el-icon><Calendar /></el-icon>
          <span>预约审批</span>
        </el-menu-item>
        <el-menu-item index="/admin/rules">
          <el-icon><Setting /></el-icon>
          <span>预约规则</span>
        </el-menu-item>
        <el-menu-item index="/admin/audit-logs">
          <el-icon><Document /></el-icon>
          <span>审计日志</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header
        style="
          background: #fff;
          border-bottom: 1px solid #e6e6e6;
          display: flex;
          align-items: center;
          justify-content: space-between;
        "
      >
        <el-button text @click="router.push('/')">
          <el-icon><ArrowLeft /></el-icon>
          返回前台
        </el-button>
        <el-dropdown>
          <span style="cursor: pointer; display: flex; align-items: center; gap: 6px">
            <el-icon><User /></el-icon>
            {{ userStore.user?.first_name || userStore.user?.username || '管理员' }}
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
  </el-container>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowDown,
  ArrowLeft,
  Calendar,
  Clock,
  DataAnalysis,
  Document,
  Location,
  School,
  Setting,
  User,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 进入管理后台时若已登录但未加载用户信息,则补拉一次
if (userStore.token && !userStore.user) {
  userStore.loadUserInfo().catch(() => {})
}

async function handleLogout() {
  await userStore.logout()
  router.push('/login')
}
</script>

<style scoped lang="scss">
.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  background: #2b3a4d;
}

.el-menu {
  border-right: none;
}
</style>
