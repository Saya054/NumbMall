<template>
  <div class="admin-exchanges">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>兑换管理</span>
        </div>
      </template>
      
      <el-form :inline="true" class="search-form">
        <el-form-item label="状态">
          <el-select v-model="status" placeholder="全部" clearable @change="loadRecords">
            <el-option label="待处理" value="pending" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadRecords">查询</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="records" style="width: 100%" v-loading="loading">
        <el-table-column prop="user_name" label="用户" width="120" />
        <el-table-column prop="product_name" label="商品名称" show-overflow-tooltip />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="points_spent" label="消耗积分" width="100" />
        <el-table-column prop="status_name" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status_name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="兑换时间" width="180" />
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              link
              type="danger"
              @click="handleCancel(row)"
              :disabled="row.status !== 'completed'"
            >
              取消兑换
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-if="total > 0"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next, jumper"
        @current-change="loadRecords"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const records = ref([])
const loading = ref(false)
const status = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    completed: 'success',
    cancelled: 'info'
  }
  return types[status] || ''
}

const loadRecords = async () => {
  loading.value = true
  try {
    const res = await api.get('/exchanges', {
      params: {
        page: page.value,
        per_page: pageSize.value,
        status: status.value
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

const handleCancel = (row) => {
  ElMessageBox.confirm(
    `确定要取消 "${row.user_name}" 兑换的 "${row.product_name}" 吗？积分将退回给用户。`,
    '取消兑换',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await api.post(`/exchanges/${row.id}/cancel`)
      ElMessage.success('兑换已取消，积分已退回')
      await loadRecords()
    } catch (error) {
      console.error('取消失败:', error)
    }
  })
}

onMounted(() => {
  loadRecords()
})
</script>

<style scoped>
.admin-exchanges {
  max-width: 1400px;
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



