<template>
  <div class="loading-container" :class="{ 'full-screen': fullScreen }">
    <div class="loading-cube-wrapper">
      <CubeLogo 
        :size="size" 
        :color="color" 
        variant="gradient"
        :animate="true"
        class="loading-cube"
      />
      <div class="loading-text" v-if="text">
        {{ text }}
      </div>
      <div class="loading-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  </div>
</template>

<script setup>
import CubeLogo from './icons/CubeLogo.vue'

const props = defineProps({
  size: {
    type: [String, Number],
    default: 48
  },
  color: {
    type: String,
    default: '#4A90E2'
  },
  text: {
    type: String,
    default: '加载中'
  },
  fullScreen: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.loading-container.full-screen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  z-index: 9999;
}

.loading-cube-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-cube {
  filter: drop-shadow(0 4px 12px rgba(74, 144, 226, 0.4));
}

.loading-text {
  color: #4A90E2;
  font-size: 14px;
  font-weight: 500;
  text-align: center;
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4A90E2;
  animation: loading-dots 1.4s infinite ease-in-out;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loading-dots {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.full-screen .loading-text {
  color: white;
}

.full-screen .loading-dots span {
  background: white;
}
</style>