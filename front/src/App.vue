<template>
  <div class="app-shell">
    <header class="app-header">
      <div>
        <p class="eyebrow">LangGraph Fund Agent</p>
        <h1>基金管家</h1>
      </div>
      <nav class="tab-nav">
        <button
          type="button"
          :class="{ active: activeTab === 'holdings' }"
          @click="activeTab = 'holdings'"
        >
          持仓管理
        </button>
        <button
          type="button"
          :class="{ active: activeTab === 'reports' }"
          @click="activeTab = 'reports'"
        >
          分析报告
        </button>
      </nav>
    </header>

    <main class="app-content">
      <HoldingsPage v-if="activeTab === 'holdings'" />
      <ReportsPage v-else />
    </main>
  </div>

  <ToastContainer />
</template>

<script setup>
import { ref } from 'vue'
import HoldingsPage from './pages/HoldingsPage.vue'
import ReportsPage from './pages/ReportsPage.vue'
import ToastContainer from './components/ui/ToastContainer.vue'

const activeTab = ref('holdings')
</script>
