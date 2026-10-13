<template>
  <Teleport to="body">
    <div class="modal-mask" @click.self="handleClose">
      <div class="modal-panel">
        <div class="modal-header">
          <h3>{{ title }}</h3>
          <button type="button" class="icon-button" @click="handleClose">×</button>
        </div>
        <div class="modal-body">
          <slot />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close'])

function handleClose() {
  emit('close')
}
</script>
