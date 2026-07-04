<template>
  <div>
    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="总用户数" :value="stats.users" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="总场地数" :value="stats.places" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="待审批预约" :value="stats.pending" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="今日预约" :value="stats.today" />
        </el-card>
      </el-col>
    </el-row>

    <el-card v-loading="loading">
      <template #header>各场地预约统计</template>
      <v-chart v-if="chartOption" :option="chartOption" autoresize style="height: 400px" />
      <el-empty v-else description="暂无预约数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { listUsers } from '@/api/user'
import { listPlaces } from '@/api/place'
import { listAllBookings } from '@/api/booking'
import { getStatistics, type Statistics } from '@/api/statistics'

// 按需注册 echarts 模块(比全量引入节省 ~800KB)
use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])

const loading = ref(false)
const stats = reactive({ users: 0, places: 0, pending: 0, today: 0 })
const chartData = ref<Statistics>({ legend: [], series: [] })

const chartOption = computed(() => {
  if (chartData.value.legend.length === 0) return null
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: {
      type: 'category',
      data: chartData.value.legend,
      axisLabel: { rotate: 20 },
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      { name: '预约数', type: 'bar', data: chartData.value.series, itemStyle: { color: '#409eff' } },
    ],
  } as Record<string, unknown>
})

async function loadStats() {
  loading.value = true
  try {
    const today = new Date().toISOString().slice(0, 10)
    const [u, p, pending, todayBooks, chart] = await Promise.all([
      listUsers({ page: 1 }),
      listPlaces({ page: 1 }),
      listAllBookings({ status: 0, page: 1 }),
      listAllBookings({ date: today, page: 1 }),
      getStatistics(),
    ])
    stats.users = u.count
    stats.places = p.count
    stats.pending = pending.count
    stats.today = todayBooks.count
    chartData.value = chart
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>
