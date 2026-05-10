<script setup>
defineProps({
  stages: {
    type: Array,
    default: () => [],
  },
})
</script>

<template>
  <section class="agent-flow card">
    <div class="card-head">
      <h2>Agent 执行流程</h2>
      <span class="hint">主链路：Planner → Emotion → Persona → Imagery/Memory → Style → Summary</span>
    </div>

    <div class="flow-list">
      <div
        v-for="stage in stages"
        :key="stage.key"
        class="flow-item"
        :class="stage.status"
      >
        <div class="flow-top">
          <span class="flow-name">{{ stage.label }}</span>
          <span class="flow-status">{{ stage.statusLabel }}</span>
        </div>
        <div class="flow-desc">{{ stage.description }}</div>
      </div>
    </div>
  </section>
</template>
