<template>
  <el-card>
    <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
      <h3 style="margin: 0">我的预约</h3>
      <el-button @click="loadList">刷新</el-button>
    </div>

    <el-table v-loading="loading" :data="bookings" border stripe>
      <el-table-column prop="place_name.name" label="场地" />
      <el-table-column prop="campus_name" label="校区" width="120" />
      <el-table-column prop="date" label="日期" width="120" />
      <el-table-column prop="time" label="时段" width="140" />
      <el-table-column prop="people" label="人数" width="80" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ row.status_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button
            type="danger"
            size="small"
            :disabled="row.status !== 0 && row.status !== 1"
            @click="handleCancel(row.id)"
          >
            取消
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { cancelBooking, listMyBookings, type Booking } from '@/api/booking'

const bookings = ref<Booking[]>([])
const loading = ref(false)

async function loadList() {
  loading.value = true
  try {
    const data = await listMyBookings()
    bookings.value = data.results
  } finally {
    loading.value = false
  }
}

function statusType(status: number) {
  const map: Record<number, string> = {
    0: 'warning',
    1: 'success',
    2: 'danger',
    3: 'info',
    4: '',
    5: 'danger',
  }
  return map[status] || ''
}

async function handleCancel(id: number) {
  await ElMessageBox.confirm('确定取消该预约吗?', '提示', { type: 'warning' })
  await cancelBooking(id)
  ElMessage.success('已取消')
  await loadList()
}

onMounted(loadList)
</script>
