<template>
  <el-card>
    <div style="display: flex; justify-content: flex-end; margin-bottom: 16px">
      <el-button type="primary" @click="openCreate">新增校区</el-button>
    </div>

    <el-table v-loading="loading" :data="rows" border stripe>
      <el-table-column prop="name" label="校区名" />
      <el-table-column prop="code" label="代码" width="120" />
      <el-table-column prop="address" label="地址" show-overflow-tooltip />
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

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑校区' : '新增校区'" width="520px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="校区名" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="代码" required>
          <el-input v-model="form.code" placeholder="如 east/west" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.address" />
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
import {
  createCampus,
  deleteCampus,
  listCampuses,
  updateCampus,
  type Campus,
} from '@/api/campus'

const rows = ref<Campus[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const dialogVisible = ref(false)
const editing = ref<Campus | null>(null)
const submitting = ref(false)
const form = reactive({
  name: '',
  code: '',
  address: '',
  sort_order: 0,
  is_active: true,
})

function reload() {
  page.value = 1
  loadList()
}

async function loadList() {
  loading.value = true
  try {
    const data = await listCampuses({ page: page.value })
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

function openCreate() {
  editing.value = null
  Object.assign(form, { name: '', code: '', address: '', sort_order: 0, is_active: true })
  dialogVisible.value = true
}

function openEdit(row: Campus) {
  editing.value = row
  Object.assign(form, {
    name: row.name,
    code: row.code,
    address: row.address,
    sort_order: row.sort_order,
    is_active: row.is_active,
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.name || !form.code) {
    ElMessage.warning('请填写校区名和代码')
    return
  }
  submitting.value = true
  try {
    if (editing.value) {
      await updateCampus(editing.value.id, form)
      ElMessage.success('已更新')
    } else {
      await createCampus(form)
      ElMessage.success('已新增')
    }
    dialogVisible.value = false
    await loadList()
  } catch {
    // 错误由请求拦截器提示(PROTECT 约束等)
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row: Campus) {
  try {
    await ElMessageBox.confirm(`确定删除校区「${row.name}」吗?`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteCampus(row.id)
    ElMessage.success('已删除')
    await loadList()
  } catch {
    // 该校区下有场地时 PROTECT 约束触发 400/500,由拦截器提示
  }
}

onMounted(loadList)
</script>
