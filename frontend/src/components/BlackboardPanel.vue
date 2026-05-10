<script setup>
import { computed } from 'vue'

const props = defineProps({
  context: {
    type: Object,
    default: () => ({}),
  },
})

const cards = computed(() => {
  const context = props.context || {}

  return [
    {
      key: 'emotion',
      label: 'Emotion',
      accent: 'soft-green',
      items: [
        { name: '标签', value: context.emotion?.label || '-' },
        { name: '强度', value: context.emotion?.intensity ?? '-' },
        {
          name: '证据',
          value: (context.emotion?.evidence || []).slice(0, 2).join('、') || '-',
        },
      ],
    },
    {
      key: 'persona',
      label: 'Persona',
      accent: 'deep-green',
      items: [
        {
          name: '语气',
          value: context.persona?.tone || '-',
        },
        {
          name: '特征',
          value: (context.persona?.core_traits || []).slice(0, 3).join('、') || '-',
        },
        {
          name: '关注点',
          value: context.persona?.focus || '-',
        },
      ],
    },
    {
      key: 'imagery',
      label: 'Imagery',
      accent: 'leaf',
      items: [
        {
          name: '意象',
          value: (context.imagery?.selected_imagery || []).slice(0, 4).join('、') || '-',
        },
        {
          name: '场景',
          value: (context.imagery?.selected_scenes || []).slice(0, 2).join('、') || '-',
        },
        {
          name: '烟火气',
          value: context.imagery?.life_breath || '-',
        },
      ],
    },
    {
      key: 'memory',
      label: 'Memory',
      accent: 'moss',
      items: [
        {
          name: '偏好意象',
          value:
            (context.memory?.preferred_imagery || []).slice(0, 3).join('、') || '-',
        },
        {
          name: '偏好语气',
          value:
            (context.memory?.preferred_emotion_styles || []).slice(0, 3).join('、') || '-',
        },
        {
          name: '最近输入',
          value: (context.memory?.recent_inputs || []).slice(-1)[0] || '-',
        },
      ],
    },
  ]
})
</script>

<template>
  <section class="blackboard card">
    <div class="card-head">
      <h2>Blackboard 状态</h2>
      <span class="hint">四个共享字段的摘要卡片</span>
    </div>

    <div class="blackboard-grid">
      <article
        v-for="card in cards"
        :key="card.key"
        class="blackboard-card"
        :class="card.accent"
      >
        <h3>{{ card.label }}</h3>
        <div class="blackboard-list">
          <div v-for="item in card.items" :key="item.name" class="blackboard-item">
            <span class="item-name">{{ item.name }}</span>
            <strong class="item-value">{{ item.value }}</strong>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.blackboard-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.blackboard-card {
  padding: 16px;
  border-radius: 18px;
  border: 1px solid rgba(134, 184, 121, 0.24);
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.96), rgba(242, 251, 238, 0.88));
}

.blackboard-card h3 {
  margin: 0 0 14px;
  font-size: 16px;
}

.blackboard-list {
  display: grid;
  gap: 10px;
}

.blackboard-item {
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(249, 255, 246, 0.9);
}

.item-name {
  display: block;
  margin-bottom: 5px;
  color: #5f7762;
  font-size: 12px;
}

.item-value {
  display: block;
  color: #223427;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.soft-green {
  box-shadow: inset 0 0 0 1px rgba(148, 209, 124, 0.22);
}

.deep-green {
  box-shadow: inset 0 0 0 1px rgba(93, 162, 103, 0.22);
}

.leaf {
  box-shadow: inset 0 0 0 1px rgba(128, 187, 100, 0.22);
}

.moss {
  box-shadow: inset 0 0 0 1px rgba(111, 160, 92, 0.22);
}

@media (max-width: 720px) {
  .blackboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>
