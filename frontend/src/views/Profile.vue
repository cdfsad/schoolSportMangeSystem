<template>
  <el-card style="max-width: 640px">
    <h3 style="margin-top: 0">个人信息</h3>
    <el-descriptions :column="1" border>
      <el-descriptions-item label="学号 / 用户名">{{ user?.username }}</el-descriptions-item>
      <el-descriptions-item label="姓名">{{ user?.first_name || '-' }}</el-descriptions-item>
      <el-descriptions-item label="角色">{{ roleText }}</el-descriptions-item>
      <el-descriptions-item label="手机号">{{ user?.phone || '-' }}</el-descriptions-item>
      <el-descriptions-item label="学院">{{ user?.college || '-' }}</el-descriptions-item>
    </el-descriptions>

    <el-divider content-position="left">修改密码</el-divider>
    <el-form :model="pwdForm" label-width="100px" style="max-width: 460px">
      <el-form-item label="旧密码">
        <el-input v-model="pwdForm.old_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="新密码">
        <el-input v-model="pwdForm.new_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="确认密码">
        <el-input v-model="pwdForm.confirm_password" type="password" show-password />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="submitting" @click="handleChangePwd">
          提交
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import request from '@/api/request'

const userStore = useUserStore()
const user = computed(() => userStore.user)
const submitting = ref(false)
const pwdForm = reactive({ old_password: '', new_password: '', confirm_password: '' })

const roleText = computed(() => {
  const map: Record<string, string> = { student: '学生', staff: '工作人员', admin: '管理员' }
  return map[user.value?.role || ''] || '未知'
})

async function handleChangePwd() {
  if (!pwdForm.old_password || !pwdForm.new_password) {
    ElMessage.warning('请填写完整')
    return
  }
  if (pwdForm.new_password !== pwdForm.confirm_password) {
    ElMessage.error('两次输入的新密码不一致')
    return
  }
  submitting.value = true
  try {
    await request.post('/auth/change-password/', pwdForm)
    ElMessage.success('密码已修改,请重新登录')
    pwdForm.old_password = pwdForm.new_password = pwdForm.confirm_password = ''
    await userStore.logout()
    window.location.href = '/login'
  } catch {
    // 错误由拦截器提示
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  if (!userStore.user) {
    userStore.loadUserInfo().catch(() => {})
  }
})
</script>
