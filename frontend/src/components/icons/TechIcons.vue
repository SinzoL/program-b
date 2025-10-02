<template>
  <div>
    <!-- 性能优先图标 -->
    <svg v-if="name === 'performance'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" :fill="color" stroke="currentColor" stroke-width="1"/>
      <circle cx="12" cy="12" r="3" :fill="color" opacity="0.3"/>
      <path d="M12 7V17M7 12H17" stroke="currentColor" stroke-width="1" opacity="0.5"/>
    </svg>

    <!-- 成本优先图标 -->
    <svg v-else-if="name === 'cost'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.1"/>
      <path d="M12 6V8M12 16V18M8.5 9.5C8.5 8.11929 9.61929 7 11 7H13C14.3807 7 15.5 8.11929 15.5 9.5C15.5 10.8807 14.3807 12 13 12H11C9.61929 12 8.5 13.1193 8.5 14.5C8.5 15.8807 9.61929 17 11 17H13C14.3807 17 15.5 15.8807 15.5 14.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <circle cx="12" cy="12" r="2" :fill="color" opacity="0.3"/>
    </svg>

    <!-- 速度优先图标 - 科技闪电 -->
    <svg v-else-if="name === 'speed'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" :fill="color" stroke="currentColor" stroke-width="1.5"/>
      <path d="M8 8L16 16M16 8L8 16" stroke="currentColor" stroke-width="0.8" opacity="0.4"/>
      <circle cx="12" cy="8" r="1.5" :fill="color" opacity="0.8"/>
      <circle cx="12" cy="16" r="1.5" :fill="color" opacity="0.8"/>
      <path d="M6 12L18 12" stroke="currentColor" stroke-width="2" opacity="0.6"/>
    </svg>

    <!-- 火箭图标 - 科技火箭 -->
    <svg v-else-if="name === 'rocket'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L15 8L22 9L16 15L17 22L12 19L7 22L8 15L2 9L9 8L12 2Z" :fill="color" opacity="0.2" stroke="currentColor" stroke-width="1"/>
      <ellipse cx="12" cy="10" rx="3" ry="6" :fill="color" opacity="0.4"/>
      <circle cx="12" cy="8" r="2" :fill="color"/>
      <path d="M9 16L12 19L15 16" stroke="currentColor" stroke-width="2" :stroke="color"/>
      <path d="M8 12L16 12M10 14L14 14" stroke="currentColor" stroke-width="1" opacity="0.6"/>
    </svg>

    <!-- 平衡模式图标 - 科技处理器 -->
    <svg v-else-if="name === 'balanced'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="7" y="7" width="10" height="10" rx="2" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.1"/>
      <rect x="9" y="9" width="6" height="6" rx="1" stroke="currentColor" stroke-width="1" :fill="color" opacity="0.3"/>
      <circle cx="12" cy="12" r="1.5" :fill="color"/>
      <path d="M12 3V7M12 17V21M3 12H7M17 12H21" stroke="currentColor" stroke-width="2"/>
      <path d="M9 3V7M15 3V7M9 17V21M15 17V21M3 9H7M3 15H7M17 9H21M17 15H21" stroke="currentColor" stroke-width="1" opacity="0.6"/>
      <circle cx="10.5" cy="10.5" r="0.5" :fill="color" opacity="0.8"/>
      <circle cx="13.5" cy="10.5" r="0.5" :fill="color" opacity="0.8"/>
      <circle cx="10.5" cy="13.5" r="0.5" :fill="color" opacity="0.8"/>
      <circle cx="13.5" cy="13.5" r="0.5" :fill="color" opacity="0.8"/>
    </svg>

    <!-- 平衡图标 - 备用 -->
    <svg v-else-if="name === 'balance'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M9 12L12 9L15 12M9 12L12 15L15 12M9 12H15" stroke="currentColor" stroke-width="2" :stroke="color"/>
      <circle cx="12" cy="12" r="8" stroke="currentColor" stroke-width="1.5" fill="none" opacity="0.3"/>
      <circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1" :fill="color" opacity="0.2"/>
      <circle cx="12" cy="12" r="1" :fill="color"/>
      <path d="M12 4V8M12 16V20M4 12H8M16 12H20" stroke="currentColor" stroke-width="1" opacity="0.5"/>
    </svg>

    <!-- CPU处理器图标 -->
    <svg v-else-if="name === 'cpu'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="6" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.1"/>
      <rect x="8" y="8" width="8" height="8" rx="1" stroke="currentColor" stroke-width="1" :fill="color" opacity="0.3"/>
      <path d="M9 2V6M12 2V6M15 2V6M9 18V22M12 18V22M15 18V22M2 9H6M2 12H6M2 15H6M18 9H22M18 12H22M18 15H22" stroke="currentColor" stroke-width="1"/>
      <circle cx="12" cy="12" r="1.5" :fill="color"/>
    </svg>

    <!-- 神经网络图标 -->
    <svg v-else-if="name === 'neural'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="6" cy="6" r="2" :fill="color" stroke="currentColor" stroke-width="1"/>
      <circle cx="18" cy="6" r="2" :fill="color" stroke="currentColor" stroke-width="1"/>
      <circle cx="6" cy="18" r="2" :fill="color" stroke="currentColor" stroke-width="1"/>
      <circle cx="18" cy="18" r="2" :fill="color" stroke="currentColor" stroke-width="1"/>
      <circle cx="12" cy="12" r="2" :fill="color" stroke="currentColor" stroke-width="1"/>
      <path d="M8 6L10 12M16 6L14 12M8 18L10 12M16 18L14 12" stroke="currentColor" stroke-width="1" opacity="0.6"/>
      <path d="M6 8L6 16M18 8L18 16" stroke="currentColor" stroke-width="1" opacity="0.3"/>
    </svg>

    <!-- 分析图标 -->
    <svg v-else-if="name === 'analyze'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 3V21H21" stroke="currentColor" stroke-width="1.5"/>
      <path d="M7 14L12 9L16 13L20 9" stroke="currentColor" stroke-width="2" :stroke="color"/>
      <circle cx="7" cy="14" r="2" :fill="color"/>
      <circle cx="12" cy="9" r="2" :fill="color"/>
      <circle cx="16" cy="13" r="2" :fill="color"/>
      <circle cx="20" cy="9" r="2" :fill="color"/>
      <path d="M7 14V20M12 9V20M16 13V20M20 9V20" stroke="currentColor" stroke-width="0.5" opacity="0.3"/>
    </svg>

    <!-- 监控图标 -->
    <svg v-else-if="name === 'monitor'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="4" width="20" height="12" rx="2" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.1"/>
      <path d="M6 8L8 10L10 8L12 10L14 8L16 10L18 8" stroke="currentColor" stroke-width="1.5" :stroke="color"/>
      <circle cx="12" cy="12" r="1" :fill="color"/>
      <path d="M8 20H16M12 16V20" stroke="currentColor" stroke-width="1.5"/>
    </svg>

    <!-- 编辑图标 -->
    <svg v-else-if="name === 'edit'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 20H21" stroke="currentColor" stroke-width="1.5"/>
      <path d="M16.5 3.5C17.3284 2.67157 18.6716 2.67157 19.5 3.5C20.3284 4.32843 20.3284 5.67157 19.5 6.5L7 19L3 20L4 16L16.5 3.5Z" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.2"/>
      <circle cx="17" cy="5" r="1" :fill="color"/>
      <path d="M15 7L17 9" stroke="currentColor" stroke-width="1"/>
    </svg>

    <!-- 魔法棒图标 -->
    <svg v-else-if="name === 'magic'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M15 4V2M15 16V14M8 9H10M20 9H22M17.8 7.8L19.2 6.4M17.8 10.2L19.2 11.6M12.2 7.8L10.8 6.4M12.2 10.2L10.8 11.6" stroke="currentColor" stroke-width="1"/>
      <path d="M15 9C16.1046 9 17 8.10457 17 7C17 5.89543 16.1046 5 15 5C13.8954 5 13 5.89543 13 7C13 8.10457 13.8954 9 15 9Z" :fill="color"/>
      <path d="M2 22L22 2" stroke="currentColor" stroke-width="2" :stroke="color"/>
      <circle cx="6" cy="18" r="2" :fill="color" opacity="0.6"/>
      <circle cx="4" cy="20" r="1" :fill="color"/>
    </svg>

    <!-- 清除图标 -->
    <svg v-else-if="name === 'clear'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 6H5H21" stroke="currentColor" stroke-width="1.5"/>
      <path d="M8 6V4C8 3.44772 8.44772 3 9 3H15C15.5523 3 16 3.44772 16 4V6M19 6V20C19 20.5523 18.5523 21 18 21H6C5.44772 21 5 20.5523 5 20V6H19Z" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.1"/>
      <path d="M10 11V17M14 11V17" stroke="currentColor" stroke-width="1.5"/>
    </svg>

    <!-- 问题图标 -->
    <svg v-else-if="name === 'question'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.1"/>
      <path d="M9.09 9C9.3251 8.33167 9.78915 7.76811 10.4 7.40913C11.0108 7.05016 11.7289 6.91894 12.4272 7.03871C13.1255 7.15849 13.7588 7.52152 14.2151 8.06353C14.6713 8.60553 14.9211 9.29152 14.92 10C14.92 12 11.92 13 11.92 13" stroke="currentColor" stroke-width="1.5"/>
      <circle cx="12" cy="17" r="1" :fill="color"/>
    </svg>

    <!-- 聊天图标 -->
    <svg v-else-if="name === 'chat'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.1"/>
      <path d="M8 9H16M8 13H12" stroke="currentColor" stroke-width="1"/>
    </svg>

    <!-- 机器人图标 -->
    <svg v-else-if="name === 'robot'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="8" width="12" height="10" rx="3" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.1"/>
      <circle cx="12" cy="6" r="2" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.3"/>
      <circle cx="9" cy="12" r="1" :fill="color"/>
      <circle cx="15" cy="12" r="1" :fill="color"/>
      <path d="M9 15H15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M6 11H4M20 11H18M6 15H4M20 15H18" stroke="currentColor" stroke-width="1"/>
    </svg>

    <!-- 网络图标 -->
    <svg v-else-if="name === 'network'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="3" :fill="color" stroke="currentColor" stroke-width="1.5"/>
      <circle cx="6" cy="6" r="2" :fill="color" opacity="0.6" stroke="currentColor" stroke-width="1"/>
      <circle cx="18" cy="6" r="2" :fill="color" opacity="0.6" stroke="currentColor" stroke-width="1"/>
      <circle cx="6" cy="18" r="2" :fill="color" opacity="0.6" stroke="currentColor" stroke-width="1"/>
      <circle cx="18" cy="18" r="2" :fill="color" opacity="0.6" stroke="currentColor" stroke-width="1"/>
      <path d="M8.5 7.5L10.5 10.5M15.5 7.5L13.5 10.5M8.5 16.5L10.5 13.5M15.5 16.5L13.5 13.5" stroke="currentColor" stroke-width="1.5" opacity="0.7"/>
      <path d="M12 9V15M9 12H15" stroke="currentColor" stroke-width="1" opacity="0.5"/>
    </svg>

    <!-- 分析统计图标 -->
    <svg v-else-if="name === 'analytics'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 3V21H21" stroke="currentColor" stroke-width="1.5"/>
      <rect x="5" y="14" width="3" height="6" :fill="color" opacity="0.6"/>
      <rect x="9" y="10" width="3" height="10" :fill="color" opacity="0.7"/>
      <rect x="13" y="6" width="3" height="14" :fill="color" opacity="0.8"/>
      <rect x="17" y="8" width="3" height="12" :fill="color" opacity="0.9"/>
      <path d="M6.5 14L10.5 10L14.5 6L18.5 8" stroke="currentColor" stroke-width="2" :stroke="color"/>
      <circle cx="6.5" cy="14" r="1.5" :fill="color"/>
      <circle cx="10.5" cy="10" r="1.5" :fill="color"/>
      <circle cx="14.5" cy="6" r="1.5" :fill="color"/>
      <circle cx="18.5" cy="8" r="1.5" :fill="color"/>
    </svg>

    <!-- 设置图标 -->
    <svg v-else-if="name === 'settings'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.3"/>
      <path d="M12 1V3M12 21V23M4.22 4.22L5.64 5.64M18.36 18.36L19.78 19.78M1 12H3M21 12H23M4.22 19.78L5.64 18.36M18.36 5.64L19.78 4.22" stroke="currentColor" stroke-width="1.5"/>
      <path d="M12 7C14.7614 7 17 9.23858 17 12C17 14.7614 14.7614 17 12 17C9.23858 17 7 14.7614 7 12C7 9.23858 9.23858 7 12 7Z" stroke="currentColor" stroke-width="1" fill="none"/>
      <circle cx="12" cy="12" r="1" :fill="color"/>
    </svg>

    <!-- 芯片图标 -->
    <svg v-else-if="name === 'chip'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="6" y="6" width="12" height="12" rx="2" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.1"/>
      <rect x="8" y="8" width="8" height="8" rx="1" stroke="currentColor" stroke-width="1" :fill="color" opacity="0.3"/>
      <circle cx="12" cy="12" r="2" :fill="color"/>
      <path d="M9 2V6M12 2V6M15 2V6M9 18V22M12 18V22M15 18V22M2 9H6M2 12H6M2 15H6M18 9H22M18 12H22M18 15H22" stroke="currentColor" stroke-width="1"/>
      <circle cx="10" cy="10" r="0.5" :fill="color" opacity="0.8"/>
      <circle cx="14" cy="10" r="0.5" :fill="color" opacity="0.8"/>
      <circle cx="10" cy="14" r="0.5" :fill="color" opacity="0.8"/>
      <circle cx="14" cy="14" r="0.5" :fill="color" opacity="0.8"/>
    </svg>

    <!-- 大脑图标 -->
    <svg v-else-if="name === 'brain'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M9.5 2C7.01 2 5 4.01 5 6.5C5 8.99 7.01 11 9.5 11H14.5C16.99 11 19 8.99 19 6.5C19 4.01 16.99 2 14.5 2C13.76 2 13.07 2.19 12.47 2.53C11.93 2.19 11.24 2 10.5 2H9.5Z" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.2"/>
      <path d="M9.5 13C7.01 13 5 15.01 5 17.5C5 19.99 7.01 22 9.5 22H14.5C16.99 22 19 19.99 19 17.5C19 15.01 16.99 13 14.5 13" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.2"/>
      <path d="M12 11V13" stroke="currentColor" stroke-width="2" :stroke="color"/>
      <circle cx="10" cy="7" r="1" :fill="color"/>
      <circle cx="14" cy="7" r="1" :fill="color"/>
      <circle cx="10" cy="17" r="1" :fill="color"/>
      <circle cx="14" cy="17" r="1" :fill="color"/>
    </svg>

    <!-- 数据库图标 -->
    <svg v-else-if="name === 'database'" :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="12" cy="5" rx="9" ry="3" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.2"/>
      <path d="M21 12C21 13.66 16.97 15 12 15S3 13.66 3 12" stroke="currentColor" stroke-width="1.5"/>
      <path d="M3 5V19C3 20.66 7.03 22 12 22S21 20.66 21 19V5" stroke="currentColor" stroke-width="1.5"/>
      <path d="M21 12C21 13.66 16.97 15 12 15S3 13.66 3 12" stroke="currentColor" stroke-width="1.5"/>
      <ellipse cx="12" cy="12" rx="6" ry="2" :fill="color" opacity="0.3"/>
      <ellipse cx="12" cy="19" rx="6" ry="2" :fill="color" opacity="0.3"/>
      <circle cx="12" cy="5" r="1" :fill="color"/>
    </svg>

    <!-- 默认图标 -->
    <svg v-else :width="size" :height="size" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" :fill="color" opacity="0.2"/>
    </svg>
  </div>
</template>

<script setup>
defineProps({
  name: {
    type: String,
    required: true
  },
  size: {
    type: [String, Number],
    default: 24
  },
  color: {
    type: String,
    default: '#409eff'
  }
})
</script>

<style scoped>
svg {
  display: inline-block;
  vertical-align: middle;
}
</style>