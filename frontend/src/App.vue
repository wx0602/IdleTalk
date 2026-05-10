<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { postChat } from './api/chat'
import AgentFlow from './components/AgentFlow.vue'
import BlackboardPanel from './components/BlackboardPanel.vue'
import ChatComposer from './components/ChatComposer.vue'
import ChatWindow from './components/ChatWindow.vue'
import TracePanel from './components/TracePanel.vue'

const loading = ref(false)
const errorMessage = ref('')
const latestResponse = ref(null)
const messages = ref([])
const activeStageIndex = ref(0)
let progressTimer = null

const stageDefs = [
  {
    key: 'planner',
    label: 'Planner',
    description: '解析输入，规划主链路',
  },
  {
    key: 'emotion',
    label: 'Emotion',
    description: '识别当前情绪状态',
  },
  {
    key: 'persona',
    label: 'Persona',
    description: '生成人格表达倾向',
  },
  {
    key: 'imagery_memory',
    label: 'Imagery + Memory',
    description: '并行读取意象与用户偏好',
  },
  {
    key: 'style',
    label: 'Style',
    description: '调用 DeepSeek 生成风格文本',
  },
  {
    key: 'summary',
    label: 'Summary',
    description: '汇总结果并封装输出',
  },
]

const blackboardContext = computed(() => latestResponse.value?.context || {})
const traceContext = computed(() => latestResponse.value?.trace || {})

const flowStages = computed(() => {
  return stageDefs.map((stage, index) => {
    let status = 'idle'
    let statusLabel = '待命'

    if (loading.value) {
      if (index < activeStageIndex.value) {
        status = 'completed'
        statusLabel = '已完成'
      } else if (index === activeStageIndex.value) {
        status = 'active'
        statusLabel = '执行中'
      } else {
        status = 'pending'
        statusLabel = '等待中'
      }
    } else if (latestResponse.value) {
      status = 'completed'
      statusLabel = '已完成'
    }

    return {
      ...stage,
      status,
      statusLabel,
    }
  })
})

function startFlowAnimation() {
  stopFlowAnimation()
  activeStageIndex.value = 0
  progressTimer = window.setInterval(() => {
    if (activeStageIndex.value < stageDefs.length - 1) {
      activeStageIndex.value += 1
    }
  }, 650)
}

function stopFlowAnimation() {
  if (progressTimer) {
    window.clearInterval(progressTimer)
    progressTimer = null
  }
}

async function submitChat(userInput) {
  errorMessage.value = ''
  loading.value = true
  startFlowAnimation()

  messages.value.push({
    id: Date.now(),
    role: 'user',
    content: userInput,
  })

  try {
    const response = await postChat({
      user_input: userInput,
      user_id: 'course_demo_user',
    })

    latestResponse.value = response
    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: response.final_response,
    })
  } catch (error) {
    errorMessage.value = error.message || '请求失败'
  } finally {
    loading.value = false
    activeStageIndex.value = stageDefs.length - 1
    stopFlowAnimation()
  }
}

onBeforeUnmount(() => {
  stopFlowAnimation()
})
</script>

<template>
  <div class="page-shell">
    <header class="hero">
      <div>
        <p class="eyebrow">软件体系结构课程设计展示</p>
        <h1>基于多 Agent 协同的汪曾祺文学人格生成系统</h1>
        <p class="hero-text">
          解构笔墨闲情，复刻温润心性，让汪曾祺的性情、风骨与人间烟火，再度重生。
        </p>
      </div>
      <div class="hero-side">
        <div class="hero-badge">Vue3 + FastAPI</div>
        <div class="hero-badge">Blackboard Architecture</div>
      </div>
    </header>

    <main class="dashboard">
      <section class="left-column">
        <AgentFlow :stages="flowStages" />
        <BlackboardPanel :context="blackboardContext" />
      </section>

      <section class="right-column">
        <ChatWindow :messages="messages" />
        <ChatComposer :loading="loading" @submit="submitChat" />
        <TracePanel :trace="traceContext" />
      </section>
    </main>

    <div v-if="errorMessage" class="error-banner">
      {{ errorMessage }}
    </div>
  </div>
</template>

<style scoped>
.page-shell {
  max-width: 1460px;
  margin: 0 auto;
  padding: 24px 20px 36px;
  position: relative;
}

.page-shell::before {
  content: '';
  position: fixed;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(244, 251, 241, 0.72), rgba(244, 251, 241, 0.56)),
    url('/bk.jpg') center center / cover no-repeat;
  pointer-events: none;
  z-index: -2;
}

.page-shell::after {
  content: '';
  position: fixed;
  inset: 0;
  background:
    radial-gradient(circle at 18% 15%, rgba(178, 228, 165, 0.22), transparent 28%),
    radial-gradient(circle at 82% 18%, rgba(153, 210, 144, 0.16), transparent 24%);
  pointer-events: none;
  z-index: -1;
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 22px 26px;
  border: 1px solid rgba(207, 230, 199, 0.9);
  border-radius: 28px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.8), rgba(233, 247, 226, 0.68));
  box-shadow: var(--shadow);
}

.eyebrow {
  margin: 0 0 10px;
  color: var(--brand-deep);
  letter-spacing: 0.08em;
  font-size: 13px;
}

.hero h1 {
  margin: 0;
  font-size: 34px;
  line-height: 1.2;
}

.hero-text {
  margin: 14px 0 0;
  max-width: 820px;
  color: var(--muted);
  line-height: 1.8;
}

.hero-side {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 12px;
}

.hero-badge {
  padding: 12px 16px;
  border-radius: 16px;
  background: rgba(121, 196, 106, 0.16);
  color: var(--brand-deep);
  white-space: nowrap;
}

.dashboard {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  margin-top: 18px;
  align-items: stretch;
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
}

.right-column {
  overflow: hidden;
}

.dashboard > section {
  min-height: 0;
  height: 100%;
  align-self: stretch;
}

.left-column > *,
.right-column > * {
  min-height: 0;
}

.right-column :deep(.chat-window) {
  flex: 1 1 0;
  min-height: 0;
  overflow: hidden;
}

.right-column :deep(.composer) {
  flex: 0 0 auto;
}

.right-column :deep(.trace-panel) {
  flex: 0 0 auto;
}

.card {
  border: 1px solid var(--line);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.74);
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow);
}

.right-column :deep(.chat-window.card) {
  background-color: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(4px);
}

:deep(.card-head) {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

:deep(.card-head h2) {
  margin: 0;
  font-size: 20px;
  white-space: nowrap;
}

:deep(.hint) {
  color: var(--muted);
  font-size: 13px;
}

:deep(.composer),
:deep(.chat-window),
:deep(.agent-flow),
:deep(.blackboard),
:deep(.trace-panel) {
  padding: 18px;
}

:deep(.composer-row) {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

:deep(.composer-input) {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid rgba(178, 212, 169, 0.95);
  border-radius: 18px;
  resize: none;
  min-height: 52px;
  max-height: 120px;
  background: rgba(250, 255, 248, 0.96);
  color: var(--text);
  line-height: 1.6;
}

:deep(.submit-button) {
  border: none;
  border-radius: 16px;
  min-width: 86px;
  padding: 14px 18px;
  background: linear-gradient(135deg, var(--brand), #a5d98f);
  color: #16311f;
  cursor: pointer;
  flex: 0 0 auto;
}

:deep(.submit-button:disabled) {
  opacity: 0.65;
  cursor: not-allowed;
}

:deep(.message-list) {
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 0;
  flex: 1 1 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 4px;
}

:deep(.message-item) {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

:deep(.message-item.user) {
  align-items: flex-end;
}

:deep(.message-item.assistant) {
  align-items: flex-start;
}

:deep(.message-role) {
  font-size: 12px;
  color: var(--muted);
}

:deep(.message-bubble) {
  max-width: 88%;
  padding: 14px 16px;
  border-radius: 18px;
  line-height: 1.8;
  white-space: pre-wrap;
}

:deep(.message-item.user .message-bubble) {
  background: #dff2d4;
}

:deep(.message-item.assistant .message-bubble) {
  background: #ffffff;
}

:deep(.flow-list) {
  display: grid;
  gap: 12px;
}

:deep(.flow-item) {
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid var(--line);
  background: rgba(250, 255, 248, 0.82);
}

:deep(.flow-item.pending) {
  opacity: 0.72;
}

:deep(.flow-item.active) {
  border-color: var(--brand-deep);
  background: rgba(209, 241, 197, 0.7);
}

:deep(.flow-item.completed) {
  border-color: var(--line-strong);
  background: rgba(224, 245, 214, 0.64);
}

:deep(.flow-top) {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

:deep(.flow-name) {
  font-weight: 700;
}

:deep(.flow-status) {
  color: var(--brand-deep);
  font-size: 13px;
}

:deep(.flow-desc) {
  color: var(--muted);
  font-size: 14px;
}

.error-banner {
  margin-top: 18px;
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid #e4bcbc;
  background: #fff3f1;
  color: #8c4444;
}

@media (max-width: 1080px) {
  .dashboard {
    grid-template-columns: 1fr;
  }

  .hero {
    flex-direction: column;
  }

  .hero-side {
    flex-direction: row;
    flex-wrap: wrap;
  }
}

@media (max-width: 720px) {
  .page-shell {
    padding: 18px 14px 28px;
  }

  .hero {
    padding: 22px 18px;
  }

  .hero h1 {
    font-size: 28px;
  }

  :deep(.composer-row) {
    flex-direction: column;
    align-items: stretch;
  }

  :deep(.submit-button) {
    width: 100%;
  }
}
</style>
