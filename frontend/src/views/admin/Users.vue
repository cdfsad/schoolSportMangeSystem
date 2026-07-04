<template>
  <el-card>
    <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
      <div style="display: flex; gap: 12px">
        <el-input
          v-model="filters.search"
          placeholder="搜索学号/姓名"
          clearable
          style="width: 220px"
          @keyup.enter="reload"
          @clear="reload"
        />
        <el-button @click="reload">搜索</el-button>
      </div>
      <div style="display: flex; gap: 12px">
        <el-upload :show-file-list="false" :before-upload="handleImport" accept=".xlsx,.xls">
          <el-button type="success">Excel 导入</el-button>
        </el-upload>
        <el-button type="primary" @click="openCreate">新增用户</el-button>
      </div>
    </div>

    <el-table v-loading="loading" :data="users" border stripe>
      <el-table-column prop="id_number" label="学号" width="150" />
      <el-table-column prop="first_name" label="姓名" width="100" />
      <el-table-column label="角色" width="110">
        <template #default="{ row }">
          <el-tag :type="roleType(row.role)">{{ roleLabel(row.role) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="手机" width="140" />
      <el-table-column prop="college" label="学院" show-overflow-tooltip />
      <el-table-column label="注册时间" width="170">
        <template #default="{ row }">{{ formatDate(row.date_joined) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page"
      :total="total"
      :page-size="pageSize"
      :page-sizes="[10, 20, 50]"
      layout="prev, pager, next, total, sizes"
      style="margin-top: 16px; justify-content: flex-end"
      @current-change="loadList"
      @size-change="handleSizeChange"
    />

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑用户' : '新增用户'" width="560px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="学号" required>
          <el-input v-model="form.id_number" placeholder="学号/手机号" />
        </el-form-item>
        <el-form-item label="姓名" required>
          <el-input v-model="form.first_name" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="学生/普通用户" value="student" />
            <el-option label="工作人员" value="staff" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="手机">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="学院">
          <el-input v-model="form.college" />
        </el-form-item>
        <el-form-item :label="editing ? '重置密码' : '密码'" :required="!editing">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            :placeholder="editing ? '留空则不修改' : '初始密码'"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadRawFile } from 'element-plus'
import {
  createUser,
  deleteUser,
  importUsers,
  listUsers,
  updateUser,
  type User,
} from '@/api/user'

const users = ref<User[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive({ search: '' })

const dialogVisible = ref(false)
const editing = ref<User | null>(null)
const submitting = ref(false)
const form = reactive({
  id_number: '',
  first_name: '',
  role: 'student',
  phone: '',
  college: '',
  password: '',
})

function roleLabel(role: string) {
  return ({ student: '学生', staff: '工作人员', admin: '管理员' } as Record<string, string>)[role] || role
}

function roleType(role: string) {
  return ({ student: 'info', staff: 'warning', admin: 'danger' } as Record<string, 'info' | 'warning' | 'danger'>)[
    role
  ] || 'info'
}

function formatDate(s: string) {
  return s ? new Date(s).toLocaleString('zh-CN') : ''
}

function reload() {
  page.value = 1
  loadList()
}

async function loadList() {
  loading.value = true
  try {
    const data = await listUsers({ page: page.value, search: filters.search || undefined })
    users.value = data.results
    total.value = data.count
  } finally {
    loading.value = false
  }
}

function handleSizeChange(size: number) {
  pageSize.value = size
  reload()
}

function openCreate() {
  editing.value = null
  Object.assign(form, {
    id_number: '',
    first_name: '',
    role: 'student',
    phone: '',
    college: '',
    password: '',
  })
  dialogVisible.value = true
}

function openEdit(row: User) {
  editing.value = row
  Object.assign(form, {
    id_number: row.id_number,
    first_name: row.first_name,
    role: row.role,
    phone: row.phone,
    college: row.college,
    password: '',
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.id_number || !form.first_name) {
    ElMessage.warning('请填写学号和姓名')
    return
  }
  if (!editing.value && !form.password) {
    ElMessage.warning('请设置初始密码')
    return
  }
  submitting.value = true
  try {
    if (editing.value) {
      const payload: Record<string, unknown> = { ...form }
      if (!payload.password) delete payload.password
      await updateUser(editing.value.id, payload)
      ElMessage.success('已更新')
    } else {
      await createUser(form)
      ElMessage.success('已新增')
    }
    dialogVisible.value = false
    await loadList()
  } catch {
    // 错误由请求拦截器提示
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row: User) {
  try {
    await ElMessageBox.confirm(`确定删除用户「${row.first_name || row.username}」吗?`, '提示', {
      type: 'warning',
    })
  } catch {
    return // 用户取消
  }
  await deleteUser(row.id)
  ElMessage.success('已删除')
  await loadList()
}

async function handleImport(file: UploadRawFile) {
  try {
    const res = await importUsers(file)
    ElMessage.success(`导入成功 ${res.success} 条,跳过 ${res.skipped} 条${res.error ? ':' + res.error : ''}`)
    await loadList()
  } catch {
    // 错误由请求拦截器提示
  }
  return false // 阻止 el-upload 默认上传行为
}

onMounted(loadList)
</script>
