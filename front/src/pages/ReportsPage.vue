<template>
  <section class="page-section">
    <div class="page-toolbar">
      <div>
        <h2>分析报告</h2>
        <p>共 {{ reports.length }} 份历史报告</p>
      </div>
      <div class="report-filter">
        <input
          v-model="threadFilter"
          type="text"
          placeholder="按 thread_id 过滤"
          @keyup.enter="loadReports"
        />
        <button type="button" class="button secondary" @click="resetFilter">重置</button>
        <button type="button" class="button" @click="loadReports">刷新</button>
      </div>
    </div>

    <div v-if="loading" class="loading card">
      <div class="spinner" />
    </div>

    <div v-else-if="reports.length === 0" class="empty-state card">
      <div>
        <p class="empty-icon">📝</p>
        <p>暂时还没有分析报告</p>
        <p class="empty-hint">等后面接入 LangGraph 后，报告会在这里留档</p>
      </div>
    </div>

    <div v-else class="report-list">
      <article v-for="report in reports" :key="report.id" class="report-card card">
        <div class="report-card-header">
          <div>
            <p class="report-thread">{{ report.thread_id }}</p>
            <p class="report-meta">第 {{ report.version }} 版 · {{ report.created_at }}</p>
          </div>
          <span class="badge" :class="statusMeta(report.status).className">
            {{ statusMeta(report.status).label }}
          </span>
        </div>

        <p class="report-overview">{{ report.content.overall }}</p>

        <div class="report-card-footer">
          <button type="button" class="button secondary" @click="openDetail(report)">
            查看详情
          </button>
          <button type="button" class="button danger ghost-danger" @click="handleDelete(report)">
            删除
          </button>
        </div>
      </article>
    </div>

    <Modal v-if="selectedReport" title="报告详情" @close="selectedReport = null">
      <div class="report-detail">
        <div class="detail-summary">
          <div>
            <p class="report-thread">{{ selectedReport.thread_id }}</p>
            <p class="report-meta">
              第 {{ selectedReport.version }} 版 · {{ selectedReport.created_at }}
            </p>
          </div>
          <span class="badge" :class="statusMeta(selectedReport.status).className">
            {{ statusMeta(selectedReport.status).label }}
          </span>
        </div>

        <section class="detail-section">
          <h3>整体判断</h3>
          <p>{{ selectedReport.content.overall }}</p>
        </section>

        <section class="detail-section">
          <h3>逐只分析</h3>
          <div class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>基金</th>
                  <th>走势</th>
                  <th>建议</th>
                  <th>理由</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="view in selectedReport.content.views" :key="view.fund_code">
                  <td>
                    <strong>{{ view.fund_code }}</strong>
                    <span>{{ view.fund_name }}</span>
                  </td>
                  <td>{{ view.trend }}</td>
                  <td>
                    <span class="badge" :class="adviceMeta(view.advice).className">
                      {{ adviceMeta(view.advice).label }}
                    </span>
                  </td>
                  <td>{{ view.reason }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="selectedReport.feedback" class="detail-section">
          <h3>上次反馈</h3>
          <p class="feedback-box">{{ selectedReport.feedback }}</p>
        </section>

        <div class="detail-actions">
          <button type="button" class="button success" @click="setStatus(selectedReport, 'approved')">
            满意，通过
          </button>
          <button type="button" class="button danger" @click="setStatus(selectedReport, 'rejected')">
            不满意，打回
          </button>
        </div>
      </div>
    </Modal>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import Modal from '../components/ui/Modal.vue'
import { deleteReport, listReports, updateReport } from '../api/reports'
import { adviceMeta, statusMeta } from '../utils/format'
import { pushToast } from '../composables/useToast'

const reports = ref([])
const loading = ref(true)
const threadFilter = ref('')
const selectedReport = ref(null)

async function loadReports() {
  loading.value = true

  try {
    reports.value = await listReports(threadFilter.value.trim())
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    loading.value = false
  }
}

function resetFilter() {
  threadFilter.value = ''
  loadReports()
}

function openDetail(report) {
  selectedReport.value = report
}

async function setStatus(report, status) {
  const payload = { status }

  if (status === 'rejected') {
    const feedback = window.prompt('说说这版哪里不对？', report.feedback ?? '')

    if (feedback === null) {
      return
    }

    payload.feedback = feedback
  }

  try {
    await updateReport(report.id, payload)
    await loadReports()
    selectedReport.value = reports.value.find((item) => item.id === report.id) ?? null
    pushToast(status === 'approved' ? '报告已通过' : '报告已打回')
  } catch (error) {
    pushToast(error.message, 'error')
  }
}

async function handleDelete(report) {
  if (!window.confirm(`确定删除第 ${report.version} 版报告吗？`)) {
    return
  }

  try {
    await deleteReport(report.id)
    if (selectedReport.value?.id === report.id) {
      selectedReport.value = null
    }
    pushToast('删除成功')
    loadReports()
  } catch (error) {
    pushToast(error.message, 'error')
  }
}

onMounted(loadReports)
</script>
