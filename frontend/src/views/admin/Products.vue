<template>
  <div class="admin-products">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商品管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增商品
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="keyword" placeholder="商品名称" clearable @keyup.enter="loadProducts" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="status" placeholder="全部" clearable @change="loadProducts">
            <el-option label="已上架" value="on_shelf" />
            <el-option label="已下架" value="off_shelf" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadProducts">查询</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="products" style="width: 100%" v-loading="loading">
        <el-table-column prop="name" label="商品名称" show-overflow-tooltip />
        <el-table-column prop="points_required" label="所需积分" width="100" />
        <el-table-column prop="stock" label="库存" width="80" />
        <el-table-column prop="status_name" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'on_shelf' ? 'success' : 'info'" size="small">
              {{ row.status_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="warning" @click="handleToggleStatus(row)">
              {{ row.status === 'on_shelf' ? '下架' : '上架' }}
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-if="total > 0"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next, jumper"
        @current-change="loadProducts"
        class="pagination"
      />
    </el-card>
    
    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="商品描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="商品图片" prop="image_url">
          <el-upload
            class="image-uploader"
            :action="`/api/upload`"
            :headers="{ Authorization: `Bearer ${token}` }"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
          >
            <img v-if="form.image_url" :src="form.image_url" class="upload-image" />
            <el-icon v-else class="upload-icon"><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">支持 jpg、png、gif、webp 格式，大小不超过 5MB</div>
        </el-form-item>
        <el-form-item label="所需积分" prop="points_required">
          <el-input-number v-model="form.points_required" :min="1" />
        </el-form-item>
        <el-form-item label="库存数量" prop="stock">
          <el-input-number v-model="form.stock" :min="0" />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="on_shelf">上架</el-radio>
            <el-radio label="off_shelf">下架</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const token = computed(() => userStore.token)

const products = ref([])
const loading = ref(false)
const keyword = ref('')
const status = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const dialogVisible = ref(false)
const dialogTitle = ref('新增商品')
const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  id: null,
  name: '',
  description: '',
  image_url: '',
  points_required: 10,
  stock: 0,
  sort_order: 0,
  status: 'off_shelf'
})

const rules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  points_required: [{ required: true, message: '请输入所需积分', trigger: 'blur' }]
}

const loadProducts = async () => {
  loading.value = true
  try {
    const res = await api.get('/products', {
      params: {
        page: page.value,
        per_page: pageSize.value,
        keyword: keyword.value,
        status: status.value
      }
    })
    products.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    console.error('加载商品失败:', error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增商品'
  Object.assign(form, {
    id: null,
    name: '',
    description: '',
    image_url: '',
    points_required: 10,
    stock: 0,
    sort_order: 0,
    status: 'off_shelf'
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑商品'
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (form.id) {
        await api.put(`/products/${form.id}`, form)
        ElMessage.success('更新成功')
      } else {
        await api.post('/products', form)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      await loadProducts()
    } catch (error) {
      console.error('提交失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

const handleToggleStatus = async (row) => {
  try {
    await api.post(`/products/${row.id}/toggle-status`)
    ElMessage.success(`商品已${row.status === 'on_shelf' ? '下架' : '上架'}`)
    await loadProducts()
  } catch (error) {
    console.error('操作失败:', error)
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除商品 "${row.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await api.delete(`/products/${row.id}`)
      ElMessage.success('删除成功')
      await loadProducts()
    } catch (error) {
      console.error('删除失败:', error)
    }
  })
}

const beforeUpload = (file) => {
  const isImage = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)
  const isLt5M = file.size / 1024 / 1024 < 5
  
  if (!isImage) {
    ElMessage.error('只能上传 jpg、png、gif、webp 格式的图片！')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB！')
    return false
  }
  return true
}

const handleUploadSuccess = (response) => {
  if (response.code === 200) {
    form.image_url = response.data.url
    ElMessage.success('图片上传成功')
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

const handleUploadError = () => {
  ElMessage.error('图片上传失败，请重试')
}

onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.admin-products {
  max-width: 1400px;
}

.image-uploader {
  display: inline-block;
}

.image-uploader :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  width: 178px;
  height: 178px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-uploader :deep(.el-upload:hover) {
  border-color: #409eff;
}

.upload-image {
  width: 178px;
  height: 178px;
  object-fit: cover;
}

.upload-icon {
  font-size: 28px;
  color: #8c939d;
}

.upload-tip {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>

