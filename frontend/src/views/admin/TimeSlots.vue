<template>
  <el-card>
    <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
      <el-select
        v-model="filters.campus"
        placeholder="全部校区"
        clearable
        style="width: 160px"
        @change="reload"
      >
        <el-option v-for="c in campuses" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-button type="primary" @click="openCreate">新增时段</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border stripe>
      <el-table-column label="校区">
        <template #default="{ row }">{{ campusName(row.campus) }}</template>
      </el-table-column>
      <el-table-column prop="start_time" label="开始时间" width="140" />
      <el-table-column prop="end_time" label="结束时间" width="140" />
      <el-table-column prop="sort_order" label="排序" width="80" />
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

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑时段' : '新增时段'" width="480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="校区" required>
          <el-select v-model="form.campus" style="width: 100%">
            <el-option v-for="c in campuses" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间" required>
          <el-time-picker v-model="form.start_time" value-format="HH:mm:ss" format="HH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间" required>
          <el-time-picker v-model="form.end_time" value-format="HH:mm:ss" format="HH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
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
import { listCampuses, type Campus } from '@/api/place'
import {
  createTimeSlot,
  deleteTimeSlot,
  listTimeSlots,
  updateTimeSlot,
  type TimeSlot,
} from '@/api/time-slot'

const rows = ref<TimeSlot[]>([])
const campuses = ref<Campus[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive({ campus: undefined as number | undefined })

const dialogVisible = ref(false)
const editing = ref<TimeSlot | null>(null)
const submitting = ref(false)
const form = reactive({
  campus: undefined as number | undefined,
  start_time: '08:00:00',
  end_time: '09:00:00',
  sort_order: 0,
  is_active: true,
})

function campusName(id: number) {
  return campuses.value.find((c) => c.id === id)?.name || id
}

function reload() {
  page.value = 1
  loadList()
}

async function loadList() {
  loading.value = true
  try {
    const data = await listTimeSlots({ campus: filters.campus, page: page.value })
    rows.value = data.results
    total.value = data.count
  } finally {
    loading.value = false
  }
}

async function loadCampuses() {
  const data = await listCampuses()
  campuses.value = data.results
}

function handleSizeChange(size: number) {
  pageSize.value = size
  reload()
}

function openCreate() {
  editing.value = null
  Object.assign(form, {
    campus: campuses.value[0]?.id,
    start_time: '08:00:00',
    end_time: '09:00:00',
    sort_order: 0,
    is_active: true,
  })
  dialogVisible.value = true
}

function openEdit(row: TimeSlot) {
  editing.value = row
  Object.assign(form, {
    campus: row.campus,
    start_time: row.start_time,
    end_time: row.end_time,
    sort_order: row.sort_order,
    is_active: row.is_active,
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.campus || !form.start_time || !form.end_time) {
    ElMessage.warning('请填写完整')
    return
  }
  submitting.value = true
  try {
    const payload = {
      campus: form.campus!,
      start_time: form.start_time,
      end_time: form.end_time,
      sort_order: form.sort_order,
      is_active: form.is_active,
    }
    if (editing.value) {
      await updateTimeSlot(editing.value.id, payload)
      ElMessage.success('已更新')
    } else {
      await createTimeSlot(payload)
      ElMessage.success('已新增')
    }
    dialogVisible.value = false
    await loadList()
  } catch {
    // 错误由请求拦截器提示(unique_together 等)
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row: TimeSlot) {
  try {
    await ElMessageBox.confirm('确定删除该时段吗?', '提示', { type: 'warning' })
  } catch {
    return
  }
  await deleteTimeSlot(row.id)
  ElMessage.success('已删除')
  await loadList()
}

onMounted(async () => {
  await loadCampuses()
  await loadList()
})
</script>
