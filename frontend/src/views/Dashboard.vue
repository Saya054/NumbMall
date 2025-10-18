<template>
  <div class="dashboard">
    <div class="stats-cards">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e6f7ff;">
            <el-icon :size="30" color="#1890ff"><TrophyBase /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-title">总积分</p>
            <h2 class="stat-value">{{ stats.total_points || 0 }}</h2>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #f6ffed;">
            <el-icon :size="30" color="#52c41a"><Wallet /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-title">可用积分</p>
            <h2 class="stat-value">{{ stats.available_points || 0 }}</h2>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fff7e6;">
            <el-icon :size="30" color="#faad14"><Star /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-title">获得大拇哥</p>
            <h2 class="stat-value">{{ stats.total_thumbs || 0 }}</h2>
          </div>
        </div>
      </el-card>
      
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fff0f6;">
            <el-icon :size="30" color="#eb2f96"><ShoppingCart /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-title">兑换次数</p>
            <h2 class="stat-value">{{ stats.total_exchanges || 0 }}</h2>
          </div>
        </div>
      </el-card>
    </div>
    
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="content-card">
          <template #header>
            <div class="card-header">
              <span>最近获得的大拇哥</span>
              <el-button text @click="$router.push('/my-points')">查看更多</el-button>
            </div>
          </template>
          
          <el-table :data="recentThumbs" style="width: 100%" v-loading="thumbsLoading">
            <el-table-column prop="thumb_type_name" label="类型" width="120" />
            <el-table-column prop="points" label="积分" width="80" />
            <el-table-column prop="reason" label="原因" show-overflow-tooltip />
            <el-table-column prop="created_at" label="时间" width="160" />
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="content-card">
          <template #header>
            <div class="card-header">
              <span>最近兑换记录</span>
              <el-button text @click="$router.push('/my-exchanges')">查看更多</el-button>
            </div>
          </template>
          
          <el-table :data="recentExchanges" style="width: 100%" v-loading="exchangesLoading">
            <el-table-column prop="product_name" label="商品" show-overflow-tooltip />
            <el-table-column prop="points_spent" label="积分" width="80" />
            <el-table-column prop="status_name" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ row.status_name }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="160" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { TrophyBase, Wallet, Star, ShoppingCart } from '@element-plus/icons-vue'
import api from '@/utils/api'

const stats = ref({})
const recentThumbs = ref([])
const recentExchanges = ref([])
const thumbsLoading = ref(false)
const exchangesLoading = ref(false)

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    completed: 'success',
    cancelled: 'info'
  }
  return types[status] || ''
}

const loadStats = async () => {
  try {
    const res = await api.get('/stats/dashboard')
    stats.value = res.data
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadRecentThumbs = async () => {
  thumbsLoading.value = true
  try {
    const res = await api.get('/thumbs', { params: { per_page: 5 } })
    recentThumbs.value = res.data.list
  } catch (error) {
    console.error('加载大拇哥记录失败:', error)
  } finally {
    thumbsLoading.value = false
  }
}

const loadRecentExchanges = async () => {
  exchangesLoading.value = true
  try {
    const res = await api.get('/exchanges', { params: { per_page: 5 } })
    recentExchanges.value = res.data.list
  } catch (error) {
    console.error('加载兑换记录失败:', error)
  } finally {
    exchangesLoading.value = false
  }
}

onMounted(() => {
  loadStats()
  loadRecentThumbs()
  loadRecentExchanges()
})
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px 0;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
  color: #333;
}

.content-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>



