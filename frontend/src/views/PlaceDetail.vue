<template>
  <el-card v-loading="loading">
    <el-page-header @back="router.back()">
      <template #content>{{ place?.name || '场地详情' }}</template>
    </el-page-header>

    <el-descriptions :column="2" border style="margin-top: 20px">
      <el-descriptions-item label="场地名">{{ place?.name }}</el-descriptions-item>
      <el-descriptions-item label="校区">{{ place?.campus_name }}</el-descriptions-item>
      <el-descriptions-item label="容纳人数">{{ place?.people }}</el-descriptions-item>
      <el-descriptions-item label="类型">{{ place?.place_type }}</el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag :type="place?.use === 1 ? 'success' : 'info'">
          {{ place?.use === 1 ? '可使用' : '不可用' }}
        </el-tag>
      </el-descriptions-item>
    </el-descriptions>

    <h3 style="margin-top: 24px">填写预约信息</h3>
    <el-form :model="form" label-width="100px" style="max-width: 520px">
      <el-form-item label="日期">
        <el-date-picker
          v-model="form.date"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="选择日期"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="时段">
        <el-input v-model="form.bkTime" placeholder="如 10:00-11:00" />
      </el-form-item>
      <el-form-item label="使用人数">
        <el-input-number
          v-model="form.people"
          :min="1"
          :max="parseInt(place?.people || '1')"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          提交预约
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPlace, type Place } from '@/api/place'
import { createBooking } from '@/api/booking'

const props = defineProps<{ id: string }>()
const router = useRouter()
const place = ref<Place | null>(null)
const loading = ref(false)
const submitting = ref(false)
const form = reactive({ date: '', bkTime: '', people: 1 })

async function loadPlace() {
  loading.value = true
  try {
    place.value = await getPlace(parseInt(props.id))
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!form.date || !form.bkTime) {
    ElMessage.warning('请填写日期和时段')
    return
  }
  submitting.value = true
  try {
    await createBooking({
      place: parseInt(props.id),
      date: form.date,
      bkTime: form.bkTime,
      people: String(form.people),
      campus: place.value?.campus,
    })
    ElMessage.success('预约成功')
    router.push('/my-bookings')
  } catch {
    // 错误由拦截器提示
  } finally {
    submitting.value = false
  }
}

onMounted(loadPlace)
</script>
