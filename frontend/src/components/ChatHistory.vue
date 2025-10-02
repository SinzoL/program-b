<template>
  <div class="chat-history-container tech-container">
    <!-- Tab切换界面 -->
    <el-tabs v-model="activeTab" class="chat-tabs tech-tabs" type="border-card">
      <!-- 当前对话Tab -->
      <el-tab-pane label="当前对话" name="current" class="tab-pane">
        <template #label>
          <span class="tab-label">
            <TechIcons name="brain" :size="16" color="#00d4ff" />
            当前对话
          </span>
        </template>
        
        <div class="current-chat">
          <!-- 空状态：显示占位符 -->
          <ChatPlaceholder v-if="chatHistory.length === 0" />
          
          <!-- 有对话记录时显示最新对话 -->
          <ChatCurrentView v-else-if="latestChat" :chat="latestChat" />
        </div>
      </el-tab-pane>

      <!-- 历史记录Tab -->
      <el-tab-pane name="history" class="tab-pane">
        <template #label>
          <span class="tab-label">
            <TechIcons name="database" :size="16" color="#00d4ff" />
            历史记录
            <el-badge v-if="chatHistory.length > 0" :value="chatHistory.length" class="tab-badge tech-badge" />
          </span>
        </template>
        
        <ChatHistoryList 
          :chat-history="chatHistory"
          @clear-history="clearHistory"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import TechIcons from './icons/TechIcons.vue'
import ChatPlaceholder from './chat/ChatPlaceholder.vue'
import ChatCurrentView from './chat/ChatCurrentView.vue'
import ChatHistoryList from './chat/ChatHistoryList.vue'

const props = defineProps({
  chatHistory: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['show-examples', 'clear-history'])

// Tab控制
const activeTab = ref('current')

// 最新的对话
const latestChat = computed(() => {
  return props.chatHistory.length > 0 ? props.chatHistory[props.chatHistory.length - 1] : null
})

// 清空历史记录
const clearHistory = () => {
  emit('clear-history')
  activeTab.value = 'current'
}

// 暴露滚动到底部的方法
const scrollToBottom = () => {
  nextTick(() => {
    // 由于组件结构改变，这里可能需要调整
    console.log('Scroll to bottom called')
  })
}

defineExpose({
  scrollToBottom
})
</script>

<style scoped>
/* 主容器 */
.chat-history-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 700px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(15, 15, 35, 0.02), rgba(0, 212, 255, 0.01));
  border-radius: 12px;
  position: relative;
}

.tech-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: 12px;
  pointer-events: none;
  background: linear-gradient(45deg, transparent 49%, rgba(0, 212, 255, 0.1) 50%, transparent 51%);
  background-size: 20px 20px;
  opacity: 0.3;
}

/* Tab容器 */
.chat-tabs {
  height: 100%;
  min-height: 700px;
  display: flex;
  flex-direction: column;
  background: transparent;
  border: none;
}

.tech-tabs :deep(.el-tabs__header) {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 255, 136, 0.05));
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px 8px 0 0;
  margin: 0;
}

.tech-tabs :deep(.el-tabs__nav-wrap) {
  background: transparent;
}

.tech-tabs :deep(.el-tabs__item) {
  color: #666;
  border: none;
  background: transparent;
  transition: all 0.3s ease;
}

.tech-tabs :deep(.el-tabs__item:hover) {
  color: #00d4ff;
}

.tech-tabs :deep(.el-tabs__item.is-active) {
  color: #00ff88;
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 212, 255, 0.05));
  border-bottom: 2px solid #00ff88;
}

.chat-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
  padding: 0;
  min-height: 650px;
  background: rgba(15, 15, 35, 0.01);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-top: none;
  border-radius: 0 0 8px 8px;
}

.chat-tabs :deep(.el-tab-pane) {
  height: 100%;
  min-height: 650px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Tab标签样式 */
.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.tech-badge :deep(.el-badge__content) {
  background: linear-gradient(135deg, #00d4ff, #0099cc);
  border: none;
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.3);
  color: white;
}

/* Tab面板 */
.tab-pane {
  height: 100%;
  overflow: hidden;
}

/* 当前对话区域 */
.current-chat {
  height: 100%;
  min-height: 650px;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-history-container {
    min-height: 600px;
  }
  
  .chat-tabs {
    min-height: 600px;
  }
  
  .chat-tabs :deep(.el-tabs__content) {
    min-height: 550px;
  }
  
  .chat-tabs :deep(.el-tab-pane) {
    min-height: 550px;
  }
  
  .current-chat {
    min-height: 550px;
    padding: 12px;
  }
}

/* 动画效果 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chat-history-container {
  animation: slideIn 0.3s ease-out;
}
</style>