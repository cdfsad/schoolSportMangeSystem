<template>
  <el-card>
    <div style="display: flex; gap: 12px; margin-bottom: 16px">
      <el-select
        v-model="filters.status"
        placeholder="全部状态"
        clearable
        style="width: 160px"
        @change="reload"
      >
        <el-option v-for="opt in STATUS_OPTIONS" :key="opt.value" :label="opt.label" :value="opt.value" />
      </el-select>
      <el-button @click="reload">刷新</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border stripe>
      <el-table-column label="预订人" width="120">
        <template #default="{ row }">{{ row.book_name?.first_name || row.book_name?.username }}</template>
      </el-table-column>
      <el-table-column label="场地">
        <template #default="{ row }">{{ row.place_name?.name }}</template>
      </el-table-column>
      <el-table-column prop="campus_name" label="校区" width="100" />
      <el-table-column prop="date" label="日期" width="120" />
      <el-table-column prop="time" label="时段" width="130" />
      <el-table-column prop="people" label="人数" width="70" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ row.status_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="审批人" width="110">
        <template #default="{ row }">{{ row.approver?.first_name || row.approver?.username || '-' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <template v-if="row.status === 0">
            <el-button type="success" size="small" @click="handleApprove(row)">通过</el-button>
            <el-button type="warning" size="small" @click="openReject(row)">拒绝</el-button>
          </template>
          <el-button v-if="row.status === 0 || row.status === 1" size="small" @click="handleCancel(row)">
            取消
          </el-button>
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

    <el-dialog v-model="rejectDialogVisible" title="拒绝预约" width="480px">
      <el-form label-width="90px">
        <el-form-item label="拒绝原因">
          <el-input v-model="rejectReason" type="textarea" :rows="3" placeholder="将通知预订人" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="warning" :loading="submitting" @click="handleReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  adminCancelBooking,
  approveBooking,
  listAllBookings,
  rejectBooking,
  type Booking,
} from '@/api/booking'

const STATUS_OPTIONS = [
  { value: 0, label: '待审批' },
  { value: 1, label: '已通过' },
  { value: 2, label: '已拒绝' },
  { value: 3, label: '已取消' },
  { value: 4, label: '已完成' },
  { value: 5, label: '已违约' },
]

const STATUS_TAG: Record<number, 'info' | 'success' | 'warning' | 'danger'> = {
  0: 'warning',
  1: 'success',
  2: 'danger',
  3: 'info',
  4: 'success',
  5: 'warning',
}

const rows = ref<Booking[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive({ status: undefined as number | undefined })

const rejectDialogVisible = ref(false)
const rejectTarget = ref<Booking | null>(null)
const rejectReason = ref('')
const submitting = ref(false)

function statusType(status: number) {
  return STATUS_TAG[status] || 'info'
}

function reload() {
  page.value = 1
  loadList()
}

async function loadList() {
  loading.value = true
  try {
    const data = await listAllBookings({ status: filters.status, page: page.value })
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

async function handleApprove(row: Booking) {
  try {
    await ElMessageBox.confirm(`确认通过预约「${row.place_name?.name} ${row.date}」?`, '提示', {
      type: 'success',
    })
  } catch {
    return
  }
  await approveBooking(row.id)
  ElMessage.success('已通过')
  await loadList()
}

function openReject(row: Booking) {
  rejectTarget.value = row
  rejectReason.value = ''
  rejectDialogVisible.value = true
}

async function handleReject() {
  if (!rejectTarget.value) return
  submitting.value = true
  try {
    await rejectBooking(rejectTarget.value.id, rejectReason.value)
    ElMessage.success('已拒绝')
    rejectDialogVisible.value = false
    await loadList()
  } catch {
    // 错误由请求拦截器提示
  } finally {
    submitting.value = false
  }
}

async function handleCancel(row: Booking) {
  try {
    await ElMessageBox.confirm(`确认取消预约「${row.place_name?.name} ${row.date}」?`, '提示', {
      type: 'warning',
    })
  } catch {
    return
  }
  await adminCancelBooking(row.id)
  ElMessage.success('已取消')
  await loadList()
}

async function handleDelete(row: Booking) {
  try {
    await ElMessageBox.confirm('确认删除该预约记录吗?(不可恢复)', '危险操作', { type: 'warning' })
  } catch {
    return
  }
  await adminCancelBooking(row.id)
  ElMessage.success('已删除')
  await loadList()
}

onMounted(loadList)
</script>
