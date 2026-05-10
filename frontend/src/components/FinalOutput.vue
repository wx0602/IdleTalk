<script setup>
defineProps({
  response: {
    type: Object,
    default: null,
  },
})
</script>

<template>
  <section class="final-output card">
    <div class="card-head">
      <h2>最终输出</h2>
      <span class="hint">前端直接使用的统一响应</span>
    </div>

    <template v-if="response">
      <div class="output-block">
        <div class="output-title">文学化回复</div>
        <div class="output-text">{{ response.final_response }}</div>
      </div>

      <div class="output-meta">
        <div class="meta-chip">
          <span>情绪</span>
          <strong>{{ response.display?.emotion || '-' }}</strong>
        </div>
        <div class="meta-chip">
          <span>语气</span>
          <strong>{{ response.display?.tone || '-' }}</strong>
        </div>
        <div class="meta-chip">
          <span>意象</span>
          <strong>{{ (response.display?.imagery || []).join('、') || '-' }}</strong>
        </div>
      </div>

      <div class="trace-box">
        <div class="trace-title">执行追踪</div>
        <pre>{{ JSON.stringify(response.trace || {}, null, 2) }}</pre>
      </div>
    </template>

    <div v-else class="empty-state">
      发送一次请求后，这里会展示 Summary Agent 汇总出的最终结果。
    </div>
  </section>
</template>
