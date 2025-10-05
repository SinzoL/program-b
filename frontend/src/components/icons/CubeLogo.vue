<template>
  <svg 
    :width="size" 
    :height="size" 
    viewBox="0 0 100 100" 
    xmlns="http://www.w3.org/2000/svg"
    class="cube-logo"
    :class="{ 'animate': animate }"
  >
    <!-- 立方体的三个面 -->
    <!-- 顶面 -->
    <path 
      d="M20 30 L50 15 L80 30 L50 45 Z" 
      :fill="topFaceColor"
      :stroke="strokeColor"
      :stroke-width="strokeWidth"
      stroke-linejoin="round"
      class="top-face"
    />
    
    <!-- 左面 -->
    <path 
      d="M20 30 L20 70 L50 85 L50 45 Z" 
      :fill="leftFaceColor"
      :stroke="strokeColor"
      :stroke-width="strokeWidth"
      stroke-linejoin="round"
      class="left-face"
    />
    
    <!-- 右面 -->
    <path 
      d="M50 45 L50 85 L80 70 L80 30 Z" 
      :fill="rightFaceColor"
      :stroke="strokeColor"
      :stroke-width="strokeWidth"
      stroke-linejoin="round"
      class="right-face"
    />
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: [String, Number],
    default: 32
  },
  color: {
    type: String,
    default: '#4A90E2'
  },
  animate: {
    type: Boolean,
    default: false
  },
  variant: {
    type: String,
    default: 'default', // default, light, dark, gradient
    validator: (value) => ['default', 'light', 'dark', 'gradient'].includes(value)
  }
})

// 根据variant计算颜色
const colors = computed(() => {
  switch (props.variant) {
    case 'light':
      return {
        top: '#ffffff',
        left: '#e8e8e8',
        right: '#d0d0d0',
        stroke: '#cccccc'
      }
    case 'dark':
      return {
        top: '#2c3e50',
        left: '#34495e',
        right: '#1a252f',
        stroke: '#1a252f'
      }
    case 'gradient':
      return {
        top: 'url(#topGradient)',
        left: 'url(#leftGradient)',
        right: 'url(#rightGradient)',
        stroke: props.color
      }
    default:
      return {
        top: props.color,
        left: adjustBrightness(props.color, -20),
        right: adjustBrightness(props.color, -40),
        stroke: adjustBrightness(props.color, -10)
      }
  }
})

const topFaceColor = computed(() => colors.value.top)
const leftFaceColor = computed(() => colors.value.left)
const rightFaceColor = computed(() => colors.value.right)
const strokeColor = computed(() => colors.value.stroke)
const strokeWidth = computed(() => props.size > 24 ? 2 : 1.5)

// 调整颜色亮度的辅助函数
function adjustBrightness(color, percent) {
  const num = parseInt(color.replace("#", ""), 16)
  const amt = Math.round(2.55 * percent)
  const R = (num >> 16) + amt
  const G = (num >> 8 & 0x00FF) + amt
  const B = (num & 0x0000FF) + amt
  return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
    (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
    (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1)
}
</script>

<style scoped>
.cube-logo {
  display: inline-block;
  transition: all 0.3s ease;
}

.cube-logo:hover {
  transform: scale(1.1);
}

.cube-logo.animate {
  animation: cube-rotate 3s ease-in-out infinite;
}

.top-face, .left-face, .right-face {
  transition: all 0.3s ease;
}

.cube-logo:hover .top-face {
  filter: brightness(1.1);
}

.cube-logo:hover .left-face {
  filter: brightness(1.05);
}

.cube-logo:hover .right-face {
  filter: brightness(0.95);
}

@keyframes cube-rotate {
  0%, 100% { 
    transform: perspective(200px) rotateX(0deg) rotateY(0deg);
  }
  25% { 
    transform: perspective(200px) rotateX(10deg) rotateY(10deg);
  }
  50% { 
    transform: perspective(200px) rotateX(0deg) rotateY(20deg);
  }
  75% { 
    transform: perspective(200px) rotateX(-10deg) rotateY(10deg);
  }
}

/* 渐变定义 */
.cube-logo svg defs {
  display: none;
}
</style>