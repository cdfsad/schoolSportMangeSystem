<template>
  <el-card>
    <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
      <div style="display: flex; gap: 12px">
        <el-select
          v-model="filters.campus"
          placeholder="全部校区"
          clearable
          style="width: 160px"
          @change="reload"
        >
          <el-option v-for="c in campuses" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-input
          v-model="filters.search"
          placeholder="搜索场地名"
          clearable
          style="width: 220px"
          @keyup.enter="reload"
          @clear="reload"
        />
      </div>
      <el-button @click="reload">刷新</el-button>
    </div>

    <el-table v-loading="loading" :data="places" border stripe>
      <el-table-column prop="name" label="场地" />
      <el-table-column prop="campus_name" label="校区" width="120" />
      <el-table-column prop="people" label="容纳人数" width="100" />
      <el-table-column prop="place_type" label="类型" width="110" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.use === 1 ? 'success' : 'info'">
            {{ row.use === 1 ? '可使用' : '不可用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="router.push(`/places/${row.id}`)">
            预约
          </el-button>
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
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { listCampuses, listPlaces, type Campus, type Place } from '@/api/place'

const router = useRouter()
const places = ref<Place[]>([])
const campuses = ref<Campus[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const filters = reactive({ campus: undefined as number | undefined, search: '' })

function reload() {
  page.value = 1
  loadList()
}

async function loadList() {
  loading.value = true
  try {
    const data = await listPlaces({
      campus: filters.campus,
      search: filters.search || undefined,
      page: page.value,
    })
    places.value = data.results
    total.value = data.count
  } finally {
    loading.value = false
  }
}

async function loadCampuses() {
  const data = await listCampuses()
  campuses.value = data.results
}

onMounted(async () => {
  await loadCampuses()
  await loadList()
})
</script>
