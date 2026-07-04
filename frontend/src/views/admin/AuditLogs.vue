<template>
  <el-card>
    <div style="display: flex; gap: 12px; margin-bottom: 16px">
      <el-input
        v-model="filters.action"
        placeholder="动作(如 approve)"
        clearable
        style="width: 180px"
        @keyup.enter="reload"
        @clear="reload"
      />
      <el-input
        v-model="filters.target_model"
        placeholder="目标模型(如 Book)"
        clearable
        style="width: 180px"
        @keyup.enter="reload"
        @clear="reload"
      />
      <el-button @click="reload">搜索</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border stripe>
      <el-table-column type="expand">
        <template #default="{ row }">
          <pre style="margin: 0; padding: 0 20px; font-size: 12px">{{ JSON.stringify(row.detail, null, 2) }}</pre>
        </template>
      </el-table-column>
      <el-table-column prop="username" label="操作人" width="120" />
      <el-table-column label="动作" width="100">
        <template #default="{ row }">
          <el-tag :type="actionType(row.action)">{{ row.action }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="target_model" label="目标模型" width="120" />
      <el-table-column prop="target_id" label="目标 ID" width="100" />
      <el-table-column prop="ip" label="IP" width="140" />
      <el-table-column label="时间" width="180">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page"
      :total="total"
      :page-size="pageSize"
      :page-sizes="[20, 50, 100]"
      layout="prev, pager, next, total, sizes"
      style="margin-top: 16px; justify-content: flex-end"
      @current-change="loadList"
      @size-change="handleSizeChange"
    />
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { listAuditLogs, type AuditLog } from '@/api/audit-log'

const rows = ref<AuditLog[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive({ action: '', target_model: '' })

const ACTION_TAG: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
  create: 'success',
  approve: 'success',
  reject: 'danger',
  cancel: 'warning',
  delete: 'danger',
  update: 'info',
}

function actionType(action: string) {
  return ACTION_TAG[action] || 'info'
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
    const data = await listAuditLogs({
      action: filters.action || undefined,
      target_model: filters.target_model || undefined,
      page: page.value,
    })
    rows.value = data.results
    total.value = data.count
  } finally {
    loading.value = false
  }
}

function handleSizeChange(size: number) {
  pageSize.value = size
  reload()
}

onMounted(loadList)
</script>
