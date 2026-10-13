<template>
  <section class="page-section">
    <div class="page-toolbar">
      <div>
        <h2>我的持仓</h2>
        <p>共 {{ holdings.length }} 只基金</p>
      </div>
      <button type="button" class="button" @click="openCreate">
  新增持仓
      </button>
    </div>

    <div v-if="loading" class="loading card">
      <div class="spinner" />
    </div>

    <div v-else-if="holdings.length === 0" class="empty-state card">
      <div>
        <p class="empty-icon">📊</p>
        <p>还没有添加任何基金</p>
        <button type="button" class="button" @click="openCreate">添加第一只</button>
      </div>
    </div>

    <div v-else class="holding-grid">
      <article v-for="holding in holdings" :key="holding.id" class="holding-card card">
        <div class="holding-top">
          <div>
            <p class="holding-code">{{ holding.fund_code }}</p>
            <p class="holding-label">基金代码</p>
          </div>
          <span class="holding-index">#{{ holding.id }}</span>
        </div>

        <div class="holding-stats">
          <div class="stat">
            <span class="stat-value">{{ formatNumber(holding.shares, 2) }}</span>
            <span class="stat-label">持有份额</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ formatNumber(holding.cost_nav) }}</span>
            <span class="stat-label">成本净值</span>
          </div>
        </div>

        <p class="holding-time">录入于 {{ holding.created_at }}</p>

        <div class="holding-actions">
          <button type="button" class="button secondary" @click="openEdit(holding)">
            编辑
          </button>
          <button type="button" class="button danger" @click="handleDelete(holding)">
            删除
          </button>
        </div>
      </article>
    </div>

    <HoldingFormModal
      v-if="modalVisible"
      :holding="editingHolding"
      @close="modalVisible = false"
      @saved="handleSaved"
    />
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import HoldingFormModal from '../components/holdings/HoldingFormModal.vue'
import {
  deleteHolding,
  listHoldings
} from '../api/holdings'
import { formatNumber } from '../utils/format'
import { pushToast } from '../composables/useToast'

const holdings = ref([])
const loading = ref(true)
const modalVisible = ref(false)
const editingHolding = ref(null)

async function loadHoldings() {
  loading.value = true
  try {
    holdings.value = await listHoldings()
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingHolding.value = null
  modalVisible.value = true
}

function openEdit(holding) {
  editingHolding.value = holding
  modalVisible.value = true
}

function handleSaved() {
  modalVisible.value = false
  loadHoldings()
}

async function handleDelete(holding) {
  if (!window.confirm(`确定删除基金 ${holding.fund_code} 吗？`)) {
    return
  }

  try {
    await deleteHolding(holding.id)
    pushToast('删除成功')
    loadHoldings()
  } catch (error) {
    pushToast(error.message, 'error')
  }
}

onMounted(loadHoldings)
</script>
