<template>
  <el-card>
    <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
      <span style="color: #909399; line-height: 32px">
        预约规则控制提前天数、每日上限、取消截止等(P3 接入校验,当前可配置)
      </span>
      <el-button type="primary" @click="openCreate">新增规则</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border stripe>
      <el-table-column label="适用场地" width="160">
        <template #default="{ row }">{{ row.place ? placeName(row.place) : '全部场地' }}</template>
      </el-table-column>
      <el-table-column label="场地类型" width="120">
        <template #default="{ row }">{{ row.place_type || '-' }}</template>
      </el-table-column>
      <el-table-column prop="advance_days" label="提前天数" width="100" />
      <el-table-column prop="daily_limit_per_user" label="每日上限" width="100" />
      <el-table-column prop="cancel_deadline_hours" label="取消截止(小时)" width="130" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '启用' : '停用' }}
          </el-tag>
        </template>
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

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑规则' : '新增规则'" width="540px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="适用场地">
          <el-select v-model="form.place" clearable placeholder="留空=全部场地" style="width: 100%">
            <el-option v-for="p in places" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="场地类型">
          <el-select v-model="form.place_type" clearable style="width: 100%">
            <el-option label="羽毛球" value="badminton" />
            <el-option label="篮球" value="basketball" />
            <el-option label="乒乓球" value="table_tennis" />
            <el-option label="健身房" value="gym" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="提前预约天数">
          <el-input-number v-model="form.advance_days" :min="0" :max="90" />
        </el-form-item>
        <el-form-item label="每日预约上限">
          <el-input-number v-model="form.daily_limit_per_user" :min="0" :max="20" />
        </el-form-item>
        <el-form-item label="取消截止(小时)">
          <el-input-number v-model="form.cancel_deadline_hours" :min="0" :max="72" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_active" />
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
import { listPlaces, type Place } from '@/api/place'
import { createRule, deleteRule, listRules, updateRule, type BookingRule } from '@/api/rule'

const rows = ref<BookingRule[]>([])
const places = ref<Place[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const dialogVisible = ref(false)
const editing = ref<BookingRule | null>(null)
const submitting = ref(false)
const form = reactive({
  place: null as number | null,
  place_type: '',
  advance_days: 7,
  daily_limit_per_user: 1,
  cancel_deadline_hours: 2,
  is_active: true,
})

function placeName(id: number) {
  return places.value.find((p) => p.id === id)?.name || id
}

function reload() {
  page.value = 1
  loadList()
}

async function loadList() {
  loading.value = true
  try {
    const data = await listRules({ page: page.value })
    rows.value = data.results
    total.value = data.count
  } finally {
    loading.value = false
  }
}

async function loadPlaces() {
  const data = await listPlaces({ page: 1 })
  places.value = data.results
}

function handleSizeChange(size: number) {
  pageSize.value = size
  reload()
}

function openCreate() {
  editing.value = null
  Object.assign(form, {
    place: null,
    place_type: '',
    advance_days: 7,
    daily_limit_per_user: 1,
    cancel_deadline_hours: 2,
    is_active: true,
  })
  dialogVisible.value = true
}

function openEdit(row: BookingRule) {
  editing.value = row
  Object.assign(form, {
    place: row.place,
    place_type: row.place_type,
    advance_days: row.advance_days,
    daily_limit_per_user: row.daily_limit_per_user,
    cancel_deadline_hours: row.cancel_deadline_hours,
    is_active: row.is_active,
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  submitting.value = true
  try {
    if (editing.value) {
      await updateRule(editing.value.id, form)
      ElMessage.success('已更新')
    } else {
      await createRule(form)
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

async function handleDelete(row: BookingRule) {
  try {
    await ElMessageBox.confirm('确定删除该规则吗?', '提示', { type: 'warning' })
  } catch {
    return
  }
  await deleteRule(row.id)
  ElMessage.success('已删除')
  await loadList()
}

onMounted(async () => {
  await loadPlaces()
  await loadList()
})
</script>
