<template>
  <Modal :title="isEdit ? '编辑持仓' : '新增持仓'" @close="handleClose">
    <form class="holding-form" @submit.prevent="handleSubmit">
      <div class="form-grid">
        <div class="field full">
          <label for="fund_code">基金代码</label>
          <input
            id="fund_code"
            v-model="form.fund_code"
            type="text"
            placeholder="例如 005827"
            maxlength="6"
          />
          <p v-if="errors.fund_code" class="field-error">{{ errors.fund_code }}</p>
        </div>

        <div class="field">
          <label for="shares">持有份额</label>
          <input
            id="shares"
            v-model="form.shares"
            type="number"
            min="0"
            step="0.01"
            placeholder="选填"
          />
        </div>

        <div class="field">
          <label for="cost_nav">成本净值</label>
          <input
            id="cost_nav"
            v-model="form.cost_nav"
            type="number"
            min="0"
            step="0.0001"
            placeholder="选填"
          />
        </div>
      </div>

      <div class="form-footer">
        <button type="button" class="button secondary" @click="handleClose">取消</button>
        <button type="submit" class="button" :disabled="submitting">
          {{ submitting ? '保存中...' : '保存' }}
        </button>
      </div>
    </form>
  </Modal>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import Modal from '../ui/Modal.vue'
import { createHolding, updateHolding } from '../../api/holdings'
import { optionalNumber } from '../../utils/format'
import { pushToast } from '../../composables/useToast'

const props = defineProps({
  holding: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'saved'])

const isEdit = computed(() => props.holding !== null)
const submitting = ref(false)
const errors = reactive({ fund_code: '' })

const form = reactive({
  fund_code: props.holding?.fund_code ?? '',
  shares: props.holding?.shares ?? '',
  cost_nav: props.holding?.cost_nav ?? ''
})

function validate() {
  errors.fund_code = ''

  if (!/^\d{6}$/.test(form.fund_code)) {
    errors.fund_code = '基金代码必须是 6 位数字'
    return false
  }

  return true
}

async function handleSubmit() {
  if (!validate()) {
    return
  }

  const payload = {
    fund_code: form.fund_code,
    shares: optionalNumber(form.shares),
    cost_nav: optionalNumber(form.cost_nav)
  }

  submitting.value = true

  try {
    if (isEdit.value) {
      await updateHolding(props.holding.id, payload)
      pushToast('更新成功')
    } else {
      await createHolding(payload)
      pushToast('添加成功')
    }
    emit('saved')
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    submitting.value = false
  }
}

function handleClose() {
  emit('close')
}
</script>
