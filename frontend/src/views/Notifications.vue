<template>
  <el-card>
    <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
      <h3 style="margin: 0">我的通知</h3>
      <el-button type="primary" @click="handleReadAll">全部已读</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border stripe>
      <el-table-column label="类型" width="120">
        <template #default="{ row }">
          <el-tag :type="typeTag(row.type)">{{ row.type_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="content" label="内容" show-overflow-tooltip />
      <el-table-column label="时间" width="170">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag v-if="!row.is_read" type="danger" size="small">未读</el-tag>
          <el-tag v-else type="info" size="small">已读</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button v-if="!row.is_read" size="small" @click="handleMarkRead(row)">标记已读</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page"
      :total="total"
      :page-size="20"
      layout="prev, pager, next, total"
      style="margin-top: 16px; justify-content: flex-end"
      @current-change="loadList"
    />
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  listNotifications,
  markAllAsRead,
  markAsRead,
  type Notification,
} from '@/api/notification'

const TYPE_TAG: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
  booking_submitted: 'info',
  booking_approved: 'success',
  booking_rejected: 'danger',
  booking_reminder: 'warning',
  booking_no_show: 'warning',
  system: 'info',
}

const rows = ref<Notification[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)

function typeTag(t: string) {
  return TYPE_TAG[t] || 'info'
}

function formatDate(s: string) {
  return s ? new Date(s).toLocaleString('zh-CN') : ''
}

async function loadList() {
  loading.value = true
  try {
    const data = await listNotifications({ page: page.value })
    rows.value = data.results
    total.value = data.count
  } finally {
    loading.value = false
  }
}

async function handleMarkRead(row: Notification) {
  await markAsRead(row.id)
  row.is_read = true
  ElMessage.success('已标记')
}

async function handleReadAll() {
  await markAllAsRead()
  ElMessage.success('全部已读')
  await loadList()
}

onMounted(loadList)
</script>
