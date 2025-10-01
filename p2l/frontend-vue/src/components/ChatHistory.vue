<template>
  <div class="chat-history-container">
    <!-- 历史记录控制按钮 - 移到顶部 -->
    <div class="history-controls">
      <el-button 
        v-if="chatHistory.length > 1"
        type="primary" 
        @click="toggleHistoryPanel"
        class="history-toggle-btn"
        :icon="showHistoryPanel ? 'ArrowUp' : 'ArrowDown'"
      >
        {{ showHistoryPanel ? '返回当前对话' : `查看历史记录 (${chatHistory.length - 1})` }}
      </el-button>
    </div>

    <!-- 当前最新对话显示区域 -->
    <div v-if="chatHistory.length > 0 && !showHistoryPanel" class="current-chat">
      <el-card shadow="hover" class="current-chat-card">
        <template #header>
          <div class="current-header">
            <div class="current-title">
              <el-icon class="header-icon"><ChatDotRound /></el-icon>
              <span>当前对话</span>
              <el-tag size="small" type="success">{{ latestChat.model }}</el-tag>
            </div>
            <div class="current-meta">
              <span class="chat-time">{{ formatTime(latestChat.timestamp) }}</span>
              <span class="chat-cost">${{ latestChat.cost.toFixed(4) }}</span>
            </div>
          </div>
        </template>
        
        <div class="current-content">
          <div class="content-section">
            <div class="section-header">
              <el-icon><User /></el-icon>
              <span>问题</span>
            </div>
            <div class="section-content user-content">{{ latestChat.prompt }}</div>
          </div>
          
          <div class="content-section">
            <div class="section-header">
              <el-icon><Robot /></el-icon>
              <span>回答 ({{ latestChat.tokens }} tokens)</span>
            </div>
            <div class="section-content ai-content" v-html="formatResponse(latestChat.response)"></div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 历史记录面板 - 替换当前对话 -->
    <div v-if="showHistoryPanel && chatHistory.length > 1" class="history-panel">
        <el-card shadow="hover" class="history-card">
          <template #header>
            <div class="history-header">
              <div class="history-title">
                <el-icon><History /></el-icon>
                <span>历史对话记录</span>
                <el-badge :value="historicalChats.length" class="history-badge" />
              </div>
              <div class="history-actions">
                <el-button 
                  type="text" 
                  size="small"
                  @click="clearHistory"
                  class="clear-btn"
                >
                  <el-icon><Delete /></el-icon>
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
              class="search-input"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
          
          <!-- 历史记录列表 -->
          <div class="history-list">
            <div v-if="filteredHistoricalChats.length === 0" class="no-results">
              <el-empty description="没有找到匹配的历史记录" />
            </div>
            
            <div v-else class="history-items">
              <div 
                v-for="(chat, index) in filteredHistoricalChats" 
                :key="chat.id"
                class="history-item"
                :class="{ 'expanded': expandedItems.has(chat.id) }"
              >
                <div class="item-header" @click="toggleItemExpansion(chat.id)">
                  <div class="item-info">
                    <div class="item-title">{{ truncateText(chat.prompt, 60) }}</div>
                    <div class="item-meta">
                      <el-tag size="small" type="info">{{ chat.model }}</el-tag>
                      <span class="item-time">{{ formatTime(chat.timestamp) }}</span>
                      <span class="item-cost">${{ chat.cost.toFixed(4) }}</span>
                      <span class="item-tokens">{{ chat.tokens }} tokens</span>
                    </div>
                  </div>
                  <el-icon class="expand-icon" :class="{ 'rotated': expandedItems.has(chat.id) }">
                    <ArrowDown />
                  </el-icon>
                </div>
                
                <!-- 展开的详细内容 -->
                <el-collapse-transition>
                  <div v-if="expandedItems.has(chat.id)" class="item-content">
                    <div class="content-section">
                      <div class="section-header">
                        <el-icon><User /></el-icon>
                        <span>问题</span>
                      </div>
                      <div class="section-content user-content">{{ chat.prompt }}</div>
                    </div>
                    
                    <div class="content-section">
                      <div class="section-header">
                        <el-icon><Robot /></el-icon>
                        <span>回答</span>
                      </div>
                      <div class="section-content ai-content" v-html="formatResponse(chat.response)"></div>
                    </div>
                  </div>
                </el-collapse-transition>
              </div>
            </div>
          </div>
        </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, defineProps, defineEmits } from 'vue'

const props = defineProps({
  chatHistory: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['show-examples', 'clear-history'])

// 控制历史记录面板显示
const showHistoryPanel = ref(false)
const searchKeyword = ref('')
const expandedItems = ref(new Set())

// 最新的对话
const latestChat = computed(() => {
  return props.chatHistory.length > 0 ? props.chatHistory[props.chatHistory.length - 1] : null
})

// 历史对话（除了最新的）
const historicalChats = computed(() => {
  if (props.chatHistory.length <= 1) return []
  return [...props.chatHistory].slice(0, -1).reverse() // 除了最新的，其他按时间倒序
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

// 切换历史记录面板
const toggleHistoryPanel = () => {
  showHistoryPanel.value = !showHistoryPanel.value
  // 如果关闭面板，清空搜索和展开状态
  if (!showHistoryPanel.value) {
    searchKeyword.value = ''
    expandedItems.value.clear()
  }
}

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
  showHistoryPanel.value = false
}

const handleShowExamples = () => {
  emit('show-examples')
}

// 截断文本
const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`
  
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
}

const formatResponse = (response) => {
  // 检查response是否存在
  if (!response || typeof response !== 'string') {
    return '暂无回复内容'
  }
  
  // 简单的代码高亮处理
  return response
    .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="code-block"><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    .replace(/\n/g, '<br>')
}

// 暴露滚动到底部的方法
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
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
  gap: 16px;
  height: 100%;
  min-height: 0; /* 允许收缩 */
  overflow: hidden;
  position: relative; /* 为覆盖层提供定位基准 */
}

/* 当前对话区域 */
.current-chat {
  flex-shrink: 0;
}

.current-chat-card {
  border: 2px solid #67c23a;
  background: linear-gradient(135deg, #f0f9ff 0%, #f6ffed 100%);
  box-shadow: 0 4px 16px rgba(103, 194, 58, 0.2);
}

.current-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.current-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  color: #303133;
}

.header-icon {
  font-size: 18px;
  color: #67c23a;
}

.current-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
}

.chat-time {
  color: #909399;
}

.chat-cost {
  color: #f56c6c;
  font-weight: 500;
}

.current-content {
  padding: 0;
}

/* 历史记录控制按钮 */
.history-controls {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-shrink: 0;
  margin-bottom: 16px; /* 与下方内容保持间距 */
}

.history-toggle-btn {
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s ease;
  min-width: 200px; /* 确保按钮有足够宽度显示文字 */
}

.history-toggle-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

/* 历史记录面板 */
.history-panel {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.history-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: hidden;
  min-height: 0;
  /* 与左侧模型排名保持一致的高度 */
  height: 600px;
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
  color: #303133;
}

.history-badge {
  margin-left: 8px;
}

.history-actions {
  display: flex;
  gap: 8px;
}

.clear-btn {
  padding: 4px 8px;
  font-size: 12px;
  color: #f56c6c;
}

.clear-btn:hover {
  color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

/* 搜索区域 */
.search-section {
  margin-bottom: 16px;
  flex-shrink: 0;
}

.search-input {
  width: 100%;
}

/* 历史记录列表 */
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
  background: #f1f1f1;
  border-radius: 3px;
}

.history-items::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.history-items::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 历史记录项 */
.history-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  margin-bottom: 12px;
  background: #fff;
  transition: all 0.3s ease;
  overflow: hidden;
}

.history-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.history-item.expanded {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
}

.item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.item-header:hover {
  background: #f8f9fa;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
  line-height: 1.4;
  word-break: break-word;
  font-size: 14px;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  flex-wrap: wrap;
}

.item-time {
  color: #909399;
}

.item-cost {
  color: #f56c6c;
  font-weight: 500;
}

.item-tokens {
  color: #67c23a;
  font-weight: 500;
}

.expand-icon {
  font-size: 16px;
  color: #909399;
  transition: transform 0.3s ease;
  margin-left: 12px;
  flex-shrink: 0;
}

.expand-icon.rotated {
  transform: rotate(180deg);
}

.item-content {
  border-top: 1px solid #f0f0f0;
  padding: 16px;
  background: #fafafa;
}

/* 内容区域 */
.content-section {
  margin-bottom: 16px;
}

.content-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-weight: 500;
  color: #606266;
  font-size: 13px;
}

.section-content {
  padding: 12px;
  border-radius: 6px;
  line-height: 1.6;
  font-size: 14px;
  word-break: break-word;
}

.user-content {
  background: #f0f9ff;
  border: 1px solid #d4edda;
  color: #303133;
}

.ai-content {
  background: #f6ffed;
  border: 1px solid #b3d8ff;
  color: #303133;
}

/* 代码样式 */
:deep(.code-block) {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 10px 0;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 13px;
}

:deep(.inline-code) {
  background: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 13px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .current-header {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
  
  .current-meta {
    align-self: flex-end;
  }
  
  .item-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .history-controls {
    flex-direction: column;
  }
  
  .history-toggle-btn,
  .examples-btn {
    width: 100%;
  }
}

/* 动画效果 */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.history-panel {
  animation: slideDown 0.3s ease-out;
}
</style>