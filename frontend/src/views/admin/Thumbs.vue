<template>
  <div class="admin-thumbs">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>发放大拇哥</span>
        </div>
      </template>
      
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px" style="max-width: 600px;">
        <el-form-item label="选择用户" prop="user_id">
          <el-select
            v-model="form.user_id"
            filterable
            remote
            placeholder="请输入用户名搜索"
            :remote-method="searchUsers"
            :loading="searchLoading"
            style="width: 100%"
          >
            <el-option
              v-for="user in userOptions"
              :key="user.id"
              :label="`${user.real_name} (${user.username})`"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="大拇哥类型" prop="thumb_type">
          <el-radio-group v-model="form.thumb_type">
            <el-radio label="single">
              <span style="font-size: 24px;">👍</span> 单大拇哥 (1积分)
            </el-radio>
            <el-radio label="double">
              <span style="font-size: 24px;">👍👍</span> 双大拇哥 (5积分)
            </el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="获得原因" prop="reason">
          <el-input
            v-model="form.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入发放大拇哥的原因"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            发放大拇哥
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>最近发放记录</span>
        </div>
      </template>
      
      <el-table :data="records" style="width: 100%" v-loading="loading">
        <el-table-column prop="user_name" label="用户" width="120" />
        <el-table-column prop="thumb_type_name" label="类型" width="150" />
        <el-table-column prop="points" label="积分" width="80" />
        <el-table-column prop="reason" label="原因" show-overflow-tooltip />
        <el-table-column prop="given_by_name" label="发放人" width="120" />
        <el-table-column prop="created_at" label="发放时间" width="180" />
      </el-table>
      
      <el-pagination
        v-if="total > 0"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadRecords"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const formRef = ref(null)
const submitting = ref(false)
const searchLoading = ref(false)
const userOptions = ref([])

const form = reactive({
  user_id: null,
  thumb_type: 'single',
  reason: ''
})

const rules = {
  user_id: [{ required: true, message: '请选择用户', trigger: 'change' }],
  thumb_type: [{ required: true, message: '请选择大拇哥类型', trigger: 'change' }],
  reason: [{ required: true, message: '请输入获得原因', trigger: 'blur' }]
}

const records = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const searchUsers = async (query) => {
  if (!query) {
    userOptions.value = []
    return
  }
  
  searchLoading.value = true
  try {
    const res = await api.get('/users', {
      params: { keyword: query, per_page: 20 }
    })
    userOptions.value = res.data.list.filter(u => u.role !== 'admin')
  } catch (error) {
    console.error('搜索用户失败:', error)
  } finally {
    searchLoading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      await api.post('/thumbs', form)
      ElMessage.success('发放成功')
      resetForm()
      await loadRecords()
    } catch (error) {
      console.error('发放失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  form.user_id = null
  form.thumb_type = 'single'
  form.reason = ''
}

const loadRecords = async () => {
  loading.value = true
  try {
    const res = await api.get('/thumbs', {
      params: {
        page: page.value,
        per_page: pageSize.value
      }
    })
    records.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    console.error('加载记录失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
.admin-thumbs {
  max-width: 1400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>

