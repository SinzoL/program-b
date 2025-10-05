<template>
  <div class="history-panel">
    <el-card shadow="hover" class="history-card tech-card">
      <template #header>
        <div class="history-header">
          <div class="history-title">
            <TechIcons name="database" :size="20" color="#00d4ff" />
            <span>历史对话记录</span>
            <el-badge :value="historicalChats.length" class="history-badge tech-badge" />
          </div>
          <div class="history-actions">
            <el-button 
              type="text" 
              size="small"
              @click="clearHistory"
              class="clear-btn tech-btn"
            >
              <TechIcons name="settings" :size="14" color="#ff6b6b" />
              清空历史
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 搜索框 -->
      <div class="search-section">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索历史对话..."
          size="default"
          class="search-input tech-input"
          clearable
        >
          <template #prefix>
            <TechIcons name="analytics" :size="16" color="#00d4ff" />
          </template>
        </el-input>
      </div>
      
      <!-- 历史记录列表 -->
      <div class="history-list">
        <div v-if="filteredHistoricalChats.length === 0" class="no-results">
          <div class="empty-state">
            <div class="empty-icon-container">
              <CubeLogo :size="48" color="#4A90E2" variant="default" :animate="true" class="empty-icon" />
              <div class="empty-glow"></div>
            </div>
            <h3 class="empty-title">
              {{ searchKeyword ? '未找到匹配记录' : '暂无对话历史' }}
            </h3>
            <p class="empty-description">
              {{ searchKeyword 
                ? '尝试调整搜索关键词或清空搜索条件' 
                : '开始您的第一次对话，创建智能交互体验' 
              }}
            </p>
            <div class="empty-actions" v-if="searchKeyword">
              <el-button 
                type="primary" 
                size="small" 
                @click="searchKeyword = ''"
                class="tech-button"
              >
                <TechIcons name="analytics" :size="14" />
                清空搜索
              </el-button>
            </div>
          </div>
        </div>
        
        <div v-else class="history-items">
          <ChatHistoryItem
            v-for="chat in filteredHistoricalChats"
            :key="chat.id"
            :chat="chat"
            :is-expanded="expandedItems.has(chat.id)"
            @toggle-expansion="toggleItemExpansion"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import TechIcons from '../icons/TechIcons.vue'
import ChatHistoryItem from './ChatHistoryItem.vue'
import CubeLogo from '../icons/CubeLogo.vue'

const props = defineProps({
  chatHistory: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['clear-history'])

const searchKeyword = ref('')
const expandedItems = ref(new Set())

// 历史对话（所有对话记录，按时间倒序）
const historicalChats = computed(() => {
  if (props.chatHistory.length === 0) return []
  return [...props.chatHistory].reverse()
})

// 过滤的历史记录（搜索功能）
const filteredHistoricalChats = computed(() => {
  if (!searchKeyword.value.trim()) {
    return historicalChats.value
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  return historicalChats.value.filter(chat => 
    chat.prompt.toLowerCase().includes(keyword) ||
    chat.response.toLowerCase().includes(keyword) ||
    chat.model.toLowerCase().includes(keyword)
  )
})

// 切换列表项展开状态
const toggleItemExpansion = (itemId) => {
  if (expandedItems.value.has(itemId)) {
    expandedItems.value.delete(itemId)
  } else {
    expandedItems.value.add(itemId)
  }
}

// 清空历史记录
const clearHistory = () => {
  emit('clear-history')
  expandedItems.value.clear()
}
</script>

<style scoped>
.history-panel {
  height: 100%;
  overflow: hidden;
}

.history-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(0, 212, 255, 0.3);
  background: linear-gradient(135deg, rgba(15, 15, 35, 0.05), rgba(0, 212, 255, 0.02));
  box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);
}

.history-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: hidden;
  min-height: 0;
  height: calc(100% - 60px);
  background: rgba(15, 15, 35, 0.02);
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #00d4ff;
}

.tech-badge :deep(.el-badge__content) {
  background: linear-gradient(135deg, #00d4ff, #0099cc);
  border: none;
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.3);
}

.history-actions {
  display: flex;
  gap: 8px;
}

.clear-btn {
  padding: 6px 12px;
  font-size: 12px;
  color: #ff6b6b;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(255, 107, 107, 0.05));
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: 6px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.clear-btn:hover {
  color: #ff6b6b;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(255, 107, 107, 0.1));
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
  transform: translateY(-1px);
}

.search-section {
  margin-bottom: 16px;
  flex-shrink: 0;
}

.tech-input :deep(.el-input__wrapper) {
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.02));
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 212, 255, 0.1);
  transition: all 0.3s ease;
}

.tech-input :deep(.el-input__wrapper:hover) {
  border-color: #00d4ff;
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.2);
}

.tech-input :deep(.el-input__wrapper.is-focus) {
  border-color: #00ff88;
  box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2);
}

.history-list {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.no-results {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.empty-state {
  text-align: center;
  max-width: 320px;
  margin: 0 auto;
}

.empty-icon-container {
  position: relative;
  display: inline-block;
  margin-bottom: 24px;
}

.empty-icon {
  position: relative;
  z-index: 2;
  filter: drop-shadow(0 4px 12px rgba(74, 144, 226, 0.4));
}

.empty-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  background: radial-gradient(circle, rgba(74, 144, 226, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  animation: empty-glow-pulse 3s ease-in-out infinite;
  z-index: 1;
}

@keyframes empty-glow-pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.6;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0.3;
  }
}

.empty-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #4A90E2;
  margin: 0 0 12px 0;
  background: linear-gradient(45deg, #4A90E2, #00d4ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.empty-description {
  font-size: 0.9rem;
  color: #888;
  line-height: 1.5;
  margin: 0 0 24px 0;
}

.empty-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.tech-button {
  background: linear-gradient(135deg, #4A90E2, #00d4ff);
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  color: white;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
}

.tech-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(74, 144, 226, 0.4);
  background: linear-gradient(135deg, #5BA0F2, #10E4FF);
}

.tech-button:active {
  transform: translateY(0);
}

.history-items {
  flex: 1;
  overflow-y: auto;
  padding-right: 8px;
}

/* 自定义滚动条 */
.history-items::-webkit-scrollbar {
  width: 6px;
}

.history-items::-webkit-scrollbar-track {
  background: rgba(0, 212, 255, 0.1);
  border-radius: 3px;
}

.history-items::-webkit-scrollbar-thumb {
  background: rgba(0, 212, 255, 0.5);
  border-radius: 3px;
}

.history-items::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 212, 255, 0.7);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .history-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
  
  .history-actions {
    align-self: flex-end;
  }
}
</style>