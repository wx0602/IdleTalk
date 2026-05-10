<script setup>
defineProps({
  trace: {
    type: Object,
    default: () => ({}),
  },
})
</script>

<template>
  <section class="trace-panel card">
    <div class="card-head">
      <h2>执行摘要</h2>
      <span class="hint">展示当前轮协同生成的关键依据</span>
    </div>

    <div class="trace-grid">
      <article class="trace-card">
        <span class="trace-label">Style 来源</span>
        <strong>{{ trace.style_source || '-' }}</strong>
      </article>

      <article class="trace-card">
        <span class="trace-label">Style 状态</span>
        <strong>{{ trace.style_status || '-' }}</strong>
      </article>

      <article class="trace-card wide">
        <span class="trace-label">参考语料</span>
        <div class="trace-tags">
          <span
            v-for="quote in trace.style_reference_quotes || []"
            :key="quote.id || quote.text"
            class="trace-tag"
          >
            {{ quote.id || 'quote' }}
          </span>
          <span v-if="!(trace.style_reference_quotes || []).length" class="trace-tag empty">
            暂无
          </span>
        </div>
      </article>

      <article class="trace-card wide">
        <span class="trace-label">参与 Agent</span>
        <div class="trace-tags">
          <span
            v-for="name in trace.agent_names || []"
            :key="name"
            class="trace-tag"
          >
            {{ name }}
          </span>
          <span v-if="!(trace.agent_names || []).length" class="trace-tag empty">
            暂无
          </span>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.trace-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.trace-card {
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid rgba(144, 190, 130, 0.22);
  background: rgba(255, 255, 255, 0.88);
}

.trace-card.wide {
  grid-column: span 2;
}

.trace-label {
  display: block;
  margin-bottom: 8px;
  color: #5d7360;
  font-size: 12px;
}

.trace-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.trace-tag {
  padding: 7px 10px;
  border-radius: 999px;
  background: rgba(223, 242, 212, 0.92);
  color: #2a492f;
  font-size: 13px;
}

.trace-tag.empty {
  background: rgba(243, 248, 241, 0.92);
  color: #768878;
}

@media (max-width: 720px) {
  .trace-grid {
    grid-template-columns: 1fr;
  }

  .trace-card.wide {
    grid-column: span 1;
  }
}
</style>
