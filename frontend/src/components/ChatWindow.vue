<script setup>
import chatBgUrl from '../assets/chat_bg.jpg'

defineProps({
  messages: {
    type: Array,
    default: () => [],
  },
})

const chatWindowStyle = {
  backgroundImage: `linear-gradient(180deg, rgba(223, 240, 215, 0.42), rgba(210, 232, 202, 0.34)), linear-gradient(180deg, rgba(255, 255, 255, 0.16), rgba(248, 252, 246, 0.12)), url(${chatBgUrl})`,
  backgroundPosition: 'center center',
  backgroundSize: 'cover',
  backgroundRepeat: 'no-repeat',
}
</script>

<template>
  <section class="chat-window card" :style="chatWindowStyle">
    <div class="card-head">
      <h2>聊天界面</h2>
      <span class="hint">展示用户输入与最终文学化输出</span>
    </div>

    <div class="message-list">
      <div
        v-for="message in messages"
        :key="message.id"
        class="message-item"
        :class="message.role"
      >
        <div class="message-role">
          {{ message.role === 'user' ? '用户' : '墨魂' }}
        </div>
        <div class="message-bubble">{{ message.content }}</div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  flex: 1 1 0;
  min-height: 0;
  box-sizing: border-box;
  position: relative;
  backdrop-filter: blur(4px);
  overflow: hidden;
}

.chat-window::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(245, 251, 242, 0.62));
  z-index: 0;
}

.chat-window > * {
  position: relative;
  z-index: 1;
}

.card-head {
  flex: 0 0 auto;
}

.message-list {
  flex: 1 1 0;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}
</style>
