<template>
  <div>
    <el-card>
      <h2 style="margin: 0 0 8px">欢迎,{{ userStore.user?.first_name || userStore.user?.username }}</h2>
      <p style="color: #888; margin: 0">角色:{{ roleText }}</p>
    </el-card>
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="8">
        <el-card shadow="hover" class="entry-card" @click="router.push('/places')">
          <el-icon size="36" color="#409eff"><OfficeBuilding /></el-icon>
          <h3>浏览场地</h3>
          <p>查看可预约的体育场馆</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="entry-card" @click="router.push('/my-bookings')">
          <el-icon size="36" color="#67c23a"><Calendar /></el-icon>
          <h3>我的预约</h3>
          <p>查看与管理你的预约</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" class="entry-card" @click="router.push('/profile')">
          <el-icon size="36" color="#e6a23c"><User /></el-icon>
          <h3>个人中心</h3>
          <p>修改密码与个人信息</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Calendar, OfficeBuilding, User } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const roleText = computed(() => {
  const map: Record<string, string> = { student: '学生', staff: '工作人员', admin: '管理员' }
  return map[userStore.user?.role || ''] || '未知'
})
</script>

<style scoped lang="scss">
.entry-card {
  cursor: pointer;
  text-align: center;
  transition: transform 0.2s;
  &:hover {
    transform: translateY(-4px);
  }
  h3 {
    margin: 12px 0 4px;
  }
  p {
    color: #888;
    margin: 0;
  }
}
</style>
