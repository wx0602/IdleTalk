<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['submit'])
const draft = ref('我今天有点难过，希望语气温和一点，最好有热汤和雨。')

function submit() {
  const text = draft.value.trim()
  if (!text || props.loading) {
    return
  }
  emit('submit', text)
}

watch(
  () => props.loading,
  (value) => {
    if (!value) {
      draft.value = draft.value.trim()
    }
  }
)
</script>

<template>
  <section class="composer card">
    <div class="composer-row">
      <textarea
        v-model="draft"
        class="composer-input"
        rows="1"
        placeholder="输入一句话，观察多 Agent 协同生成过程"
        @keydown.enter.exact.prevent="submit"
      />
      <button class="submit-button" :disabled="loading" @click="submit">
        {{ loading ? '执行中' : '发送' }}
      </button>
    </div>
  </section>
</template>
