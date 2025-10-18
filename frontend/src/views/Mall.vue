<template>
  <div class="mall">
    <el-card class="search-card">
      <el-input
        v-model="keyword"
        placeholder="搜索商品"
        clearable
        @clear="loadProducts"
        @keyup.enter="loadProducts"
        style="width: 300px;"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </el-card>
    
    <div class="products-grid" v-loading="loading">
      <el-card
        v-for="product in products"
        :key="product.id"
        class="product-card"
        shadow="hover"
      >
        <div class="product-image">
          <img
            v-if="product.image_url"
            :src="product.image_url"
            :alt="product.name"
          />
          <div v-else class="no-image">
            <el-icon :size="60" color="#ccc"><Picture /></el-icon>
            <p>暂无图片</p>
          </div>
        </div>
        
        <div class="product-info">
          <h3 class="product-name">{{ product.name }}</h3>
          <p class="product-desc">{{ product.description || '暂无描述' }}</p>
          
          <div class="product-footer">
            <div class="product-price">
              <span class="price-label">所需积分:</span>
              <span class="price-value">{{ product.points_required }}</span>
            </div>
            
            <div class="product-stock">
              库存: {{ product.stock }}
            </div>
          </div>
          
          <el-button
            type="primary"
            :disabled="product.stock === 0 || userStore.userInfo.available_points < product.points_required"
            @click="handleExchange(product)"
            class="exchange-button"
          >
            {{ product.stock === 0 ? '已售罄' : '立即兑换' }}
          </el-button>
        </div>
      </el-card>
      
      <el-empty v-if="!loading && products.length === 0" description="暂无商品" />
    </div>
    
    <el-pagination
      v-if="total > 0"
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      @current-change="loadProducts"
      class="pagination"
    />

    <el-dialog
      v-model="exchangeDialogVisible"
      :title="selectedProduct ? `兑换 ${selectedProduct.name}` : '兑换商品'"
      width="420px"
      destroy-on-close
    >
      <div v-if="selectedProduct" class="exchange-dialog-body">
        <p class="exchange-info">
          可用积分：<span class="exchange-highlight">{{ userStore.userInfo.available_points }}</span>
        </p>
        <p class="exchange-info">
          单件所需积分：<span class="exchange-highlight">{{ selectedProduct.points_required }}</span>
        </p>
        <p class="exchange-info">
          库存：<span class="exchange-highlight">{{ selectedProduct.stock }}</span>
        </p>
        <el-input-number
          v-model="exchangeQuantity"
          :min="1"
          :max="Math.max(1, maxExchangeQuantity)"
          :disabled="exchangeSubmitting || maxExchangeQuantity === 0"
          controls-position="right"
          class="exchange-quantity"
        />
        <p class="exchange-tip">
          本次最多可兑换 {{ maxExchangeQuantity }} 件
        </p>
      </div>
      <template #footer>
        <el-button :disabled="exchangeSubmitting" @click="exchangeDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="exchangeSubmitting"
          :disabled="maxExchangeQuantity === 0"
          @click="confirmExchange"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Picture } from '@element-plus/icons-vue'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const products = ref([])
const loading = ref(false)
const keyword = ref('')
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)
const exchangeDialogVisible = ref(false)
const selectedProduct = ref(null)
const exchangeQuantity = ref(1)
const exchangeSubmitting = ref(false)

const loadProducts = async () => {
  loading.value = true
  try {
    const res = await api.get('/products', {
      params: {
        page: page.value,
        per_page: pageSize.value,
        status: 'on_shelf',
        keyword: keyword.value
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

const maxExchangeQuantity = computed(() => {
  if (!selectedProduct.value) return 0
  const product = selectedProduct.value
  const stockLimit = Number(product.stock) > 0 ? Number(product.stock) : 0
  const pointsRequired = Number(product.points_required) || 0
  const availablePoints = Number(userStore.userInfo.available_points) || 0
  const pointsLimit =
    pointsRequired > 0 ? Math.floor(availablePoints / pointsRequired) : stockLimit
  return Math.max(0, Math.min(stockLimit, pointsLimit))
})

const handleExchange = (product) => {
  selectedProduct.value = product
  exchangeQuantity.value = 1
  exchangeDialogVisible.value = true
}

const resetExchangeState = () => {
  selectedProduct.value = null
  exchangeQuantity.value = 1
  exchangeSubmitting.value = false
}

const confirmExchange = async () => {
  if (!selectedProduct.value) return
  if (maxExchangeQuantity.value === 0) {
    ElMessage.warning('当前不能兑换该商品')
    return
  }

  if (exchangeQuantity.value < 1) {
    ElMessage.warning('兑换数量至少为 1 件')
    exchangeQuantity.value = 1
    return
  }

  if (exchangeQuantity.value > maxExchangeQuantity.value) {
    ElMessage.warning(`最多可兑换 ${maxExchangeQuantity.value} 件`)
    exchangeQuantity.value = maxExchangeQuantity.value
    return
  }

  exchangeSubmitting.value = true
  try {
    await api.post('/exchanges', {
      product_id: selectedProduct.value.id,
      quantity: exchangeQuantity.value
    })
    ElMessage.success('兑换成功')
    exchangeDialogVisible.value = false
    await userStore.getUserInfo()
    await loadProducts()
  } catch (error) {
    console.error('兑换失败:', error)
  } finally {
    exchangeSubmitting.value = false
  }
}

watch(exchangeDialogVisible, (visible) => {
  if (!visible) {
    resetExchangeState()
  }
})

watch(maxExchangeQuantity, (newMax) => {
  if (!exchangeDialogVisible.value) return
  if (newMax > 0 && exchangeQuantity.value > newMax) {
    exchangeQuantity.value = newMax
  }
})

onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.mall {
  max-width: 1400px;
}

.search-card {
  margin-bottom: 20px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  min-height: 400px;
}

.product-card {
  cursor: pointer;
  transition: transform 0.3s;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-5px);
}

.product-image {
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 4px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}

.product-image img {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
}

.no-image {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}

.no-image p {
  margin-top: 10px;
  font-size: 12px;
  color: #999;
}

.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.product-name {
  font-size: 16px;
  font-weight: bold;
  margin: 0 0 10px 0;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-desc {
  font-size: 14px;
  color: #666;
  margin: 0 0 15px 0;
  height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.product-price {
  display: flex;
  align-items: baseline;
  gap: 5px;
}

.price-label {
  font-size: 12px;
  color: #999;
}

.price-value {
  font-size: 20px;
  font-weight: bold;
  color: #ff4d4f;
}

.product-stock {
  font-size: 12px;
  color: #999;
}

.exchange-button {
  width: 100%;
  margin-top: auto;
}

.pagination {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.exchange-dialog-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.exchange-info {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.exchange-highlight {
  color: #ff4d4f;
  font-weight: 600;
  margin-left: 4px;
}

.exchange-quantity {
  width: 100%;
}

.exchange-tip {
  margin: 0;
  font-size: 12px;
  color: #999;
}
</style>
