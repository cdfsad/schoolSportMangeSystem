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
        <el-button @click="reload">搜索</el-button>
      </div>
      <el-button type="primary" @click="openCreate">新增场地</el-button>
    </div>

    <el-table v-loading="loading" :data="places" border stripe>
      <el-table-column prop="name" label="场地名" />
      <el-table-column prop="campus_name" label="校区" width="120" />
      <el-table-column label="类型" width="110">
        <template #default="{ row }">{{ placeTypeLabel(row.place_type) }}</template>
      </el-table-column>
      <el-table-column prop="people" label="容纳人数" width="100" />
      <el-table-column prop="location" label="位置" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.use === 1 ? 'success' : 'info'">
            {{ row.use === 1 ? '可使用' : '不可用' }}
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

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑场地' : '新增场地'" width="560px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="场地名" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="校区" required>
          <el-select v-model="form.campus" style="width: 100%">
            <el-option v-for="c in campuses" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.place_type" style="width: 100%">
            <el-option label="羽毛球" value="badminton" />
            <el-option label="篮球" value="basketball" />
            <el-option label="乒乓球" value="table_tennis" />
            <el-option label="健身房" value="gym" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="容纳人数" required>
          <el-input-number v-model="form.capacity" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="form.location" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.use" :active-value="1" :inactive-value="0" />
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
import {
  createPlace,
  deletePlace,
  listCampuses,
  listPlaces,
  updatePlace,
  type Campus,
  type Place,
} from '@/api/place'

const PLACE_TYPE_LABELS: Record<string, string> = {
  badminton: '羽毛球',
  basketball: '篮球',
  table_tennis: '乒乓球',
  gym: '健身房',
  other: '其他',
}

const places = ref<Place[]>([])
const campuses = ref<Campus[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive({ campus: undefined as number | undefined, search: '' })

const dialogVisible = ref(false)
const editing = ref<Place | null>(null)
const submitting = ref(false)
const form = reactive({
  name: '',
  campus: undefined as number | undefined,
  place_type: 'other',
  capacity: 10,
  location: '',
  use: 1,
})

function placeTypeLabel(t: string) {
  return PLACE_TYPE_LABELS[t] || t
}

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

function handleSizeChange(size: number) {
  pageSize.value = size
  reload()
}

function openCreate() {
  editing.value = null
  Object.assign(form, {
    name: '',
    campus: campuses.value[0]?.id,
    place_type: 'other',
    capacity: 10,
    location: '',
    use: 1,
  })
  dialogVisible.value = true
}

function openEdit(row: Place) {
  editing.value = row
  Object.assign(form, {
    name: row.name,
    campus: row.campus,
    place_type: row.place_type || 'other',
    capacity: row.capacity || parseInt(row.people) || 10,
    location: row.location,
    use: row.use,
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.name || !form.campus) {
    ElMessage.warning('请填写场地名和校区')
    return
  }
  submitting.value = true
  try {
    // capacity 写入 capacity 字段,同时同步到 people(service 层读 people 做容量校验)
    const payload = {
      name: form.name,
      campus: form.campus!,
      place_type: form.place_type,
      capacity: form.capacity,
      people: String(form.capacity),
      location: form.location,
      use: form.use,
    }
    if (editing.value) {
      await updatePlace(editing.value.id, payload)
      ElMessage.success('已更新')
    } else {
      await createPlace(payload)
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

async function handleDelete(row: Place) {
  try {
    await ElMessageBox.confirm(`确定删除场地「${row.name}」吗?(软删除)`, '提示', { type: 'warning' })
  } catch {
    return // 用户取消
  }
  try {
    await deletePlace(row.id)
    ElMessage.success('已删除')
    await loadList()
  } catch {
    // Campus/Place PROTECT 等错误由拦截器提示
  }
}

onMounted(async () => {
  await loadCampuses()
  await loadList()
})
</script>
